# Instalação nativa local

Este modo é recomendado quando o objetivo é monitorar o Fedora real, como acontece durante o desenvolvimento local.

## Características

- Instala o pacote Python no usuário atual com `pip install --user`.
- Cria atalho local em `~/.local/share/applications`.
- Copia o ícone para `~/.local/share/icons`.
- Não instala o SysSense como root.
- Não cria serviço em background.
- Não altera configurações do sistema.

## Requisitos Fedora

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

As dependências Python (`psutil` e `speedtest-cli`) são instaladas pelo `pip` no ambiente do usuário.

## Instalar

Na raiz do projeto:

```bash
./packaging/native/install.sh
```

## Rodar

```bash
syssense
```

Ou pelo menu de aplicativos do GNOME.

## Remover

```bash
./packaging/native/uninstall.sh
```

## Segurança

Mesmo em modo nativo, o SysSense continua sendo somente leitura na v0.1:

- não encerra processos;
- não altera serviços;
- não grava métricas em disco;
- não usa `shell=True`;
- executa apenas consultas de leitura com timeout.

O modo nativo tem menos isolamento que Flatpak, mas é o modo correto para um monitor que precisa enxergar processos e métricas reais do host.
