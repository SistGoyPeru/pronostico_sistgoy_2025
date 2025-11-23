import streamlit as st
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from extract_calendar import CalendarExtractor, StatisticsCalculator
from league_manager import LeagueManager

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Pronósticos Deportivos",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados - Diseño Completo Casa de Apuestas - Tema Morado
st.markdown("""
    <style>
    /* ========== FONDOS PRINCIPALES ========== */
    .main {
        background-color: #000000 !important;
    }
    
    .block-container {
        background-color: #000000 !important;
        padding-top: 2rem !important;
    }
    
    .stApp {
        background-color: #000000 !important;
    }
    
    /* ========== TARJETAS DE MÉTRICAS ESTILO CUOTAS ========== */
    .stMetric {
        background: linear-gradient(135deg, #1a0f1f 0%, #0a050f 100%);
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 3px 10px rgba(147, 51, 234, 0.3);
        border: 2px solid #9333ea;
        transition: all 0.3s ease;
    }
    .stMetric:hover {
        border-color: #a855f7;
        box-shadow: 0 5px 15px rgba(168, 85, 247, 0.5);
        transform: translateY(-2px);
    }
    .stMetric label {
        color: #8b949e !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        margin-bottom: 8px !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #c084fc !important;
        font-size: 2.4rem !important;
        font-weight: 900 !important;
        text-shadow: 0 2px 8px rgba(192, 132, 252, 0.6);
        font-family: 'Arial Black', sans-serif !important;
    }
    
    /* ========== TÍTULOS ESTILO BETTING ========== */
    h1 {
        color: #f0b90b !important;
        text-align: center;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
        text-shadow: 0 3px 15px rgba(240, 185, 11, 0.6);
        margin-bottom: 1.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 3px !important;
        border-bottom: 3px solid #9333ea;
        padding-bottom: 15px;
    }
    
    h2, h3 {
        color: #f0b90b !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
        text-shadow: 0 2px 8px rgba(240, 185, 11, 0.4);
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-left: 12px;
        border-left: 4px solid #a855f7;
    }
    
    /* ========== TEXTO GENERAL ========== */
    p, div, span, label {
        color: #ffffff !important;
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
    }
    
    .stMarkdown {
        color: #ffffff !important;
    }
    
    /* ========== SIDEBAR ESTILO BETTING ========== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0a14 0%, #000000 100%) !important;
        border-right: 3px solid #9333ea !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #a855f7 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* ========== BOTONES ESTILO APOSTAR ========== */
    .stButton > button {
        background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%) !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 16px 32px !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #9333ea 0%, #7e22ce 100%) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.7) !important;
        transform: translateY(-3px) !important;
    }
    
    /* ========== INPUTS Y SELECTORES ========== */
    .stSelectbox, .stTextInput {
        background-color: #000000 !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div {
        background-color: #0a050f !important;
        border: 2px solid #9333ea !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox label {
        color: #f0b90b !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.95rem !important;
    }
    
    /* Dropdown options */
    [data-baseweb="select"] > div {
        background-color: #0a050f !important;
        border: 2px solid #9333ea !important;
    }
    
    [role="option"] {
        background-color: #0a050f !important;
        color: #ffffff !important;
    }
    
    [role="option"]:hover {
        background-color: #1a0f2e !important;
        color: #a855f7 !important;
    }
    
    /* ========== EXPANDERS ESTILO PARTIDOS ========== */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #0f0a19 0%, #0a050f 100%) !important;
        border-radius: 8px !important;
        border: 2px solid #30363d !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #1a0f2e 0%, #0f0a19 100%) !important;
        border-color: #a855f7 !important;
        box-shadow: 0 3px 10px rgba(168, 85, 247, 0.4) !important;
    }
    
    /* ========== TABLAS ESTILO ODDS ========== */
    .stDataFrame {
        background-color: #0a0f0a !important;
        border-radius: 8px !important;
        border: 2px solid #30363d !important;
    }
    
    /* ========== ALERT BOXES ========== */
    .stAlert {
        background-color: #0f0a19 !important;
        border-left: 5px solid #a855f7 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    /* ========== HEADER Y TOOLBAR ========== */
    header[data-testid="stHeader"] {
        background-color: #000000 !important;
        border-bottom: 2px solid #9333ea !important;
    }
    
    /* Botón Share y otros botones del header */
    button[kind="header"] {
        background-color: #0a050f !important;
        border: 2px solid #9333ea !important;
        color: #a855f7 !important;
        border-radius: 6px !important;
    }
    
    button[kind="header"]:hover {
        background-color: #1a0f2e !important;
        border-color: #a855f7 !important;
        color: #c084fc !important;
    }
    
    /* Toolbar superior */
    .stToolbar {
        background-color: #000000 !important;
    }
    
    [data-testid="stToolbar"] {
        background-color: #000000 !important;
    }
    
    
    /* ========== SCROLLBAR MORADO ========== */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    ::-webkit-scrollbar-track {
        background: #000000;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #a855f7 0%, #9333ea 100%);
        border-radius: 6px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #9333ea 0%, #7e22ce 100%);
    }
    
    /* ========== DIVISORES ========== */
    hr {
        border: none !important;
        border-top: 2px solid #9333ea !important;
        margin: 2rem 0 !important;
    }
    
    /* ========== CAPTIONS Y TEXTOS PEQUEÑOS ========== */
    .caption, small {
        color: #8b949e !important;
        font-size: 0.85rem !important;
    }
    
    /* ========== GRÁFICOS PLOTLY ========== */
    .js-plotly-plot {
        border-radius: 8px !important;
        border: 2px solid #30363d !important;
    }
    
    /* ========== RESPONSIVE DESIGN - MÓVILES ========== */
    
    /* Tablets y pantallas medianas (768px - 1024px) */
    @media screen and (max-width: 1024px) {
        .block-container {
            padding: 1rem !important;
        }
        
        h1 {
            font-size: 2.2rem !important;
            letter-spacing: 2px !important;
        }
        
        h2, h3 {
            font-size: 1.4rem !important;
        }
        
    
        .stMetric {
            padding: 15px !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }
        
        .stButton > button {
            padding: 14px 24px !important;
            font-size: 1rem !important;
        }
    }
    
    /* Móviles (max 768px) */
    @media screen and (max-width: 768px) {
        .block-container {
            padding: 0.5rem !important;
            padding-top: 1rem !important;
        }
        
        /* Títulos más pequeños */
        h1 {
            font-size: 1.8rem !important;
            letter-spacing: 1px !important;
            padding-bottom: 10px;
            margin-bottom: 1rem !important;
        }
        
        h2, h3 {
            font-size: 1.2rem !important;
            letter-spacing: 1px !important;
            margin-top: 1.5rem !important;
            padding-left: 8px;
        }
        
        /* Texto más legible en móvil */
        p, div, span, label {
            font-size: 1rem !important;
        }
        
        /* Métricas optimizadas para móvil */
        .stMetric {
            padding: 12px !important;
            margin-bottom: 10px !important;
        }
        
        .stMetric label {
            font-size: 0.75rem !important;
            letter-spacing: 0.8px !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }
        
        /* Botones táctiles más grandes */
        .stButton > button {
            padding: 16px 20px !important;
            font-size: 0.95rem !important;
            width: 100% !important;
            letter-spacing: 1px !important;
        }
        
        /* Selectores más fáciles de tocar */
        .stSelectbox > div > div {
            padding: 12px !important;
            font-size: 1rem !important;
        }
        
        .stSelectbox label {
            font-size: 0.9rem !important;
        }
        
        /* Expanders optimizados */
        .streamlit-expanderHeader {
            padding: 10px 12px !important;
            font-size: 0.95rem !important;
        }
        
        /* Sidebar responsive */
        [data-testid="stSidebar"] {
            min-width: 250px !important;
        }
        
        /* Scrollbar más delgado en móvil */
        ::-webkit-scrollbar {
            width: 8px !important;
            height: 8px !important;
        }
        
        /* Divisores más compactos */
        hr {
            margin: 1.5rem 0 !important;
        }
    }
    
    /* Móviles pequeños (max 480px) */
    @media screen and (max-width: 480px) {
        h1 {
            font-size: 1.5rem !important;
            letter-spacing: 0.5px !important;
        }
        
        h2, h3 {
            font-size: 1.1rem !important;
        }
        
        .stMetric {
            padding: 10px !important;
        }
        
        .stMetric label {
            font-size: 0.7rem !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
        
        .stButton > button {
            padding: 14px 16px !important;
            font-size: 0.9rem !important;
        }
        
        [data-testid="stSidebar"] {
            min-width: 200px !important;
        }
    }
    
    /* Orientación horizontal en móviles */
    @media screen and (max-width: 768px) and (orientation: landscape) {
        h1 {
            font-size: 1.6rem !important;
            margin-bottom: 0.8rem !important;
        }
        
        .stMetric {
            padding: 8px !important;
        }
        
        .stMetric [data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
        }
    }
    
    /* Touch-friendly: aumentar áreas táctiles */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button,
        .streamlit-expanderHeader,
        button[kind="header"] {
            min-height: 44px !important;
            min-width: 44px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Función para calcular precisión de pronósticos
def calculate_prediction_accuracy(df, stats):
    """
    Calcula la precisión de los pronósticos 1X2 para partidos jugados
    """
    played_matches = df.filter(pl.col("GA").is_not_null())
    
    if len(played_matches) == 0:
        return 0.0, 0, 0
    
    correct_predictions = 0
    total_matches = len(played_matches)
    
    for i in range(len(played_matches)):
        match = played_matches[i]
        home_team = match["Local"][0]
        away_team = match["Visita"][0]
        home_goals = match["GA"][0]
        away_goals = match["GC"][0]
        
        # Determinar resultado real
        if home_goals > away_goals:
            real_result = "home"
        elif home_goals < away_goals:
            real_result = "away"
        else:
            real_result = "draw"
        
        # Calcular pronóstico
        h_win_pct = stats.team_home_percentage_wins(home_team)
        h_draw_pct = stats.team_home_percentage_draws(home_team)
        a_win_pct = stats.team_away_percentage_wins(away_team)
        a_draw_pct = stats.team_away_percentage_draws(away_team)
        
        pred_home_win = h_win_pct
        pred_draw = (h_draw_pct + a_draw_pct) / 2
        pred_away_win = a_win_pct
        
        # Normalizar
        total_1x2 = pred_home_win + pred_draw + pred_away_win
        if total_1x2 > 0:
            pred_home_win = (pred_home_win / total_1x2) * 100
            pred_draw = (pred_draw / total_1x2) * 100
            pred_away_win = (pred_away_win / total_1x2) * 100
        
        # Determinar pronóstico más probable
        max_prob = max(pred_home_win, pred_draw, pred_away_win)
        if max_prob == pred_home_win:
            predicted_result = "home"
        elif max_prob == pred_draw:
            predicted_result = "draw"
        else:
            predicted_result = "away"
        
        # Verificar si el pronóstico fue correcto
        if predicted_result == real_result:
            correct_predictions += 1
    
    accuracy = (correct_predictions / total_matches) * 100 if total_matches > 0 else 0
    return accuracy, correct_predictions, total_matches

# Título principal
st.markdown("<h1>⚽ Dashboard de Pronósticos Deportivos</h1>", unsafe_allow_html=True)

# Inicializar historial de precisión en session_state
if 'league_accuracy_history' not in st.session_state:
    st.session_state['league_accuracy_history'] = {}

# Mostrar resumen de ligas con mejores aciertos
if st.session_state.get('league_accuracy_history'):
    st.markdown("### 🏆 Resumen: Ligas con Mejores Pronósticos")
    
    # Ordenar ligas por precisión
    sorted_leagues = sorted(
        st.session_state['league_accuracy_history'].items(),
        key=lambda x: x[1]['accuracy'],
        reverse=True
    )
    
    # Mostrar top 5 en columnas
    if len(sorted_leagues) > 0:
        num_cols = min(5, len(sorted_leagues))
        cols = st.columns(num_cols)
        
        for idx, (league_name, data) in enumerate(sorted_leagues[:5]):
            with cols[idx]:
                accuracy = data['accuracy']
                correct = data['correct']
                total = data['total']
                
                # Color según precisión
                if accuracy >= 60:
                    color = "#4fc3f7"  # Azul suave
                    icon = "🥇"
                elif accuracy >= 50:
                    color = "#66bb6a"  # Verde suave
                    icon = "🥈"
                elif accuracy >= 40:
                    color = "#ffa726"  # Naranja suave
                    icon = "🥉"
                else:
                    color = "#ef5350"  # Rojo suave
                    icon = "📊"
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #2a3f5f 0%, #1e2d3d 100%); 
                            padding: 18px; 
                            border-radius: 12px; 
                            border-left: 5px solid {color};
                            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);'>
                    <div style='font-size: 1.8rem; margin-bottom: 8px;'>{icon}</div>
                    <div style='font-size: 1.05rem; color: #e8f4f8; margin-bottom: 8px; font-weight: bold;'>{league_name[:20]}...</div>
                    <div style='font-size: 2.2rem; color: {color}; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>{accuracy:.1f}%</div>
                    <div style='font-size: 1rem; color: #b0bec5;'>{correct}/{total} aciertos</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")

# Sidebar - Logo y Configuración
try:
    st.sidebar.image("LOGO.jpg", use_container_width=True)
except:
    pass  # Si no se encuentra el logo, continuar sin él

st.sidebar.header("🏆 Configuración")

# Inicializar gestor de ligas
manager = LeagueManager()

# Ligas por defecto (para asegurar que estén en el sistema)
default_leagues = {
    # Europa - Top 5 Leagues
    "🇩🇪 Alemania - Bundesliga": "https://www.livefutbol.com/competition/co12/alemania-bundesliga/all-matches/",
    "🇩🇪 Alemania - 2. Bundesliga": "https://www.livefutbol.com/competition/co3/alemania-2-bundesliga/all-matches/",
    "🇪🇸 España - La Liga": "https://www.livefutbol.com/competition/co97/espana-primera-division/all-matches/",
    "🇪🇸 España - Segunda División": "https://www.livefutbol.com/competition/co110/espana-segunda-division/all-matches/",
    "🇪🇸 España - Liga Femenina": "https://www.livefutbol.com/competition/co2737/espana-mujeres-primera-division/all-matches/",
    "ES España - primera-federacion-grupo-1": "https://www.livefutbol.com/competition/co6373/espana-primera-federacion-grupo-1/all-matches/",
    "ES España - primera-federacion-grupo-2": "https://www.livefutbol.com/competition/co6515/espana-primera-federacion-grupo-2/all-matches/",
    "🇬🇧 Inglaterra - Premier League": "https://www.livefutbol.com/competition/co91/inglaterra-premier-league/all-matches/",
    "🇬🇧 Inglaterra - Championship": "https://www.livefutbol.com/competition/co20/inglaterra-championship/all-matches/",
    "🇮🇹 Italia - Serie A": "https://www.livefutbol.com/competition/co111/italia-serie-a/all-matches/",
    "🇮🇹 Italia - Serie B": "https://www.livefutbol.com/competition/co113/italia-serie-b/all-matches/",
    "🇫🇷 Francia - Ligue 1": "https://www.livefutbol.com/competition/co71/francia-ligue-1/all-matches/",
    "🇫🇷 Francia - Ligue 2": "https://www.livefutbol.com/competition/co72/francia-ligue-2/all-matches/",
    
    # Europa - Otras Ligas
    "🇵🇹 Portugal - Primeira Liga": "https://www.livefutbol.com/competition/co123/portugal-primeira-liga/all-matches/",
    "🇳🇱 Países Bajos - Eredivisie": "https://www.livefutbol.com/competition/co37/paises-bajos-eredivisie/all-matches/",
    "🇧🇪 Bélgica - Pro League": "https://www.livefutbol.com/competition/co49/belgica-pro-league/all-matches/",
   
    # América del Sur
    "🇵🇪 Perú - Primera División": "https://www.livefutbol.com/competition/co100/peru-primera-division/all-matches/",
}

# Migrar ligas por defecto si no existen
for name, url in default_leagues.items():
    
    manager.add_league(name, url)

# Obtener todas las ligas actualizadas
ligas = manager.get_leagues_dict()

# Sección de Gestión de Ligas
with st.sidebar.expander("⚙️ Gestionar Ligas", expanded=False):
    tab1, tab2 = st.tabs(["Agregar", "Eliminar"])
    
    with tab1:
        st.markdown("##### Agregar Nueva Liga")
        new_league_name = st.text_input("Nombre de la Liga", placeholder="Ej: 🇧🇷 Brasil - Serie A")
        new_league_url = st.text_input("URL (livefutbol.com)", placeholder="https://www.livefutbol.com/...")
        
        if st.button("💾 Guardar Liga", use_container_width=True):
            if new_league_name and new_league_url:
                if "livefutbol.com" in new_league_url:
                    if manager.add_league(new_league_name, new_league_url):
                        st.success(f"Liga '{new_league_name}' agregada!")
                        st.rerun()
                    else:
                        st.error("Error: La liga ya existe o hubo un problema.")
                else:
                    st.error("La URL debe ser de livefutbol.com")
            else:
                st.warning("Completa todos los campos")
                
    with tab2:
        st.markdown("##### Eliminar Liga")
        league_to_delete = st.selectbox("Seleccionar para eliminar", options=list(ligas.keys()))
        
        if st.button("🗑️ Eliminar Seleccionada", type="primary", use_container_width=True):
            # Encontrar ID de la liga seleccionada
            leagues_list = manager.get_all_leagues()
            league_id = next((l['id'] for l in leagues_list if l['name'] == league_to_delete), None)
            
            if league_id:
                if manager.delete_league(league_id):
                    st.success(f"Liga '{league_to_delete}' eliminada!")
                    st.rerun()
                else:
                    st.error("Error al eliminar la liga")

# Selector principal de ligas
liga_seleccionada = st.sidebar.selectbox(
    "Selecciona una liga:",
    options=list(ligas.keys()),
    index=0 if list(ligas.keys()) else None
)

# Botón para cargar datos
if st.sidebar.button("🔄 Cargar Datos", type="primary"):
    with st.spinner(f"Cargando datos de {liga_seleccionada}..."):
        url = ligas[liga_seleccionada]
        extractor = CalendarExtractor(url)
        extractor.fetch_and_parse()
        df = extractor.get_dataframe()
        st.session_state['df'] = df
        st.session_state['liga'] = liga_seleccionada
        
        # Calcular precisión de pronósticos para esta liga
        stats_temp = StatisticsCalculator(df)
        accuracy, correct, total = calculate_prediction_accuracy(df, stats_temp)
        
        # Guardar en historial de precisión
        st.session_state['league_accuracy_history'][liga_seleccionada] = {
            'accuracy': accuracy,
            'correct': correct,
            'total': total
        }
        
        st.success(f"✅ Datos cargados exitosamente! Precisión: {accuracy:.1f}% ({correct}/{total})")

# Verificar si hay datos cargados
if 'df' not in st.session_state:
    st.info("👈 Selecciona una liga y presiona 'Cargar Datos' para comenzar")
    st.stop()

df = st.session_state['df']
stats = StatisticsCalculator(df)

# Información de la liga
st.markdown(f"### 📊 Análisis de: {st.session_state['liga']}")

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    played = stats.count_played_matches()
    st.metric("🎮 Partidos Jugados", played)

with col2:
    upcoming = stats.count_upcoming_matches()
    st.metric("📅 Partidos Pendientes", upcoming)

with col3:
    pct_played = stats.percentage_played()
    st.metric("📈 Temporada Completada", f"{pct_played:.1f}%")

with col4:
    avg_goals = stats.average_goals_per_match()
    st.metric("⚽ Media de Goles", f"{avg_goals:.2f}")

st.markdown("---")

# Dos columnas para gráficos
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🎯 Distribución de Goles")
    
    # Gráfico de barras - Over/Under
    over_under_data = {
        'Categoría': ['Más de 0.5', 'Más de 1.5', 'Más de 2.5', 'Menos de 3.5', 'Menos de 4.5'],
        'Porcentaje': [
            stats.percentage_over_goals(0),
            stats.percentage_over_goals(1),
            stats.percentage_over_goals(2),
            stats.percentage_under_goals(4),
            stats.percentage_under_goals(5)
        ]
    }
    
    fig_over_under = go.Figure(data=[
        go.Bar(
            x=over_under_data['Categoría'],
            y=over_under_data['Porcentaje'],
            marker=dict(
                color=over_under_data['Porcentaje'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Porcentaje")
            ),
            text=[f"{val:.1f}%" for val in over_under_data['Porcentaje']],
            textposition='outside'
        )
    ])
    
    fig_over_under.update_layout(
        title="Estadísticas Over/Under",
        xaxis_title="Categoría",
        yaxis_title="Porcentaje (%)",
        template="plotly_dark",
        height=400,
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig_over_under, use_container_width=True)

with col_right:
    st.markdown("### 📊 Estadísticas Especiales")
    
    # Gráfico de dona - Estadísticas especiales
    special_stats = {
        'Ambos Marcan': stats.percentage_both_teams_score(),
        'No Marcan': 100 - stats.percentage_both_teams_score(),
    }
    
    fig_btts = go.Figure(data=[
        go.Pie(
            labels=list(special_stats.keys()),
            values=list(special_stats.values()),
            hole=0.4,
            marker=dict(colors=['#00d4ff', '#ff4b4b']),
            textinfo='label+percent',
            textfont=dict(size=14)
        )
    ])
    
    fig_btts.update_layout(
        title="Ambos Equipos Marcan (BTTS)",
        template="plotly_dark",
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_btts, use_container_width=True)

st.markdown("---")

# Sección de métricas detalladas
st.markdown("### 📈 Métricas Detalladas")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pct_0_0 = stats.percentage_exact_goals(0)
    st.metric("🚫 Partidos 0-0", f"{pct_0_0:.1f}%")

with col2:
    pct_over_0 = stats.percentage_over_goals(0)
    st.metric("✅ Más de 0.5", f"{pct_over_0:.1f}%")

with col3:
    pct_over_1 = stats.percentage_over_goals(1)
    st.metric("⚡ Más de 1.5", f"{pct_over_1:.1f}%")

with col4:
    pct_over_2 = stats.percentage_over_goals(2)
    st.metric("🔥 Más de 2.5", f"{pct_over_2:.1f}%")

with col5:
    pct_btts = stats.percentage_both_teams_score()
    st.metric("🎯 BTTS", f"{pct_btts:.1f}%")

st.markdown("---")

# Sección de análisis de partidos jugados por fecha
st.markdown("### 📊 Análisis de Partidos Jugados (Pronóstico vs Resultado Real)")

# Obtener partidos jugados
played_matches = df.filter(pl.col("GA").is_not_null())

if len(played_matches) > 0:
    # Obtener fechas de partidos jugados
    played_dates = played_matches["Fecha"].unique().to_list()
    played_dates = [d for d in played_dates if d is not None]
    played_dates = sorted(played_dates, reverse=True)  # Más recientes primero
    
    if len(played_dates) > 0:
        # Selector de fecha para partidos jugados
        selected_played_date = st.selectbox(
            "Selecciona una fecha de partidos jugados:",
            options=played_dates,
            index=0,
            key="played_date_selector"
        )
        
        # Filtrar partidos de la fecha seleccionada
        played_date_matches = played_matches.filter(pl.col("Fecha") == selected_played_date)
        
        st.markdown(f"#### 📅 Partidos Jugados el {selected_played_date}")
        st.markdown(f"**Total de partidos:** {len(played_date_matches)}")
        
        # Contadores de aciertos
        total_matches = len(played_date_matches)
        correct_predictions = 0
        
        # Mostrar cada partido con comparación
        for i in range(len(played_date_matches)):
            match = played_date_matches[i]
            home_team = match["Local"][0]
            away_team = match["Visita"][0]
            home_goals = match["GA"][0]
            away_goals = match["GC"][0]
            total_goals = home_goals + away_goals
            
            # Determinar resultado real
            if home_goals > away_goals:
                real_result = f"Victoria {home_team}"
                result_icon = "🏠"
            elif home_goals < away_goals:
                real_result = f"Victoria {away_team}"
                result_icon = "✈️"
            else:
                real_result = "Empate"
                result_icon = "🤝"
            
            # Calcular pronóstico
            h_win_pct = stats.team_home_percentage_wins(home_team)
            h_draw_pct = stats.team_home_percentage_draws(home_team)
            a_win_pct = stats.team_away_percentage_wins(away_team)
            a_draw_pct = stats.team_away_percentage_draws(away_team)
            
            pred_home_win = h_win_pct
            pred_draw = (h_draw_pct + a_draw_pct) / 2
            pred_away_win = a_win_pct
            
            # Normalizar
            total_1x2 = pred_home_win + pred_draw + pred_away_win
            if total_1x2 > 0:
                pred_home_win = (pred_home_win / total_1x2) * 100
                pred_draw = (pred_draw / total_1x2) * 100
                pred_away_win = (pred_away_win / total_1x2) * 100
            
            # Determinar pronóstico más probable
            max_prob = max(pred_home_win, pred_draw, pred_away_win)
            if max_prob == pred_home_win:
                predicted_result = f"Victoria {home_team}"
                pred_icon = "🏠"
            elif max_prob == pred_draw:
                predicted_result = "Empate"
                pred_icon = "🤝"
            else:
                predicted_result = f"Victoria {away_team}"
                pred_icon = "✈️"
            
            # Verificar si el pronóstico fue correcto
            is_correct = predicted_result == real_result
            if is_correct:
                correct_predictions += 1
                accuracy_icon = "✅"
                accuracy_color = "success"
            else:
                accuracy_icon = "❌"
                accuracy_color = "error"
            
            # Calcular pronósticos adicionales
            h_avg = stats.team_home_average_goals(home_team)
            a_avg = stats.team_away_average_goals(away_team)
            h_over_25 = stats.team_home_percentage_over_goals(home_team, 2)
            a_over_25 = stats.team_away_percentage_over_goals(away_team, 2)
            h_btts = stats.team_home_percentage_btts(home_team)
            a_btts = stats.team_away_percentage_btts(away_team)
            
            pred_avg_goals = (h_avg + a_avg) / 2
            pred_over_25 = (h_over_25 + a_over_25) / 2
            pred_btts = (h_btts + a_btts) / 2
            
            # Verificar aciertos adicionales
            over25_correct = (total_goals > 2 and pred_over_25 >= 50) or (total_goals <= 2 and pred_over_25 < 50)
            btts_real = home_goals > 0 and away_goals > 0
            btts_correct = (btts_real and pred_btts >= 50) or (not btts_real and pred_btts < 50)
            
            with st.expander(f"{accuracy_icon} {home_team} {home_goals}-{away_goals} {away_team}"):
                # Resumen de aciertos
                st.markdown("**📊 Resumen de Aciertos:**")
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                with col_sum1:
                    if is_correct:
                        st.success("✅ Resultado 1X2")
                    else:
                        st.error("❌ Resultado 1X2")
                with col_sum2:
                    if over25_correct:
                        st.success("✅ Over/Under 2.5")
                    else:
                        st.error("❌ Over/Under 2.5")
                with col_sum3:
                    if btts_correct:
                        st.success("✅ BTTS")
                    else:
                        st.error("❌ BTTS")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{result_icon} Resultado Real:**")
                    st.info(f"""
                    **Resultado 1X2:**
                    - {real_result}
                    - Marcador: **{home_goals}-{away_goals}**
                    
                    **Estadísticas de Goles:**
                    - Total goles: **{total_goals}**
                    - Más de 1.5: {'✅ SÍ' if total_goals > 1 else '❌ NO'}
                    - Más de 2.5: {'✅ SÍ' if total_goals > 2 else '❌ NO'}
                    - Más de 3.5: {'✅ SÍ' if total_goals > 3 else '❌ NO'}
                    - Menos de 3.5: {'✅ SÍ' if total_goals < 4 else '❌ NO'}
                    
                    **Otros Mercados:**
                    - BTTS: {'✅ SÍ' if btts_real else '❌ NO'}
                    - Partido con goles: {'✅ SÍ' if total_goals > 0 else '❌ NO'}
                    """)
                
                with col2:
                    st.markdown(f"**{pred_icon} Pronóstico del Sistema:**")
                    
                    # Pronóstico 1X2
                    result_status = "✅ ACERTADO" if is_correct else "❌ FALLADO"
                    if is_correct:
                        st.success(f"""
                        **Resultado 1X2:** {result_status}
                        - Predicción: **{predicted_result}**
                        - Prob. Victoria Local: {pred_home_win:.1f}%
                        - Prob. Empate: {pred_draw:.1f}%
                        - Prob. Victoria Visitante: {pred_away_win:.1f}%
                        """)
                    else:
                        st.error(f"""
                        **Resultado 1X2:** {result_status}
                        - Predicción: **{predicted_result}**
                        - Prob. Victoria Local: {pred_home_win:.1f}%
                        - Prob. Empate: {pred_draw:.1f}%
                        - Prob. Victoria Visitante: {pred_away_win:.1f}%
                        """)
                    
                    # Pronóstico de goles
                    over25_status = "✅ ACERTADO" if over25_correct else "❌ FALLADO"
                    over25_prediction = "Más de 2.5" if pred_over_25 >= 50 else "Menos de 2.5"
                    
                    if over25_correct:
                        st.success(f"""
                        **Over/Under 2.5:** {over25_status}
                        - Predicción: **{over25_prediction}**
                        - Prob. Más de 2.5: {pred_over_25:.1f}%
                        - Goles esperados: {pred_avg_goals:.2f}
                        """)
                    else:
                        st.error(f"""
                        **Over/Under 2.5:** {over25_status}
                        - Predicción: **{over25_prediction}**
                        - Prob. Más de 2.5: {pred_over_25:.1f}%
                        - Goles esperados: {pred_avg_goals:.2f}
                        """)
                    
                    # Pronóstico BTTS
                    btts_status = "✅ ACERTADO" if btts_correct else "❌ FALLADO"
                    btts_prediction = "Ambos marcan" if pred_btts >= 50 else "No ambos marcan"
                    
                    if btts_correct:
                        st.success(f"""
                        **BTTS:** {btts_status}
                        - Predicción: **{btts_prediction}**
                        - Probabilidad BTTS: {pred_btts:.1f}%
                        """)
                    else:
                        st.error(f"""
                        **BTTS:** {btts_status}
                        - Predicción: **{btts_prediction}**
                        - Probabilidad BTTS: {pred_btts:.1f}%
                        """)
        
        # Mostrar estadísticas de precisión
        st.markdown("---")
        accuracy_pct = (correct_predictions / total_matches) * 100 if total_matches > 0 else 0
        
        col_acc1, col_acc2, col_acc3 = st.columns(3)
        with col_acc1:
            st.metric("✅ Pronósticos Acertados", f"{correct_predictions}/{total_matches}")
        with col_acc2:
            st.metric("📊 Precisión", f"{accuracy_pct:.1f}%")
        with col_acc3:
            if accuracy_pct >= 60:
                st.success("🎯 Excelente precisión")
            elif accuracy_pct >= 40:
                st.warning("⚠️ Precisión moderada")
            else:
                st.error("❌ Baja precisión")

st.markdown("---")

# Sección de pronósticos por fechas
st.markdown("### 📅 Pronósticos por Fechas")

# Obtener partidos próximos
upcoming_matches = stats.get_upcoming_matches()

if len(upcoming_matches) > 0:
    # Agrupar por fecha
    dates = upcoming_matches["Fecha"].unique().to_list()
    dates = [d for d in dates if d is not None]
    dates = sorted(dates)
    
    if len(dates) > 0:
        # Selector de fecha
        selected_date = st.selectbox(
            "Selecciona una fecha:",
            options=dates,
            index=0,
            key="date_selector"
        )
        
        # Filtrar partidos de la fecha seleccionada
        date_matches = upcoming_matches.filter(pl.col("Fecha") == selected_date)
        
        st.markdown(f"#### 📆 Partidos del {selected_date}")
        st.markdown(f"**Total de partidos:** {len(date_matches)}")
        
        # MEJOR APUESTA DE LA FECHA
        st.markdown("### 💎 Mejor Apuesta de esta Fecha")
        
        best_match_date = None
        best_probability_date = 0
        best_prediction_date = None
        best_market_date = None
        
        # Lista para guardar el mejor pronóstico de cada partido
        match_summaries = []
        
        # Analizar todos los partidos de esta fecha para encontrar el mejor
        for i in range(len(date_matches)):
            match = date_matches[i]
            home_team = match["Local"][0]
            away_team = match["Visita"][0]
            match_time = match["Hora"][0]
            
            # Calcular probabilidades 1X2
            h_win_pct = stats.team_home_percentage_wins(home_team)
            h_draw_pct = stats.team_home_percentage_draws(home_team)
            a_win_pct = stats.team_away_percentage_wins(away_team)
            a_draw_pct = stats.team_away_percentage_draws(away_team)
            
            pred_home_win = h_win_pct
            pred_draw = (h_draw_pct + a_draw_pct) / 2
            pred_away_win = a_win_pct
            
            # Normalizar
            total_1x2 = pred_home_win + pred_draw + pred_away_win
            if total_1x2 > 0:
                pred_home_win = (pred_home_win / total_1x2) * 100
                pred_draw = (pred_draw / total_1x2) * 100
                pred_away_win = (pred_away_win / total_1x2) * 100
            
            # Calcular estadísticas de goles
            h_over_25 = stats.team_home_percentage_over_goals(home_team, 2)
            a_over_25 = stats.team_away_percentage_over_goals(away_team, 2)
            pred_over_25 = (h_over_25 + a_over_25) / 2
            
            h_btts = stats.team_home_percentage_btts(home_team)
            a_btts = stats.team_away_percentage_btts(away_team)
            pred_btts = (h_btts + a_btts) / 2
            
            # Encontrar la probabilidad más alta entre todos los mercados
            all_probabilities = [
                (pred_home_win, f"Victoria {home_team}", "1X2", home_team, away_team, match),
                (pred_draw, "Empate", "1X2", home_team, away_team, match),
                (pred_away_win, f"Victoria {away_team}", "1X2", home_team, away_team, match),
                (pred_over_25, "Más de 2.5 goles", "Goles", home_team, away_team, match),
                (pred_btts, "Ambos Marcan (BTTS)", "BTTS", home_team, away_team, match),
            ]
            
            # Encontrar la mejor opción para ESTE partido
            best_prob_match = 0
            best_pred_match = ""
            best_type_match = ""
            
            for prob, market_name, market_type, h_team, a_team, m in all_probabilities:
                # Actualizar mejor del día
                if prob > best_probability_date:
                    best_probability_date = prob
                    best_prediction_date = market_name
                    best_market_date = market_type
                    best_match_date = {
                        'home': h_team,
                        'away': a_team,
                        'date': m["Fecha"][0],
                        'time': m["Hora"][0],
                        'round': m["Jornada"][0],
                        'prob_home': pred_home_win,
                        'prob_draw': pred_draw,
                        'prob_away': pred_away_win,
                        'prob_over25': pred_over_25,
                        'prob_btts': pred_btts
                    }
                
                # Actualizar mejor de ESTE partido
                if prob > best_prob_match:
                    best_prob_match = prob
                    best_pred_match = market_name
                    best_type_match = market_type
            
            # Calcular cuota implícita
            implied_odd = 100 / best_prob_match if best_prob_match > 0 else 0
            
            # Guardar resumen del partido
            match_summaries.append({
                "Hora": match_time,
                "Partido": f"{home_team} vs {away_team}",
                "Mejor Pronóstico": best_pred_match,
                "Probabilidad": f"{best_prob_match:.1f}%",
                "Cuota": f"{implied_odd:.2f}",
                "Tipo": best_type_match,
                "prob_val": best_prob_match  # Para colorear
            })
        
        # Mostrar la mejor apuesta de la fecha
        if best_match_date:
            # Calcular cuota
            best_odd_date = 100 / best_probability_date if best_probability_date > 0 else 0
            
            # Color según probabilidad - Paleta suave y profesional
            if best_probability_date >= 70:
                bg_color = "#1e3a2e"  # Verde oscuro suave
                border_color = "#66bb6a"
                confidence = "MUY ALTA"
                confidence_icon = "🟢"
            elif best_probability_date >= 60:
                bg_color = "#1e2d3d"
                border_color = "#4fc3f7"
                confidence = "ALTA"
                confidence_icon = "🔵"
            elif best_probability_date >= 55:
                bg_color = "#3e2723"
                border_color = "#ffb74d"
                confidence = "MEDIA"
                confidence_icon = "🟡"
            else:
                bg_color = "#2a3f5f"
                border_color = "#ffa726"
                confidence = "BAJA"
                confidence_icon = "🟠"
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {bg_color} 0%, #1a1d29 100%); 
                        padding: 20px; 
                        border-radius: 12px; 
                        border-left: 5px solid {border_color};
                        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
                        margin-bottom: 20px;'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                    <div style='font-size: 1.2rem; color: #ffffff; font-weight: bold;'>
                        ⚽ {best_match_date['home']} vs {best_match_date['away']}
                    </div>
                    <div style='background-color: {border_color}; color: #000; padding: 6px 16px; border-radius: 16px; font-weight: bold; font-size: 1rem;'>
                        {confidence_icon} {confidence}
                    </div>
                </div>
                <div style='color: #cccccc; font-size: 1rem; margin-bottom: 12px;'>
                    ⏰ {best_match_date['time']} | 🏆 {best_match_date['round']}
                </div>
                <div style='background-color: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;'>
                    <div style='font-size: 1.3rem; color: {border_color}; font-weight: bold; margin-bottom: 8px;'>
                        💰 {best_prediction_date}
                    </div>
                    <div style='display: flex; gap: 25px; margin-top: 12px;'>
                        <div>
                            <div style='color: #cccccc; font-size: 0.95rem;'>Probabilidad</div>
                            <div style='font-size: 2rem; color: {border_color}; font-weight: bold;'>{best_probability_date:.1f}%</div>
                        </div>
                        <div>
                            <div style='color: #cccccc; font-size: 0.95rem;'>Cuota</div>
                            <div style='font-size: 2rem; color: #ffd700; font-weight: bold;'>{best_odd_date:.2f}</div>
                        </div>
                        <div>
                            <div style='color: #cccccc; font-size: 0.95rem;'>Mercado</div>
                            <div style='font-size: 1.5rem; color: #ffffff; font-weight: bold;'>{best_market_date}</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar tabla resumen de todos los partidos
        if match_summaries:
            st.markdown("### 📊 Resumen de Pronósticos de la Fecha")
            
            # Crear DataFrame
            import pandas as pd
            df_summary = pd.DataFrame(match_summaries)
            
            # Ordenar por probabilidad (de mayor a menor)
            df_summary = df_summary.sort_values(by='prob_val', ascending=False)
            
            # Función para colorear probabilidad
            def color_prob(val):
                if val >= 70:
                    color = '#66bb6a' # Verde
                    weight = 'bold'
                elif val >= 55:
                    color = '#ffa726' # Naranja
                    weight = 'bold'
                else:
                    color = '#ef5350' # Rojo
                    weight = 'normal'
                return f'color: {color}; font-weight: {weight}'
            
            # Estilizar tabla
            st.dataframe(
                df_summary.style
                .map(color_prob, subset=['prob_val'])
                .format({'prob_val': '{:.1f}%'})
                .set_properties(**{
                    'background-color': '#0a050f',
                    'color': '#ffffff',
                    'border-color': '#9333ea'
                })
                .set_table_styles([
                    {'selector': 'th', 'props': [
                        ('background-color', '#1a0f2e'),
                        ('color', '#a855f7'),
                        ('font-weight', 'bold'),
                        ('border-bottom', '2px solid #9333ea')
                    ]},
                    {'selector': 'td', 'props': [
                        ('padding', '10px'),
                        ('border-bottom', '1px solid #30363d')
                    ]}
                ]),
                use_container_width=True,
                column_config={
                    "Hora": st.column_config.TextColumn("⏰ Hora", width="small"),
                    "Partido": st.column_config.TextColumn("⚽ Partido", width="large"),
                    "Mejor Pronóstico": st.column_config.TextColumn("💎 Mejor Opción", width="medium"),
                    "Probabilidad": st.column_config.TextColumn("📊 Prob.", width="small"),
                    "Cuota": st.column_config.TextColumn("💰 Cuota", width="small"),
                    "Tipo": st.column_config.TextColumn("🏷️ Mercado", width="small"),
                    "prob_val": None  # Ocultar columna numérica usada para color
                },
                hide_index=True
            )
            
            # --- BOTÓN DE WHATSAPP ---
            st.markdown("### 📲 Compartir Resultados")
            
            # Generar mensaje para WhatsApp
            wa_text = f"*📊 PRONÓSTICOS SISTGOY - {selected_date}* ⚽\n\n"
            wa_text += "*💎 MEJORES OPORTUNIDADES:*\n\n"
            
            # Iterar sobre el dataframe ordenado para el mensaje
            for index, row in df_summary.iterrows():
                # Solo incluir las de probabilidad media/alta para no saturar
                if row['prob_val'] >= 55:
                    icon = "🟢" if row['prob_val'] >= 70 else "🟡"
                    wa_text += f"{icon} *{row['Partido']}*\n"
                    wa_text += f"   └ {row['Mejor Pronóstico']} ({row['Tipo']})\n"
                    wa_text += f"   └ Prob: {row['Probabilidad']} | Cuota: {row['Cuota']}\n\n"
            
            wa_text += "🚀 *Generado por SistGoy Pronósticos*"
            
            # Codificar mensaje para URL
            import urllib.parse
            wa_encoded = urllib.parse.quote(wa_text)
            wa_link = f"https://wa.me/?text={wa_encoded}"
            
            # Botón de enlace
            st.link_button(
                label="📤 Enviar Resumen por WhatsApp",
                url=wa_link,
                type="primary",
                help="Clic para abrir WhatsApp con el resumen listo para enviar"
            )
            # -------------------------
        
        st.markdown("---")
        st.markdown("### 📋 Todos los Partidos de la Fecha")
        
        
        # Mostrar cada partido con pronósticos
        for i in range(len(date_matches)):
            match = date_matches[i]
            home_team = match["Local"][0]
            away_team = match["Visita"][0]
            match_time = match["Hora"][0]
            match_round = match["Jornada"][0]
            
            with st.expander(f"⚽ {home_team} vs {away_team} - {match_time} ({match_round})"):
                # Estadísticas de los equipos
                col_home, col_away = st.columns(2)
                
                with col_home:
                    st.markdown(f"**🏠 {home_team} (Local)**")
                    h_matches = stats.team_home_count_matches(home_team)
                    h_avg = stats.team_home_average_goals(home_team)
                    h_over_15 = stats.team_home_percentage_over_goals(home_team, 1)
                    h_over_25 = stats.team_home_percentage_over_goals(home_team, 2)
                    h_over_35 = stats.team_home_percentage_over_goals(home_team, 3)
                    h_under_35 = 100 - h_over_35
                    h_btts = stats.team_home_percentage_btts(home_team)
                    
                    st.write(f"- Partidos local: {h_matches}")
                    st.write(f"- Media goles: {h_avg:.2f}")
                    st.write(f"- Más de 2.5: {h_over_25:.1f}%")
                    st.write(f"- BTTS: {h_btts:.1f}%")
                
                with col_away:
                    st.markdown(f"**✈️ {away_team} (Visita)**")
                    a_matches = stats.team_away_count_matches(away_team)
                    a_avg = stats.team_away_average_goals(away_team)
                    a_over_15 = stats.team_away_percentage_over_goals(away_team, 1)
                    a_over_25 = stats.team_away_percentage_over_goals(away_team, 2)
                    a_over_35 = stats.team_away_percentage_over_goals(away_team, 3)
                    a_under_35 = 100 - a_over_35
                    a_btts = stats.team_away_percentage_btts(away_team)
                    
                    st.write(f"- Partidos visita: {a_matches}")
                    st.write(f"- Media goles: {a_avg:.2f}")
                    st.write(f"- Más de 2.5: {a_over_25:.1f}%")
                    st.write(f"- BTTS: {a_btts:.1f}%")
                
                # Calcular todas las probabilidades primero
                h_win_pct = stats.team_home_percentage_wins(home_team)
                h_draw_pct = stats.team_home_percentage_draws(home_team)
                a_win_pct = stats.team_away_percentage_wins(away_team)
                a_draw_pct = stats.team_away_percentage_draws(away_team)
                
                pred_home_win = h_win_pct
                pred_draw = (h_draw_pct + a_draw_pct) / 2
                pred_away_win = a_win_pct
                
                total_1x2 = pred_home_win + pred_draw + pred_away_win
                if total_1x2 > 0:
                    pred_home_win = (pred_home_win / total_1x2) * 100
                    pred_draw = (pred_draw / total_1x2) * 100
                    pred_away_win = (pred_away_win / total_1x2) * 100
                
                pred_avg = (h_avg + a_avg) / 2
                pred_over_15 = (h_over_15 + a_over_15) / 2
                pred_over_25 = (h_over_25 + a_over_25) / 2
                pred_over_35 = (h_over_35 + a_over_35) / 2
                pred_under_35 = (h_under_35 + a_under_35) / 2
                pred_btts = (h_btts + a_btts) / 2
                
                # RESUMEN EJECUTIVO - Mejores Oportunidades
                st.markdown("---")
                st.markdown("### 🌟 RESUMEN: Mejores Oportunidades")
                
                # Crear lista de todas las apuestas con sus probabilidades
                all_bets = [
                    (f"Victoria {home_team}", pred_home_win, 100/pred_home_win if pred_home_win > 0 else 0),
                    ("Empate", pred_draw, 100/pred_draw if pred_draw > 0 else 0),
                    (f"Victoria {away_team}", pred_away_win, 100/pred_away_win if pred_away_win > 0 else 0),
                    ("Más de 1.5 goles", pred_over_15, 100/pred_over_15 if pred_over_15 > 0 else 0),
                    ("Más de 2.5 goles", pred_over_25, 100/pred_over_25 if pred_over_25 > 0 else 0),
                    ("Menos de 3.5 goles", pred_under_35, 100/pred_under_35 if pred_under_35 > 0 else 0),
                    ("Ambos Marcan (BTTS)", pred_btts, 100/pred_btts if pred_btts > 0 else 0),
                ]
                
                # Ordenar por probabilidad descendente
                all_bets_sorted = sorted(all_bets, key=lambda x: x[1], reverse=True)
                
                # Mostrar top 3 mejores probabilidades
                st.markdown("**🎯 Top 3 Apuestas con Mayor Probabilidad:**")
                
                col_top1, col_top2, col_top3 = st.columns(3)
                
                with col_top1:
                    bet_name, bet_prob, bet_odd = all_bets_sorted[0]
                    st.success(f"""
                    **🥇 {bet_name}**
                    - Probabilidad: **{bet_prob:.1f}%**
                    - Cuota: **{bet_odd:.2f}**
                    """)
                
                with col_top2:
                    bet_name, bet_prob, bet_odd = all_bets_sorted[1]
                    st.info(f"""
                    **🥈 {bet_name}**
                    - Probabilidad: **{bet_prob:.1f}%**
                    - Cuota: **{bet_odd:.2f}**
                    """)
                
                with col_top3:
                    bet_name, bet_prob, bet_odd = all_bets_sorted[2]
                    st.warning(f"""
                    **🥉 {bet_name}**
                    - Probabilidad: **{bet_prob:.1f}%**
                    - Cuota: **{bet_odd:.2f}**
                    """)
                
                st.caption("💡 Estas son las apuestas con mayor probabilidad según nuestro análisis estadístico")
                
                st.markdown("---")
                
                # Pronóstico combinado
                st.markdown("**🎯 Pronóstico del Encuentro:**")
                
                # Calcular probabilidades 1X2
                h_win_pct = stats.team_home_percentage_wins(home_team)
                h_draw_pct = stats.team_home_percentage_draws(home_team)
                a_win_pct = stats.team_away_percentage_wins(away_team)
                a_draw_pct = stats.team_away_percentage_draws(away_team)
                
                # Promedio de probabilidades 1X2
                pred_home_win = h_win_pct
                pred_draw = (h_draw_pct + a_draw_pct) / 2
                pred_away_win = a_win_pct
                
                # Normalizar para que sumen 100%
                total_1x2 = pred_home_win + pred_draw + pred_away_win
                if total_1x2 > 0:
                    pred_home_win = (pred_home_win / total_1x2) * 100
                    pred_draw = (pred_draw / total_1x2) * 100
                    pred_away_win = (pred_away_win / total_1x2) * 100
                
                # Mostrar pronóstico 1X2
                st.markdown("**⚽ Pronóstico 1X2 (Victoria/Empate/Derrota):**")
                col1x2_1, col1x2_2, col1x2_3 = st.columns(3)
                
                # Calcular cuotas (odds) - 100 / probabilidad
                odd_home_win = 100 / pred_home_win if pred_home_win > 0 else 0
                odd_draw = 100 / pred_draw if pred_draw > 0 else 0
                odd_away_win = 100 / pred_away_win if pred_away_win > 0 else 0
                
                with col1x2_1:
                    st.metric(f"🏠 {home_team}", f"{pred_home_win:.1f}%", delta=f"Cuota: {odd_home_win:.2f}")
                with col1x2_2:
                    st.metric("🤝 Empate", f"{pred_draw:.1f}%", delta=f"Cuota: {odd_draw:.2f}")
                with col1x2_3:
                    st.metric(f"✈️ {away_team}", f"{pred_away_win:.1f}%", delta=f"Cuota: {odd_away_win:.2f}")
                
                # Calcular otras estadísticas
                pred_avg = (h_avg + a_avg) / 2
                pred_over_15 = (h_over_15 + a_over_15) / 2
                pred_over_25 = (h_over_25 + a_over_25) / 2
                pred_over_35 = (h_over_35 + a_over_35) / 2
                pred_under_35 = (h_under_35 + a_under_35) / 2
                pred_btts = (h_btts + a_btts) / 2
                
                # Doble Oportunidad
                st.markdown("---")
                st.markdown("**🎲 Doble Oportunidad:**")
                
                # Calcular probabilidades de doble oportunidad
                pred_1x = pred_home_win + pred_draw  # Local o Empate
                pred_x2 = pred_draw + pred_away_win  # Empate o Visitante
                pred_12 = pred_home_win + pred_away_win  # Local o Visitante
                
                # Calcular cuotas de doble oportunidad
                odd_1x = 100 / pred_1x if pred_1x > 0 else 0
                odd_x2 = 100 / pred_x2 if pred_x2 > 0 else 0
                odd_12 = 100 / pred_12 if pred_12 > 0 else 0
                
                col_dc1, col_dc2, col_dc3 = st.columns(3)
                with col_dc1:
                    st.metric("1X (Local o Empate)", f"{pred_1x:.1f}%", delta=f"Cuota: {odd_1x:.2f}")
                with col_dc2:
                    st.metric("X2 (Empate o Visitante)", f"{pred_x2:.1f}%", delta=f"Cuota: {odd_x2:.2f}")
                with col_dc3:
                    st.metric("12 (Local o Visitante)", f"{pred_12:.1f}%", delta=f"Cuota: {odd_12:.2f}")
                

                st.markdown("---")
                st.markdown("**⚽ Mercados Combinados (Resultado + Goles)**")
                
                # Calcular probabilidades combinadas
                # Victoria Local + Goles
                prob_home_over25 = (pred_home_win / 100) * (pred_over_25 / 100) * 100
                prob_home_under25 = (pred_home_win / 100) * ((100 - pred_over_25) / 100) * 100
                
                # Victoria Visitante + Goles
                prob_away_over25 = (pred_away_win / 100) * (pred_over_25 / 100) * 100
                prob_away_under25 = (pred_away_win / 100) * ((100 - pred_over_25) / 100) * 100
                
                # Empate + Goles
                prob_draw_over25 = (pred_draw / 100) * (pred_over_25 / 100) * 100
                prob_draw_under25 = (pred_draw / 100) * ((100 - pred_over_25) / 100) * 100
                
                # Calcular cuotas combinadas
                odd_home_over25 = 100 / prob_home_over25 if prob_home_over25 > 0 else 0
                odd_home_under25 = 100 / prob_home_under25 if prob_home_under25 > 0 else 0
                odd_away_over25 = 100 / prob_away_over25 if prob_away_over25 > 0 else 0
                odd_away_under25 = 100 / prob_away_under25 if prob_away_under25 > 0 else 0
                odd_draw_over25 = 100 / prob_draw_over25 if prob_draw_over25 > 0 else 0
                odd_draw_under25 = 100 / prob_draw_under25 if prob_draw_under25 > 0 else 0
                
                # Mostrar en columnas
                col_comb1, col_comb2, col_comb3 = st.columns(3)
                
                with col_comb1:
                    st.markdown(f"**🏠 {home_team} Gana**")
                    st.metric("+ Más de 2.5 goles", f"{prob_home_over25:.1f}%", delta=f"Cuota: {odd_home_over25:.2f}")
                    st.metric("+ Menos de 2.5 goles", f"{prob_home_under25:.1f}%", delta=f"Cuota: {odd_home_under25:.2f}")
                
                with col_comb2:
                    st.markdown("**🤝 Empate**")
                    st.metric("+ Más de 2.5 goles", f"{prob_draw_over25:.1f}%", delta=f"Cuota: {odd_draw_over25:.2f}")
                    st.metric("+ Menos de 2.5 goles", f"{prob_draw_under25:.1f}%", delta=f"Cuota: {odd_draw_under25:.2f}")
                
                with col_comb3:
                    st.markdown(f"**✈️ {away_team} Gana**")
                    st.metric("+ Más de 2.5 goles", f"{prob_away_over25:.1f}%", delta=f"Cuota: {odd_away_over25:.2f}")
                    st.metric("+ Menos de 2.5 goles", f"{prob_away_under25:.1f}%", delta=f"Cuota: {odd_away_under25:.2f}")
                
                st.caption("💡 Mercados combinados: Probabilidad de que ocurran AMBOS eventos (resultado Y goles)")
                
                st.markdown("---")
                st.markdown("**📊 Otras Estadísticas:**")
                
                # Métricas principales
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("⚽ Goles Esperados", f"{pred_avg:.2f}")
                with col2:
                    st.metric("🔥 Prob. Más 2.5", f"{pred_over_25:.1f}%")
                with col3:
                    st.metric("🎯 Prob. BTTS", f"{pred_btts:.1f}%")
                
                # Análisis detallado
                st.markdown("**📊 Análisis Detallado:**")
                
                # Recomendación principal
                recommendations = []
                
                if pred_over_25 >= 70:
                    recommendations.append(("✅ MÁS DE 2.5 GOLES", "success", f"Alta probabilidad ({pred_over_25:.1f}%)"))
                elif pred_over_25 >= 55:
                    recommendations.append(("⚠️ MÁS DE 2.5 GOLES", "warning", f"Probabilidad moderada ({pred_over_25:.1f}%)"))
                
                if pred_under_35 >= 70:
                    recommendations.append(("✅ MENOS DE 3.5 GOLES", "success", f"Alta probabilidad ({pred_under_35:.1f}%)"))
                
                if pred_btts >= 70:
                    recommendations.append(("✅ AMBOS MARCAN (BTTS)", "success", f"Alta probabilidad ({pred_btts:.1f}%)"))
                elif pred_btts >= 55:
                    recommendations.append(("⚠️ AMBOS MARCAN (BTTS)", "warning", f"Probabilidad moderada ({pred_btts:.1f}%)"))
                
                
                if pred_over_15 >= 85:
                    recommendations.append(("✅ MÁS DE 1.5 GOLES", "success", f"Muy alta probabilidad ({pred_over_15:.1f}%)"))
                
                if pred_avg >= 3.5:
                    recommendations.append(("🔥 PARTIDO CON MUCHOS GOLES", "info", f"Media esperada: {pred_avg:.2f}"))
                elif pred_avg <= 2.0:
                    recommendations.append(("❄️ PARTIDO CON POCOS GOLES", "info", f"Media esperada: {pred_avg:.2f}"))
                
                # Mostrar recomendaciones
                if recommendations:
                    for rec_text, rec_type, rec_detail in recommendations:
                        if rec_type == "success":
                            st.success(f"**{rec_text}** - {rec_detail}")
                        elif rec_type == "warning":
                            st.warning(f"**{rec_text}** - {rec_detail}")
                        else:
                            st.info(f"**{rec_text}** - {rec_detail}")
                else:
                    st.info("📊 Partido equilibrado - Revisar estadísticas detalladas")
                
                # Tabla de probabilidades
                st.markdown("**📈 Tabla de Probabilidades:**")

                prob_data = {
                    "Mercado": ["Más de 1.5", "Más de 2.5", "Más de 3.5", "Menos de 3.5", "BTTS"],
                    "Probabilidad": [
                        f"{pred_over_15:.1f}%",
                        f"{pred_over_25:.1f}%",
                        f"{pred_over_35:.1f}%",
                        f"{pred_under_35:.1f}%",
                        f"{pred_btts:.1f}%"
                    ]
                }
                st.table(prob_data)
    else:
        st.info("No hay fechas disponibles para partidos próximos")
else:
    st.info("No hay partidos próximos programados")

st.markdown("---")

# Tabla de datos
st.markdown("### 📋 Últimos Partidos")

# Filtrar solo partidos jugados
played_matches = df.filter(pl.col("GA").is_not_null())

if len(played_matches) > 0:
    # Ordenar por fecha descendente y tomar los últimos 10
    display_df = played_matches.tail(10).reverse()
    
    # Crear columna de resultado
    display_df = display_df.with_columns([
        (pl.col("GA").cast(str) + " - " + pl.col("GC").cast(str)).alias("Resultado"),
        (pl.col("GA") + pl.col("GC")).alias("Total Goles")
    ])
    
    # Seleccionar columnas para mostrar
    display_df = display_df.select([
        "Jornada", "Fecha", "Hora", "Local", "Visita", "Resultado", "Total Goles"
    ])
    
    # Convertir a pandas para styling
    import pandas as pd
    df_pandas = display_df.to_pandas()
    
    
    # Función para colorear filas según total de goles
    def color_rows(row):
        total_goles = row['Total Goles']
        if total_goles >= 4:
            return ['background-color: #1a0f2e; color: #c084fc'] * len(row)  # Morado claro para muchos goles
        elif total_goles >= 3:
            return ['background-color: #0f0a19; color: #a855f7'] * len(row)  # Morado medio
        elif total_goles >= 2:
            return ['background-color: #0a050f; color: #ffffff'] * len(row)  # Oscuro con texto blanco
        else:
            return ['background-color: #050309; color: #8b949e'] * len(row)  # Muy oscuro para pocos goles
    
    # Aplicar estilos
    styled_df = df_pandas.style.apply(color_rows, axis=1)\
        .set_properties(**{
            'text-align': 'center',
            'font-size': '1rem',
            'font-weight': '600',
            'padding': '12px',
            'border': '1px solid #30363d'
        })\
        .set_table_styles([
            {'selector': 'thead th', 
             'props': [
                 ('background', 'linear-gradient(135deg, #9333ea 0%, #7e22ce 100%)'),
                 ('color', '#ffffff'),
                 ('font-weight', '900'),
                 ('text-transform', 'uppercase'),
                 ('letter-spacing', '1px'),
                 ('padding', '14px'),
                 ('font-size', '0.95rem'),
                 ('border', '2px solid #a855f7'),
                 ('text-align', 'center')
             ]},
            {'selector': 'tbody tr:hover',
             'props': [
                 ('background-color', '#1a0f2e !important'),
                 ('color', '#c084fc !important'),
                 ('transform', 'scale(1.01)'),
                 ('box-shadow', '0 4px 12px rgba(168, 85, 247, 0.3)')
             ]},
            {'selector': 'table',
             'props': [
                 ('border-collapse', 'separate'),
                 ('border-spacing', '0'),
                 ('border-radius', '8px'),
                 ('overflow', 'hidden'),
                 ('border', '2px solid #9333ea'),
                 ('box-shadow', '0 4px 15px rgba(147, 51, 234, 0.2)')
             ]}
        ])
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        height=450
    )
    
    # Leyenda de colores
    st.markdown("""
    <div style='display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;'>
        <div style='background: linear-gradient(135deg, #1a0f2e 0%, #0f0a19 100%); padding: 8px 16px; border-radius: 6px; border: 1px solid #a855f7;'>
            <span style='color: #c084fc; font-weight: 700;'>🔥 4+ goles</span>
        </div>
        <div style='background: linear-gradient(135deg, #0f0a19 0%, #0a050f 100%); padding: 8px 16px; border-radius: 6px; border: 1px solid #9333ea;'>
            <span style='color: #a855f7; font-weight: 700;'>⚽ 3 goles</span>
        </div>
        <div style='background: linear-gradient(135deg, #0a050f 0%, #050309 100%); padding: 8px 16px; border-radius: 6px; border: 1px solid #7e22ce;'>
            <span style='color: #ffffff; font-weight: 700;'>🎯 2 goles</span>
        </div>
        <div style='background: linear-gradient(135deg, #050309 0%, #000000 100%); padding: 8px 16px; border-radius: 6px; border: 1px solid #6b21a8;'>
            <span style='color: #8b949e; font-weight: 700;'>📊 0-1 goles</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.info("No hay partidos jugados disponibles")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Dashboard de Pronósticos Deportivos | Datos actualizados en tiempo real</p>",
    unsafe_allow_html=True
)
