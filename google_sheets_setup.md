# Guía de Configuración: Google Sheets para Usuarios

Para que el sistema pueda guardar usuarios en Google Sheets, necesitas generar unas "credenciales" especiales. Sigue estos pasos:

## Paso 1: Crear Proyecto en Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Haz clic en el selector de proyectos (arriba a la izquierda) y selecciona **"Nuevo Proyecto"**.
3. Ponle un nombre (ej: `SistGoy-Auth`) y dale a **Crear**.

## Paso 2: Habilitar APIs
1. En el menú de la izquierda, ve a **"APIs y servicios" > "Biblioteca"**.
2. Busca **"Google Sheets API"** y haz clic en **Habilitar**.
3. Vuelve a la Biblioteca, busca **"Google Drive API"** y haz clic en **Habilitar**.

## Paso 3: Crear Cuenta de Servicio (Service Account)
1. Ve a **"APIs y servicios" > "Credenciales"**.
2. Haz clic en **"Crear Credenciales"** > **"Cuenta de servicio"**.
3. Ponle un nombre (ej: `gestor-usuarios`) y dale a **Crear y continuar**.
4. En "Rol", selecciona **"Proyecto" > "Editor"**. Dale a **Continuar** y luego a **Listo**.

## Paso 4: Descargar la Llave (JSON)
1. En la lista de "Cuentas de servicio", haz clic en el email de la cuenta que acabas de crear (ej: `gestor-usuarios@...`).
2. Ve a la pestaña **"Claves"**.
3. Haz clic en **"Agregar clave"** > **"Crear clave nueva"**.
4. Selecciona **JSON** y dale a **Crear**.
5. Se descargará un archivo en tu PC. **Cámbiale el nombre a `credentials.json`**.
6. **Mueve ese archivo `credentials.json` a la carpeta de tu proyecto** (donde está `dashboard.py`).

## Paso 5: Crear y Compartir la Hoja de Cálculo
1. Ve a [Google Sheets](https://docs.google.com/spreadsheets/) y crea una hoja nueva llamada **`SistGoy_Usuarios`**.
2. En la primera fila, escribe estos encabezados exactos:
   - Columna A: `username`
   - Columna B: `password`
   - Columna C: `email`
   - Columna D: `name`
   - Columna E: `created_at`
3. Haz clic en el botón **"Compartir"** (arriba a la derecha).
4. Copia el **email de la cuenta de servicio** (el que aparece en el Paso 4.1, algo como `gestor-usuarios@sistgoy-auth...`).
5. Pégalo en el cuadro de compartir, asegúrate de que tenga permisos de **Editor**, y dale a **Enviar**.

¡Listo! Una vez tengas el archivo `credentials.json` en la carpeta y la hoja compartida, el sistema funcionará.
