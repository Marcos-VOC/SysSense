# Plano de Reestruturação Interna

Este documento registra ideias aprovadas para melhorar a organização técnica do SysSense a partir da série `v0.4.x`.

O objetivo é deixar o projeto mais fácil de manter sem aumentar o peso do aplicativo, sem mudar a proposta native-first e sem transformar a interface em algo mais complexo do que precisa ser.

## Motivação

O SysSense cresceu rápido entre as versões `v0.1` e `v0.3`. Na série `v0.4`, a interface foi dividida em módulos menores dentro de `src/syssense/ui/`, mantendo `src/syssense/window.py` como coordenador da janela, callbacks, threading e atualização geral.

Este documento permanece como registro das decisões de reestruturação já aplicadas e dos limites que ainda devem guiar mudanças futuras.

A reestruturação deve ser incremental. Cada etapa precisa manter o aplicativo funcionando e passar pelos testes antes de seguir para a próxima.

## Diretrizes

- Manter o aplicativo leve e rápido.
- Evitar novas dependências sem necessidade clara.
- Preservar GTK 4 + libadwaita como base visual.
- Separar responsabilidades sem criar abstrações excessivas.
- Não alterar o visual do usuário apenas por causa da refatoração.
- Não implementar temas visuais personalizados nesta etapa.

## Proposta Técnica

### 1. Separar Estilos

Mover o CSS embutido em `window.py` para um arquivo dedicado, por exemplo:

```text
src/syssense/resources/styles.css
```

Benefícios:

- facilita revisar cores, espaçamentos e estados visuais;
- reduz o tamanho de `window.py`;
- deixa claro o que é estrutura da interface e o que é aparência.

Cuidados:

- manter carregamento simples via `Gtk.CssProvider`;
- garantir que o CSS continue disponível quando instalado via `pip`/script nativo;
- atualizar `pyproject.toml` se o arquivo precisar entrar como package data.

### 2. Criar Formatadores

Extrair funções pequenas de formatação para um módulo dedicado:

```text
src/syssense/formatters.py
```

Exemplos:

- bytes para `KB/s`, `MB/s`, `GB`;
- porcentagens;
- uptime;
- carga do sistema;
- textos de disco e rede.

Benefícios:

- melhora testes unitários;
- evita duplicação de strings e conversões;
- reduz risco de inconsistência visual entre cards.

### 3. Dividir a Interface em Módulos

Separar componentes da UI em arquivos menores dentro de:

```text
src/syssense/ui/
```

Possível organização:

```text
src/syssense/ui/
├── __init__.py
├── sidebar.py
├── overview.py
├── processes.py
├── disk.py
├── services.py
└── preferences.py
```

Responsabilidades sugeridas:

- `sidebar.py`: navegação, indicador de status e rodapé;
- `overview.py`: cards principais e atualização da dashboard;
- `processes.py`: abas por memória, CPU e comparação;
- `disk.py`: tabela/lista de partições;
- `services.py`: serviços systemd e logs recentes;
- `preferences.py`: painel de preferências e seleção de cards.

Benefícios:

- reduz o acoplamento de `window.py`;
- facilita testar e revisar mudanças;
- torna mais simples adicionar novas seções no futuro.

Cuidados:

- evitar que os módulos virem classes grandes demais;
- manter callbacks e threading centralizados o suficiente para não duplicar lógica;
- preservar o comportamento atual antes de redesenhar telas.

### 4. Avaliar Gtk.Builder Depois

Arquivos `.ui` do GTK Builder podem ser considerados no futuro, mas não são prioridade imediata.

Vantagens possíveis:

- separação forte entre layout e lógica;
- leitura visual melhor para telas grandes.

Riscos:

- aumenta a curva de manutenção;
- pode dificultar callbacks dinâmicos;
- exige mais cuidado no empacotamento.

Decisão atual: manter a UI em Python por enquanto e priorizar CSS/formatadores/módulos menores.

## Ordem Recomendada

1. Extrair `formatters.py` com testes. Concluído na primeira etapa de reestruturação.
2. Extrair `styles.css` sem alterar aparência. Concluído na primeira etapa de reestruturação.
3. Criar `ui/sidebar.py` e mover a sidebar. Concluído na `v0.4`.
4. Criar `ui/preferences.py` e mover o painel de preferências. Concluído na `v0.4`.
5. Criar `ui/overview.py` e mover os cards principais. Concluído na `v0.4`.
6. Implementar reorganização manual dos cards após `overview.py`, com controles simples e persistência em `config.json`. Concluído na `v0.4`.
7. Mover Processos para `ui/processes.py`. Concluído na `v0.4`.
8. Mover Disco para `ui/disk.py`. Concluído na `v0.4`.
9. Mover Serviços para `ui/services.py`. Concluído na `v0.4`.
10. Atualizar documentação técnica e validações a cada etapa.

## Fora do Escopo Inicial

- temas visuais configuráveis;
- reorganização manual dos cards por arrastar e soltar;
- gráficos históricos;
- instalação via RPM/COPR;
- integração com IA externa.

Esses pontos podem voltar ao roadmap depois que a base interna estiver mais simples de manter.

## Estado Atual

A reestruturação prevista para a série `v0.4` foi aplicada:

- `src/syssense/resources/styles.css` concentra os estilos GTK.
- `src/syssense/formatters.py` concentra formatação de unidades e textos de métricas.
- `tests/test_formatters.py` cobre os formatadores extraídos.
- `pyproject.toml` inclui os recursos CSS no pacote instalável.
- `src/syssense/ui/` concentra os principais componentes visuais da aplicação.
- `src/syssense/window.py` permanece como coordenador da janela, callbacks, threading e atualização geral.

Os itens que ficaram fora do escopo, como temas configuráveis, gráficos históricos, RPM/COPR e arrastar e soltar para cards, devem ser reavaliados em roadmaps futuros.
