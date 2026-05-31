#!/usr/bin/env bash
# Bloquea acceso a archivos .env y a archivos en .gitignore.
# Se invoca como PreToolUse hook para los tools Read, Edit y Write.

INPUT=$(cat)

# Extraer file_path del JSON de entrada (Read, Edit y Write usan la misma clave)
FILE_PATH=$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null)

# Sin ruta → no aplica (ej. Bash sin file_path)
[ -z "$FILE_PATH" ] && exit 0

BASENAME=$(basename "$FILE_PATH")

# ── 1. Bloquear archivos .env ──────────────────────────────────────────────
# Cubre: .env  .env.local  .env.production  .env.staging  etc.
# Excepciones permitidas: .env.example  .env.sample  .env.template
if printf '%s' "$BASENAME" | grep -qE '^\.env(\..*)?$'; then
    if ! printf '%s' "$BASENAME" | grep -qE '^\.env\.(example|sample|template)$'; then
        python3 -c "
import json, sys
path = sys.argv[1]
print(json.dumps({
    'continue': False,
    'stopReason': (
        '🔒 Acceso bloqueado: \"' + path + '\" es un archivo .env.\n'
        'Los archivos .env contienen credenciales y secretos que no deben ser leídos por Claude.\n'
        'Si necesitas que Claude use una variable de entorno, pásala explícitamente en el mensaje.'
    )
}))
" "$FILE_PATH"
        exit 2
    fi
fi

# ── 2. Bloquear archivos en .gitignore ─────────────────────────────────────
# git check-ignore devuelve exit 0 si el archivo está ignorado
DIR_PATH=$(dirname "$FILE_PATH")
REPO_DIR=$(git -C "$DIR_PATH" rev-parse --show-toplevel 2>/dev/null)

if [ -n "$REPO_DIR" ]; then
    if git -C "$REPO_DIR" check-ignore -q "$FILE_PATH" 2>/dev/null; then
        python3 -c "
import json, sys
path = sys.argv[1]
print(json.dumps({
    'continue': False,
    'stopReason': (
        '🔒 Acceso bloqueado: \"' + path + '\" está en .gitignore.\n'
        'Los archivos ignorados por git suelen contener secretos, credenciales o datos sensibles.\n'
        'Si el acceso es realmente necesario, añade una excepción manual en el script validate_sensitive_files.sh.'
    )
}))
" "$FILE_PATH"
        exit 2
    fi
fi

exit 0
