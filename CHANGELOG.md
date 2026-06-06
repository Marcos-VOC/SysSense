# Changelog

Todas as mudanças relevantes do SysSense serão documentadas aqui.

## [0.1.0] - 2026-06-06

### Adicionado

- Dashboard em GTK 4 + libadwaita com cards para CPU, memória, armazenamento, temperatura, rede, carga do sistema, uptime e internet.
- Aba de processos com visualização por memória, por CPU e comparação responsiva.
- Aba de disco com partições, uso, espaço livre e alertas.
- Aba de serviços com coleta de falhas systemd e logs recentes.
- Diagnóstico local por regras.
- Teste de velocidade sob demanda usando `speedtest-cli`.
- Metadados profissionais para desktop Linux: `.desktop`, AppStream/metainfo e ícone SVG.
- Manifest inicial Flatpak para distribuição local e futura publicação.
- Documentação de segurança e privacidade.
- Scripts de instalação nativa local e remoção.
- Detecção de modo Flatpak com aviso de processos limitados ao sandbox.

### Alterado

- Interface migrada para GTK 4 e libadwaita.
- Atualização automática das métricas principais ajustada para 2.5 segundos.
- Estrutura reorganizada para `data/`, `packaging/flatpak/` e pacote instalável via `pyproject.toml`.
- Chamadas externas endurecidas com ambiente controlado, timeout, sem shell e sanitização de texto.

### Observações

- O Flatpak ainda precisa de validação em ambiente com `flatpak` e `flatpak-builder` instalados.
- Leitura de serviços/logs pode ter limitações dentro do sandbox Flatpak, dependendo das permissões do sistema.
