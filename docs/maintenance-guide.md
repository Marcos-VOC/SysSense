# Guia Completo de Manutenção do SysSense

Este guia explica a estrutura, o uso e o funcionamento interno do SysSense para permitir manutenção manual com segurança.

Ele foi escrito para quem quer alterar o projeto sem depender de memória da conversa, entendendo não apenas o que existe, mas também como as partes se conectam e como modificar cada uma.

## 1. Visão Mental do Projeto

O SysSense é um aplicativo GTK/libadwaita com três camadas principais:

```text
Coleta de dados  ->  Regras/formatação/configuração  ->  Interface GTK
collectors.py       diagnostics.py/config.py/etc.       window.py + ui/
```

A regra prática é:

- se a mudança envolve buscar dados do sistema, comece por `collectors.py`;
- se a mudança envolve decidir se algo é alerta, comece por `diagnostics.py`;
- se a mudança envolve salvar preferência, comece por `config.py`;
- se a mudança envolve texto ou unidade, comece por `formatters.py`;
- se a mudança envolve tela, comece por `src/syssense/ui/`;
- se a mudança envolve callbacks, timer, threading ou atualização de widgets, veja `window.py`.

## 2. Como Rodar o Projeto

### 2.1 Desenvolvimento

Na raiz do projeto:

```bash
python3 -m pip install -r requirements.txt
./run.sh
```

Ou diretamente:

```bash
PYTHONPATH=src /usr/bin/python3 -m syssense.main
```

### 2.2 Instalação Nativa

```bash
./packaging/native/install.sh
```

Depois:

```bash
syssense
```

### 2.3 Remoção

```bash
./packaging/native/uninstall.sh
```

## 3. Comandos de Validação

Use antes de commits importantes:

```bash
git diff --check
python3 -m compileall src/syssense
python3 -m unittest
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```

Para testar empacotamento Python:

```bash
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
test -f /tmp/syssense-install-test/syssense/resources/styles.css
rm -rf /tmp/syssense-install-test
```

Limpeza:

```bash
rm -rf build src/syssense.egg-info
find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
```

## 4. Estrutura de Diretórios

```text
data/
```

Arquivos de integração desktop:

- `.desktop`;
- ícone;
- AppStream/metainfo.

```text
docs/
```

Documentação do projeto, releases, roadmap, testes e manutenção.

```text
packaging/
```

Scripts de instalação nativa e manifest Flatpak.

```text
src/syssense/
```

Código principal do aplicativo.

```text
tests/
```

Testes unitários com `unittest`.

## 5. Entrada da Aplicação

Arquivo:

```text
src/syssense/main.py
```

Ele cria uma aplicação libadwaita. O padrão usado é:

```python
class SysSenseApplication(Adw.Application):
    def do_activate(self):
        window = SysSenseWindow(self)
        window.present()
```

Quando o usuário executa:

```bash
syssense
```

o entry point definido em `pyproject.toml` chama:

```toml
[project.scripts]
syssense = "syssense.main:main"
```

Para mudar o comando instalado, edite esse bloco.

## 6. Janela Principal

Arquivo:

```text
src/syssense/window.py
```

Classe principal:

```python
class SysSenseWindow(Adw.ApplicationWindow):
```

Responsabilidades:

- carregar CSS;
- montar header bar;
- montar sidebar e páginas;
- iniciar coleta inicial;
- criar timer de atualização;
- executar coletas em threads;
- atualizar widgets no loop GTK;
- aplicar alertas;
- abrir/fechar painéis internos;
- salvar preferências.

### 6.1 Por Que Threads Existem

GTK não deve ser bloqueado. Coletas como CPU, serviços, logs e speedtest podem demorar. Por isso o padrão é:

```python
thread = threading.Thread(target=self._fetch_data, daemon=True)
thread.start()
```

Depois que a thread termina, ela agenda atualização visual no loop principal:

```python
GLib.idle_add(self._on_data_ready, data)
```

Regra importante:

- colete dados na thread;
- altere widgets apenas via callback no loop GTK.

### 6.2 Cache Global

`window.py` mantém:

```python
self.dados_cache = {}
self.lock = threading.Lock()
```

O cache guarda a última visão conhecida do sistema. O lock evita conflito entre thread de coleta e atualização da UI.

### 6.3 Timer de Atualização

O intervalo vem de:

```python
self.user_config["refresh_interval"]
```

Para reiniciar o timer:

```python
GLib.source_remove(self.refresh_timer_id)
self.refresh_timer_id = GLib.timeout_add(interval_ms, self._on_auto_refresh)
```

Se adicionar uma nova métrica que deve atualizar automaticamente, ela precisa entrar no fluxo de coleta e atualização chamado pelo timer.

## 7. Coleta de Dados

Arquivo:

```text
src/syssense/collectors.py
```

As funções retornam dicionários. Exemplo:

```python
def get_memory_info() -> dict[str, Any]:
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "percent": mem.percent,
    }
```

### 7.1 Como Adicionar uma Nova Métrica

1. Crie uma função em `collectors.py`.
2. Retorne um dicionário simples.
3. Trate exceções e retorne fallback seguro.
4. Inclua a chamada no fluxo de coleta em `window.py`.
5. Crie ou atualize widgets em `ui/overview.py` ou outro módulo.
6. Atualize `_update_overview()` ou a função de atualização correspondente.
7. Adicione testes.
8. Atualize documentação.

Exemplo de forma segura:

```python
def get_example_info() -> dict[str, Any]:
    try:
        return {"value": 123}
    except Exception as exc:
        return {"error": str(exc), "value": 0}
```

### 7.2 Comandos Externos

Para comandos como `systemctl` e `journalctl`, use:

```python
_run_readonly_command(["systemctl", "list-units", "--failed"], timeout=5)
```

Não use:

```python
subprocess.run("systemctl ...", shell=True)
```

Motivos:

- `shell=False` reduz risco;
- lista de argumentos evita parsing frágil;
- timeout evita travamento;
- ambiente controlado evita dependência de PATH inesperado.

## 8. Diagnósticos e Alertas

Arquivo:

```text
src/syssense/diagnostics.py
```

As regras ficam em:

```python
REGRAS = [
    {
        "campo": "mem_percent",
        "limite": 85,
        "operador": "gt",
        "severidade": "alta",
        "mensagem": "Memória em uso crítico ({valor}%)."
    }
]
```

### 8.1 Campos Suportados

Atualmente:

- `mem_percent`;
- `disco_percent`;
- `failed_services`;
- `cpu_percent`;
- `swap_percent`.

Para adicionar um campo:

1. Adicione regra em `REGRAS`.
2. Atualize `_avaliar_regra()`.
3. Atualize `_valor_campo()`.
4. Se a mensagem usa placeholder novo, atualize `_formatar_mensagem()`.
5. Adicione teste em `tests/test_diagnostics.py`.

### 8.2 Severidade

Valores usados:

- `alta`;
- `media`;
- `baixa`.

A UI transforma esses níveis em cores/classes CSS.

## 9. Configuração Persistente

Arquivo:

```text
src/syssense/config.py
```

Arquivo gerado no computador do usuário:

```text
~/.config/syssense/config.json
```

### 9.1 Defaults

```python
DEFAULT_CONFIG = {
    "refresh_interval": 2.5,
    "critical_toasts": True,
    "show_speedtest": True,
    "visible_cards": {...},
    "card_order": [...]
}
```

### 9.2 Como Adicionar Uma Preferência

1. Adicione chave em `DEFAULT_CONFIG`.
2. Atualize `normalize_config()`.
3. Se a preferência aparece na UI, edite `ui/preferences.py`.
4. Conecte callback em `window.py`.
5. Salve com `self._save_user_config()`.
6. Adicione teste em `tests/test_config.py`.
7. Documente no README e neste guia.

Exemplo:

```python
config["nova_opcao"] = bool(raw_config.get("nova_opcao", config["nova_opcao"]))
```

## 10. Interface GTK

Interface visual fica principalmente em:

```text
src/syssense/ui/
```

`window.py` chama funções `build_*` que retornam dataclasses de referências.

Exemplo:

```python
refs = build_sidebar(...)
self.sidebar = refs.container
self.nav_buttons = refs.nav_buttons
```

Esse padrão existe porque o módulo de UI cria widgets, mas `window.py` precisa atualizar alguns deles depois.

## 11. Dashboard

Arquivo:

```text
src/syssense/ui/overview.py
```

Função principal:

```python
build_overview_tab(...)
```

Ela cria:

- toolbar de organização;
- `Gtk.FlowBox`;
- card de CPU;
- card de memória;
- card de armazenamento;
- card de temperatura;
- card de rede;
- card de carga;
- card de uptime;
- card de internet.

### 11.1 Como Adicionar Um Card

1. Adicione chave em `config.DEFAULT_CARD_ORDER`.
2. Adicione entrada em `DEFAULT_CONFIG["visible_cards"]`.
3. Adicione label em `CARD_LABELS`.
4. Crie o widget em `build_overview_tab()`.
5. Registre com `_append_overview_card(...)`.
6. Inclua referência na dataclass `OverviewRefs`, se o widget precisar ser atualizado.
7. Em `window.py`, atribua `self.novo_widget = refs.novo_widget`.
8. Atualize `_update_overview()`.
9. Atualize testes de config.
10. Atualize README/spec.

### 11.2 Ordem dos Cards

A ordem fica em:

```python
self.user_config["card_order"]
```

O menu de organização chama:

```python
self._on_card_order_changed(...)
```

Esse método troca posições na lista e salva o config.

## 12. Sidebar

Arquivo:

```text
src/syssense/ui/sidebar.py
```

Ela cria:

- botões de navegação;
- indicador de risco;
- botão de preferências;
- rodapé com intervalo e modo.

Para adicionar uma nova página:

1. Adicione botão na lista de itens da sidebar.
2. Crie a página em `window.py` ou módulo `ui`.
3. Adicione a página ao `self.page_stack`.
4. Atualize `_set_active_nav()`, se necessário.
5. Atualize documentação.

## 13. Processos

Arquivo:

```text
src/syssense/ui/processes.py
```

Cria abas:

- Por Memória;
- Por CPU;
- Comparar.

`window.py` atualiza listas com:

```python
clear_process_list(self.mem_list)
append_process_row(self.mem_list, [...])
```

Se quiser mudar colunas:

1. Ajuste headers em `build_processes_tab()`.
2. Ajuste pesos de largura.
3. Ajuste os valores em `_update_processes()`.
4. Verifique responsividade.

## 14. Disco

Arquivos:

- `src/syssense/ui/disk.py`;
- partes do card de armazenamento em `src/syssense/ui/overview.py`;
- lógica de seleção e desenho em `window.py`.

O card de armazenamento usa `Gtk.DrawingArea`.

O desenho recebe:

```python
def _draw_disk_chart(self, area, cr, width, height):
```

GTK passa um contexto Cairo (`cr`). Nele são desenhados arcos para representar usado/livre.

Para alterar cores do gráfico, edite o método de desenho ou classes CSS relacionadas.

## 15. Serviços

Arquivo:

```text
src/syssense/ui/services.py
```

Dados vêm de:

```python
collectors.get_failed_services()
collectors.get_recent_logs(50)
```

Essas funções usam `systemctl` e `journalctl` em modo somente leitura.

Se a consulta falhar, a UI mostra estado de indisponibilidade em vez de quebrar.

## 16. Preferências

Arquivo:

```text
src/syssense/ui/preferences.py
```

O painel é interno, não é popup externo do sistema.

Ele contém:

- combo de intervalo;
- switch de toasts críticos;
- switches de cards visíveis.

Ao alterar intervalo:

```python
self._restart_refresh_timer()
```

Ao alterar card visível:

```python
self._apply_card_visibility()
```

## 17. CSS GTK

Arquivo:

```text
src/syssense/resources/styles.css
```

GTK CSS parece CSS comum, mas não suporta todas as propriedades do CSS web.

Evite propriedades como:

```css
max-width: 300px;
```

Use preferencialmente:

- `padding`;
- `margin`;
- `border-radius`;
- `border`;
- `background`;
- `color`;
- `min-width`;
- `min-height`;
- classes GTK suportadas.

### 17.1 Como Aplicar Uma Classe

No Python:

```python
widget.get_style_context().add_class("minha-classe")
```

No CSS:

```css
.minha-classe {
    background: #202124;
    border-radius: 14px;
}
```

### 17.2 Como Remover Uma Classe

```python
widget.get_style_context().remove_class("minha-classe")
```

Isso é usado em alertas para alternar bordas e estados visuais.

## 18. Teste de Internet

Fluxo:

1. Usuário clica em `Testar Velocidade`.
2. Botão é desativado.
3. Uma thread chama `collectors.speedtest()`.
4. Resultado volta via `GLib.idle_add`.
5. UI mostra download/upload ou erro amigável.

Pontos importantes:

- usa `timeout=12`;
- usa `secure=True`;
- erros técnicos são convertidos para mensagens curtas;
- tooltip guarda detalhe quando necessário;
- o teste só roda quando o usuário pede.

## 19. Empacotamento

### 19.1 Python

Arquivo:

```text
pyproject.toml
```

Campos importantes:

```toml
[project]
name = "syssense"
version = "0.4.0"

[project.scripts]
syssense = "syssense.main:main"
```

Recursos CSS entram pelo bloco:

```toml
[tool.setuptools.package-data]
"syssense.resources" = ["*.css"]
```

### 19.2 Desktop

Arquivo:

```text
data/applications/br.com.syssense.desktop
```

Define nome, comando, ícone e categorias.

### 19.3 AppStream

Arquivo:

```text
data/metainfo/br.com.syssense.metainfo.xml
```

Define descrição, releases e metadados usados por lojas/centros de software.

## 20. Instalação Nativa

Arquivo:

```text
packaging/native/install.sh
```

O script:

1. localiza Python;
2. verifica Fedora/GNOME em melhor esforço;
3. valida GTK 4/libadwaita;
4. valida `pip`;
5. roda `pip install --user`;
6. copia `.desktop`;
7. copia ícone;
8. atualiza cache desktop/ícones.

Não usa `sudo`.

## 21. Flatpak

Arquivo:

```text
packaging/flatpak/br.com.syssense.yml
```

O Flatpak é experimental porque o sandbox pode esconder processos e serviços reais do host.

Use Flatpak para:

- validar empacotamento;
- testar isolamento;
- preparar distribuição futura.

Use nativo para:

- monitorar o computador real.

## 22. Testes

Os testes ficam em:

```text
tests/
```

Padrões atuais:

- `unittest`;
- mocks para comandos externos;
- sem depender de internet;
- sem depender do estado real do systemd;
- sem depender de métricas reais da máquina.

Para adicionar teste:

```python
import unittest

class MeuTeste(unittest.TestCase):
    def test_algo(self):
        self.assertEqual(1 + 1, 2)
```

Rode:

```bash
python3 -m unittest
```

## 23. Como Fazer Uma Release

Checklist resumido:

1. Atualizar versão em:
   - `README.md`;
   - `pyproject.toml`;
   - `src/syssense/__init__.py`;
   - `CHANGELOG.md`;
   - `data/metainfo/br.com.syssense.metainfo.xml`.
2. Rodar validações.
3. Testar instalação nativa.
4. Limpar artefatos.
5. Commitar.
6. Criar tag.
7. Fazer push.

Comandos:

```bash
git add .
git commit -m "Release v0.4.0"
git tag v0.4.0
git push origin main --tags
```

## 24. Alterações Comuns

### 24.1 Mudar Intervalos de Refresh

Arquivo:

```text
src/syssense/config.py
```

Edite:

```python
REFRESH_OPTIONS_SECONDS = (1.0, 2.5, 5.0, 10.0)
```

Depois atualize documentação e testes.

### 24.2 Mudar Limites de Alerta

Arquivo:

```text
src/syssense/diagnostics.py
```

Edite os valores `limite` em `REGRAS`.

Exemplo:

```python
{
    "campo": "mem_percent",
    "limite": 85,
    "operador": "gt",
    "severidade": "alta",
}
```

### 24.3 Mudar Visual de Cards

Arquivo:

```text
src/syssense/resources/styles.css
```

Procure classes como:

- `.card-custom`;
- `.metric-card`;
- `.light-card`;
- `.alert-high`;
- `.alert-medium`.

### 24.4 Mudar Texto de Uma Tela

Procure o texto:

```bash
rg "Texto atual" src/syssense
```

Altere no módulo correspondente.

### 24.5 Adicionar Dependência

1. Adicione em `requirements.txt`.
2. Adicione em `pyproject.toml`.
3. Se afetar Flatpak, atualize `packaging/flatpak/br.com.syssense.yml`.
4. Atualize README.
5. Explique o motivo em documentação.

## 25. Cuidados Importantes

- Não atualizar widgets GTK diretamente fora da thread principal.
- Não usar `shell=True`.
- Não adicionar funções destrutivas sem rever `SECURITY.md`.
- Não gravar métricas em disco sem atualizar `PRIVACY.md`.
- Não transformar Flatpak em modo recomendado enquanto ele não enxergar o host corretamente.
- Não adicionar dependência pesada sem necessidade real.
- Não misturar grandes refatorações com mudanças visuais na mesma release.

## 26. Troubleshooting

### GTK 4 não encontrado

Instale:

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

### App não abre pelo menu

Reinstale:

```bash
./packaging/native/install.sh
```

Atualize cache:

```bash
update-desktop-database ~/.local/share/applications
gtk-update-icon-cache -q ~/.local/share/icons/hicolor
```

### Preferências ficaram estranhas

Apague:

```bash
rm ~/.config/syssense/config.json
```

O app recria defaults seguros.

### Speedtest falha

Possíveis causas:

- sem internet;
- servidor de teste indisponível;
- DNS instável;
- bloqueio temporário do speedtest.

O app deve mostrar erro amigável e manter layout estável.

## 27. Onde Atualizar Documentação

Ao mudar comportamento público:

- `README.md`;
- `CHANGELOG.md`;
- `docs/project-spec.md`;
- `docs/maintenance-guide.md`, se afetar manutenção;
- `SECURITY.md`, se afetar segurança;
- `PRIVACY.md`, se afetar dados/rede;
- `data/metainfo/br.com.syssense.metainfo.xml`, se for release.

## 28. Princípio de Evolução

O SysSense deve continuar:

- leve;
- local;
- claro;
- somente leitura;
- fácil de instalar;
- fácil de manter;
- honesto sobre limitações.

Quando uma mudança ameaçar essas propriedades, ela deve ser tratada como decisão de roadmap, não como ajuste pequeno.
