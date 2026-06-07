# Roadmap v0.4

Este documento registra o que ficou fora da `v0.3.4` e deve orientar a próxima etapa do SysSense.

## Proposta

A `v0.4` deve focar em organização interna, manutenção e preparação para crescimento do projeto. A ideia é preservar o comportamento visual e funcional validado na `v0.3.4`, enquanto o código da interface é dividido em módulos menores.

## Objetivos Principais

- Reduzir o tamanho e a responsabilidade de `src/syssense/window.py`.
- Separar componentes de UI em módulos pequenos e previsíveis.
- Manter callbacks, threading e atualização de widgets funcionando como hoje.
- Permitir reorganização manual dos cards da dashboard.
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

### 4. Reorganização Manual dos Cards

A reorganização manual deve ser implementada depois que `overview.py` existir, para evitar aumentar ainda mais a responsabilidade de `window.py`.

Proposta inicial:

- permitir mover cards da dashboard por controles simples, como botões de subir/descer ou mover esquerda/direita;
- persistir a ordem em `~/.config/syssense/config.json`;
- manter uma opção de restaurar ordem padrão;
- evitar arrastar e soltar como primeira implementação, pois isso aumenta complexidade visual e de eventos no GTK;
- garantir que cards ocultos não quebrem a ordem salva.

O arrastar e soltar pode ser avaliado depois, se a versão com controles simples estiver estável.

## Ordem de Implementação

1. Criar `src/syssense/ui/`. Concluído.
2. Mover a sidebar para `ui/sidebar.py`. Concluído.
3. Mover o painel de preferências para `ui/preferences.py`. Concluído.
4. Mover a dashboard e os cards principais para `ui/overview.py`. Concluído.
5. Implementar reorganização manual dos cards com controles simples e persistência em `config.json`. Concluído.
6. Mover Processos para `ui/processes.py`. Concluído.
7. Mover Disco para `ui/disk.py`. Concluído.
8. Mover Serviços para `ui/services.py`. Concluído.
9. Atualizar documentação e validações finais da `v0.4`. Concluído.

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
