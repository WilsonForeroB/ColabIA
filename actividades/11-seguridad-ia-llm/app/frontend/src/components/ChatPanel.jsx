// ChatPanel — historial de la conversación.
// Cada mensaje es { role: 'user'|'assistant', content, blocked }.
// Cuando blocked=true (una defensa de secure.py cortó la petición) la burbuja
// se pinta en amarillo con la etiqueta "Bloqueado por defensa".

export default function ChatPanel({ messages, loading }) {
  return (
    <div className="card chat">
      <h2>💬 Conversación</h2>
      <div className="messages">
        {messages.length === 0 && (
          <p className="empty">Envía una consulta para empezar.</p>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={
              'bubble ' +
              (m.role === 'user'
                ? 'bubble-user'
                : m.blocked
                ? 'bubble-blocked'
                : 'bubble-assistant')
            }
          >
            <div className="bubble-role">
              {m.role === 'user' ? 'Tú' : m.blocked ? '🛡️ Bloqueado por defensa' : 'Asistente'}
            </div>
            <div className="bubble-text">{m.content}</div>
          </div>
        ))}

        {loading && <div className="bubble bubble-assistant">…pensando</div>}
      </div>
    </div>
  )
}
