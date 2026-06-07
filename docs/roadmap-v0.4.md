# Roadmap v0.4

Este documento registra o que ficou fora da `v0.3.4` e deve orientar a próxima etapa do SysSense.

## Proposta

A `v0.4` deve focar em organização interna, manutenção e preparação para crescimento do projeto. A ideia é preservar o comportamento visual e funcional validado na `v0.3.4`, enquanto o código da interface é dividido em módulos menores.

## Objetivos Principais

- Reduzir o tamanho e a responsabilidade de `src/syssense/window.py`.
- Separar componentes de UI em módulos pequenos e previsíveis.
- Manter callbacks, threading e atualização de widgets funcionando como hoje.
- Evitar mudanças visuais grandes durante a refatoração.
- Manter o app leve, sem novas dependências obrigatórias.

## Escopo Técnico

### 1. Criar pacote de UI

Estrutura proposta:

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

### 2. Mover Componentes Gradualmente

- `sidebar.py`: navegação, rodapé, indicador de status e botões laterais.
- `overview.py`: cards principais, grid responsiva e card de armazenamento.
- `processes.py`: listas de processos e comparação.
- `disk.py`: tela de disco e cards de partições.
- `services.py`: tela de serviços systemd e logs recentes.
- `preferences.py`: painel interno de preferências e switches.

### 3. Manter Regras de Segurança

- Não adicionar ações destrutivas.
- Não exigir sudo para uso normal.
- Não gravar histórico de métricas.
- Não adicionar telemetria.

## Fora do Escopo Inicial

- temas visuais configuráveis;
- reorganização manual dos cards por arrastar e soltar;
- gráficos históricos;
- RPM/COPR;
- integração com IA externa.

Esses itens podem ser reavaliados depois que a separação interna da interface estiver estável.

## Validação Obrigatória

Cada etapa da refatoração deve passar por:

```bash
python3 -m compileall src/syssense
python3 -m unittest
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```
