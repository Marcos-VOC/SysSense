#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." >/dev/null 2>&1 && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="$(command -v python3 || true)"
fi

if [[ -z "${PYTHON_BIN:-}" ]]; then
    echo "Python 3 não encontrado." >&2
    exit 1
fi

CHECK_ENV=(env -u PYTHONPATH -u PYTHONHOME PYTHONNOUSERSITE=1)
PIP_ENV=(env -u PYTHONPATH -u PYTHONHOME)

if ! "${CHECK_ENV[@]}" "$PYTHON_BIN" - <<'PY'
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
PY
then
    cat >&2 <<'EOF'
GTK 4/libadwaita para Python não estão disponíveis.

No Fedora, instale os pacotes do sistema e rode este script novamente:

  sudo dnf install python3-gobject gtk4 libadwaita
EOF
    exit 1
fi

"${PIP_ENV[@]}" "$PYTHON_BIN" -m pip install --user "$PROJECT_DIR"

APP_ID="br.com.syssense"
LOCAL_BIN="${HOME}/.local/bin/syssense"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
ICONS_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
DESKTOP_FILE="${APPLICATIONS_DIR}/${APP_ID}.desktop"
ICON_FILE="${ICONS_DIR}/${APP_ID}.svg"
LEGACY_DESKTOP_FILE="${APPLICATIONS_DIR}/syssense.desktop"
LEGACY_ICON_FILE="${ICONS_DIR}/syssense.svg"

if [[ ! -x "$LOCAL_BIN" ]]; then
    echo "O comando ${LOCAL_BIN} não foi criado pelo pip." >&2
    exit 1
fi

mkdir -p "$APPLICATIONS_DIR" "$ICONS_DIR"
rm -f "$LEGACY_ICON_FILE"
install -m 0644 "$PROJECT_DIR/data/icons/hicolor/scalable/apps/${APP_ID}.svg" "$ICON_FILE"
sed \
    -e "s|^Exec=.*|Exec=${LOCAL_BIN}|" \
    -e "s|^Icon=.*|Icon=${ICON_FILE}|" \
    "$PROJECT_DIR/data/applications/${APP_ID}.desktop" > "$DESKTOP_FILE"
chmod 0644 "$DESKTOP_FILE"

# Compatibilidade para favoritos antigos que apontavam para syssense.desktop.
cp "$DESKTOP_FILE" "$LEGACY_DESKTOP_FILE"
{
    echo "NoDisplay=true"
    echo "Hidden=false"
} >> "$LEGACY_DESKTOP_FILE"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q "${HOME}/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

cat <<EOF
SysSense instalado em modo nativo.

Comando:
  ${LOCAL_BIN}

Atalho:
  ${DESKTOP_FILE}

Ícone:
  ${ICON_FILE}

Este modo roda como seu usuário normal e lê as métricas reais do Fedora.
EOF
