# SysSense

SysSense é um monitor de sistema para Fedora/GNOME feito em Python com GTK 4 e libadwaita.

O foco da v0.1 é oferecer uma dashboard simples, bonita e local para acompanhar CPU, memória, armazenamento, processos, rede, temperatura, uptime, serviços systemd, diagnósticos e teste de internet.

## Status

Versão atual: `0.1.0`

Modos oficiais:

- **Nativo local**: recomendado para monitoramento completo do Fedora.
- **Flatpak sandbox**: recomendado para quem prefere isolamento, aceitando limitações em processos, serviços e logs.

## Funcionalidades

- Dashboard em cards com CPU, RAM, armazenamento, temperatura, rede, carga do sistema, uptime e internet.
- Gráfico de armazenamento com seleção de partição ou visão geral.
- Processos por memória, por CPU e comparação responsiva.
- Aba de disco com partições montadas e alertas de uso.
- Aba de serviços systemd com falhas e logs recentes.
- Diagnóstico local baseado em regras.
- Teste de velocidade sob demanda.
- Interface escura com GTK 4 + libadwaita.
- Atualização automática das métricas principais a cada 2.5 segundos.

## Qual instalação escolher?

Use **nativo local** se você quer que o app funcione como um monitor de sistema completo, vendo os processos e métricas reais do Fedora.

Use **Flatpak sandbox** se você prefere isolamento do app. Nesse modo, o SysSense roda dentro do sandbox do Flatpak e algumas informações refletem o sandbox, não o host completo. A aba de processos, por exemplo, pode mostrar apenas `syssense` e `bwrap`.

Os dois modos são somente leitura na v0.1: o SysSense não altera configurações, não encerra processos e não controla serviços.

## Instalação nativa local

Este modo instala o app no usuário atual, sem instalar o SysSense como root.

Pré-requisito Fedora:

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
│   ├── applications/       # .desktop canônico
│   ├── icons/              # ícone hicolor
│   └── metainfo/           # metadados AppStream
├── docs/
│   ├── flatpak-spike.md
│   └── release-v0.1.md
├── packaging/
│   ├── flatpak/            # manifest Flatpak
│   └── native/             # instalação local sem root
├── src/
│   └── syssense/
│       ├── collectors.py   # coleta de métricas
│       ├── diagnostics.py  # regras de diagnóstico
│       ├── main.py         # Adw.Application
│       └── window.py       # interface GTK/libadwaita
├── CHANGELOG.md
├── pyproject.toml
├── requirements.txt
└── run.sh
```

## Validação

```bash
python3 -m compileall src/syssense
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
```

## Segurança e privacidade

SysSense é somente leitura na v0.1. Ele não altera configurações do sistema, não encerra processos, não controla serviços e não possui telemetria.

A única ação de rede intencional é o teste de velocidade, iniciado manualmente pelo usuário. Detalhes estão em `SECURITY.md` e `PRIVACY.md`.

## Roadmap

- `v0.1.0`: primeira versão pública com instalação nativa local e manifest Flatpak.
- `v0.1.1`: ajustes após testes reais de usuários no Flatpak.
- `v0.2.0`: melhorias em serviços/logs via DBus e capturas de tela oficiais.

## Licença

MIT. Veja `LICENSE`.
