# Release v0.2

Este documento registra o escopo técnico da série `v0.2.x` do SysSense.

## Proposta

A série `v0.2` consolida o projeto como um monitor de sistema local para Fedora/GNOME, com foco em uso nativo, segurança por desenho e uma experiência visual mais estável.

O modo nativo local é o caminho recomendado para usuários finais, porque permite que o SysSense enxergue processos, métricas, serviços e logs do host com as permissões normais do usuário. O Flatpak continua existindo como opção de teste isolado, mas não é tratado como modo principal de monitoramento completo.

## v0.2.0

Principais mudanças:

- alertas visuais discretos para memória crítica e armazenamento elevado;
- tráfego de rede em tempo real no card de rede;
- alertas automáticos com mensagens mais úteis e principais consumidores de CPU/memória;
- feedback visual melhor nas ações de Serviços e no painel de alertas;
- fallback mais amigável quando serviços, logs ou permissões não estão disponíveis.

## v0.2.1

Principais mudanças:

- testes leves com `unittest`;
- documentação de instalação nativa e Flatpak revisada;
- remoção da aba manual de Diagnóstico em favor de alertas automáticos na sidebar e nos cards;
- painel de status na sidebar com lista de alertas ativos;
- README atualizado com captura de tela e validações;
- tabela de níveis de alerta documentada;
- políticas de segurança e privacidade revisadas;
- limpeza de cache e artefatos locais antes de publicação.

## Validação recomendada

```bash
python3 -m compileall src/syssense
python3 -m unittest
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
```

Depois da validação:

```bash
rm -rf /tmp/syssense-install-test
find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
```
