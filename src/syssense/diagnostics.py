"""
Módulo de diagnóstico do sistema.
Define regras de análise e funções para diagnosticar problemas baseados em dados coletados.
"""

from typing import Dict, List, Any
import html


# Regras de diagnóstico como dados estruturados (não if-else)
REGRAS = [
    {
        "campo": "mem_percent",
        "limite": 85,
        "operador": "gt",
        "severidade": "alta",
        "mensagem": "Memória em uso crítico ({valor}%). Verifique antes de abrir novos aplicativos. Principais consumidores: {processos_memoria}."
    },
    {
        "campo": "mem_percent",
        "limite": 70,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "Memória com uso elevado ({valor}%). Considere fechar aplicações não utilizadas."
    },
    {
        "campo": "disco_percent",
        "limite": 90,
        "operador": "gt",
        "severidade": "alta",
        "mensagem": "Disco praticamente cheio ({valor}%). Revise downloads, cache e arquivos grandes com urgência."
    },
    {
        "campo": "disco_percent",
        "limite": 70,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "Disco com espaço limitado ({valor}%). Considere liberar espaço em breve."
    },
    {
        "campo": "failed_services",
        "limite": 0,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "Há {valor} serviço(s) systemd com falha. Abra a aba Serviços para revisar nomes e logs recentes."
    },
    {
        "campo": "cpu_percent",
        "limite": 80,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "CPU em uso intenso ({valor}%). Verifique tarefas pesadas em execução. Principais consumidores: {processos_cpu}."
    },
    {
        "campo": "swap_percent",
        "limite": 50,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "Swap em uso ({valor}%). Memória RAM pode estar insuficiente para a carga atual."
    }
]


def _avaliar_regra(regra: Dict[str, Any], dados: Dict[str, Any]) -> bool:
    """Avalia se uma regra se aplica aos dados."""
    campo = regra.get('campo')
    limite = regra.get('limite')
    operador = regra.get('operador')
    
    # Extrai valor dos dados
    valor = None
    
    if campo == 'mem_percent':
        valor = dados.get('memoria', {}).get('percent', 0)
    elif campo == 'disco_percent':
        # Usa a maior partição
        partitions = dados.get('disco', {}).get('partitions', [])
        if partitions:
            valor = max(p.get('percent', 0) for p in partitions)
        else:
            valor = 0
    elif campo == 'failed_services':
        valor = dados.get('servicos', {}).get('count', 0)
    elif campo == 'cpu_percent':
        valor = dados.get('cpu', {}).get('percent', 0)
    elif campo == 'swap_percent':
        valor = dados.get('memoria', {}).get('swap_percent', 0)
    
    if valor is None:
        return False
    
    # Avalia condição
    if operador == 'gt':
        return valor > limite
    elif operador == 'gte':
        return valor >= limite
    elif operador == 'lt':
        return valor < limite
    elif operador == 'lte':
        return valor <= limite
    elif operador == 'eq':
        return valor == limite
    
    return False


# Compatibilidade com versões anteriores que usavam o nome com erro de digitação.
_evaluar_regra = _avaliar_regra


def _valor_campo(campo: str, dados: Dict[str, Any]) -> Any:
    """Extrai o valor de um campo de diagnóstico."""
    if campo == 'mem_percent':
        return round(dados.get('memoria', {}).get('percent', 0), 1)
    if campo == 'disco_percent':
        partitions = dados.get('disco', {}).get('partitions', [])
        if partitions:
            return round(max(p.get('percent', 0) for p in partitions), 1)
        return 0
    if campo == 'failed_services':
        return dados.get('servicos', {}).get('count', 0)
    if campo == 'cpu_percent':
        return round(dados.get('cpu', {}).get('percent', 0), 1)
    if campo == 'swap_percent':
        return round(dados.get('memoria', {}).get('swap_percent', 0), 1)
    return None


def _formatar_processos(processos: list[dict], campo: str, limite: int = 3) -> str:
    """Resume os principais processos consumidores."""
    principais = []
    for proc in processos[:limite]:
        nome = proc.get('name') or 'desconhecido'
        valor = proc.get(campo, 0)
        principais.append(f"{nome} ({valor:.1f}%)")
    return ", ".join(principais) if principais else "nenhum processo relevante"


def _formatar_mensagem(regra: Dict[str, Any], dados: Dict[str, Any]) -> tuple[str, Any]:
    """Preenche placeholders de uma regra com dados reais."""
    campo = regra.get('campo')
    valor = _valor_campo(campo, dados)
    mensagem = regra['mensagem']

    if valor is not None:
        mensagem = mensagem.replace('{valor}', str(valor))

    processos = dados.get('processos', {})
    mensagem = mensagem.replace(
        '{processos_memoria}',
        _formatar_processos(processos.get('by_memory', []), 'memory_percent')
    )
    mensagem = mensagem.replace(
        '{processos_cpu}',
        _formatar_processos(processos.get('by_cpu', []), 'cpu_percent')
    )

    services = dados.get('servicos', {}).get('failed_services', [])
    servicos = ", ".join(service.get('name', '') for service in services[:3] if service.get('name'))
    mensagem = mensagem.replace('{servicos}', servicos or 'não informado')

    return mensagem, valor


def diagnosticar_por_regras(dados: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Avalia todas as regras contra os dados coletados.
    Retorna lista de alertas ativos organizados por severidade.
    
    Args:
        dados: dict com chaves 'cpu', 'memoria', 'disco', 'processos', 'servicos', 'temperatura'
    
    Returns:
        Lista de dicts com {'severidade', 'mensagem', 'campo'}
    """
    alertas = []
    
    for regra in REGRAS:
        if _avaliar_regra(regra, dados):
            campo = regra.get('campo')
            mensagem, valor = _formatar_mensagem(regra, dados)
            
            alertas.append({
                'severidade': regra['severidade'],
                'mensagem': mensagem,
                'campo': campo,
                'valor': valor,
            })
    
    severidade_order = {'alta': 0, 'media': 1, 'baixa': 2}
    melhores_por_campo = {}
    for alerta in alertas:
        campo = alerta.get('campo')
        atual = melhores_por_campo.get(campo)
        if atual is None:
            melhores_por_campo[campo] = alerta
            continue
        if severidade_order.get(alerta['severidade'], 3) < severidade_order.get(atual['severidade'], 3):
            melhores_por_campo[campo] = alerta

    alertas_deduplicados = list(melhores_por_campo.values())
    alertas_deduplicados.sort(key=lambda x: severidade_order.get(x['severidade'], 3))

    return alertas_deduplicados


def diagnosticar_com_ia(dados: Dict[str, Any]) -> str:
    """
    [RESERVADO PARA VERSÃO FUTURA]
    Geraria diagnóstico personalizado via API de IA (Anthropic, OpenAI).
    
    Args:
        dados: dict com informações do sistema
    
    Returns:
        String com diagnóstico em português (MVP: vazio)
    """
    pass


def gerar_resumo_diagnostico(alertas: List[Dict[str, Any]]) -> str:
    """Gera resumo em português para exibição na UI."""
    if not alertas:
        return (
            "<b>Sistema funcionando normalmente.</b>\n\n"
            "Nenhum alerta ativo foi encontrado nas regras locais."
        )
    
    resumo_parts = ["<b>Diagnóstico do Sistema</b>\n"]
    
    alertas_por_severidade = {}
    for alerta in alertas:
        sev = alerta['severidade']
        if sev not in alertas_por_severidade:
            alertas_por_severidade[sev] = []
        alertas_por_severidade[sev].append(alerta['mensagem'])
    
    if 'alta' in alertas_por_severidade:
        resumo_parts.append("\n<b>Alertas críticos</b>\n")
        for msg in alertas_por_severidade['alta']:
            resumo_parts.append(f"• {html.escape(msg)}\n")
    
    if 'media' in alertas_por_severidade:
        resumo_parts.append("\n<b>Atenção</b>\n")
        for msg in alertas_por_severidade['media']:
            resumo_parts.append(f"• {html.escape(msg)}\n")
    
    if 'baixa' in alertas_por_severidade:
        resumo_parts.append("\n<b>Informações</b>\n")
        for msg in alertas_por_severidade['baixa']:
            resumo_parts.append(f"• {html.escape(msg)}\n")
    
    return "".join(resumo_parts)
