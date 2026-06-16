# Ludoteca viva – Dashboard Streamlit

Esta app crea un dashboard visual para la Google Sheet:

**Ludoteca viva – Tazelo2010 – base dinámica**

## Archivos

- `app.py`: aplicación principal.
- `requirements.txt`: dependencias para Streamlit Cloud.

## Cómo publicarla

1. Crear una cuenta en GitHub.
2. Crear un repositorio nuevo, por ejemplo: `ludoteca-viva-dashboard`.
3. Subir estos dos archivos:
   - `app.py`
   - `requirements.txt`
4. Abrir https://share.streamlit.io/
5. Conectar GitHub.
6. Elegir el repositorio.
7. En “Main file path”, poner:
   `app.py`
8. Deploy.

## Importante

La Google Sheet tiene que estar compartida como:

“Cualquier persona con el enlace puede ver”

La app lee la hoja `Colección actual` mediante exportación CSV, sin credenciales privadas.

## Qué muestra

- Métricas de colección.
- Competitivos, cooperativos, campañas, party.
- Sin estrenar.
- Alta y baja fricción.
- Juegos sin rotar.
- Jugados recientemente.
- Recomendación “¿Qué juego saco hoy?”.
- Filtros laterales por tipo, jugadores, fricción y estreno.

## Próximas mejoras posibles

- Carátulas de juegos si agregamos una columna con URL de imagen.
- Favoritos si agregamos columna “Favorito”.
- Tiempo estimado a 2 jugadores.
- Botón para registrar partida.
- Versión privada con login o credenciales Google.
