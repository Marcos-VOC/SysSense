#!/usr/bin/env bash

set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

if [[ ! -x "$PYTHON_BIN" ]]; then
    PYTHON_BIN="$(command -v python3 || true)"
fi

CLEAN_ENV=(env -u PYTHONPATH -u PYTHONHOME)

APP_ID="br.com.syssense"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
ICONS_DIR="${HOME}/.local/share/icons/hicolor/scalable/apps"

if [[ -n "${PYTHON_BIN:-}" ]]; then
    "${CLEAN_ENV[@]}" "$PYTHON_BIN" -m pip uninstall -y syssense || true
else
    echo "Python 3 não encontrado; removendo apenas atalhos e ícones locais."
fi

rm -f "${APPLICATIONS_DIR}/${APP_ID}.desktop"
rm -f "${ICONS_DIR}/${APP_ID}.svg"
rm -f "${APPLICATIONS_DIR}/syssense.desktop"
rm -f "${ICONS_DIR}/syssense.svg"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPLICATIONS_DIR" >/dev/null 2>&1 || true
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q "${HOME}/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi

echo "SysSense removido do modo nativo local."
