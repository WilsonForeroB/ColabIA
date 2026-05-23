---
name: pull-request
description: >
  Crea Pull Requests en GitHub con formato estandarizado siguiendo Conventional Commits.
  Usa esta skill cuando el usuario diga "crear PR", "abrir pull request", "make PR",
  "subir cambios", "PR a develop", o cualquier variación. La skill lee el diff del
  branch actual vs develop, genera el título y body con IA, pide confirmación al
  humano, y crea el PR. NUNCA hace merge — eso es responsabilidad exclusiva del humano.
---

# Pull Request Skill

Automatiza la creación de PRs con formato consistente hacia `develop`.

## Reglas importantes

- **Base branch siempre es `develop`** — nunca `main` ni otro
- **Nunca hacer merge** — solo crear el PR y esperar al humano
- **Siempre pedir confirmación** antes de ejecutar `gh pr create`
- El humano revisa, edita si quiere, y aprueba antes de crear

---

## Flujo paso a paso

### 1. Verificar prerequisitos

```bash
# Verificar que gh CLI está autenticado
gh auth status

# Verificar branch actual (no debe ser develop ni main)
git branch --show-current

# Verificar que hay diferencias con develop
git log develop..HEAD --oneline
```

Si el branch actual es `develop` o `main`, detente y avisa al usuario.
Si no hay commits sobre `develop`, detente y avisa.

### 2. Obtener el diff

```bash
# Commits nuevos vs develop
git log develop..HEAD --oneline

# Diff completo para contexto de la IA
git diff develop..HEAD
```

### 3. Generar título y body con IA

Usa el diff y los commits para generar:

**Título** — Conventional Commits:

```
<type>(<scope>): <descripción corta en imperativo>
```

Tipos válidos: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`, `style`, `perf`

**Body** con exactamente estas dos secciones:

```markdown
## What changed
- <cambio concreto 1>
- <cambio concreto 2>

## Why
- <razón o motivación 1>
- <razón o motivación 2>
```

Reglas del contenido:
- Bullets concisos, en inglés o el idioma del proyecto
- "What changed" describe el **qué** técnico
- "Why" describe el **contexto, problema o motivación**
- Sin mencionar archivos individuales a menos que sea crítico
- Sin sección de screenshots, testing ni checklist

### 4. Mostrar preview y pedir confirmación

Presenta al usuario:

```
📋 PR Preview
─────────────────────────────
Título:  feat(auth): add JWT refresh token logic

Base:    develop
Branch:  feature/jwt-refresh

## What changed
- Added refresh token endpoint
- Extended token expiry to 7 days

## Why
- Users were being logged out unexpectedly
- Aligns with new session management policy
─────────────────────────────
¿Crear este PR? (sí / no / editar)
```

- Si dice **sí** → ejecutar paso 5
- Si dice **no** → cancelar
- Si dice **editar** → dejar que el usuario dicte los cambios y volver a mostrar preview

### 5. Crear el PR

```bash
gh pr create \
  --base develop \
  --title "<título generado>" \
  --body "<body generado>"
```

Después de crear, muestra la URL del PR al usuario.

---

## Errores comunes

| Situación | Acción |
|---|---|
| Branch actual es `develop` o `main` | Avisar y detener |
| No hay commits sobre `develop` | Avisar: "No hay cambios nuevos respecto a develop" |
| `gh` no autenticado | Indicar: `gh auth login` |
| Remote no configurado | Indicar: `git remote -v` para diagnosticar |

---

## Ejemplo de PR bien formado

**Título:**

```
fix(api): handle null response from payment gateway
```

**Body:**

```markdown
## What changed
- Added null check before parsing payment gateway response
- Returns 422 with descriptive error when gateway response is empty

## Why
- Gateway occasionally returns empty body on network timeouts
- Was causing unhandled exceptions in production
```
