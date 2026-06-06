"""
Módulo de diagnóstico do sistema.
Define regras de análise e funções para diagnosticar problemas baseados em dados coletados.
"""

from typing import Dict, List, Any
import json


# Regras de diagnóstico como dados estruturados (não if-else)
REGRAS = [
    {
        "campo": "mem_percent",
        "limite": 85,
        "operador": "gt",
        "severidade": "alta",
        "mensagem": "Memória em uso crítico ({valor}%). Principais processos consumindo RAM detectados."
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
        "mensagem": "Disco praticamente cheio ({valor}%). Libere espaço urgentemente."
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
        "mensagem": "Há {valor} serviço(s) systemd com falha. Verifique a aba Serviços."
    },
    {
        "campo": "cpu_percent",
        "limite": 80,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "CPU em uso intenso ({valor}%). Aplicação pode estar travada ou pesada."
    },
    {
        "campo": "swap_percent",
        "limite": 50,
        "operador": "gt",
        "severidade": "media",
        "mensagem": "Swap memory em uso ({valor}%). Memória RAM pode estar insuficiente."
    }
]


def _evaluar_regra(regra: Dict[str, Any], dados: Dict[str, Any]) -> bool:
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
        if _evaluar_regra(regra, dados):
            # Prepara mensagem com valores reais
            mensagem = regra['mensagem']
            
            # Substitui placeholders
            campo = regra.get('campo')
            valor = None
            
            if campo == 'mem_percent':
                valor = round(dados.get('memoria', {}).get('percent', 0), 1)
            elif campo == 'disco_percent':
                partitions = dados.get('disco', {}).get('partitions', [])
                if partitions:
                    valor = round(max(p.get('percent', 0) for p in partitions), 1)
            elif campo == 'failed_services':
                valor = dados.get('servicos', {}).get('count', 0)
            elif campo == 'cpu_percent':
                valor = round(dados.get('cpu', {}).get('percent', 0), 1)
            elif campo == 'swap_percent':
                valor = round(dados.get('memoria', {}).get('swap_percent', 0), 1)
            
            if valor is not None:
                mensagem = mensagem.replace('{valor}', str(valor))
            
            alertas.append({
                'severidade': regra['severidade'],
                'mensagem': mensagem,
                'campo': campo
            })
    
    # Ordena por severidade (alta primeiro)
    severidade_order = {'alta': 0, 'media': 1, 'baixa': 2}
    alertas.sort(key=lambda x: severidade_order.get(x['severidade'], 3))
    
    return alertas


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
        return "✓ Sistema funcionando normalmente. Nenhum alerta ativo."
    
    resumo_parts = ["🔍 Diagnóstico do Sistema:\n"]
    
    alertas_por_severidade = {}
    for alerta in alertas:
        sev = alerta['severidade']
        if sev not in alertas_por_severidade:
            alertas_por_severidade[sev] = []
        alertas_por_severidade[sev].append(alerta['mensagem'])
    
    if 'alta' in alertas_por_severidade:
        resumo_parts.append("⚠️  ALERTAS CRÍTICOS:\n")
        for msg in alertas_por_severidade['alta']:
            resumo_parts.append(f"  • {msg}\n")
    
    if 'media' in alertas_por_severidade:
        resumo_parts.append("\n⚡ ATENÇÃO:\n")
        for msg in alertas_por_severidade['media']:
            resumo_parts.append(f"  • {msg}\n")
    
    if 'baixa' in alertas_por_severidade:
        resumo_parts.append("\nℹ️  INFORMAÇÕES:\n")
        for msg in alertas_por_severidade['baixa']:
            resumo_parts.append(f"  • {msg}\n")
    
    return "".join(resumo_parts)
