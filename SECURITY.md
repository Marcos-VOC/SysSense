# Security Policy

## Escopo

SysSense e um monitor local de sistema. A v0.1 foi desenhada para ser somente leitura:

- nao altera configuracoes do sistema;
- nao mata processos;
- nao inicia, para ou reinicia servicos;
- nao escreve arquivos de configuracao do usuario;
- nao executa comandos via shell;
- nao coleta credenciais.

## Dados acessados

O app le informacoes locais necessarias para monitoramento:

- CPU, memoria, uptime, rede, armazenamento e processos via `psutil`;
- temperatura via sensores expostos pelo sistema;
- servicos com falha via `systemctl list-units --failed --output=json`;
- logs recentes via `journalctl`, apenas quando a aba de servicos e atualizada;
- rede externa somente quando o usuario clica em testar velocidade.

## Chamadas externas

As chamadas para `systemctl` e `journalctl` usam lista de argumentos fixa, sem `shell=True`, com timeout e ambiente controlado.

O teste de velocidade usa `speedtest-cli` e pode se comunicar com servidores externos de teste. Ele so roda por acao explicita do usuario.

## Flatpak

O manifest Flatpak usa permissoes de leitura para `/proc` e `/sys`, porque um monitor de sistema precisa enxergar algumas metricas do host. Permissoes amplas, como acesso completo ao home do usuario, nao sao declaradas.

No Flatpak, a lista de processos e limitada pelo sandbox. Isso e esperado e preserva isolamento.

Permissoes adicionais devem seguir este criterio:

1. provar a necessidade durante o spike;
2. escolher a permissao mais restrita possivel;
3. documentar o motivo;
4. validar que a UI falha de forma amigavel quando a permissao nao existir.

## Modo nativo local

O modo nativo local e recomendado para monitoramento completo do host. Ele roda como o usuario atual e continua sendo somente leitura. Nao usa privilegios elevados para executar o app e nao instala servicos em background.

## Relatar vulnerabilidades

Para a v0.1, abra uma issue privada ou entre em contato com o mantenedor antes de divulgar publicamente uma falha. Inclua:

- versao do SysSense;
- forma de instalacao;
- sistema operacional;
- passos de reproducao;
- impacto esperado.

## Principios de manutencao

- Preferir APIs estruturadas a parsing textual.
- Usar subprocessos apenas para consultas de leitura.
- Nunca usar `shell=True`.
- Limitar timeouts de operacoes bloqueantes.
- Sanitizar texto vindo de comandos externos antes de exibir na UI.
- Manter permissoes Flatpak minimizadas.
