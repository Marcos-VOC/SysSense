# Testes e Validação

Este documento reúne os comandos recomendados para validar o SysSense durante desenvolvimento e antes de uma release.

## Testes Python

```bash
python3 -m compileall src/syssense
python3 -m unittest
```

Os testes usam `unittest` e mocks para evitar dependência do estado real da máquina, internet, `systemctl` ou `journalctl`.

## Metadados Desktop

```bash
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
```

## Empacotamento Python

```bash
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
rm -rf /tmp/syssense-install-test
```

## Scripts Nativos

```bash
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```

Para teste real da instalação nativa:

```bash
./packaging/native/uninstall.sh
./packaging/native/install.sh
syssense
```

## Limpeza

```bash
rm -rf build src/syssense.egg-info
find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
```

## Lint Opcional

`ruff` pode ser usado como ferramenta opcional de desenvolvimento, sem virar dependência do usuário final:

```bash
python3 -m pip install ruff
ruff check src tests
```
