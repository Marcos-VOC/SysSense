# Changelog

Todas as mudancas relevantes do SysSense serao documentadas aqui.

## [0.1.0] - 2026-06-06

### Adicionado

- Dashboard em GTK 4 + libadwaita com cards para CPU, memoria, armazenamento, temperatura, rede, carga do sistema, uptime e internet.
- Aba de processos com visualizacao por memoria, por CPU e comparacao responsiva.
- Aba de disco com particoes, uso, espaco livre e alertas.
- Aba de servicos com coleta de falhas systemd e logs recentes.
- Diagnostico local por regras.
- Teste de velocidade sob demanda usando `speedtest-cli`.
- Metadados profissionais para desktop Linux: `.desktop`, AppStream/metainfo e icone SVG.
- Manifest inicial Flatpak para distribuicao local e futura publicacao.
- Documentacao de seguranca e privacidade.
- Scripts de instalacao nativa local e remocao.
- Deteccao de modo Flatpak com aviso de processos limitados ao sandbox.

### Alterado

- Interface migrada para GTK 4 e libadwaita.
- Atualizacao automatica das metricas principais ajustada para 2.5 segundos.
- Estrutura reorganizada para `data/`, `packaging/flatpak/` e pacote instalavel via `pyproject.toml`.
- Chamadas externas endurecidas com ambiente controlado, timeout, sem shell e sanitizacao de texto.

### Observacoes

- O Flatpak ainda precisa de validacao em ambiente com `flatpak` e `flatpak-builder` instalados.
- Leitura de servicos/logs pode ter limitacoes dentro do sandbox Flatpak, dependendo das permissoes do sistema.
