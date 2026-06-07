# Release v0.3

Este documento registra o escopo técnico da série `v0.3.x` do SysSense.

## Proposta

A série `v0.3` consolida o SysSense como um monitor nativo local mais configurável, com melhor acabamento visual e uma base interna mais preparada para manutenção.

O foco continua sendo Fedora/GNOME, modo nativo local como caminho recomendado e operação somente leitura.

## Principais Mudanças

- instalação nativa refinada com checagens mais claras;
- testes ampliados para coletores, diagnósticos, configuração e formatadores;
- configuração persistente em `~/.config/syssense/config.json`;
- seleção de cards visíveis na dashboard;
- reorganização automática da grade quando cards são ocultados;
- painéis internos de status e preferências, sem popups externos do sistema;
- transições leves entre seções, guias de processos e mensagens de alerta;
- primeira etapa de reestruturação com CSS separado e formatadores dedicados.

## Organização Técnica

A partir desta série:

- `src/syssense/config.py` cuida das preferências locais;
- `src/syssense/formatters.py` centraliza formatação de unidades e textos;
- `src/syssense/resources/styles.css` concentra estilos GTK;
- `pyproject.toml` inclui o CSS como recurso do pacote instalável.

`src/syssense/window.py` ainda concentra a maior parte da interface. A divisão em módulos menores fica documentada em `docs/restructure-roadmap.md` e deve acontecer em etapas futuras.

## Validação Recomendada

```bash
python3 -m compileall src/syssense
python3 -m unittest
python3 -m pip install --no-deps --target /tmp/syssense-install-test .
desktop-file-validate data/applications/br.com.syssense.desktop
appstreamcli validate --no-net data/metainfo/br.com.syssense.metainfo.xml
bash -n packaging/native/install.sh packaging/native/uninstall.sh
```

Depois da validação:

```bash
rm -rf /tmp/syssense-install-test build src/syssense.egg-info
find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

## Fora do Escopo

- temas visuais configuráveis;
- reorganização manual dos cards;
- gráficos históricos;
- RPM/COPR;
- integração com IA externa.
