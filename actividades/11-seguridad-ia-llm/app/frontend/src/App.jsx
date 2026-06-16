import { useEffect, useState } from 'react'
import StatusBadge from './components/StatusBadge'
import FileUploader from './components/FileUploader'
import ChatPanel from './components/ChatPanel'
import AttackPanel from './components/AttackPanel'

// App — componente raíz. Mantiene el estado global y conecta los paneles:
//   - text:     contenido del textarea (controlado, para que AttackPanel lo rellene)
//   - messages: historial mostrado en ChatPanel
//   - mode:     "vulnerable" | "secure", lo reporta el backend en /api/status
//   - status:   info de configuración para la cabecera
export default function App() {
  const [text, setText] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState(null)

  // Al montar, preguntamos al backend en qué modo está y su configuración.
  // Esto demuestra la vulnerabilidad 3: en main.py /api/status filtra el
  // system prompt completo; en secure.py solo una vista previa recortada.
  useEffect(() => {
    fetch('/api/status')
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus(null))
  }, [])

  // Envía la consulta al backend y añade pregunta + respuesta al historial.
  async function handleSend({ text, fileContent }) {
    setLoading(true)
    // Mostramos de inmediato lo que el usuario envió.
    setMessages((prev) => [...prev, { role: 'user', content: text || '(fichero adjunto)' }])

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, file_content: fileContent || null }),
      })
      const data = await res.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response, blocked: data.blocked },
      ])
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error de conexión: ${e.message}`, blocked: false },
      ])
    } finally {
      setLoading(false)
      setText('') // Limpiamos el campo tras enviar
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🔐 Actividad 11 — Seguridad en IA</h1>
        <StatusBadge mode={status?.mode} />
      </header>

      {/* La vista previa del system prompt evidencia la fuga en modo vulnerable */}
      {status && (
        <div className="config-bar">
          <span>Modelo: <code>{status.model}</code></span>
          <span>System prompt: <code>{status.system_prompt_preview}</code></span>
        </div>
      )}

      <main className="grid">
        <section className="col-left">
          <FileUploader text={text} setText={setText} onSend={handleSend} loading={loading} />
          <ChatPanel messages={messages} loading={loading} />
        </section>
        <aside className="col-right">
          {/* Cargar un ataque solo rellena el textarea; el envío es manual */}
          <AttackPanel onUse={(payload) => setText(payload)} />
        </aside>
      </main>
    </div>
  )
}
