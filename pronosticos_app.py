import streamlit as st
import polars as pl
import numpy as np
from scipy.stats import poisson
from datetime import datetime
import os
import subprocess
import time

# Configuración de la página
st.set_page_config(
    page_title="Pronósticos de Fútbol - Método Poisson",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #00d4ff;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
    }
    .stMetric label {
        color: #00d4ff !important;
        font-weight: 600;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
    }
    h1, h2, h3 {
        color: #00d4ff !important;
    }
    .match-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #3b82f6;
        margin: 10px 0;
    }
    .prob-high {
        color: #10b981;
        font-weight: bold;
    }
    .prob-medium {
        color: #f59e0b;
        font-weight: bold;
    }
    .prob-low {
        color: #ef4444;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

class PoissonPredictor:
    def __init__(self, df):
        self.df = df
        self.played_matches = df.filter(pl.col("GA").is_not_null())
        
    def calculate_team_stats(self, team_name):
        """Calcula estadísticas ofensivas y defensivas de un equipo"""
        home_matches = self.played_matches.filter(pl.col("Local") == team_name)
        away_matches = self.played_matches.filter(pl.col("Visita") == team_name)
        
        # Goles anotados
        home_goals_scored = home_matches["GA"].sum() if len(home_matches) > 0 else 0
        away_goals_scored = away_matches["GC"].sum() if len(away_matches) > 0 else 0
        total_goals_scored = home_goals_scored + away_goals_scored
        
        # Goles recibidos
        home_goals_conceded = home_matches["GC"].sum() if len(home_matches) > 0 else 0
        away_goals_conceded = away_matches["GA"].sum() if len(away_matches) > 0 else 0
        total_goals_conceded = home_goals_conceded + away_goals_conceded
        
        # Partidos jugados
        total_matches = len(home_matches) + len(away_matches)
        
        if total_matches == 0:
            return {
                'goals_scored_avg': 0,
                'goals_conceded_avg': 0,
                'home_goals_scored_avg': 0,
                'away_goals_scored_avg': 0,
                'matches_played': 0
            }
        
        return {
            'goals_scored_avg': total_goals_scored / total_matches,
            'goals_conceded_avg': total_goals_conceded / total_matches,
            'home_goals_scored_avg': home_goals_scored / len(home_matches) if len(home_matches) > 0 else 0,
            'away_goals_scored_avg': away_goals_scored / len(away_matches) if len(away_matches) > 0 else 0,
            'home_goals_conceded_avg': home_goals_conceded / len(home_matches) if len(home_matches) > 0 else 0,
            'away_goals_conceded_avg': away_goals_conceded / len(away_matches) if len(away_matches) > 0 else 0,
            'matches_played': total_matches
        }
    
    def calculate_league_average(self):
        """Calcula el promedio de goles de la liga"""
        total_goals = (self.played_matches["GA"] + self.played_matches["GC"]).sum()
        total_matches = len(self.played_matches)
        if total_matches == 0:
            return 2.5
        return total_goals / (total_matches * 2)
    
    def predict_match(self, home_team, away_team):
        """Predice el resultado usando distribución de Poisson"""
        home_stats = self.calculate_team_stats(home_team)
        away_stats = self.calculate_team_stats(away_team)
        league_avg = self.calculate_league_average()
        
        # Si no hay datos suficientes
        if home_stats['matches_played'] < 3 or away_stats['matches_played'] < 3:
            return None
        
        # Calcular fuerza de ataque y defensa
        home_attack_strength = home_stats['home_goals_scored_avg'] / league_avg if league_avg > 0 else 1
        home_defense_strength = home_stats['home_goals_conceded_avg'] / league_avg if league_avg > 0 else 1
        away_attack_strength = away_stats['away_goals_scored_avg'] / league_avg if league_avg > 0 else 1
        away_defense_strength = away_stats['away_goals_conceded_avg'] / league_avg if league_avg > 0 else 1
        
        # Goles esperados
        home_expected_goals = home_attack_strength * away_defense_strength * league_avg
        away_expected_goals = away_attack_strength * home_defense_strength * league_avg
        
        # Calcular probabilidades para cada resultado
        max_goals = 6
        prob_matrix = np.zeros((max_goals + 1, max_goals + 1))
        
        for i in range(max_goals + 1):
            for j in range(max_goals + 1):
                prob_matrix[i][j] = poisson.pmf(i, home_expected_goals) * poisson.pmf(j, away_expected_goals)
        
        # Probabilidades 1X2
        prob_home = np.sum(np.tril(prob_matrix, -1))  # Local gana
        prob_draw = np.sum(np.diag(prob_matrix))       # Empate
        prob_away = np.sum(np.triu(prob_matrix, 1))    # Visitante gana
        
        # Over/Under múltiples líneas
        total_goals_matrix = np.arange(max_goals + 1)[:, None] + np.arange(max_goals + 1)
        
        prob_over_05 = np.sum(prob_matrix[np.where(total_goals_matrix > 0.5)])
        prob_over_15 = np.sum(prob_matrix[np.where(total_goals_matrix > 1.5)])
        prob_over_25 = np.sum(prob_matrix[np.where(total_goals_matrix > 2.5)])
        prob_over_35 = np.sum(prob_matrix[np.where(total_goals_matrix > 3.5)])
        prob_over_45 = np.sum(prob_matrix[np.where(total_goals_matrix > 4.5)])
        
        prob_under_15 = 1 - prob_over_15
        prob_under_25 = 1 - prob_over_25
        prob_under_35 = 1 - prob_over_35
        
        # BTTS (Ambos equipos anotan)
        prob_btts_yes = 1 - prob_matrix[0, :].sum() - prob_matrix[:, 0].sum() + prob_matrix[0, 0]
        prob_btts_no = 1 - prob_btts_yes
        
        # Doble Oportunidad
        prob_1x = prob_home + prob_draw
        prob_12 = prob_home + prob_away
        prob_x2 = prob_draw + prob_away
        
        # Gana y anota (ambos equipos)
        prob_home_win_btts = 0
        prob_away_win_btts = 0
        for i in range(1, max_goals + 1):
            for j in range(1, max_goals + 1):
                if i > j:
                    prob_home_win_btts += prob_matrix[i, j]
                elif j > i:
                    prob_away_win_btts += prob_matrix[i, j]
        
        # Handicap Asiático
        prob_home_minus_15 = np.sum(prob_matrix[np.where((np.arange(max_goals + 1)[:, None] - 
                                                           np.arange(max_goals + 1)) > 1.5)])
        prob_away_plus_15 = 1 - prob_home_minus_15
        
        prob_away_minus_15 = np.sum(prob_matrix[np.where((np.arange(max_goals + 1) - 
                                                           np.arange(max_goals + 1)[:, None]) > 1.5)])
        prob_home_plus_15 = 1 - prob_away_minus_15
        
        # Resultado más probable
        most_likely_score = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
        
        # Top 5 resultados más probables
        flat_indices = np.argsort(prob_matrix.ravel())[::-1][:5]
        top_scores = []
        for idx in flat_indices:
            score = np.unravel_index(idx, prob_matrix.shape)
            prob = prob_matrix[score] * 100
            top_scores.append({
                'score': f"{score[0]}-{score[1]}",
                'prob': round(prob, 2)
            })
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_expected_goals': round(home_expected_goals, 2),
            'away_expected_goals': round(away_expected_goals, 2),
            # 1X2
            'prob_home': round(prob_home * 100, 2),
            'prob_draw': round(prob_draw * 100, 2),
            'prob_away': round(prob_away * 100, 2),
            # Over/Under
            'prob_over_05': round(prob_over_05 * 100, 2),
            'prob_over_15': round(prob_over_15 * 100, 2),
            'prob_over_25': round(prob_over_25 * 100, 2),
            'prob_over_35': round(prob_over_35 * 100, 2),
            'prob_over_45': round(prob_over_45 * 100, 2),
            'prob_under_15': round(prob_under_15 * 100, 2),
            'prob_under_25': round(prob_under_25 * 100, 2),
            'prob_under_35': round(prob_under_35 * 100, 2),
            # BTTS
            'prob_btts_yes': round(prob_btts_yes * 100, 2),
            'prob_btts_no': round(prob_btts_no * 100, 2),
            # Doble Oportunidad
            'prob_1x': round(prob_1x * 100, 2),
            'prob_12': round(prob_12 * 100, 2),
            'prob_x2': round(prob_x2 * 100, 2),
            # Gana y anota
            'prob_home_win_btts': round(prob_home_win_btts * 100, 2),
            'prob_away_win_btts': round(prob_away_win_btts * 100, 2),
            # Handicap Asiático
            'prob_home_minus_15': round(prob_home_minus_15 * 100, 2),
            'prob_away_plus_15': round(prob_away_plus_15 * 100, 2),
            'prob_home_plus_15': round(prob_home_plus_15 * 100, 2),
            'prob_away_minus_15': round(prob_away_minus_15 * 100, 2),
            # Resultados exactos
            'most_likely_score': f"{most_likely_score[0]}-{most_likely_score[1]}",
            'top_scores': top_scores,
            'home_stats': home_stats,
            'away_stats': away_stats
        }
    
    def get_upcoming_matches(self):
        """Obtiene los próximos partidos"""
        return self.df.filter(pl.col("GA").is_null())
    
    def calculate_accuracy(self):
        """Calcula el porcentaje de aciertos del modelo en partidos ya jugados"""
        if len(self.played_matches) < 10:
            return None
        
        correct_1x2 = 0
        correct_over_25 = 0
        correct_btts = 0
        correct_double_chance = 0
        total = 0
        
        for row in self.played_matches.iter_rows(named=True):
            home = row['Local']
            away = row['Visita']
            ga = row['GA']
            gc = row['GC']
            
            # Verificar que ambos equipos tengan suficientes partidos previos
            home_stats = self.calculate_team_stats(home)
            away_stats = self.calculate_team_stats(away)
            
            if home_stats['matches_played'] < 3 or away_stats['matches_played'] < 3:
                continue
            
            prediction = self.predict_match(home, away)
            if not prediction:
                continue
            
            total += 1
            
            # Resultado real
            if ga > gc:
                real_result = 'home'
            elif ga < gc:
                real_result = 'away'
            else:
                real_result = 'draw'
            
            # Predicción 1X2
            max_prob = max(prediction['prob_home'], prediction['prob_draw'], prediction['prob_away'])
            if prediction['prob_home'] == max_prob:
                predicted_result = 'home'
            elif prediction['prob_draw'] == max_prob:
                predicted_result = 'draw'
            else:
                predicted_result = 'away'
            
            if predicted_result == real_result:
                correct_1x2 += 1
            
            # Doble Oportunidad - tomamos la más probable
            max_dc = max(prediction['prob_1x'], prediction['prob_12'], prediction['prob_x2'])
            if prediction['prob_1x'] == max_dc and real_result in ['home', 'draw']:
                correct_double_chance += 1
            elif prediction['prob_12'] == max_dc and real_result in ['home', 'away']:
                correct_double_chance += 1
            elif prediction['prob_x2'] == max_dc and real_result in ['draw', 'away']:
                correct_double_chance += 1
            
            # Over/Under 2.5
            total_goals = ga + gc
            predicted_over = prediction['prob_over_25'] > prediction['prob_under_25']
            real_over = total_goals > 2.5
            
            if predicted_over == real_over:
                correct_over_25 += 1
            
            # BTTS
            predicted_btts = prediction['prob_btts_yes'] > prediction['prob_btts_no']
            real_btts = ga > 0 and gc > 0
            
            if predicted_btts == real_btts:
                correct_btts += 1
        
        if total == 0:
            return None
        
        return {
            'total_predictions': total,
            'accuracy_1x2': round(correct_1x2 / total * 100, 2),
            'accuracy_over_25': round(correct_over_25 / total * 100, 2),
            'accuracy_btts': round(correct_btts / total * 100, 2),
            'accuracy_double_chance': round(correct_double_chance / total * 100, 2)
        }

def update_league_data():
    """Actualiza los datos de las ligas desde internet"""
    try:
        with st.spinner("🔄 Actualizando datos de las ligas desde internet..."):
            result = subprocess.run(
                ["python", "extract_calendar.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                st.success("✅ Datos actualizados correctamente")
                return True
            else:
                st.error(f"❌ Error al actualizar datos: {result.stderr}")
                return False
    except subprocess.TimeoutExpired:
        st.error("⏱️ Timeout: La actualización tomó demasiado tiempo")
        return False
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return False

def load_league_data():
    """Carga los datos de todas las ligas"""
    ligas = {
        "Premier League": "calendario_premier_league.csv",
        "La Liga": "calendario_la_liga.csv",
        "La Liga 2": "calendario_la_liga_2.csv",
        "Serie A": "calendario_serie_a.csv",
        "Bundesliga": "calendario_bundesliga.csv",
        "Ligue 1": "calendario_ligue_1.csv"
    }
    
    data = {}
    for nombre, archivo in ligas.items():
        if os.path.exists(archivo):
            data[nombre] = pl.read_csv(archivo)
    
    return data

def get_prob_color(prob):
    """Retorna clase CSS según probabilidad"""
    if prob >= 50:
        return "prob-high"
    elif prob >= 30:
        return "prob-medium"
    else:
        return "prob-low"

def main():
    st.title("⚽ Pronósticos de Fútbol - Método Poisson")
    st.markdown("### Sistema de predicción basado en distribución de Poisson")
    
    # Sidebar
    st.sidebar.title("🎯 Configuración")
    
    # Botón para actualizar datos
    if st.sidebar.button("🔄 Actualizar Datos desde Internet", type="primary"):
        if update_league_data():
            st.rerun()
    
    # Mostrar última actualización
    csv_files = ["calendario_premier_league.csv", "calendario_la_liga.csv", 
                 "calendario_la_liga_2.csv", "calendario_serie_a.csv", 
                 "calendario_bundesliga.csv", "calendario_ligue_1.csv"]
    
    existing_files = [f for f in csv_files if os.path.exists(f)]
    if existing_files:
        last_modified = max([os.path.getmtime(f) for f in existing_files])
        last_update = datetime.fromtimestamp(last_modified).strftime("%Y-%m-%d %H:%M:%S")
        st.sidebar.info(f"📅 Última actualización: {last_update}")
    
    # Cargar datos
    league_data = load_league_data()
    
    if not league_data:
        st.error("❌ No se encontraron archivos CSV.")
        st.info("👆 Haz clic en 'Actualizar Datos desde Internet' para descargar los datos de las ligas")
        return
    
    # Mostrar precisión de pronósticos
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Precisión del Modelo")
    
    with st.sidebar.expander("Ver tasas de acierto por liga"):
        for league_name, df in league_data.items():
            predictor = PoissonPredictor(df)
            accuracy = predictor.calculate_accuracy()
            
            if accuracy:
                st.markdown(f"**{league_name}**")
                st.markdown(f"- 1X2: {accuracy['accuracy_1x2']}%")
                st.markdown(f"- Over 2.5: {accuracy['accuracy_over_25']}%")
                st.markdown(f"- BTTS: {accuracy['accuracy_btts']}%")
                st.markdown(f"- Doble Oportunidad: {accuracy['accuracy_double_chance']}%")
                st.markdown(f"*Basado en {accuracy['total_predictions']} predicciones*")
                st.markdown("---")
    
    # Selector de vista
    view_mode = st.sidebar.radio(
        "Modo de visualización",
        ["📊 Pronósticos por Liga", "📅 Pronósticos por Fecha", "🎯 Liga + Fecha", 
         "📈 Estadísticas por Liga", "🔍 Resultados vs Pronósticos", "📊 Precisión del Modelo"]
    )
    
    if view_mode == "📊 Pronósticos por Liga":
        # Selector de liga
        selected_league = st.sidebar.selectbox(
            "Selecciona una liga",
            list(league_data.keys())
        )
        
        df = league_data[selected_league]
        predictor = PoissonPredictor(df)
        upcoming = predictor.get_upcoming_matches()
        
        st.header(f"🏆 {selected_league}")
        
        # Estadísticas generales
        played = predictor.played_matches
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Partidos Jugados", len(played))
        with col2:
            st.metric("Partidos por Jugar", len(upcoming))
        with col3:
            avg_goals = (played["GA"] + played["GC"]).mean() if len(played) > 0 else 0
            st.metric("Goles Promedio", f"{avg_goals:.2f}")
        with col4:
            total_matches = len(df)
            progress = (len(played) / total_matches * 100) if total_matches > 0 else 0
            st.metric("Progreso", f"{progress:.1f}%")
        
        st.markdown("---")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            show_all = st.checkbox("Mostrar todos los partidos", value=False)
        with col2:
            min_prob = st.slider("Probabilidad mínima (%)", 0, 100, 40)
        
        st.subheader("🔮 Próximos Partidos")
        
        # Procesar cada partido
        predictions = []
        for row in upcoming.iter_rows(named=True):
            home = row['Local']
            away = row['Visita']
            fecha = row['Fecha']
            hora = row['Hora']
            
            prediction = predictor.predict_match(home, away)
            if prediction:
                prediction['fecha'] = fecha
                prediction['hora'] = hora
                predictions.append(prediction)
        
        # Ordenar por fecha
        predictions.sort(key=lambda x: (x['fecha'] or '9999', x['hora'] or '99:99'))
        
        # Mostrar predicciones
        count = 0
        for pred in predictions:
            max_prob = max(pred['prob_home'], pred['prob_draw'], pred['prob_away'])
            
            if not show_all and max_prob < min_prob:
                continue
            
            count += 1
            
            with st.container():
                st.markdown(f"""
                <div class="match-card">
                    <h4>📅 {pred['fecha']} - ⏰ {pred['hora']}</h4>
                    <h3>{pred['home_team']} 🆚 {pred['away_team']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("#### 🎲 1X2")
                    st.markdown(f"**1:** <span class='{get_prob_color(pred['prob_home'])}'>{pred['prob_home']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**X:** <span class='{get_prob_color(pred['prob_draw'])}'>{pred['prob_draw']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**2:** <span class='{get_prob_color(pred['prob_away'])}'>{pred['prob_away']}%</span>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### ⚽ Goles")
                    st.markdown(f"**Local:** {pred['home_expected_goals']}")
                    st.markdown(f"**Visitante:** {pred['away_expected_goals']}")
                    st.markdown(f"**Resultado:** {pred['most_likely_score']}")
                
                with col3:
                    st.markdown("#### 📊 Over/Under 2.5")
                    st.markdown(f"**Over:** <span class='{get_prob_color(pred['prob_over_25'])}'>{pred['prob_over_25']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**Under:** <span class='{get_prob_color(pred['prob_under_25'])}'>{pred['prob_under_25']}%</span>", unsafe_allow_html=True)
                
                with col4:
                    st.markdown("#### 🎯 BTTS")
                    st.markdown(f"**Sí:** <span class='{get_prob_color(pred['prob_btts_yes'])}'>{pred['prob_btts_yes']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**No:** <span class='{get_prob_color(pred['prob_btts_no'])}'>{pred['prob_btts_no']}%</span>", unsafe_allow_html=True)
                
                # Expandir para más pronósticos
                with st.expander("📈 Ver más pronósticos"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**🔢 Doble Oportunidad**")
                        st.markdown(f"- 1X: <span class='{get_prob_color(pred['prob_1x'])}'>{pred['prob_1x']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- 12: <span class='{get_prob_color(pred['prob_12'])}'>{pred['prob_12']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- X2: <span class='{get_prob_color(pred['prob_x2'])}'>{pred['prob_x2']}%</span>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.markdown("**⚽ Gana y Anota**")
                        st.markdown(f"- Local: <span class='{get_prob_color(pred['prob_home_win_btts'])}'>{pred['prob_home_win_btts']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Visitante: <span class='{get_prob_color(pred['prob_away_win_btts'])}'>{pred['prob_away_win_btts']}%</span>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**📊 Over/Under 1.5**")
                        st.markdown(f"- Over: <span class='{get_prob_color(pred['prob_over_15'])}'>{pred['prob_over_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Under: <span class='{get_prob_color(pred['prob_under_15'])}'>{pred['prob_under_15']}%</span>", unsafe_allow_html=True)
                        
                        st.markdown("**📊 Over/Under 3.5**")
                        st.markdown(f"- Over: <span class='{get_prob_color(pred['prob_over_35'])}'>{pred['prob_over_35']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Under: <span class='{get_prob_color(pred['prob_under_35'])}'>{pred['prob_under_35']}%</span>", unsafe_allow_html=True)
                        
                        st.markdown("**📊 Over/Under 4.5**")
                        st.markdown(f"- Over: <span class='{get_prob_color(pred['prob_over_45'])}'>{pred['prob_over_45']}%</span>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("**🎲 Handicap Asiático**")
                        st.markdown(f"- Local -1.5: <span class='{get_prob_color(pred['prob_home_minus_15'])}'>{pred['prob_home_minus_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Local +1.5: <span class='{get_prob_color(pred['prob_home_plus_15'])}'>{pred['prob_home_plus_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Visitante +1.5: <span class='{get_prob_color(pred['prob_away_plus_15'])}'>{pred['prob_away_plus_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Visitante -1.5: <span class='{get_prob_color(pred['prob_away_minus_15'])}'>{pred['prob_away_minus_15']}%</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("**🎯 Top 5 Resultados Exactos**")
                    cols = st.columns(5)
                    for idx, score_data in enumerate(pred['top_scores']):
                        with cols[idx]:
                            st.markdown(f"**{score_data['score']}**")
                            st.markdown(f"<span class='{get_prob_color(score_data['prob'])}'>{score_data['prob']}%</span>", unsafe_allow_html=True)
                
                # Expandir para ver estadísticas
                with st.expander("📈 Ver estadísticas de equipos"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🏠 {pred['home_team']}**")
                        home_stats = pred['home_stats']
                        st.markdown(f"- Partidos jugados: {home_stats['matches_played']}")
                        st.markdown(f"- Goles anotados (promedio): {home_stats['goals_scored_avg']:.2f}")
                        st.markdown(f"- Goles recibidos (promedio): {home_stats['goals_conceded_avg']:.2f}")
                        st.markdown(f"- Como local (goles): {home_stats['home_goals_scored_avg']:.2f}")
                    
                    with col2:
                        st.markdown(f"**✈️ {pred['away_team']}**")
                        away_stats = pred['away_stats']
                        st.markdown(f"- Partidos jugados: {away_stats['matches_played']}")
                        st.markdown(f"- Goles anotados (promedio): {away_stats['goals_scored_avg']:.2f}")
                        st.markdown(f"- Goles recibidos (promedio): {away_stats['goals_conceded_avg']:.2f}")
                        st.markdown(f"- Como visitante (goles): {away_stats['away_goals_scored_avg']:.2f}")
                
                st.markdown("---")
        
        if count == 0:
            st.info("No hay partidos que cumplan con los filtros seleccionados.")
    
    elif view_mode == "📅 Pronósticos por Fecha":
        st.header("📅 Pronósticos por Fecha")
        
        # Recopilar todas las fechas
        all_dates = set()
        for df in league_data.values():
            upcoming = df.filter(pl.col("GA").is_null())
            dates = upcoming["Fecha"].unique().to_list()
            all_dates.update([d for d in dates if d])
        
        all_dates = sorted(list(all_dates))
        
        if not all_dates:
            st.warning("No hay fechas futuras disponibles.")
            return
        
        selected_date = st.sidebar.selectbox("Selecciona una fecha", all_dates)
        min_prob = st.sidebar.slider("Probabilidad mínima (%)", 0, 100, 40)
        
        st.subheader(f"🗓️ Partidos del {selected_date}")
        
        # Recopilar todos los partidos de esa fecha
        all_predictions = []
        
        for league_name, df in league_data.items():
            predictor = PoissonPredictor(df)
            upcoming = predictor.get_upcoming_matches()
            date_matches = upcoming.filter(pl.col("Fecha") == selected_date)
            
            for row in date_matches.iter_rows(named=True):
                home = row['Local']
                away = row['Visita']
                hora = row['Hora']
                
                prediction = predictor.predict_match(home, away)
                if prediction:
                    prediction['liga'] = league_name
                    prediction['hora'] = hora
                    all_predictions.append(prediction)
        
        # Ordenar por hora
        all_predictions.sort(key=lambda x: x['hora'] or '99:99')
        
        # Mostrar por liga
        for league_name in league_data.keys():
            league_preds = [p for p in all_predictions if p['liga'] == league_name]
            
            if not league_preds:
                continue
            
            st.markdown(f"### 🏆 {league_name}")
            
            for pred in league_preds:
                max_prob = max(pred['prob_home'], pred['prob_draw'], pred['prob_away'])
                
                if max_prob < min_prob:
                    continue
                
                with st.container():
                    st.markdown(f"""
                    <div class="match-card">
                        <h4>⏰ {pred['hora']}</h4>
                        <h3>{pred['home_team']} 🆚 {pred['away_team']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown("#### 🎲 1X2")
                        st.markdown(f"**1:** <span class='{get_prob_color(pred['prob_home'])}'>{pred['prob_home']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"**X:** <span class='{get_prob_color(pred['prob_draw'])}'>{pred['prob_draw']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"**2:** <span class='{get_prob_color(pred['prob_away'])}'>{pred['prob_away']}%</span>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("#### ⚽ Goles")
                        st.markdown(f"**Local:** {pred['home_expected_goals']}")
                        st.markdown(f"**Visitante:** {pred['away_expected_goals']}")
                        st.markdown(f"**Resultado:** {pred['most_likely_score']}")
                    
                    with col3:
                        st.markdown("#### 📊 Over/Under 2.5")
                        st.markdown(f"**Over:** <span class='{get_prob_color(pred['prob_over_25'])}'>{pred['prob_over_25']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"**Under:** <span class='{get_prob_color(pred['prob_under_25'])}'>{pred['prob_under_25']}%</span>", unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown("#### 🎯 BTTS")
                        st.markdown(f"**Sí:** <span class='{get_prob_color(pred['prob_btts_yes'])}'>{pred['prob_btts_yes']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"**No:** <span class='{get_prob_color(pred['prob_btts_no'])}'>{pred['prob_btts_no']}%</span>", unsafe_allow_html=True)
                    
                    # Más pronósticos
                    with st.expander("📈 Ver más pronósticos"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**🔢 Doble Oportunidad**")
                            st.markdown(f"- 1X: <span class='{get_prob_color(pred['prob_1x'])}'>{pred['prob_1x']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- 12: <span class='{get_prob_color(pred['prob_12'])}'>{pred['prob_12']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- X2: <span class='{get_prob_color(pred['prob_x2'])}'>{pred['prob_x2']}%</span>", unsafe_allow_html=True)
                            st.markdown("---")
                            st.markdown("**⚽ Gana y Anota**")
                            st.markdown(f"- Local: <span class='{get_prob_color(pred['prob_home_win_btts'])}'>{pred['prob_home_win_btts']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- Visitante: <span class='{get_prob_color(pred['prob_away_win_btts'])}'>{pred['prob_away_win_btts']}%</span>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**📊 Más Over/Under**")
                            st.markdown(f"- Over 1.5: <span class='{get_prob_color(pred['prob_over_15'])}'>{pred['prob_over_15']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- Under 1.5: <span class='{get_prob_color(pred['prob_under_15'])}'>{pred['prob_under_15']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- Over 3.5: <span class='{get_prob_color(pred['prob_over_35'])}'>{pred['prob_over_35']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- Under 3.5: <span class='{get_prob_color(pred['prob_under_35'])}'>{pred['prob_under_35']}%</span>", unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown("**🎲 Handicap Asiático**")
                            st.markdown(f"- Local -1.5: <span class='{get_prob_color(pred['prob_home_minus_15'])}'>{pred['prob_home_minus_15']}%</span>", unsafe_allow_html=True)
                            st.markdown(f"- Visitante +1.5: <span class='{get_prob_color(pred['prob_away_plus_15'])}'>{pred['prob_away_plus_15']}%</span>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.markdown("**🎯 Top 5 Resultados Exactos**")
                        cols = st.columns(5)
                        for idx, score_data in enumerate(pred['top_scores']):
                            with cols[idx]:
                                st.markdown(f"**{score_data['score']}**")
                                st.markdown(f"<span class='{get_prob_color(score_data['prob'])}'>{score_data['prob']}%</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
    
    elif view_mode == "🎯 Liga + Fecha":
        st.header("🎯 Pronósticos por Liga en Fecha Específica")
        
        # Selector de liga
        selected_league = st.sidebar.selectbox(
            "Selecciona una liga",
            list(league_data.keys())
        )
        
        df = league_data[selected_league]
        predictor = PoissonPredictor(df)
        upcoming = predictor.get_upcoming_matches()
        
        # Obtener fechas disponibles de esta liga
        available_dates = upcoming["Fecha"].unique().to_list()
        available_dates = sorted([d for d in available_dates if d])
        
        if not available_dates:
            st.warning(f"No hay fechas futuras disponibles para {selected_league}")
            return
        
        selected_date = st.sidebar.selectbox("Selecciona una fecha", available_dates)
        min_prob = st.sidebar.slider("Probabilidad mínima (%)", 0, 100, 40)
        
        st.subheader(f"🏆 {selected_league} - 📅 {selected_date}")
        
        # Estadísticas de la liga
        played = predictor.played_matches
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Partidos Jugados", len(played))
        with col2:
            st.metric("Por Jugar", len(upcoming))
        with col3:
            avg_goals = (played["GA"] + played["GC"]).mean() if len(played) > 0 else 0
            st.metric("Goles Promedio", f"{avg_goals:.2f}")
        with col4:
            date_matches = upcoming.filter(pl.col("Fecha") == selected_date)
            st.metric("Partidos en esta fecha", len(date_matches))
        
        st.markdown("---")
        
        # Filtrar partidos de la fecha seleccionada
        date_matches = upcoming.filter(pl.col("Fecha") == selected_date)
        
        # Procesar predicciones
        predictions = []
        for row in date_matches.iter_rows(named=True):
            home = row['Local']
            away = row['Visita']
            hora = row['Hora']
            jornada = row['Jornada']
            
            prediction = predictor.predict_match(home, away)
            if prediction:
                prediction['hora'] = hora
                prediction['jornada'] = jornada
                predictions.append(prediction)
        
        # Ordenar por hora
        predictions.sort(key=lambda x: x['hora'] or '99:99')
        
        if not predictions:
            st.info("No hay partidos con suficientes datos históricos para esta fecha.")
            return
        
        # Mostrar jornada si existe
        if predictions and predictions[0].get('jornada'):
            st.markdown(f"### 📋 {predictions[0]['jornada']}")
        
        # Resumen de mejores oportunidades
        st.markdown("### ⭐ Mejores Oportunidades del Día")
        
        best_predictions = []
        for pred in predictions:
            max_prob = max(pred['prob_home'], pred['prob_draw'], pred['prob_away'])
            pred['max_prob'] = max_prob
            pred['best_outcome'] = 'Local' if pred['prob_home'] == max_prob else ('Empate' if pred['prob_draw'] == max_prob else 'Visitante')
            if max_prob >= min_prob:
                best_predictions.append(pred)
        
        best_predictions.sort(key=lambda x: x['max_prob'], reverse=True)
        
        if best_predictions[:3]:
            col1, col2, col3 = st.columns(3)
            
            for idx, (col, pred) in enumerate(zip([col1, col2, col3], best_predictions[:3])):
                with col:
                    st.markdown(f"""
                    <div class="match-card" style="background: linear-gradient(135deg, #0f766e 0%, #115e59 100%);">
                        <h4>🥇 TOP {idx + 1}</h4>
                        <h5>{pred['home_team']} vs {pred['away_team']}</h5>
                        <p>⏰ {pred['hora']}</p>
                        <h3>{pred['best_outcome']}: {pred['max_prob']:.1f}%</h3>
                        <p>Resultado probable: {pred['most_likely_score']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🔮 Todos los Partidos")
        
        # Mostrar todas las predicciones
        count = 0
        for pred in predictions:
            if pred['max_prob'] < min_prob:
                continue
            
            count += 1
            
            with st.container():
                st.markdown(f"""
                <div class="match-card">
                    <h4>⏰ {pred['hora']}</h4>
                    <h3>{pred['home_team']} 🆚 {pred['away_team']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Información principal
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("#### 🎲 1X2")
                    st.markdown(f"**1:** <span class='{get_prob_color(pred['prob_home'])}'>{pred['prob_home']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**X:** <span class='{get_prob_color(pred['prob_draw'])}'>{pred['prob_draw']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**2:** <span class='{get_prob_color(pred['prob_away'])}'>{pred['prob_away']}%</span>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### ⚽ Goles")
                    st.markdown(f"**Local:** {pred['home_expected_goals']}")
                    st.markdown(f"**Visitante:** {pred['away_expected_goals']}")
                    st.markdown(f"**Resultado:** {pred['most_likely_score']}")
                
                with col3:
                    st.markdown("#### 📊 Over/Under")
                    st.markdown(f"**Over 2.5:** <span class='{get_prob_color(pred['prob_over_25'])}'>{pred['prob_over_25']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**Under 2.5:** <span class='{get_prob_color(pred['prob_under_25'])}'>{pred['prob_under_25']}%</span>", unsafe_allow_html=True)
                
                with col4:
                    st.markdown("#### 🎯 BTTS")
                    st.markdown(f"**Sí:** <span class='{get_prob_color(pred['prob_btts_yes'])}'>{pred['prob_btts_yes']}%</span>", unsafe_allow_html=True)
                    st.markdown(f"**No:** <span class='{get_prob_color(pred['prob_btts_no'])}'>{pred['prob_btts_no']}%</span>", unsafe_allow_html=True)
                
                # Más pronósticos
                with st.expander("📈 Ver más pronósticos"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**🔢 Doble Oportunidad**")
                        st.markdown(f"- 1X: <span class='{get_prob_color(pred['prob_1x'])}'>{pred['prob_1x']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- 12: <span class='{get_prob_color(pred['prob_12'])}'>{pred['prob_12']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- X2: <span class='{get_prob_color(pred['prob_x2'])}'>{pred['prob_x2']}%</span>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown("**⚽ Gana y Anota**")
                        st.markdown(f"- Local: <span class='{get_prob_color(pred['prob_home_win_btts'])}'>{pred['prob_home_win_btts']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Visitante: <span class='{get_prob_color(pred['prob_away_win_btts'])}'>{pred['prob_away_win_btts']}%</span>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("**📊 Más Over/Under**")
                        st.markdown(f"- Over 1.5: <span class='{get_prob_color(pred['prob_over_15'])}'>{pred['prob_over_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Under 1.5: <span class='{get_prob_color(pred['prob_under_15'])}'>{pred['prob_under_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Over 3.5: <span class='{get_prob_color(pred['prob_over_35'])}'>{pred['prob_over_35']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Under 3.5: <span class='{get_prob_color(pred['prob_under_35'])}'>{pred['prob_under_35']}%</span>", unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown("**🎲 Handicap Asiático**")
                        st.markdown(f"- Local -1.5: <span class='{get_prob_color(pred['prob_home_minus_15'])}'>{pred['prob_home_minus_15']}%</span>", unsafe_allow_html=True)
                        st.markdown(f"- Visitante +1.5: <span class='{get_prob_color(pred['prob_away_plus_15'])}'>{pred['prob_away_plus_15']}%</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown("**🎯 Top 5 Resultados Exactos**")
                    cols = st.columns(5)
                    for idx, score_data in enumerate(pred['top_scores']):
                        with cols[idx]:
                            st.markdown(f"**{score_data['score']}**")
                            st.markdown(f"<span class='{get_prob_color(score_data['prob'])}'>{score_data['prob']}%</span>", unsafe_allow_html=True)
                
                # Expandir para ver más detalles
                with st.expander("📊 Ver estadísticas de equipos"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**🏠 {pred['home_team']}**")
                        home_stats = pred['home_stats']
                        st.markdown(f"- Partidos jugados: {home_stats['matches_played']}")
                        st.markdown(f"- Goles anotados (promedio): {home_stats['goals_scored_avg']:.2f}")
                        st.markdown(f"- Goles recibidos (promedio): {home_stats['goals_conceded_avg']:.2f}")
                        st.markdown(f"- Como local (goles): {home_stats['home_goals_scored_avg']:.2f}")
                    
                    with col2:
                        st.markdown(f"**✈️ {pred['away_team']}**")
                        away_stats = pred['away_stats']
                        st.markdown(f"- Partidos jugados: {away_stats['matches_played']}")
                        st.markdown(f"- Goles anotados (promedio): {away_stats['goals_scored_avg']:.2f}")
                        st.markdown(f"- Goles recibidos (promedio): {away_stats['goals_conceded_avg']:.2f}")
                        st.markdown(f"- Como visitante (goles): {away_stats['away_goals_scored_avg']:.2f}")
                
                st.markdown("---")
        
        if count == 0:
            st.info("No hay partidos que cumplan con los filtros seleccionados.")
    
    elif view_mode == "📈 Estadísticas por Liga":
        st.header("📈 Estadísticas Detalladas por Liga")
        
        # Selector de liga
        selected_league = st.sidebar.selectbox(
            "Selecciona una liga",
            list(league_data.keys())
        )
        
        df = league_data[selected_league]
        predictor = PoissonPredictor(df)
        played = predictor.played_matches
        upcoming = predictor.get_upcoming_matches()
        
        st.markdown(f"## 🏆 {selected_league}")
        
        # Estadísticas generales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Partidos Jugados", len(played))
        with col2:
            st.metric("🔮 Por Jugar", len(upcoming))
        with col3:
            total = len(df)
            progress = (len(played) / total * 100) if total > 0 else 0
            st.metric("📈 Progreso", f"{progress:.1f}%")
        with col4:
            avg_goals = (played["GA"] + played["GC"]).mean() if len(played) > 0 else 0
            st.metric("⚽ Goles/Partido", f"{avg_goals:.2f}")
        with col5:
            league_avg = predictor.calculate_league_average()
            st.metric("🎯 Promedio Liga", f"{league_avg:.2f}")
        
        st.markdown("---")
        
        # Tabs para diferentes estadísticas
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Local/Visitante", "⚽ Goles", "📊 Mercados", "👥 Equipos"])
        
        with tab1:
            st.subheader("Análisis Local vs Visitante")
            
            home_matches = played.filter(pl.col("GA").is_not_null())
            
            if len(home_matches) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🏠 Equipos Locales")
                    home_wins = len(home_matches.filter(pl.col("GA") > pl.col("GC")))
                    home_draws = len(home_matches.filter(pl.col("GA") == pl.col("GC")))
                    home_losses = len(home_matches.filter(pl.col("GA") < pl.col("GC")))
                    
                    st.metric("Victorias", f"{home_wins} ({home_wins/len(home_matches)*100:.1f}%)")
                    st.metric("Empates", f"{home_draws} ({home_draws/len(home_matches)*100:.1f}%)")
                    st.metric("Derrotas", f"{home_losses} ({home_losses/len(home_matches)*100:.1f}%)")
                    
                    home_goals = home_matches["GA"].sum()
                    st.metric("Goles Anotados", f"{home_goals} ({home_goals/len(home_matches):.2f}/partido)")
                    
                    home_conceded = home_matches["GC"].sum()
                    st.metric("Goles Recibidos", f"{home_conceded} ({home_conceded/len(home_matches):.2f}/partido)")
                
                with col2:
                    st.markdown("### ✈️ Equipos Visitantes")
                    away_wins = len(home_matches.filter(pl.col("GC") > pl.col("GA")))
                    away_draws = home_draws
                    away_losses = home_wins
                    
                    st.metric("Victorias", f"{away_wins} ({away_wins/len(home_matches)*100:.1f}%)")
                    st.metric("Empates", f"{away_draws} ({away_draws/len(home_matches)*100:.1f}%)")
                    st.metric("Derrotas", f"{away_losses} ({away_losses/len(home_matches)*100:.1f}%)")
                    
                    away_goals = home_matches["GC"].sum()
                    st.metric("Goles Anotados", f"{away_goals} ({away_goals/len(home_matches):.2f}/partido)")
                    
                    away_conceded = home_matches["GA"].sum()
                    st.metric("Goles Recibidos", f"{away_conceded} ({away_conceded/len(home_matches):.2f}/partido)")
        
        with tab2:
            st.subheader("⚽ Estadísticas de Goles")
            
            if len(played) > 0:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 📊 Distribución Total")
                    total_goals = played["GA"] + played["GC"]
                    
                    goals_0 = len(played.filter(total_goals == 0))
                    goals_1 = len(played.filter(total_goals == 1))
                    goals_2 = len(played.filter(total_goals == 2))
                    goals_3 = len(played.filter(total_goals == 3))
                    goals_4 = len(played.filter(total_goals == 4))
                    goals_5plus = len(played.filter(total_goals >= 5))
                    
                    st.metric("0 goles", f"{goals_0} ({goals_0/len(played)*100:.1f}%)")
                    st.metric("1 gol", f"{goals_1} ({goals_1/len(played)*100:.1f}%)")
                    st.metric("2 goles", f"{goals_2} ({goals_2/len(played)*100:.1f}%)")
                    st.metric("3 goles", f"{goals_3} ({goals_3/len(played)*100:.1f}%)")
                    st.metric("4 goles", f"{goals_4} ({goals_4/len(played)*100:.1f}%)")
                    st.metric("5+ goles", f"{goals_5plus} ({goals_5plus/len(played)*100:.1f}%)")
                
                with col2:
                    st.markdown("### 📈 Over/Under")
                    
                    over_05 = len(played.filter(total_goals > 0.5))
                    over_15 = len(played.filter(total_goals > 1.5))
                    over_25 = len(played.filter(total_goals > 2.5))
                    over_35 = len(played.filter(total_goals > 3.5))
                    over_45 = len(played.filter(total_goals > 4.5))
                    
                    under_05 = len(played) - over_05
                    under_15 = len(played) - over_15
                    under_25 = len(played) - over_25
                    under_35 = len(played) - over_35
                    under_45 = len(played) - over_45
                    
                    st.metric("Over 0.5", f"{over_05} partidos ({over_05/len(played)*100:.1f}%)")
                    st.metric("Under 0.5", f"{under_05} partidos ({under_05/len(played)*100:.1f}%)")
                    st.markdown("---")
                    
                    st.metric("Over 1.5", f"{over_15} partidos ({over_15/len(played)*100:.1f}%)")
                    st.metric("Under 1.5", f"{under_15} partidos ({under_15/len(played)*100:.1f}%)")
                    st.markdown("---")
                    
                    st.metric("Over 2.5", f"{over_25} partidos ({over_25/len(played)*100:.1f}%)")
                    st.metric("Under 2.5", f"{under_25} partidos ({under_25/len(played)*100:.1f}%)")
                    st.markdown("---")
                    
                    st.metric("Over 3.5", f"{over_35} partidos ({over_35/len(played)*100:.1f}%)")
                    st.metric("Under 3.5", f"{under_35} partidos ({under_35/len(played)*100:.1f}%)")
                    st.markdown("---")
                    
                    st.metric("Over 4.5", f"{over_45} partidos ({over_45/len(played)*100:.1f}%)")
                    st.metric("Under 4.5", f"{under_45} partidos ({under_45/len(played)*100:.1f}%)")
                
                with col3:
                    st.markdown("### 🎯 BTTS & Clean Sheets")
                    
                    btts_yes = len(played.filter((pl.col("GA") > 0) & (pl.col("GC") > 0)))
                    btts_no = len(played) - btts_yes
                    
                    st.metric("BTTS Sí", f"{btts_yes} ({btts_yes/len(played)*100:.1f}%)")
                    st.metric("BTTS No", f"{btts_no} ({btts_no/len(played)*100:.1f}%)")
                    
                    home_cs = len(played.filter(pl.col("GC") == 0))
                    away_cs = len(played.filter(pl.col("GA") == 0))
                    
                    st.metric("Clean Sheets Local", f"{home_cs} ({home_cs/len(played)*100:.1f}%)")
                    st.metric("Clean Sheets Visitante", f"{away_cs} ({away_cs/len(played)*100:.1f}%)")
        
        with tab3:
            st.subheader("📊 Análisis de Mercados")
            
            if len(played) > 0:
                total_goals = played["GA"] + played["GC"]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🎲 Resultados 1X2")
                    
                    home_wins = len(played.filter(pl.col("GA") > pl.col("GC")))
                    draws = len(played.filter(pl.col("GA") == pl.col("GC")))
                    away_wins = len(played.filter(pl.col("GA") < pl.col("GC")))
                    
                    st.markdown(f"**Victoria Local (1):** {home_wins/len(played)*100:.1f}%")
                    st.progress(home_wins/len(played))
                    
                    st.markdown(f"**Empate (X):** {draws/len(played)*100:.1f}%")
                    st.progress(draws/len(played))
                    
                    st.markdown(f"**Victoria Visitante (2):** {away_wins/len(played)*100:.1f}%")
                    st.progress(away_wins/len(played))
                
                with col2:
                    st.markdown("### 📈 Tendencias de Mercado")
                    
                    # Doble Oportunidad
                    double_1x = home_wins + draws
                    double_12 = home_wins + away_wins
                    double_x2 = draws + away_wins
                    
                    st.markdown(f"**1X (Local o Empate):** {double_1x/len(played)*100:.1f}%")
                    st.markdown(f"**12 (Local o Visitante):** {double_12/len(played)*100:.1f}%")
                    st.markdown(f"**X2 (Empate o Visitante):** {double_x2/len(played)*100:.1f}%")
                    
                    st.markdown("---")
                    
                    # Combinaciones populares
                    over_25 = len(played.filter(total_goals > 2.5))
                    btts_yes = len(played.filter((pl.col("GA") > 0) & (pl.col("GC") > 0)))
                    
                    st.markdown(f"**Over 2.5 + BTTS:** {len(played.filter((total_goals > 2.5) & (pl.col('GA') > 0) & (pl.col('GC') > 0)))/len(played)*100:.1f}%")
                    st.markdown(f"**Under 2.5 + BTTS No:** {len(played.filter((total_goals < 2.5) & ((pl.col('GA') == 0) | (pl.col('GC') == 0))))/len(played)*100:.1f}%")
        
        with tab4:
            st.subheader("👥 Estadísticas por Equipo")
            
            # Obtener todos los equipos
            teams = set()
            for row in played.iter_rows(named=True):
                teams.add(row['Local'])
                teams.add(row['Visita'])
            
            teams = sorted(list(teams))
            
            selected_team = st.selectbox("Selecciona un equipo", teams)
            
            if selected_team:
                stats = predictor.calculate_team_stats(selected_team)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 📊 General")
                    st.metric("Partidos Jugados", stats['matches_played'])
                    st.metric("Goles Anotados (promedio)", f"{stats['goals_scored_avg']:.2f}")
                    st.metric("Goles Recibidos (promedio)", f"{stats['goals_conceded_avg']:.2f}")
                    
                    diff = stats['goals_scored_avg'] - stats['goals_conceded_avg']
                    st.metric("Diferencia de Goles", f"{diff:+.2f}")
                
                with col2:
                    st.markdown("### 🏠 Como Local")
                    team_home = played.filter(pl.col("Local") == selected_team)
                    
                    if len(team_home) > 0:
                        home_w = len(team_home.filter(pl.col("GA") > pl.col("GC")))
                        home_d = len(team_home.filter(pl.col("GA") == pl.col("GC")))
                        home_l = len(team_home.filter(pl.col("GA") < pl.col("GC")))
                        
                        st.metric("Partidos", len(team_home))
                        st.metric("V-E-D", f"{home_w}-{home_d}-{home_l}")
                        st.metric("Goles Anotados", f"{stats['home_goals_scored_avg']:.2f}")
                        st.metric("Goles Recibidos", f"{stats['home_goals_conceded_avg']:.2f}")
                
                with col3:
                    st.markdown("### ✈️ Como Visitante")
                    team_away = played.filter(pl.col("Visita") == selected_team)
                    
                    if len(team_away) > 0:
                        away_w = len(team_away.filter(pl.col("GC") > pl.col("GA")))
                        away_d = len(team_away.filter(pl.col("GA") == pl.col("GC")))
                        away_l = len(team_away.filter(pl.col("GC") < pl.col("GA")))
                        
                        st.metric("Partidos", len(team_away))
                        st.metric("V-E-D", f"{away_w}-{away_d}-{away_l}")
                        st.metric("Goles Anotados", f"{stats['away_goals_scored_avg']:.2f}")
                        st.metric("Goles Recibidos", f"{stats['away_goals_conceded_avg']:.2f}")
                
                st.markdown("---")
                
                # Últimos partidos
                st.markdown("### 📋 Últimos Partidos")
                
                team_matches = played.filter(
                    (pl.col("Local") == selected_team) | (pl.col("Visita") == selected_team)
                ).sort("Fecha", descending=True).head(10)
                
                for row in team_matches.iter_rows(named=True):
                    home = row['Local']
                    away = row['Visita']
                    score = f"{row['GA']}-{row['GC']}"
                    fecha = row['Fecha']
                    
                    if home == selected_team:
                        if row['GA'] > row['GC']:
                            result = "✅ Victoria"
                            color = "green"
                        elif row['GA'] == row['GC']:
                            result = "⚪ Empate"
                            color = "orange"
                        else:
                            result = "❌ Derrota"
                            color = "red"
                        match_info = f"{home} vs {away}"
                    else:
                        if row['GC'] > row['GA']:
                            result = "✅ Victoria"
                            color = "green"
                        elif row['GA'] == row['GC']:
                            result = "⚪ Empate"
                            color = "orange"
                        else:
                            result = "❌ Derrota"
                            color = "red"
                        match_info = f"{away} @ {home}"
                    
                    st.markdown(f"**{fecha}** - {match_info} - **{score}** - {result}")
                
                # Próximos partidos
                st.markdown("### 🔮 Próximos Partidos")
                
                team_upcoming = upcoming.filter(
                    (pl.col("Local") == selected_team) | (pl.col("Visita") == selected_team)
                ).sort("Fecha").head(5)
                
                if len(team_upcoming) > 0:
                    for row in team_upcoming.iter_rows(named=True):
                        home = row['Local']
                        away = row['Visita']
                        fecha = row['Fecha']
                        hora = row['Hora']
                        
                        location = "🏠" if home == selected_team else "✈️"
                        st.markdown(f"{location} **{fecha} {hora}** - {home} vs {away}")
                else:
                    st.info("No hay próximos partidos programados")
    
    elif view_mode == "🔍 Resultados vs Pronósticos":
        st.header("🔍 Comparación: Resultados Reales vs Pronósticos")
        st.markdown("### Análisis de partidos ya disputados")
        
        # Selector de liga
        selected_league = st.sidebar.selectbox(
            "Selecciona una liga",
            list(league_data.keys())
        )
        
        df = league_data[selected_league]
        predictor = PoissonPredictor(df)
        played = predictor.played_matches
        
        if len(played) == 0:
            st.warning("No hay partidos jugados en esta liga todavía.")
            return
        
        # Obtener fechas disponibles
        available_dates = played["Fecha"].unique().to_list()
        available_dates = sorted([d for d in available_dates if d], reverse=True)
        
        selected_date = st.sidebar.selectbox("Selecciona una fecha", available_dates)
        
        st.subheader(f"🏆 {selected_league} - 📅 {selected_date}")
        
        # Filtrar partidos de la fecha seleccionada
        date_matches = played.filter(pl.col("Fecha") == selected_date)
        
        if len(date_matches) == 0:
            st.info("No hay partidos en esta fecha.")
            return
        
        st.markdown(f"**Partidos disputados:** {len(date_matches)}")
        st.markdown("---")
        
        # Contadores de aciertos
        correct_1x2 = 0
        correct_over = 0
        correct_btts = 0
        total_analyzed = 0
        
        # Analizar cada partido
        for row in date_matches.iter_rows(named=True):
            home = row['Local']
            away = row['Visita']
            ga = row['GA']
            gc = row['GC']
            hora = row['Hora']
            
            # Calcular pronóstico
            prediction = predictor.predict_match(home, away)
            
            if not prediction:
                continue
            
            total_analyzed += 1
            
            # Resultado real
            if ga > gc:
                real_result = '1 (Local)'
                real_icon = "🏠"
            elif ga < gc:
                real_result = '2 (Visitante)'
                real_icon = "✈️"
            else:
                real_result = 'X (Empate)'
                real_icon = "🤝"
            
            # Predicción 1X2
            max_prob = max(prediction['prob_home'], prediction['prob_draw'], prediction['prob_away'])
            if prediction['prob_home'] == max_prob:
                predicted_result = '1 (Local)'
                predicted_icon = "🏠"
            elif prediction['prob_draw'] == max_prob:
                predicted_result = 'X (Empate)'
                predicted_icon = "🤝"
            else:
                predicted_result = '2 (Visitante)'
                predicted_icon = "✈️"
            
            result_correct = predicted_result == real_result
            if result_correct:
                correct_1x2 += 1
            
            # Over/Under 2.5
            total_goals = ga + gc
            predicted_over = prediction['prob_over_25'] > prediction['prob_under_25']
            real_over = total_goals > 2.5
            over_correct = predicted_over == real_over
            if over_correct:
                correct_over += 1
            
            # BTTS
            predicted_btts = prediction['prob_btts_yes'] > prediction['prob_btts_no']
            real_btts = ga > 0 and gc > 0
            btts_correct = predicted_btts == real_btts
            if btts_correct:
                correct_btts += 1
            
            # Mostrar partido
            with st.container():
                st.markdown(f"""
                <div class="match-card">
                    <h4>⏰ {hora if hora else 'N/A'}</h4>
                    <h3>{home} {ga} - {gc} {away}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("#### 🎲 Resultado 1X2")
                    st.markdown(f"**Real:** {real_icon} {real_result}")
                    st.markdown(f"**Pronóstico:** {predicted_icon} {predicted_result}")
                    if result_correct:
                        st.success("✅ ACIERTO")
                    else:
                        st.error("❌ FALLO")
                    st.markdown(f"**Probabilidades:**")
                    st.markdown(f"- Local: {prediction['prob_home']}%")
                    st.markdown(f"- Empate: {prediction['prob_draw']}%")
                    st.markdown(f"- Visitante: {prediction['prob_away']}%")
                
                with col2:
                    st.markdown("#### ⚽ Goles Esperados")
                    st.markdown(f"**Real:** {total_goals} goles")
                    st.markdown(f"**Pronóstico:**")
                    st.markdown(f"- Local: {prediction['home_expected_goals']}")
                    st.markdown(f"- Visitante: {prediction['away_expected_goals']}")
                    st.markdown(f"- Total: {prediction['home_expected_goals'] + prediction['away_expected_goals']:.2f}")
                    st.markdown(f"**Marcador probable:** {prediction['most_likely_score']}")
                
                with col3:
                    st.markdown("#### 📊 Over/Under 2.5")
                    real_ou = "Over" if real_over else "Under"
                    pred_ou = "Over" if predicted_over else "Under"
                    st.markdown(f"**Real:** {real_ou} 2.5")
                    st.markdown(f"**Pronóstico:** {pred_ou} 2.5")
                    if over_correct:
                        st.success("✅ ACIERTO")
                    else:
                        st.error("❌ FALLO")
                    st.markdown(f"**Probabilidades:**")
                    st.markdown(f"- Over: {prediction['prob_over_25']}%")
                    st.markdown(f"- Under: {prediction['prob_under_25']}%")
                
                with col4:
                    st.markdown("#### 🎯 BTTS")
                    real_btts_text = "Sí" if real_btts else "No"
                    pred_btts_text = "Sí" if predicted_btts else "No"
                    st.markdown(f"**Real:** {real_btts_text}")
                    st.markdown(f"**Pronóstico:** {pred_btts_text}")
                    if btts_correct:
                        st.success("✅ ACIERTO")
                    else:
                        st.error("❌ FALLO")
                    st.markdown(f"**Probabilidades:**")
                    st.markdown(f"- Sí: {prediction['prob_btts_yes']}%")
                    st.markdown(f"- No: {prediction['prob_btts_no']}%")
                
                st.markdown("---")
        
        # Resumen de aciertos
        if total_analyzed > 0:
            st.markdown("---")
            st.markdown("### 📊 Resumen de Aciertos en esta Fecha")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Partidos Analizados", total_analyzed)
            
            with col2:
                accuracy_1x2 = (correct_1x2 / total_analyzed * 100) if total_analyzed > 0 else 0
                st.metric("Aciertos 1X2", f"{correct_1x2}/{total_analyzed}", f"{accuracy_1x2:.1f}%")
            
            with col3:
                accuracy_over = (correct_over / total_analyzed * 100) if total_analyzed > 0 else 0
                st.metric("Aciertos Over/Under", f"{correct_over}/{total_analyzed}", f"{accuracy_over:.1f}%")
            
            with col4:
                accuracy_btts = (correct_btts / total_analyzed * 100) if total_analyzed > 0 else 0
                st.metric("Aciertos BTTS", f"{correct_btts}/{total_analyzed}", f"{accuracy_btts:.1f}%")
    
    elif view_mode == "📊 Precisión del Modelo":
        st.header("📊 Precisión del Modelo Poisson")
        st.markdown("### Tasa de aciertos en predicciones de partidos ya jugados")
        
        # Calcular precisión para todas las ligas
        accuracy_data = []
        
        for league_name, df in league_data.items():
            predictor = PoissonPredictor(df)
            accuracy = predictor.calculate_accuracy()
            
            if accuracy:
                accuracy_data.append({
                    'Liga': league_name,
                    '1X2': accuracy['accuracy_1x2'],
                    'Over 2.5': accuracy['accuracy_over_25'],
                    'BTTS': accuracy['accuracy_btts'],
                    'Doble Oportunidad': accuracy['accuracy_double_chance'],
                    'Predicciones': accuracy['total_predictions']
                })
        
        if accuracy_data:
            # Mostrar tabla comparativa
            st.markdown("### 📈 Comparativa por Liga")
            
            # Crear DataFrame para mostrar
            import pandas as pd
            df_accuracy = pd.DataFrame(accuracy_data)
            
            # Estilo para la tabla
            st.dataframe(
                df_accuracy.style.highlight_max(axis=0, subset=['1X2', 'Over 2.5', 'BTTS', 'Doble Oportunidad'], color='lightgreen'),
                use_container_width=True
            )
            
            # Métricas generales
            st.markdown("---")
            st.markdown("### 🎯 Promedio General")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                avg_1x2 = sum([d['1X2'] for d in accuracy_data]) / len(accuracy_data)
                st.metric("1X2", f"{avg_1x2:.2f}%")
            
            with col2:
                avg_over = sum([d['Over 2.5'] for d in accuracy_data]) / len(accuracy_data)
                st.metric("Over 2.5", f"{avg_over:.2f}%")
            
            with col3:
                avg_btts = sum([d['BTTS'] for d in accuracy_data]) / len(accuracy_data)
                st.metric("BTTS", f"{avg_btts:.2f}%")
            
            with col4:
                avg_dc = sum([d['Doble Oportunidad'] for d in accuracy_data]) / len(accuracy_data)
                st.metric("Doble Oportunidad", f"{avg_dc:.2f}%")
            
            with col5:
                total_pred = sum([d['Predicciones'] for d in accuracy_data])
                st.metric("Total Predicciones", total_pred)
            
            # Gráfico de barras por liga
            st.markdown("---")
            st.markdown("### 📊 Precisión por Liga y Mercado")
            
            # Seleccionar mercado para visualizar
            market = st.selectbox(
                "Selecciona el mercado",
                ["1X2", "Over 2.5", "BTTS", "Doble Oportunidad"]
            )
            
            # Crear gráfico de barras simple con st.bar_chart
            chart_data = pd.DataFrame({
                'Liga': [d['Liga'] for d in accuracy_data],
                'Precisión (%)': [d[market] for d in accuracy_data]
            })
            chart_data = chart_data.set_index('Liga')
            
            st.bar_chart(chart_data)
            
            # Mejor y peor liga por mercado
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏆 Mejor Liga por Mercado")
                for market in ["1X2", "Over 2.5", "BTTS", "Doble Oportunidad"]:
                    best = max(accuracy_data, key=lambda x: x[market])
                    st.markdown(f"**{market}:** {best['Liga']} ({best[market]:.2f}%)")
            
            with col2:
                st.markdown("### 📉 Liga con Menor Precisión")
                for market in ["1X2", "Over 2.5", "BTTS", "Doble Oportunidad"]:
                    worst = min(accuracy_data, key=lambda x: x[market])
                    st.markdown(f"**{market}:** {worst['Liga']} ({worst[market]:.2f}%)")
            
            # Información adicional
            st.markdown("---")
            st.info("""
            ℹ️ **Nota sobre la precisión:**
            - Los porcentajes se calculan comparando las predicciones del modelo con los resultados reales de partidos ya jugados.
            - Solo se consideran partidos donde ambos equipos tienen al menos 3 partidos previos para hacer predicciones confiables.
            - Una precisión alta indica que el modelo está prediciendo correctamente los resultados basándose en las estadísticas históricas.
            - La **Doble Oportunidad** generalmente tiene mayor precisión porque cubre dos de tres resultados posibles.
            """)
        else:
            st.warning("No hay suficientes datos para calcular la precisión del modelo.")

if __name__ == "__main__":
    main()
