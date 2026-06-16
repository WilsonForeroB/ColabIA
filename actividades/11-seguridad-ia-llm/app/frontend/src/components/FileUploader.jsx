import { useState } from 'react'

// FileUploader — zona de entrada. El usuario puede:
//   (a) pegar/escribir texto en el textarea, y/o
//   (b) subir un fichero (.txt/.md) cuyo contenido se lee en el navegador.
// Al pulsar "Enviar al LLM" llama a onSend({ text, fileContent }).
//
// El `text` lo controla el padre (App) para que el AttackPanel pueda
// rellenarlo al pulsar "Usar este ataque": por eso es un componente controlado.
export default function FileUploader({ text, setText, onSend, loading }) {
  const [fileName, setFileName] = useState('')      // Nombre del fichero subido (UI)
  const [fileContent, setFileContent] = useState('') // Contenido leído del fichero

  // Lee el fichero seleccionado como texto plano usando FileReader.
  function handleFile(e) {
    const file = e.target.files[0]
    if (!file) return
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = (ev) => setFileContent(ev.target.result)
    reader.readAsText(file)
  }

  // Limpia el fichero adjunto (por si el usuario quiere mandar solo texto).
  function clearFile() {
    setFileName('')
    setFileContent('')
  }

  function handleSubmit() {
    // No enviamos si no hay nada que mandar ni mientras carga una respuesta.
    if (loading || (!text.trim() && !fileContent.trim())) return
    onSend({ text, fileContent })
  }

  return (
    <div className="card">
      <h2>📄 Entrada</h2>

      <textarea
        className="textarea"
        placeholder="Pega o escribe tu consulta aquí…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={5}
      />

      <div className="file-row">
        <label className="file-label">
          Subir fichero
          <input type="file" accept=".txt,.md" onChange={handleFile} hidden />
        </label>
        {fileName && (
          <span className="file-name">
            {fileName} <button className="link" onClick={clearFile}>✕</button>
          </span>
        )}
        <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Enviando…' : 'Enviar al LLM'}
        </button>
      </div>
    </div>
  )
}
