# Release v0.1

Este documento serve como checklist para publicar o SysSense v0.1 no GitHub.

## Objetivo da v0.1

Entregar uma primeira versão pública, usável no Fedora/GNOME, com dois modos claros: nativo local para monitoramento completo e Flatpak para execução sandboxed.

## Antes de publicar

- Confirmar nome final do repositório: sugestão `syssense`.
- Atualizar a URL real em `README.md` e `data/metainfo/br.com.syssense.metainfo.xml`.
- Escolher licença final. O projeto está preparado como MIT.
- Revisar `SECURITY.md` e `PRIVACY.md` antes de publicar.
- Adicionar screenshots reais em `docs/screenshots/` ou na área de assets do GitHub.
- Rodar instalação nativa local e spike Flatpak em Fedora.
- Criar tag Git:

```bash
git tag -a v0.1.0 -m "SysSense v0.1.0"
git push origin main --tags
```

## Comandos de validação

```bash
python3 -m compileall src/syssense
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
```

Quando Flatpak estiver disponível:

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

- Fedora/GNOME é o alvo principal.
- Flatpak é sandboxed por design; processos, serviços e logs podem ser limitados.
- Instalação nativa local é o modo recomendado para monitoramento completo.
- O app não altera o sistema; ele apenas lê informações e executa diagnósticos locais.
