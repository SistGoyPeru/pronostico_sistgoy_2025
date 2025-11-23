import streamlit as st
import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from extract_calendar import CalendarExtractor, StatisticsCalculator

# Configuración de la página
st.set_page_config(
    page_title="Dashboard de Pronósticos Deportivos",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #2d3142;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #e0e0e0 !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #00d4ff !important;
        font-size: 2rem !important;
    }
    h1 {
        color: #00d4ff;
        text-align: center;
        font-weight: bold;
    }
    h2, h3 {
        color: #00d4ff;
    }
    </style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<h1>⚽ Dashboard de Pronósticos Deportivos</h1>", unsafe_allow_html=True)

# Sidebar - Logo y Configuración
try:
    st.sidebar.image("LOGO.jpg", use_container_width=True)
except:
    pass  # Si no se encuentra el logo, continuar sin él

st.sidebar.header("🏆 Configuración")

ligas = {
    # Europa - Top 5 Leagues
    "🇩🇪 Alemania - Bundesliga": "https://www.livefutbol.com/competition/co12/alemania-bundesliga/all-matches/",
    "🇩🇪 Alemania - 2. Bundesliga": "https://www.livefutbol.com/competition/co3/alemania-2-bundesliga/all-matches/",
    "🇪🇸 España - La Liga": "https://www.livefutbol.com/competition/co97/espana-primera-division/all-matches/",
    "🇪🇸 España - Segunda División": "https://www.livefutbol.com/competition/co110/espana-segunda-division/all-matches/",
    "🇬🇧 Inglaterra - Premier League": "https://www.livefutbol.com/competition/co91/inglaterra-premier-league/all-matches/",
    "🇬🇧 Inglaterra - Championship": "https://www.livefutbol.com/competition/co20/inglaterra-championship/all-matches/",
    "🇮🇹 Italia - Serie A": "https://www.livefutbol.com/competition/co11/italia-serie-a/all-matches/",
    "🇮🇹 Italia - Serie B": "https://www.livefutbol.com/competition/co14/italia-serie-b/all-matches/",
    "🇫🇷 Francia - Ligue 1": "https://www.livefutbol.com/competition/co71/francia-ligue-1/all-matches/",
    "🇫🇷 Francia - Ligue 2": "https://www.livefutbol.com/competition/co15/francia-ligue-2/all-matches/",
    
    # Europa - Otras Ligas
    "🇵🇹 Portugal - Primeira Liga": "https://www.livefutbol.com/competition/co17/portugal-primeira-liga/all-matches/",
    "🇳🇱 Países Bajos - Eredivisie": "https://www.livefutbol.com/competition/co18/paises-bajos-eredivisie/all-matches/",
    "🇧🇪 Bélgica - Pro League": "https://www.livefutbol.com/competition/co19/belgica-pro-league/all-matches/",
    "🇹🇷 Turquía - Süper Lig": "https://www.livefutbol.com/competition/co20/turquia-super-lig/all-matches/",
    "🇷🇺 Rusia - Premier League": "https://www.livefutbol.com/competition/co43/rusia-premier-league/all-matches/",
    "🇺🇦 Ucrania - Premier League": "https://www.livefutbol.com/competition/co44/ucrania-premier-league/all-matches/",
    "🇬🇷 Grecia - Super League": "https://www.livefutbol.com/competition/co45/grecia-super-league/all-matches/",
    "🇦🇹 Austria - Bundesliga": "https://www.livefutbol.com/competition/co46/austria-bundesliga/all-matches/",
    "🇨🇭 Suiza - Super League": "https://www.livefutbol.com/competition/co47/suiza-super-league/all-matches/",
    "🇩🇰 Dinamarca - Superliga": "https://www.livefutbol.com/competition/co48/dinamarca-superliga/all-matches/",
    "🇸🇪 Suecia - Allsvenskan": "https://www.livefutbol.com/competition/co49/suecia-allsvenskan/all-matches/",
    "🇳🇴 Noruega - Eliteserien": "https://www.livefutbol.com/competition/co50/noruega-eliteserien/all-matches/",
    "🇨🇿 República Checa - Liga": "https://www.livefutbol.com/competition/co51/republica-checa-liga/all-matches/",
    "🇵🇱 Polonia - Ekstraklasa": "https://www.livefutbol.com/competition/co52/polonia-ekstraklasa/all-matches/",
    "🇷🇴 Rumania - Liga 1": "https://www.livefutbol.com/competition/co53/rumania-liga-1/all-matches/",
    "🇭🇷 Croacia - HNL": "https://www.livefutbol.com/competition/co54/croacia-hnl/all-matches/",
    "🇷🇸 Serbia - SuperLiga": "https://www.livefutbol.com/competition/co55/serbia-superliga/all-matches/",
    "🇸🇰 Eslovaquia - Fortuna Liga": "https://www.livefutbol.com/competition/co56/eslovaquia-fortuna-liga/all-matches/",
    "🇸🇮 Eslovenia - PrvaLiga": "https://www.livefutbol.com/competition/co57/eslovenia-prvaliga/all-matches/",
    "🇧🇬 Bulgaria - First League": "https://www.livefutbol.com/competition/co58/bulgaria-first-league/all-matches/",
    
    # América del Sur
    "🇧🇷 Brasil - Serie A": "https://www.livefutbol.com/competition/co3/brasil-serie-a/all-matches/",
    "🇧🇷 Brasil - Serie B": "https://www.livefutbol.com/competition/co4/brasil-serie-b/all-matches/",
    "🇦🇷 Argentina - Liga Profesional": "https://www.livefutbol.com/competition/co5/argentina-liga-profesional/all-matches/",
    "🇨🇴 Colombia - Primera A": "https://www.livefutbol.com/competition/co6/colombia-primera-a/all-matches/",
    "🇨🇱 Chile - Primera División": "https://www.livefutbol.com/competition/co7/chile-primera-division/all-matches/",
    "🇺🇾 Uruguay - Primera División": "https://www.livefutbol.com/competition/co59/uruguay-primera-division/all-matches/",
    "🇪🇨 Ecuador - Serie A": "https://www.livefutbol.com/competition/co60/ecuador-serie-a/all-matches/",
    "🇵🇪 Perú - Primera División": "https://www.livefutbol.com/competition/co100/peru-primera-division/all-matches/",
    "🇵🇾 Paraguay - Primera División": "https://www.livefutbol.com/competition/co61/paraguay-primera-division/all-matches/",
    "🇧🇴 Bolivia - Primera División": "https://www.livefutbol.com/competition/co62/bolivia-primera-division/all-matches/",
    "🇻🇪 Venezuela - Primera División": "https://www.livefutbol.com/competition/co63/venezuela-primera-division/all-matches/",
    
    # América del Norte y Central
    "🇲🇽 México - Liga MX": "https://www.livefutbol.com/competition/co10/mexico-liga-mx/all-matches/",
    "🇺🇸 USA - MLS": "https://www.livefutbol.com/competition/co64/usa-mls/all-matches/",
    "🇨🇷 Costa Rica - Primera División": "https://www.livefutbol.com/competition/co65/costa-rica-primera-division/all-matches/",
    "🇭🇳 Honduras - Liga Nacional": "https://www.livefutbol.com/competition/co66/honduras-liga-nacional/all-matches/",
    "🇬🇹 Guatemala - Liga Nacional": "https://www.livefutbol.com/competition/co67/guatemala-liga-nacional/all-matches/",
    
    # Asia
    "🇯🇵 Japón - J1 League": "https://www.livefutbol.com/competition/co68/japon-j1-league/all-matches/",
    "🇰🇷 Corea del Sur - K League 1": "https://www.livefutbol.com/competition/co69/corea-del-sur-k-league-1/all-matches/",
    "🇨🇳 China - Super League": "https://www.livefutbol.com/competition/co70/china-super-league/all-matches/",
    "🇸🇦 Arabia Saudita - Pro League": "https://www.livefutbol.com/competition/co71/arabia-saudita-pro-league/all-matches/",
    "🇦🇪 Emiratos Árabes - Pro League": "https://www.livefutbol.com/competition/co72/emiratos-arabes-pro-league/all-matches/",
    "🇶🇦 Qatar - Stars League": "https://www.livefutbol.com/competition/co73/qatar-stars-league/all-matches/",
    
    # África
    "🇿🇦 Sudáfrica - Premier Division": "https://www.livefutbol.com/competition/co74/sudafrica-premier-division/all-matches/",
    "🇪🇬 Egipto - Premier League": "https://www.livefutbol.com/competition/co75/egipto-premier-league/all-matches/",
    "🇲🇦 Marruecos - Botola Pro": "https://www.livefutbol.com/competition/co76/marruecos-botola-pro/all-matches/",
}



liga_seleccionada = st.sidebar.selectbox(
    "Selecciona una liga:",
    options=list(ligas.keys()),
    index=1  # Bundesliga por defecto
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
        st.success("✅ Datos cargados exitosamente!")

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
                
                # Análisis de Valor vs Casas de Apuestas
                st.markdown("---")
                st.markdown("**💰 Comparación con Casas de Apuestas**")
                
                # Explicación clara
                st.info("""
                **¿Cómo funciona?**
                
                Las casas de apuestas ofrecen cuotas basadas en sus análisis. Nosotros calculamos cuotas basadas en 
                estadísticas reales de los equipos. Si nuestra cuota es **MAYOR** que la de las casas, significa que 
                encontramos una **oportunidad de valor** (value bet).
                
                **Ejemplo:** Si calculamos cuota 2.50 para Victoria Local y las casas ofrecen 1.80, nuestra cuota es mejor 
                → hay valor en apostar por Victoria Local.
                """)
                
                # Mostrar cuotas calculadas vs típicas del mercado
                st.markdown("##### 📊 Cuotas Calculadas vs Mercado")
                
                # Crear comparación visual mejorada
                col_comp1, col_comp2 = st.columns(2)
                
                with col_comp1:
                    st.markdown("**🎯 Mercado 1X2**")
                    
                    # Victoria Local
                    market_home = "1.50-3.50"
                    valor_home = "✅ VALOR" if odd_home_win > 3.50 else "⚠️ REVISAR" if odd_home_win > 2.50 else "❌ NO"
                    st.markdown(f"""
                    **Victoria {home_team}**
                    - 🔢 Nuestra cuota: **{odd_home_win:.2f}**
                    - 🏢 Mercado típico: {market_home}
                    - {valor_home}
                    """)
                    
                    # Empate
                    market_draw = "2.80-4.50"
                    valor_draw = "✅ VALOR" if odd_draw > 4.50 else "⚠️ REVISAR" if odd_draw > 3.65 else "❌ NO"
                    st.markdown(f"""
                    **Empate**
                    - 🔢 Nuestra cuota: **{odd_draw:.2f}**
                    - 🏢 Mercado típico: {market_draw}
                    - {valor_draw}
                    """)
                    
                    # Victoria Visitante
                    market_away = "1.50-3.50"
                    valor_away = "✅ VALOR" if odd_away_win > 3.50 else "⚠️ REVISAR" if odd_away_win > 2.50 else "❌ NO"
                    st.markdown(f"""
                    **Victoria {away_team}**
                    - 🔢 Nuestra cuota: **{odd_away_win:.2f}**
                    - 🏢 Mercado típico: {market_away}
                    - {valor_away}
                    """)
                
                with col_comp2:
                    st.markdown("**🎲 Doble Oportunidad**")
                    
                    # 1X
                    market_1x = "1.10-1.50"
                    valor_1x = "✅ VALOR" if odd_1x > 1.50 else "⚠️ REVISAR" if odd_1x > 1.30 else "❌ NO"
                    st.markdown(f"""
                    **1X (Local o Empate)**
                    - 🔢 Nuestra cuota: **{odd_1x:.2f}**
                    - 🏢 Mercado típico: {market_1x}
                    - {valor_1x}
                    """)
                    
                    # X2
                    market_x2 = "1.10-1.50"
                    valor_x2 = "✅ VALOR" if odd_x2 > 1.50 else "⚠️ REVISAR" if odd_x2 > 1.30 else "❌ NO"
                    st.markdown(f"""
                    **X2 (Empate o Visitante)**
                    - 🔢 Nuestra cuota: **{odd_x2:.2f}**
                    - 🏢 Mercado típico: {market_x2}
                    - {valor_x2}
                    """)
                    
                    # 12
                    market_12 = "1.15-1.40"
                    valor_12 = "✅ VALOR" if odd_12 > 1.40 else "⚠️ REVISAR" if odd_12 > 1.27 else "❌ NO"
                    st.markdown(f"""
                    **12 (Local o Visitante)**
                    - 🔢 Nuestra cuota: **{odd_12:.2f}**
                    - 🏢 Mercado típico: {market_12}
                    - {valor_12}
                    """)
                
                # Leyenda
                st.caption("✅ = Cuota alta, posible valor | ⚠️ = Revisar, cuota media | ❌ = Cuota baja, sin valor")
                
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
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
else:
    st.info("No hay partidos jugados disponibles")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666;'>Dashboard de Pronósticos Deportivos | Datos actualizados en tiempo real</p>",
    unsafe_allow_html=True
)
