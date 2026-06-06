# SysSense

SysSense e um monitor de sistema para Fedora/GNOME feito em Python com GTK 4 e libadwaita.

O foco da v0.1 e oferecer uma dashboard simples, bonita e local para acompanhar CPU, memoria, armazenamento, processos, rede, temperatura, uptime, servicos systemd, diagnosticos e teste de internet.

## Status

Versao atual: `0.1.0`

Modos oficiais:

- **Nativo local**: recomendado para monitoramento completo do Fedora.
- **Flatpak sandbox**: recomendado para quem prefere isolamento, aceitando limitacoes em processos, servicos e logs.

## Funcionalidades

- Dashboard em cards com CPU, RAM, armazenamento, temperatura, rede, carga do sistema, uptime e internet.
- Grafico de armazenamento com selecao de particao ou visao geral.
- Processos por memoria, por CPU e comparacao responsiva.
- Aba de disco com particoes montadas e alertas de uso.
- Aba de servicos systemd com falhas e logs recentes.
- Diagnostico local baseado em regras.
- Teste de velocidade sob demanda.
- Interface escura com GTK 4 + libadwaita.
- Atualizacao automatica das metricas principais a cada 2.5 segundos.

## Qual instalacao escolher?

Use **nativo local** se voce quer que o app funcione como um monitor de sistema completo, vendo os processos e metricas reais do Fedora.

Use **Flatpak sandbox** se voce prefere isolamento do app. Nesse modo, o SysSense roda dentro do sandbox do Flatpak e algumas informacoes refletem o sandbox, nao o host completo. A aba de processos, por exemplo, pode mostrar apenas `syssense` e `bwrap`.

Os dois modos sao somente leitura na v0.1: o SysSense nao altera configuracoes, nao encerra processos e nao controla servicos.

## Instalacao nativa local

Este modo instala o app no usuario atual, sem instalar o SysSense como root.

Pre-requisito Fedora:

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

Instalar:

```bash
./packaging/native/install.sh
```

Rodar:

```bash
syssense
```

Remover:

```bash
./packaging/native/uninstall.sh
```

O instalador cria um atalho em `~/.local/share/applications/br.com.syssense.desktop` e usa `~/.local/bin/syssense` como comando.

## Rodar em desenvolvimento

```bash
python3 -m pip install -r requirements.txt
./run.sh
```

Ou diretamente:

```bash
PYTHONPATH=src /usr/bin/python3 -m syssense.main
```

## Build Flatpak local

Instale as ferramentas:

```bash
sudo dnf install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
```

Construa:

```bash
cd packaging/flatpak
flatpak-builder --force-clean ../../flatpak-build br.com.syssense.yml
```

Rode sem instalar:

```bash
flatpak-builder --run ../../flatpak-build br.com.syssense.yml syssense
```

Instale localmente:

```bash
flatpak-builder --user --install --force-clean ../../flatpak-build br.com.syssense.yml
flatpak run br.com.syssense
```

## Estrutura do projeto

```text
SysSense/
├── data/
│   ├── applications/       # .desktop canonico
│   ├── icons/              # icone hicolor
│   └── metainfo/           # metadados AppStream
├── docs/
│   ├── flatpak-spike.md
│   └── release-v0.1.md
├── packaging/
│   ├── flatpak/            # manifest Flatpak
│   └── native/             # instalacao local sem root
├── src/
│   └── syssense/
│       ├── collectors.py   # coleta de metricas
│       ├── diagnostics.py  # regras de diagnostico
│       ├── main.py         # Adw.Application
│       └── window.py       # interface GTK/libadwaita
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
└── run.sh
```

## Validacao

```bash
python3 -m compileall src/syssense
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
```

## Seguranca e privacidade

SysSense e somente leitura na v0.1. Ele nao altera configuracoes do sistema, nao encerra processos, nao controla servicos e nao possui telemetria.

A unica acao de rede intencional e o teste de velocidade, iniciado manualmente pelo usuario. Detalhes estao em `SECURITY.md` e `PRIVACY.md`.

## Roadmap

- `v0.1.0`: primeira versao publica com instalacao nativa local e manifest Flatpak.
- `v0.1.1`: ajustes apos testes reais de usuarios no Flatpak.
- `v0.2.0`: melhorias em servicos/logs via DBus e capturas de tela oficiais.

## Licenca

MIT. Veja `LICENSE`.
