# Spike Flatpak

Este documento registra a estrategia tecnica para distribuir o SysSense como Flatpak na v0.1.

## Objetivo

Empacotar o SysSense em modo sandbox para quem prefere isolamento do app. Este modo nao substitui totalmente a instalacao nativa quando o objetivo e monitorar todos os processos reais do host.

## Arquivos criados

- `packaging/flatpak/br.com.syssense.yml`: manifest Flatpak.
- `pyproject.toml`: pacote Python instalavel e comando `syssense`.
- `data/applications/br.com.syssense.desktop`: launcher desktop canonico.
- `data/metainfo/br.com.syssense.metainfo.xml`: metadados AppStream.
- `data/icons/hicolor/scalable/apps/br.com.syssense.svg`: icone do app.

## Base tecnica

O manifest usa:

- Runtime: `org.gnome.Platform`.
- SDK: `org.gnome.Sdk`.
- Runtime version: `50`.
- Command: `syssense`.

O GNOME Runtime fornece GTK, libadwaita e PyGObject. As dependencias Python que nao fazem parte do runtime sao empacotadas como modulos:

- `psutil==7.2.2`
- `speedtest-cli==2.1.3`

## Permissoes escolhidas

O SysSense e um monitor de sistema. Sem permissoes extras, o sandbox Flatpak tende a esconder informacoes do host. Por isso o manifest inclui:

- `--socket=wayland`
- `--socket=fallback-x11`
- `--share=ipc`
- `--share=network`
- `--filesystem=/proc:ro`
- `--filesystem=/sys:ro`
- `--talk-name=org.freedesktop.systemd1`
- `--system-talk-name=org.freedesktop.systemd1`

### Por que essas permissoes existem

- `/proc:ro`: CPU, memoria, uptime, processos e parte das metricas do `psutil`.
- `/sys:ro`: sensores, informacoes de hardware e algumas leituras de disco.
- `network`: necessario para o teste de internet.
- `systemd1`: tentativa de permitir consulta de servicos systemd.

Permissoes mais amplas, como `--filesystem=/run/host:ro`, nao ficam habilitadas por padrao. Elas so devem ser consideradas se o spike provar que alguma metrica essencial fica incorreta dentro do sandbox.

## Como validar o spike

Instale as ferramentas no Fedora:

```bash
sudo dnf install flatpak flatpak-builder
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install flathub org.gnome.Platform//50 org.gnome.Sdk//50
```

Build local:

```bash
cd packaging/flatpak
flatpak-builder --force-clean ../../flatpak-build br.com.syssense.yml
```

Rodar sem instalar:

```bash
flatpak-builder --run ../../flatpak-build br.com.syssense.yml syssense
```

Instalar localmente:

```bash
flatpak-builder --user --install --force-clean ../../flatpak-build br.com.syssense.yml
flatpak run br.com.syssense
```

Desinstalar:

```bash
flatpak uninstall --user br.com.syssense
```

## Checklist funcional dentro do Flatpak

Ao rodar o app empacotado, verificar:

- CPU atualiza.
- RAM atualiza.
- Armazenamento mostra `Tudo`, `/home`, `/`, `/boot/efi` quando existirem.
- Processos aparecem nas tres abas, mas limitados ao sandbox Flatpak.
- Rede mostra bytes enviados/recebidos.
- Temperatura aparece ou exibe "Sensor nao disponivel" sem quebrar UI.
- Tempo ligado aparece corretamente.
- Teste de internet roda ou mostra erro curto sem deformar o card.
- Aba Servicos lista falhas ou exibe estado vazio sem travar.
- Diagnostico executa usando os dados coletados.

## Resultado do spike

O build Flatpak local foi executado em Fedora e o app abriu corretamente.

Validacoes feitas:

- Pacote Python construiu e instalou em alvo temporario com `pip install --no-deps --target`.
- `python3 -m compileall src/syssense` passou.
- `desktop-file-validate data/applications/br.com.syssense.desktop` passou.
- `appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml` passou.
- `flatpak-builder --force-clean ../../flatpak-build br.com.syssense.yml` concluiu depois de usar wheel pre-compilado de `psutil`.
- `flatpak-builder --run ../../flatpak-build br.com.syssense.yml syssense` abriu o app.

Resultado observado:

- Dashboard abriu e coletou metricas basicas.
- Aba de processos mostrou apenas processos do sandbox, como `syssense` e `bwrap`.

Isso e esperado: Flatpak isola processos fora do sandbox. Para ver os processos reais do Fedora, use o modo nativo local.

## Riscos conhecidos

- `psutil` dentro de Flatpak enxerga uma visao parcial do host. A lista de processos fica limitada ao namespace do sandbox.
- `systemctl` e `journalctl` podem nao funcionar da mesma forma dentro do sandbox. A alternativa mais robusta no futuro e consultar systemd/logs via DBus ou exibir essa funcionalidade como "limitada no Flatpak".
- `speedtest-cli` depende de rede externa e pode falhar por servidor indisponivel, DNS, proxy ou captive portal.
- Logs podem conter dados sensiveis do proprio sistema. Por isso a UI limita a quantidade de linhas e o codigo sanitiza caracteres de controle.

## Proximo passo tecnico

Rodar o build em uma maquina Fedora com Flatpak instalado e preencher a tabela abaixo:

| Area | Esperado | Resultado |
|------|----------|-----------|
| Dashboard | CPU/RAM/disco/rede/uptime aparecem | Pendente |
| Processos | Lista limitada ao sandbox, com aviso na UI | Confirmado |
| Temperatura | Valor real ou fallback amigavel | Pendente |
| Servicos | Falhas systemd ou fallback amigavel | Pendente |
| Logs | Logs recentes ou fallback amigavel | Pendente |
| Speedtest | Resultado ou erro curto com tooltip | Pendente |
