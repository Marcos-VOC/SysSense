# Release v0.1

Este documento serve como checklist para publicar o SysSense v0.1 no GitHub.

## Objetivo da v0.1

Entregar uma primeira versao publica, usavel no Fedora/GNOME, com dois modos claros: nativo local para monitoramento completo e Flatpak para execucao sandboxed.

## Antes de publicar

- Confirmar nome final do repositorio: sugestao `syssense`.
- Atualizar a URL real em `README.md` e `data/metainfo/br.com.syssense.metainfo.xml`.
- Escolher licenca final. O projeto esta preparado como MIT.
- Revisar `SECURITY.md` e `PRIVACY.md` antes de publicar.
- Adicionar screenshots reais em `docs/screenshots/` ou na area de assets do GitHub.
- Rodar instalacao nativa local e spike Flatpak em Fedora.
- Criar tag Git:

```bash
git tag -a v0.1.0 -m "SysSense v0.1.0"
git push origin main --tags
```

## Comandos de validacao

```bash
python3 -m compileall src/syssense
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
```

Quando Flatpak estiver disponivel:

```bash
cd packaging/flatpak
flatpak-builder --force-clean ../../flatpak-build br.com.syssense.yml
flatpak-builder --run ../../flatpak-build br.com.syssense.yml syssense
```

## Estrutura esperada

```text
SysSense/
├── data/
│   ├── applications/
│   ├── icons/
│   └── metainfo/
├── docs/
├── packaging/
│   ├── flatpak/
│   └── native/
├── src/
│   └── syssense/
├── CHANGELOG.md
├── README.md
├── pyproject.toml
├── requirements.txt
└── run.sh
```

## Limites honestos da v0.1

- Fedora/GNOME e o alvo principal.
- Flatpak e sandboxed por design; processos, servicos e logs podem ser limitados.
- Instalacao nativa local e o modo recomendado para monitoramento completo.
- O app nao altera o sistema; ele apenas le informacoes e executa diagnosticos locais.
