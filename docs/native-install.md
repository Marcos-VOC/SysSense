# Instalacao nativa local

Este modo e recomendado quando o objetivo e monitorar o Fedora real, como acontece durante o desenvolvimento local.

## Caracteristicas

- Instala o pacote Python no usuario atual com `pip install --user`.
- Cria atalho local em `~/.local/share/applications`.
- Copia o icone para `~/.local/share/icons`.
- Nao instala o SysSense como root.
- Nao cria servico em background.
- Nao altera configuracoes do sistema.

## Requisitos Fedora

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

As dependencias Python (`psutil` e `speedtest-cli`) sao instaladas pelo `pip` no ambiente do usuario.

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

- nao encerra processos;
- nao altera servicos;
- nao grava metricas em disco;
- nao usa `shell=True`;
- executa apenas consultas de leitura com timeout.

O modo nativo tem menos isolamento que Flatpak, mas e o modo correto para um monitor que precisa enxergar processos e metricas reais do host.
