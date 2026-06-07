# Checklist de Release

Este checklist reúne os passos recomendados antes de publicar uma nova versão do SysSense.

## 1. Conferir Versão

Atualize a versão nos arquivos:

- `README.md`;
- `pyproject.toml`;
- `src/syssense/__init__.py`;
- `CHANGELOG.md`;
- `data/metainfo/br.com.syssense.metainfo.xml`.

## 2. Rodar Validações

```bash
git diff --check
python3 -m compileall src/syssense
python3 -m unittest
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```

## 3. Testar Instalação Nativa

```bash
./packaging/native/install.sh
```

Depois, abra o SysSense pelo menu de aplicativos e valide os fluxos principais:

- dashboard;
- processos;
- disco;
- serviços;
- preferências;
- painel de riscos;
- teste manual de internet.

## 4. Limpar Artefatos Locais

```bash
rm -rf /tmp/syssense-install-test build src/syssense.egg-info
find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
```

## 5. Commit, Tag e Push

```bash
git status --short
git add .
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

Substitua `vX.Y.Z` pela versão real.
