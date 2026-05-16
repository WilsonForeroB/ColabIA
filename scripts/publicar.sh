#!/bin/bash
# Sincroniza actividades/ y README.md hacia la rama develop
# sin llevar archivos internos de Claude (.claude/, CLAUDE.md)
set -e

RAMA_ORIGEN="claude/config-inicial"
RAMA_DESTINO="develop"

echo "→ Cambiando a $RAMA_DESTINO..."
git checkout "$RAMA_DESTINO"

echo "→ Copiando actividades/ desde $RAMA_ORIGEN..."
git checkout "$RAMA_ORIGEN" -- actividades/

echo "→ Copiando README.md desde $RAMA_ORIGEN..."
git checkout "$RAMA_ORIGEN" -- README.md

echo "→ Haciendo commit..."
git add actividades/ README.md
git commit -m "Publicar actividades desde $RAMA_ORIGEN"

echo "→ Publicando en origin/$RAMA_DESTINO..."
git push origin "$RAMA_DESTINO"

echo "→ Volviendo a $RAMA_ORIGEN..."
git checkout "$RAMA_ORIGEN"

echo "✅ Listo. develop actualizado sin archivos internos de Claude."
