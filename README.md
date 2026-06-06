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

## Instalação

Antes de instalar, escolha o modo de execução:

| Modo | Quando usar | O que esperar |
|------|-------------|---------------|
| **Nativo local** | Melhor opção para uso diário como monitor de sistema. | Mostra processos e métricas reais do Fedora, rodando como usuário normal. |
| **Flatpak sandbox** | Melhor opção para testar o app com isolamento. | O app fica isolado; processos, serviços e logs podem refletir apenas o sandbox. |

Os dois modos são somente leitura na v0.1: o SysSense não altera configurações, não encerra processos e não controla serviços.

### Opção recomendada: nativo local

Use este modo se você quer que o SysSense funcione como na máquina de desenvolvimento, vendo o sistema real.

1. Instale os pacotes GTK/libadwaita do Fedora:

   ```bash
   sudo dnf install python3-gobject gtk4 libadwaita
   ```

2. Clone o repositório e entre na pasta:

   ```bash
   git clone https://github.com/Marcos-VOC/SysSense.git
   cd SysSense
   ```

3. Instale no usuário atual:

   ```bash
   ./packaging/native/install.sh
   ```

4. Abra pelo menu de aplicativos procurando por `SysSense`, ou rode:

   ```bash
   syssense
   ```

O instalador cria:

- comando: `~/.local/bin/syssense`;
- atalho: `~/.local/share/applications/br.com.syssense.desktop`;
- ícone: `~/.local/share/icons/hicolor/scalable/apps/br.com.syssense.svg`.

Para atualizar uma instalação nativa, entre na pasta do projeto atualizada e rode novamente:

```bash
./packaging/native/install.sh
```

Para remover:

```bash
./packaging/native/uninstall.sh
```

### Opção isolada: Flatpak sandbox

Use este modo se você quer testar o app isolado. Por causa do sandbox, a aba de processos pode mostrar apenas processos internos do Flatpak, como `syssense` e `bwrap`. Para monitoramento completo do host, use a instalação nativa local.

1. Instale as ferramentas:

   ```bash
   sudo dnf install flatpak flatpak-builder
   flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
   flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
   ```

2. Clone o repositório e entre no manifest:

   ```bash
   git clone https://github.com/Marcos-VOC/SysSense.git
   cd SysSense/packaging/flatpak
   ```

3. Construa:

   ```bash
   flatpak-builder --force-clean ../../flatpak-build br.com.syssense.yml
   ```

4. Rode sem instalar:

   ```bash
   flatpak-builder --run ../../flatpak-build br.com.syssense.yml syssense
   ```

5. Opcionalmente, instale no usuário atual:

   ```bash
   flatpak-builder --user --install --force-clean ../../flatpak-build br.com.syssense.yml
   flatpak run br.com.syssense
   ```

Para remover a instalação Flatpak local:

```bash
flatpak uninstall --user br.com.syssense
```

## Rodar em desenvolvimento

Use este modo se você está editando o código localmente:

```bash
python3 -m pip install -r requirements.txt
./run.sh
```

Ou diretamente:

```bash
PYTHONPATH=src /usr/bin/python3 -m syssense.main
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
