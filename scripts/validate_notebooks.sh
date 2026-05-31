#!/usr/bin/env bash
# Valida todos los .ipynb del repositorio antes de un git pull.
# Se invoca como PreToolUse hook en .claude/settings.json.
# Recibe el JSON del tool use por stdin; filtra solo comandos git pull.

# Leer stdin y extraer el comando bash que Claude va a ejecutar
INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)

# Solo actuar si el comando es git pull (cualquier forma)
if ! printf '%s' "$COMMAND" | grep -qE '(^|\s)git pull(\s|$)'; then
    exit 0
fi

REPO_DIR="$(git -C "$(dirname "$0")/.." rev-parse --show-toplevel 2>/dev/null || echo '/home/user/ColabIA')"
ERRORES=0
ARCHIVOS_CON_ERROR=()

# Buscar todos los .ipynb en actividades/
while IFS= read -r -d '' notebook; do
    resultado=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
    json.loads(content)
    print('ok')
except json.JSONDecodeError as e:
    print(f'JSON inválido: {e}')
except Exception as e:
    print(f'Error: {e}')
" "$notebook" 2>&1)

    if [ "$resultado" != "ok" ]; then
        ARCHIVOS_CON_ERROR+=("$notebook: $resultado")
        ERRORES=$((ERRORES + 1))
    fi
done < <(find "$REPO_DIR/actividades" -name "*.ipynb" -print0 2>/dev/null)

if [ "$ERRORES" -gt 0 ]; then
    # Devolver JSON con mensaje bloqueante para Claude Code
    python3 -c "
import json, sys
archivos = sys.argv[1:]
msg = '❌ ' + str(len(archivos)) + ' notebook(s) con JSON inválido detectado(s) antes del pull:\n'
for a in archivos:
    msg += '  • ' + a + '\n'
msg += '\nCorrígelos primero para evitar conflictos de merge.'
print(json.dumps({'continue': False, 'stopReason': msg}))
" "${ARCHIVOS_CON_ERROR[@]}"
    exit 2
fi

# Todo OK: mensaje informativo sin bloquear
python3 -c "
import json
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'additionalContext': '✅ Todos los notebooks .ipynb son JSON válido.'}}))
"
exit 0
