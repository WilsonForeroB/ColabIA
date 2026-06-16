# Manual rápido — GestorPro 2024

## Instalación

GestorPro 2024 requiere Windows 10/11 o macOS 12+. Descarga el instalador
desde el portal de cliente y ejecuta `GestorProSetup.exe`. La instalación
necesita 2 GB libres y permisos de administrador.

## Activación de licencia

Tras la instalación, introduce tu clave de licencia en
Ayuda > Activar producto. La clave tiene el formato `GP24-XXXX-XXXX-XXXX`.
La licencia se valida online; si estás detrás de un proxy corporativo,
configúralo en Preferencias > Red.

## Errores comunes

- **Error 502 al sincronizar:** el servidor no responde. Reintenta en unos
  minutos o revisa tu conexión.
- **La exportación a PDF falla con informes grandes:** actualiza a la versión
  12.4.2, que corrige una fuga de memoria en el módulo de exportación.
- **No arranca tras actualizar:** borra la caché en
  `%APPDATA%/GestorPro/cache` y reinicia.

## Actualizaciones

GestorPro busca actualizaciones automáticamente al iniciar. Para forzar la
comprobación: Ayuda > Buscar actualizaciones.

---

Pregunta sugerida para probar: "Según el manual, ¿cómo soluciono el fallo
de exportación a PDF con informes grandes?"
