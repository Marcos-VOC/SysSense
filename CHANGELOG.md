# Changelog

Todas as mudanças relevantes do SysSense serão documentadas aqui.

## [Não lançado]

### Corrigido

- Popover de preferências pode ser fechado pela engrenagem ou por clique fora da área.
- Popover de preferências fecha automaticamente após alterar o intervalo de atualização.
- Cards ocultos na dashboard deixam de reservar espaço visual, permitindo que os cards seguintes preencham a grade.

### Experimental

- Troca das seções principais passa a usar transição lateral leve.
- Guias internas de Processos passam a usar transição lateral leve.
- Popovers de alertas e configurações passam a revelar o conteúdo com animação curta.
- Painel de riscos passa a abrir dentro da janela do aplicativo, sem popup externo do sistema.
- Painel de configurações passa a abrir dentro da janela do aplicativo, com a mesma linguagem visual do painel de riscos.
- Painéis internos de riscos e configurações ganharam mais distância da sidebar.
- Mensagens curtas de alerta nos cards passam a aparecer e sumir com revelação suave.

## [0.3.4] - 2026-06-07

### Adicionado

- Preferências locais em `~/.config/syssense/config.json`.
- Popover discreto de preferências na sidebar.
- Seleção de cards visíveis na dashboard.
- Opções fixas de intervalo de atualização: `1s`, `2.5s`, `5s` e `10s`.
- Opções para exibir/ocultar toasts críticos e cards da dashboard.

### Alterado

- Rodapé da sidebar passa a refletir o intervalo de atualização configurado.
- Cards da dashboard respeitam preferências persistidas.

## [0.3.3] - 2026-06-07

### Adicionado

- Configuração persistente validada com defaults seguros.
- Testes para configuração ausente, inválida e salva em JSON.

## [0.3.2] - 2026-06-07

### Alterado

- Alertas automáticos agora removem duplicidades por categoria, mantendo a maior severidade ativa.
- Mensagens dos alertas ficaram mais acionáveis.
- Aba Serviços ganhou estados mais claros para tudo certo, falhas detectadas e indisponibilidade.
- Aba Disco passou a exibir o sistema de arquivos junto das informações de uso.
- Processos ganharam tooltip com o valor completo quando o texto é truncado.

## [0.3.1] - 2026-06-07

### Adicionado

- Testes adicionais para coletores, serviços, logs, speedtest e configuração.
- Testes de deduplicação e ordenação de alertas.
- Documento `docs/testing.md` com comandos de validação.

## [0.3.0] - 2026-06-07

### Alterado

- Instalador nativo local ganhou checagens mais claras para Fedora, GTK/libadwaita, `pip` e `PATH`.
- Desinstalador nativo ganhou mensagens mais seguras quando Python não está disponível.
- Documentação registra que RPM/COPR seguem como possibilidade futura, sem prioridade imediata.

## [0.2.1] - 2026-06-06

### Adicionado

- Testes leves com `unittest` para diagnóstico e detecção de modo de execução.
- Documentação revisada para instalação nativa, Flatpak sandbox, segurança e privacidade.
- Painel de status na sidebar para listar alertas automáticos ativos.
- Tabela de níveis de alerta no README.

### Alterado

- Projeto consolidado como native-first: a instalação nativa local é o modo recomendado para monitoramento completo do Fedora.
- Aba manual de Diagnóstico removida; as regras agora alimentam alertas automáticos na sidebar e nos cards.
- README reorganizado com instruções mais claras, captura de tela e validações recomendadas.
- Mensagens e documentação revisadas com acentuação e terminologia mais polidas.
- Painel de alertas refinado visualmente para combinar com os cards da dashboard.

### Corrigido

- Reset do alerta visual de memória sem depender de sinal frágil do toast.
- Textos do instalador nativo com acentuação correta.
- Warning de CSS causado por propriedade não suportada pelo GTK.
- Erro na aba Serviços ao renderizar logs recentes.

## [0.2.0] - 2026-06-06

### Adicionado

- Alertas visuais discretos para memória crítica e armazenamento elevado.
- Leitura de rede em tempo real no card de tráfego, com tooltip de acumulado.
- Diagnóstico automático mais explicativo, incluindo principais consumidores de CPU e memória.
- Melhor feedback visual em ações de Serviços e no painel de alertas.

### Alterado

- Aba de Serviços passa a exibir falhas e logs com mensagens de fallback mais amigáveis.
- Aba de Processos informa quando o app está rodando em Flatpak sandbox.
- Documentação do spike Flatpak registra a limitação real de processos no sandbox.

## [0.1.0] - 2026-06-06

### Adicionado

- Dashboard em GTK 4 + libadwaita com cards para CPU, memória, armazenamento, temperatura, rede, carga do sistema, uptime e internet.
- Aba de processos com visualização por memória, por CPU e comparação responsiva.
- Aba de disco com partições, uso, espaço livre e alertas.
- Aba de serviços com coleta de falhas systemd e logs recentes.
- Diagnóstico local por regras.
- Teste de velocidade sob demanda usando `speedtest-cli`.
- Metadados profissionais para desktop Linux: `.desktop`, AppStream/metainfo e ícone SVG.
- Manifest inicial Flatpak para distribuição local e futura publicação.
- Documentação de segurança e privacidade.
- Scripts de instalação nativa local e remoção.
- Detecção de modo Flatpak com aviso de processos limitados ao sandbox.

### Alterado

- Interface migrada para GTK 4 e libadwaita.
- Atualização automática das métricas principais ajustada para 2.5 segundos.
- Estrutura reorganizada para `data/`, `packaging/flatpak/` e pacote instalável via `pyproject.toml`.
- Chamadas externas endurecidas com ambiente controlado, timeout, sem shell e sanitização de texto.

### Observações

- O Flatpak ainda precisa de validação em ambiente com `flatpak` e `flatpak-builder` instalados.
- Leitura de serviços/logs pode ter limitações dentro do sandbox Flatpak, dependendo das permissões do sistema.
