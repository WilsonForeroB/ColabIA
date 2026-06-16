// StatusBadge — chip visual que indica en qué modo corre el backend.
// Rojo = VULNERABLE (main.py), Verde = SEGURO (secure.py).
// El modo lo reporta el backend en GET /api/status, así que es fiable:
// refleja qué fichero está ejecutando uvicorn, no una selección del frontend.

export default function StatusBadge({ mode }) {
  const isSecure = mode === 'secure'
  return (
    <span className={`badge ${isSecure ? 'badge-secure' : 'badge-vulnerable'}`}>
      {isSecure ? '● SEGURO' : '● VULNERABLE'}
    </span>
  )
}
