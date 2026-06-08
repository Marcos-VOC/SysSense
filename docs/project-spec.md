# SysSense - Especificação Atual do Projeto

Documento atualizado a partir da especificação original `SysSense_Spec_v2.docx`, refletindo o estado real do SysSense na versão `0.4.0`.

## 1. Visão Geral

SysSense é um monitor de sistema desktop para Fedora/GNOME feito em Python, GTK 4 e libadwaita.

O aplicativo tem como proposta oferecer uma dashboard local, leve e somente leitura para acompanhar:

- CPU;
- memória RAM e swap;
- armazenamento e partições;
- processos;
- tráfego de rede;
- temperatura;
- uptime;
- carga do sistema;
- serviços systemd;
- logs recentes;
- alertas automáticos;
- teste manual de velocidade da internet.

O modo recomendado é a instalação nativa local, porque um monitor de sistema precisa enxergar métricas reais do host. O Flatpak permanece como modo experimental para teste isolado, com limitações conhecidas em processos, serviços e logs.

## 2. Escopo Atual

| Item | Estado |
|------|--------|
| Versão atual | `0.4.0` |
| Sistema alvo principal | Fedora/GNOME |
| Interface | GTK 4 + libadwaita |
| Linguagem | Python 3 |
| Execução recomendada | Nativa local |
| Execução experimental | Flatpak sandbox |
| Segurança | Somente leitura |
| Telemetria | Não possui |
| Rede | Usada apenas no speedtest manual |
| Configuração persistente | `~/.config/syssense/config.json` |

## 3. Objetivos

- Monitorar recursos locais sem exigir privilégios administrativos.
- Mostrar informações úteis em uma interface visual simples.
- Alertar automaticamente sobre uso elevado ou crítico.
- Evitar ações destrutivas como encerrar processos, apagar arquivos ou reiniciar serviços.
- Manter uma estrutura de código compreensível para manutenção manual.
- Oferecer instalação simples para usuários Fedora.
- Preservar documentação suficiente para evolução futura.

## 4. Fora do Escopo Atual

- Controle de processos.
- Controle de serviços systemd.
- Limpeza automática de arquivos.
- Telemetria.
- Histórico persistente de métricas.
- Suporte oficial a outras distribuições.
- Temas visuais configuráveis.
- Integração com IA externa.
- RPM/COPR oficial.

Esses itens podem ser reavaliados em versões futuras, mas não fazem parte da proposta fechada na `v0.4.0`.

## 5. Stack Técnica

### 5.1 Interface

- `Gtk 4`: widgets, layout, eventos e renderização.
- `libadwaita`: janela principal, header bar, toast overlay e integração visual GNOME.
- `PyGObject`: ponte Python para GTK/libadwaita.
- `CSS GTK`: estilos em `src/syssense/resources/styles.css`.

### 5.2 Dados do Sistema

- `psutil`: CPU, memória, disco, rede, processos, temperatura e uptime.
- `systemctl`: consulta somente leitura de serviços com falha.
- `journalctl`: consulta somente leitura de logs recentes.
- `speedtest-cli`: teste manual de velocidade, iniciado apenas pelo usuário.

### 5.3 Empacotamento

- `pyproject.toml`: metadados Python, dependências e entry point `syssense`.
- `data/applications/br.com.syssense.desktop`: atalho desktop.
- `data/metainfo/br.com.syssense.metainfo.xml`: metadados AppStream.
- `data/icons/hicolor/scalable/apps/br.com.syssense.svg`: ícone.
- `packaging/native/install.sh`: instalação local sem root.
- `packaging/flatpak/br.com.syssense.yml`: manifest Flatpak experimental.

## 6. Estrutura Atual

```text
SysSense/
├── data/
│   ├── applications/
│   ├── icons/
│   └── metainfo/
├── docs/
│   ├── maintenance-guide.md
│   ├── project-spec.md
│   ├── release-checklist.md
│   ├── release-v0.1.md
│   ├── release-v0.2.md
│   ├── release-v0.3.md
│   ├── release-v0.4.md
│   ├── roadmap-v0.3.md
│   ├── roadmap-v0.4.md
│   ├── restructure-roadmap.md
│   └── testing.md
├── packaging/
│   ├── flatpak/
│   └── native/
├── src/
│   └── syssense/
│       ├── collectors.py
│       ├── config.py
│       ├── diagnostics.py
│       ├── formatters.py
│       ├── main.py
│       ├── resources/
│       │   └── styles.css
│       ├── ui/
│       │   ├── disk.py
│       │   ├── overview.py
│       │   ├── preferences.py
│       │   ├── processes.py
│       │   ├── services.py
│       │   └── sidebar.py
│       └── window.py
├── tests/
├── CHANGELOG.md
├── LICENSE
├── PRIVACY.md
├── README.md
├── SECURITY.md
├── pyproject.toml
├── requirements.txt
└── run.sh
```

## 7. Arquitetura

### 7.1 `main.py`

Cria a aplicação libadwaita, registra o ID `br.com.syssense` e instancia `SysSenseWindow` quando o app é ativado.

### 7.2 `window.py`

Coordena a janela principal. Depois da reestruturação da `v0.4.0`, ele não concentra mais toda a construção visual.

Responsabilidades atuais:

- inicializar CSS;
- montar janela e stacks principais;
- controlar navegação;
- iniciar threads de coleta;
- manter cache de dados;
- atualizar widgets;
- aplicar alertas automáticos;
- salvar preferências;
- coordenar painéis internos;
- gerenciar speedtest manual;
- desenhar o gráfico de armazenamento.

### 7.3 `collectors.py`

Contém funções de coleta de dados. Elas retornam dicionários simples e devem ser seguras para rodar em threads.

Principais funções:

- `get_runtime_info()`;
- `get_cpu_info()`;
- `get_memory_info()`;
- `get_disk_info()`;
- `get_top_processes()`;
- `get_network_info()`;
- `get_temperature()`;
- `get_uptime()`;
- `get_failed_services()`;
- `get_recent_logs()`;
- `speedtest()`.

### 7.4 `diagnostics.py`

Define regras locais de alerta em `REGRAS`.

Cada regra possui:

- `campo`;
- `limite`;
- `operador`;
- `severidade`;
- `mensagem`.

O diagnóstico não usa IA na versão atual. A função `diagnosticar_com_ia()` existe apenas como reserva futura.

### 7.5 `config.py`

Controla preferências persistentes:

- intervalo de atualização;
- toasts críticos;
- cards visíveis;
- ordem dos cards.

O módulo sempre normaliza configurações inválidas antes de usar ou salvar.

### 7.6 `formatters.py`

Centraliza formatações de texto:

- bytes;
- velocidade de rede;
- uptime;
- carga do sistema.

### 7.7 `ui/`

Pacote criado na `v0.4.0` para separar a interface em componentes menores:

- `sidebar.py`: barra lateral;
- `preferences.py`: painel de preferências;
- `overview.py`: dashboard, cards e menu de ordenação;
- `processes.py`: abas e listas de processos;
- `disk.py`: tela de disco;
- `services.py`: serviços e logs.

## 8. Fluxo de Execução

1. O usuário inicia `syssense`.
2. `main.py` cria `Adw.Application`.
3. A aplicação ativa `SysSenseWindow`.
4. `window.py` carrega CSS e monta a UI.
5. A tela inicial mostra um loading.
6. Uma thread coleta os dados iniciais.
7. A UI é atualizada no loop principal GTK via `GLib.idle_add`.
8. Um timer chama novas coletas conforme o intervalo configurado.
9. Alertas são recalculados a cada atualização.
10. A interface reflete métricas, alertas e preferências.

## 9. Segurança

O SysSense é somente leitura:

- não usa `sudo`;
- não encerra processos;
- não edita arquivos do sistema;
- não controla serviços;
- não grava histórico de métricas;
- não coleta telemetria.

Comandos externos são chamados com:

- `shell=False`;
- timeout;
- ambiente controlado;
- limite e sanitização de texto.

## 10. Alertas

| Área | Atenção | Crítico |
|------|---------|---------|
| Memória RAM | acima de 70% | acima de 85% |
| Armazenamento | acima de 70% | acima de 90% |
| CPU | acima de 80% | sem crítico na `v0.4.0` |
| Swap | acima de 50% | sem crítico na `v0.4.0` |
| Serviços | qualquer falha | sem crítico na `v0.4.0` |

Os alertas aparecem em três níveis visuais:

- indicador na sidebar;
- painel interno de status;
- mensagens curtas e bordas nos cards afetados.

## 11. Preferências

Arquivo:

```text
~/.config/syssense/config.json
```

Exemplo:

```json
{
  "refresh_interval": 2.5,
  "critical_toasts": true,
  "show_speedtest": true,
  "visible_cards": {
    "cpu": true,
    "memory": true,
    "storage": true,
    "temperature": true,
    "network": true,
    "load": true,
    "uptime": true,
    "internet": true
  },
  "card_order": [
    "cpu",
    "memory",
    "storage",
    "temperature",
    "network",
    "load",
    "uptime",
    "internet"
  ]
}
```

Se o arquivo for apagado ou quebrado, o app volta aos defaults seguros.

## 12. Instalação

Modo recomendado:

```bash
./packaging/native/install.sh
```

O instalador:

- valida Python;
- valida GTK 4/libadwaita;
- instala o pacote com `pip install --user`;
- copia atalho `.desktop`;
- copia ícone;
- atualiza caches desktop quando possível.

## 13. Validação

Comandos principais:

```bash
git diff --check
python3 -m compileall src/syssense
python3 -m unittest
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```

## 14. Roadmap Futuro

Possibilidades futuras:

- histórico leve de métricas;
- gráficos simples;
- exportação de relatório;
- suporte melhor a outras distribuições;
- RPM/COPR;
- temas configuráveis;
- arrastar e soltar para organizar cards;
- documentação `.docx` revisada periodicamente.

## 15. Documentos Relacionados

- `README.md`;
- `docs/maintenance-guide.md`;
- `docs/testing.md`;
- `docs/release-checklist.md`;
- `SECURITY.md`;
- `PRIVACY.md`;
- `CHANGELOG.md`.
