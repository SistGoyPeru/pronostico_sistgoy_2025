# ⚽ Dashboard de Pronósticos Deportivos

Sistema avanzado de análisis y pronósticos para partidos de fútbol basado en estadísticas históricas.

## 🌟 Características

### 📊 Análisis de Partidos Jugados
- Comparación de pronósticos vs resultados reales
- Validación de precisión del sistema
- Métricas de acierto para 1X2, Over/Under y BTTS

### 📅 Pronósticos por Fechas
- **Resumen de Mejores Oportunidades**: Top 3 apuestas con mayor probabilidad
- **Pronóstico 1X2**: Victoria Local, Empate, Victoria Visitante con cuotas
- **Doble Oportunidad**: 1X, X2, 12 con probabilidades y cuotas
- **Mercados Combinados**: Resultado + Goles (ej: Victoria Local + Más de 2.5)
- **Estadísticas Detalladas**: Over/Under, BTTS, goles esperados

### 🌍 Cobertura Global
Más de 65 ligas de fútbol de todo el mundo:
- 🇪🇺 Europa (30 ligas)
- 🌎 América del Sur (11 ligas)
- 🌎 América del Norte y Central (5 ligas)
- 🌏 Asia (6 ligas)
- 🌍 África (3 ligas)

## 🚀 Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos

1. Clona el repositorio:
```bash
git clone https://github.com/TU_USUARIO/pronosticos.git
cd pronosticos
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run dashboard.py
```

## 📦 Dependencias

- `streamlit`: Framework para la interfaz web
- `polars`: Procesamiento eficiente de datos
- `requests`: Obtención de datos web
- `beautifulsoup4`: Web scraping
- `plotly`: Visualizaciones interactivas

## 🎯 Uso

1. **Selecciona una liga** en el sidebar
2. **Carga los datos** haciendo clic en "🔄 Cargar Datos"
3. **Explora las secciones**:
   - Análisis de partidos jugados para validar precisión
   - Pronósticos por fechas para partidos futuros
   - Estadísticas generales de la liga

## 📈 Metodología

El sistema calcula probabilidades basándose en:
- Rendimiento histórico de equipos como local y visitante
- Estadísticas de goles (promedio, over/under)
- Patrones de ambos equipos marcan (BTTS)
- Normalización de probabilidades 1X2

Las cuotas se calculan como: `Cuota = 100 / Probabilidad`

## 🔧 Estructura del Proyecto

```
pronosticos/
├── dashboard.py              # Aplicación principal Streamlit
├── extract_calendar.py       # Extracción y análisis de datos
├── LOGO.jpg                  # Logo de la aplicación
├── requirements.txt          # Dependencias Python
└── README.md                # Este archivo
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, por favor abre un issue en GitHub.

---

⚽ **Desarrollado con pasión por el fútbol y el análisis de datos**
