#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." >/dev/null 2>&1 && pwd)"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="$(command -v python3 || true)"
fi

if [[ -z "${PYTHON_BIN:-}" ]]; then
    echo "Python 3 nao encontrado." >&2
    exit 1
fi

if ! "$PYTHON_BIN" - <<'PY'
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
PY
then
    cat >&2 <<'EOF'
GTK 4/libadwaita para Python nao estao disponiveis.

No Fedora, instale os pacotes do sistema e rode este script novamente:

  sudo dnf install python3-gobject gtk4 libadwaita
EOF
    exit 1
fi

"$PYTHON_BIN" -m pip install --user "$PROJECT_DIR"

APP_ID="br.com.syssense"
LOCAL_BIN="${HOME}/.local/bin/syssense"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
ICONS_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"
DESKTOP_FILE="${APPLICATIONS_DIR}/${APP_ID}.desktop"
ICON_FILE="${ICONS_DIR}/${APP_ID}.svg"

if [[ ! -x "$LOCAL_BIN" ]]; then
    echo "O comando ${LOCAL_BIN} nao foi criado pelo pip." >&2
    exit 1
fi

mkdir -p "$APPLICATIONS_DIR" "$ICONS_DIR"
sed "s|^Exec=.*|Exec=${LOCAL_BIN}|" \
    "$PROJECT_DIR/data/applications/${APP_ID}.desktop" > "$DESKTOP_FILE"
chmod 0644 "$DESKTOP_FILE"
install -m 0644 "$PROJECT_DIR/data/icons/hicolor/scalable/apps/${APP_ID}.svg" "$ICON_FILE"

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

Este modo roda como seu usuario normal e le as metricas reais do Fedora.
EOF
