# Privacy

SysSense roda localmente e nao possui telemetria.

## O que fica local

As seguintes informacoes sao lidas e exibidas apenas na propria interface:

- uso de CPU e memoria;
- processos em execucao;
- particoes e uso de armazenamento;
- trafego de rede acumulado informado pelo sistema;
- temperatura, quando disponivel;
- uptime;
- servicos systemd com falha;
- logs recentes do sistema.

O app nao envia essas informacoes para o mantenedor e nao possui servidor proprio.

No modo Flatpak, algumas informacoes podem refletir apenas o sandbox. No modo nativo local, as metricas refletem o host conforme as permissoes normais do usuario no Fedora.

## Quando existe rede

A rede so e usada em uma funcionalidade: teste de velocidade. Esse teste e iniciado manualmente pelo usuario no botao "Testar Velocidade".

Ao executar o teste, `speedtest-cli` consulta servidores externos de medicao. Isso pode expor informacoes normais de conexao, como endereco IP publico, provedor e resultado do teste, aos servicos envolvidos no teste de velocidade.

## Logs

Logs do sistema podem conter nomes de usuario, caminhos locais, nomes de dispositivos, mensagens de servicos e outros detalhes sensiveis. O SysSense limita a quantidade de linhas exibidas e remove caracteres de controle, mas nao tenta classificar ou apagar semanticamente todo dado sensivel.

## Arquivos

O SysSense nao grava historico de metricas, logs ou resultados de diagnostico em disco na v0.1.
