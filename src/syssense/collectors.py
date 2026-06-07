"""
Módulo de coleta de dados do sistema.
Funções puras que retornam dicts com informações de hardware e sistema.
Todas são seguras para rodar em threading (sem efeitos colaterais).
"""

import psutil
import os
import subprocess
import re
from typing import Dict, Any
from datetime import datetime


SAFE_SUBPROCESS_ENV = {
    'PATH': '/usr/bin:/bin',
    'LANG': 'C.UTF-8',
    'LC_ALL': 'C.UTF-8',
}


def get_runtime_info() -> Dict[str, Any]:
    """Retorna informações sobre o modo de execução do app."""
    is_flatpak = bool(os.environ.get('FLATPAK_ID')) or os.path.exists('/.flatpak-info')
    return {
        'is_flatpak': is_flatpak,
        'mode': 'sandbox' if is_flatpak else 'native',
        'process_scope': 'sandbox' if is_flatpak else 'host',
        'description': (
            'Executando em Flatpak sandbox. Algumas métricas podem refletir o sandbox.'
            if is_flatpak
            else 'Executando nativamente. Métricas refletem o host conforme permissões do usuário.'
        ),
    }


def _clean_text(value: Any, max_chars: int = 500) -> str:
    """Remove caracteres de controle e limita texto vindo do sistema."""
    text = str(value or '')
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text[:max_chars]


def _run_readonly_command(command: list[str], timeout: int = 5) -> subprocess.CompletedProcess:
    """Executa comandos de consulta sem shell e com ambiente previsível."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=SAFE_SUBPROCESS_ENV,
        shell=False,
        check=False,
    )


def get_cpu_info() -> Dict[str, Any]:
    """Retorna informações de CPU."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        load_avg = os.getloadavg()
        
        return {
            'percent': cpu_percent,
            'cores_physical': cpu_count,
            'cores_logical': cpu_count_logical,
            'load_avg': {
                '1min': round(load_avg[0], 2),
                '5min': round(load_avg[1], 2),
                '15min': round(load_avg[2], 2)
            }
        }
    except Exception as e:
        return {'error': str(e), 'percent': 0}


def get_memory_info() -> Dict[str, Any]:
    """Retorna informações de RAM."""
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent,
            'swap_total': swap.total,
            'swap_used': swap.used,
            'swap_percent': swap.percent
        }
    except Exception as e:
        return {'error': str(e), 'percent': 0}


def get_disk_info() -> Dict[str, Any]:
    """Retorna informações de disco e partições, sem duplicar bind mounts."""
    try:
        partitions_by_key = {}
        preferred_mounts = {
            '/', '/home', '/boot', '/boot/efi',
            '/run/host/root', '/run/host/root/home',
            '/run/host/root/boot', '/run/host/root/boot/efi'
        }

        def mount_score(mountpoint: str) -> tuple[int, int]:
            if mountpoint in preferred_mounts:
                return (0, len(mountpoint))
            if mountpoint.startswith('/run/host'):
                return (1, len(mountpoint))
            if mountpoint.count('/') <= 2:
                return (2, len(mountpoint))
            return (3, len(mountpoint))

        for part in psutil.disk_partitions(all=False):
            try:
                if not os.path.isdir(part.mountpoint):
                    continue
                usage = psutil.disk_usage(part.mountpoint)
                key = (part.device, part.fstype, usage.total)
                item = {
                    'device': part.device,
                    'mountpoint': part.mountpoint,
                    'fstype': part.fstype,
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent
                }
                current = partitions_by_key.get(key)
                if current is None or mount_score(item['mountpoint']) < mount_score(current['mountpoint']):
                    partitions_by_key[key] = item
            except (PermissionError, OSError):
                continue

        partitions = sorted(partitions_by_key.values(), key=lambda p: mount_score(p['mountpoint']))
        return {
            'partitions': partitions
        }
    except Exception as e:
        return {'error': str(e), 'partitions': []}


def get_top_processes(n: int = 10) -> Dict[str, Any]:
    """Retorna top N processos por memória e CPU."""
    try:
        processes_by_memory = []
        processes_by_cpu = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                pinfo = proc.info
                processes_by_memory.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'memory_percent': pinfo['memory_percent'],
                    'cpu_percent': pinfo['cpu_percent']
                })
                processes_by_cpu.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'memory_percent': pinfo['memory_percent'],
                    'cpu_percent': pinfo['cpu_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Ordena e pega top N
        processes_by_memory.sort(key=lambda x: x['memory_percent'], reverse=True)
        processes_by_cpu.sort(key=lambda x: x['cpu_percent'], reverse=True)
        
        return {
            'by_memory': processes_by_memory[:n],
            'by_cpu': processes_by_cpu[:n]
        }
    except Exception as e:
        return {'error': str(e), 'by_memory': [], 'by_cpu': []}


def get_network_info() -> Dict[str, Any]:
    """Retorna informações de tráfego de rede."""
    try:
        net_io = psutil.net_io_counters()
        
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
    except Exception as e:
        return {'error': str(e)}


def get_temperature() -> Dict[str, Any]:
    """Retorna temperatura do processador ou indica indisponibilidade."""
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return {'disponivel': False}
        
        # Tenta pegar temperatura do core (mais comum)
        if 'coretemp' in temps:
            core_temps = temps['coretemp']
            if core_temps:
                temp_value = core_temps[0].current
                return {
                    'disponivel': True,
                    'celsius': round(temp_value, 1),
                    'label': core_temps[0].label or 'CPU'
                }
        
        # Fallback: primeira temperatura disponível
        for name, entries in temps.items():
            if entries:
                temp_value = entries[0].current
                return {
                    'disponivel': True,
                    'celsius': round(temp_value, 1),
                    'label': entries[0].label or name
                }
        
        return {'disponivel': False}
    except Exception as e:
        return {'disponivel': False, 'error': str(e)}


def get_uptime() -> Dict[str, Any]:
    """Retorna tempo que o sistema está ligado."""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        return {
            'boot_time': boot_time.isoformat(),
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': f"{days}d {hours}h {minutes}m"
        }
    except Exception as e:
        return {'error': str(e)}


def get_failed_services() -> Dict[str, Any]:
    """Retorna serviços systemd com falha."""
    try:
        result = _run_readonly_command(
            ['systemctl', 'list-units', '--failed', '--output=json'],
            timeout=5,
        )
        
        if result.returncode != 0:
            return {'failed_services': [], 'count': 0}
        
        import json
        data = json.loads(result.stdout)
        services = []
        
        for unit in data:
            services.append({
                'name': _clean_text(unit.get('unit', ''), 160),
                'state': _clean_text(unit.get('state', ''), 80),
                'sub_state': _clean_text(unit.get('sub', ''), 80)
            })
        
        return {
            'failed_services': services,
            'count': len(services)
        }
    except Exception as e:
        return {'failed_services': [], 'count': 0, 'error': str(e)}


def get_recent_logs(lines: int = 50) -> Dict[str, Any]:
    """Retorna logs recentes do journalctl."""
    try:
        safe_lines = max(0, min(int(lines), 100))
        result = _run_readonly_command(
            ['journalctl', '-n', str(safe_lines), '--no-pager', '-o', 'short'],
            timeout=5,
        )
        
        if result.returncode != 0:
            return {'logs': []}
        
        log_lines = [
            _clean_text(line.strip(), 500)
            for line in result.stdout.strip().split('\n')
            if line.strip()
        ]
        return {
            'logs': log_lines
        }
    except Exception as e:
        return {'logs': [], 'error': str(e)}


def speedtest() -> Dict[str, Any]:
    """Executa teste de velocidade (operação pesada, sempre em thread)."""
    try:
        from speedtest import Speedtest
        st = Speedtest()
        st.get_servers([])
        st.get_best_server()
        st.download()
        st.upload()
        results = st.results.dict()
        
        return {
            'success': True,
            'download_mbps': round(results['download'] / 1_000_000, 2),
            'upload_mbps': round(results['upload'] / 1_000_000, 2),
            'ping_ms': round(results['ping'], 2),
            'server': results.get('server', {}).get('sponsor', 'Unknown')
        }
    except ImportError:
        return {'success': False, 'error': 'speedtest-cli não instalado'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
