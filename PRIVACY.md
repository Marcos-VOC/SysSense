# Privacy

SysSense roda localmente e não possui telemetria.

## O que fica local

As seguintes informações são lidas e exibidas apenas na própria interface:

- uso de CPU e memória;
- processos em execução;
- partições e uso de armazenamento;
- tráfego de rede acumulado informado pelo sistema;
- temperatura, quando disponível;
- uptime;
- serviços systemd com falha;
- logs recentes do sistema.

O app não envia essas informações para o mantenedor e não possui servidor próprio.

No modo Flatpak, algumas informações podem refletir apenas o sandbox. No modo nativo local, as métricas refletem o host conforme as permissões normais do usuário no Fedora.

## Quando existe rede

A rede só é usada em uma funcionalidade: teste de velocidade. Esse teste é iniciado manualmente pelo usuário no botão "Testar Velocidade".

Ao executar o teste, `speedtest-cli` consulta servidores externos de medição. Isso pode expor informações normais de conexão, como endereço IP público, provedor e resultado do teste, aos serviços envolvidos no teste de velocidade.

## Logs

Logs do sistema podem conter nomes de usuário, caminhos locais, nomes de dispositivos, mensagens de serviços e outros detalhes sensíveis. O SysSense limita a quantidade de linhas exibidas e remove caracteres de controle, mas não tenta classificar ou apagar semanticamente todo dado sensível.

## Arquivos

O SysSense não grava histórico de métricas, logs ou resultados de diagnóstico em disco na versão atual. Ele salva apenas preferências locais em `~/.config/syssense/config.json`, como intervalo de atualização e cards visíveis.
