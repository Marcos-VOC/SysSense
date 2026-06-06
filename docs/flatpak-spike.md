# Spike Flatpak

Este documento registra a estratégia técnica para distribuir o SysSense como Flatpak na v0.1.

## Objetivo

Empacotar o SysSense em modo sandbox para quem prefere isolamento do app. Este modo não substitui totalmente a instalação nativa quando o objetivo é monitorar todos os processos reais do host.

## Arquivos criados

- `packaging/flatpak/br.com.syssense.yml`: manifest Flatpak.
- `pyproject.toml`: pacote Python instalável e comando `syssense`.
- `data/applications/br.com.syssense.desktop`: launcher desktop canônico.
- `data/metainfo/br.com.syssense.metainfo.xml`: metadados AppStream.
- `data/icons/hicolor/scalable/apps/br.com.syssense.svg`: ícone do app.

## Base técnica

O manifest usa:

- Runtime: `org.gnome.Platform`.
- SDK: `org.gnome.Sdk`.
- Runtime version: `50`.
- Command: `syssense`.

O GNOME Runtime fornece GTK, libadwaita e PyGObject. As dependências Python que não fazem parte do runtime são empacotadas como módulos:

- `psutil==7.2.2`
- `speedtest-cli==2.1.3`

## Permissões escolhidas

O SysSense é um monitor de sistema. Sem permissões extras, o sandbox Flatpak tende a esconder informações do host. Por isso o manifest inclui:

- `--socket=wayland`
- `--socket=fallback-x11`
- `--share=ipc`
- `--share=network`
- `--filesystem=/proc:ro`
- `--filesystem=/sys:ro`
- `--talk-name=org.freedesktop.systemd1`
- `--system-talk-name=org.freedesktop.systemd1`

### Por que essas permissões existem

- `/proc:ro`: CPU, memória, uptime, processos e parte das métricas do `psutil`.
- `/sys:ro`: sensores, informações de hardware e algumas leituras de disco.
- `network`: necessário para o teste de internet.
- `systemd1`: tentativa de permitir consulta de serviços systemd.

Permissões mais amplas, como `--filesystem=/run/host:ro`, não ficam habilitadas por padrão. Elas só devem ser consideradas se o spike provar que alguma métrica essencial fica incorreta dentro do sandbox.

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
- Processos aparecem nas três abas, mas limitados ao sandbox Flatpak.
- Rede mostra bytes enviados/recebidos.
- Temperatura aparece ou exibe "Sensor não disponível" sem quebrar UI.
- Tempo ligado aparece corretamente.
- Teste de internet roda ou mostra erro curto sem deformar o card.
- Aba Serviços lista falhas ou exibe estado vazio sem travar.
- Diagnóstico executa usando os dados coletados.

## Resultado do spike

O build Flatpak local foi executado em Fedora e o app abriu corretamente.

Validações feitas:

- Pacote Python construiu e instalou em alvo temporário com `pip install --no-deps --target`.
- `python3 -m compileall src/syssense` passou.
- `desktop-file-validate data/applications/br.com.syssense.desktop` passou.
- `appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml` passou.
- `flatpak-builder --force-clean ../../flatpak-build br.com.syssense.yml` concluiu depois de usar wheel pré-compilado de `psutil`.
- `flatpak-builder --run ../../flatpak-build br.com.syssense.yml syssense` abriu o app.

Resultado observado:

- Dashboard abriu e coletou métricas básicas.
- Aba de processos mostrou apenas processos do sandbox, como `syssense` e `bwrap`.

Isso é esperado: Flatpak isola processos fora do sandbox. Para ver os processos reais do Fedora, use o modo nativo local.

## Riscos conhecidos

- `psutil` dentro de Flatpak enxerga uma visão parcial do host. A lista de processos fica limitada ao namespace do sandbox.
- `systemctl` e `journalctl` podem não funcionar da mesma forma dentro do sandbox. A alternativa mais robusta no futuro é consultar systemd/logs via DBus ou exibir essa funcionalidade como "limitada no Flatpak".
- `speedtest-cli` depende de rede externa e pode falhar por servidor indisponível, DNS, proxy ou captive portal.
- Logs podem conter dados sensíveis do próprio sistema. Por isso a UI limita a quantidade de linhas e o código sanitiza caracteres de controle.

## Próximo passo técnico

Rodar o build em uma máquina Fedora com Flatpak instalado e preencher a tabela abaixo:

| Área | Esperado | Resultado |
|------|----------|-----------|
| Dashboard | CPU/RAM/disco/rede/uptime aparecem | Pendente |
| Processos | Lista limitada ao sandbox, com aviso na UI | Confirmado |
| Temperatura | Valor real ou fallback amigavel | Pendente |
| Serviços | Falhas systemd ou fallback amigável | Pendente |
| Logs | Logs recentes ou fallback amigável | Pendente |
| Speedtest | Resultado ou erro curto com tooltip | Pendente |
