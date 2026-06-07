# Release v0.4

Este documento registra o escopo técnico da série `v0.4.x` do SysSense.

## Proposta

A série `v0.4` consolida a reestruturação interna da interface sem mudar a proposta principal do aplicativo: monitoramento local, nativo, somente leitura e focado em Fedora/GNOME.

O objetivo foi reduzir a responsabilidade de `src/syssense/window.py`, separar telas em módulos menores e preparar o projeto para manutenção mais tranquila nas próximas versões.

## Principais Mudanças

- criação do pacote `src/syssense/ui/`;
- extração da sidebar para `ui/sidebar.py`;
- extração do painel de preferências para `ui/preferences.py`;
- extração da dashboard e dos cards principais para `ui/overview.py`;
- extração da tela de processos para `ui/processes.py`;
- extração da tela de disco para `ui/disk.py`;
- extração da tela de serviços para `ui/services.py`;
- reorganização manual dos cards da dashboard com persistência em `~/.config/syssense/config.json`;
- ajustes nos painéis internos para fechar com `Esc` ou clique fora;
- troca do seletor de partição do card de armazenamento para um menu interno mais previsível.

## Organização Técnica

A partir desta série, a interface fica distribuída assim:

```text
src/syssense/
├── window.py             # janela principal, callbacks, threading e coordenação
├── ui/
│   ├── sidebar.py        # navegação lateral
│   ├── overview.py       # dashboard e cards
│   ├── preferences.py    # painel interno de preferências
│   ├── processes.py      # listas de processos
│   ├── disk.py           # tela de disco
│   └── services.py       # tela de serviços systemd
├── config.py             # preferências persistentes
├── collectors.py         # coleta de métricas
├── diagnostics.py        # regras de alertas
├── formatters.py         # formatação de textos e unidades
└── resources/styles.css  # estilos GTK
```

`window.py` ainda coordena coleta, threading, cache de dados e atualização geral da aplicação. Os módulos em `ui/` concentram a construção visual e helpers de renderização das telas.

## Validação Recomendada

```bash
python3 -m compileall src/syssense
python3 -m unittest
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```

Depois da validação:

```bash
rm -rf /tmp/syssense-install-test build src/syssense.egg-info
find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
```

## Fora do Escopo

- temas visuais configuráveis;
- arrastar e soltar para reorganizar cards;
- gráficos históricos;
- pacote RPM/COPR;
- suporte oficial a outras distribuições;
- integração com IA externa.
