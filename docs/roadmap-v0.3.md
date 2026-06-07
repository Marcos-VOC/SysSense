# Roadmap v0.3

Este documento registra as decisões alinhadas para a série `v0.3.x`.

## v0.3.0 - Instalação Nativa

- Melhorar `packaging/native/install.sh`.
- Melhorar `packaging/native/uninstall.sh`.
- Manter instalação via `git clone` + `install.sh` como caminho recomendado.
- Não priorizar RPM/COPR nesta série.

Decisão: RPM/COPR seguem como possibilidade futura, mas não entram como obrigação da v0.3.

## v0.3.1 - Estabilidade e Testes

- Ampliar testes de `diagnostics.py`.
- Ampliar testes de `collectors.py`.
- Simular falhas de `systemctl`, `journalctl`, `speedtest`, sensores e permissões.
- Criar documentação de validação em `docs/testing.md`.
- Manter `ruff` apenas como ferramenta opcional.

## v0.3.2 - Refinamento do Monitoramento

- Remover alertas duplicados por categoria.
- Tornar mensagens de alerta mais acionáveis.
- Melhorar estados visuais da aba Serviços.
- Melhorar legibilidade da aba Disco.
- Adicionar tooltips úteis em carga do sistema e processos.

Fora do escopo: gráficos históricos, filtros avançados de logs e ordenação interativa de processos.

## v0.3.3 - Configuração Mínima

- Criar configuração em `~/.config/syssense/config.json`.
- Criar painel discreto de preferências.
- Permitir escolher intervalo de atualização.
- Permitir ligar/desligar toasts críticos.
- Permitir exibir/ocultar o card de teste de internet.
- Manter limites dos alertas fixos.

## v0.3.4 - Personalização da Dashboard

- Permitir escolher quais cards aparecem na dashboard.
- Persistir essa escolha no mesmo arquivo de configuração.
- Reorganizar automaticamente a grade quando cards forem ocultados.
- Manter painéis de status e preferências dentro da janela do aplicativo.
- Aplicar transições leves em navegação e alertas.
- Iniciar reestruturação interna com `formatters.py` e `resources/styles.css`.
- Não implementar temas visuais nesta série.
- Não implementar reorganização manual de ordem dos cards.

## Movido para v0.4

- Dividir `window.py` em módulos menores de UI.
- Criar pacote `src/syssense/ui/`.
- Mover sidebar, dashboard, processos, disco, serviços e preferências em etapas.
- Manter temas visuais, reorganização manual de cards, RPM/COPR e IA externa fora do escopo inicial.

Detalhes estão em `docs/roadmap-v0.4.md` e `docs/restructure-roadmap.md`.
