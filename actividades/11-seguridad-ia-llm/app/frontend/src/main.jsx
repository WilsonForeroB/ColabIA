import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './App.css'

// Punto de entrada: monta el componente <App /> dentro de #root (index.html).
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
