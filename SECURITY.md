# Security Policy

## Escopo

SysSense é um monitor local de sistema. A versão atual foi desenhada para ser somente leitura:

- não altera configurações do sistema;
- não mata processos;
- não inicia, para ou reinicia serviços;
- escreve apenas preferências locais em `~/.config/syssense/config.json`, quando o usuário altera opções;
- não executa comandos via shell;
- não coleta credenciais.

## Dados acessados

O app lê informações locais necessárias para monitoramento:

- CPU, memória, uptime, rede, armazenamento e processos via `psutil`;
- temperatura via sensores expostos pelo sistema;
- serviços com falha via `systemctl list-units --failed --output=json`;
- logs recentes via `journalctl`, apenas quando a aba de serviços é atualizada;
- rede externa somente quando o usuário clica em testar velocidade.

## Chamadas externas

As chamadas para `systemctl` e `journalctl` usam lista de argumentos fixa, sem `shell=True`, com timeout e ambiente controlado.

O teste de velocidade usa `speedtest-cli` e pode se comunicar com servidores externos de teste. Ele só roda por ação explícita do usuário.

## Flatpak

O manifest Flatpak usa permissões de leitura para `/proc` e `/sys`, porque um monitor de sistema precisa enxergar algumas métricas do host. Permissões amplas, como acesso completo ao home do usuário, não são declaradas.

No Flatpak, a lista de processos é limitada pelo sandbox. Isso é esperado e preserva isolamento.

Permissões adicionais devem seguir este critério:

1. provar a necessidade durante o spike;
2. escolher a permissão mais restrita possível;
3. documentar o motivo;
4. validar que a UI falha de forma amigável quando a permissão não existir.

## Modo nativo local

O modo nativo local é recomendado para monitoramento completo do host. Ele roda como o usuário atual e continua sendo somente leitura. Não usa privilégios elevados para executar o app e não instala serviços em background.

## Relatar vulnerabilidades

Para a versão atual, abra uma issue privada ou entre em contato com o mantenedor antes de divulgar publicamente uma falha. Inclua:

- versão do SysSense;
- forma de instalação;
- sistema operacional;
- passos de reprodução;
- impacto esperado.

## Princípios de manutenção

- Preferir APIs estruturadas a parsing textual.
- Usar subprocessos apenas para consultas de leitura.
- Nunca usar `shell=True`.
- Limitar timeouts de operações bloqueantes.
- Sanitizar texto vindo de comandos externos antes de exibir na UI.
- Manter permissões Flatpak minimizadas.
