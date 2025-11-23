import polars as pl
from extract_calendar import CalendarExtractor, StatisticsCalculator
from datetime import datetime


def calculate_odds_comparison(df, stats):
    """
    Extrae y calcula las cuotas calculadas vs mercado para todos los partidos próximos.
    
    Returns:
        DataFrame con todas las comparaciones de cuotas
    """
    
    # Obtener partidos próximos
    upcoming_matches = stats.get_upcoming_matches()
    
    if len(upcoming_matches) == 0:
        print("No hay partidos próximos disponibles")
        return None
    
    # Lista para almacenar todos los datos
    all_odds_data = []
    
    # Procesar cada partido
    for i in range(len(upcoming_matches)):
        match = upcoming_matches[i]
        home_team = match["Local"][0]
        away_team = match["Visita"][0]
        match_date = match["Fecha"][0]
        match_time = match["Hora"][0]
        match_round = match["Jornada"][0]
        
        # Calcular estadísticas de los equipos
        h_win_pct = stats.team_home_percentage_wins(home_team)
        h_draw_pct = stats.team_home_percentage_draws(home_team)
        a_win_pct = stats.team_away_percentage_wins(away_team)
        a_draw_pct = stats.team_away_percentage_draws(away_team)
        
        # Calcular probabilidades 1X2
        pred_home_win = h_win_pct
        pred_draw = (h_draw_pct + a_draw_pct) / 2
        pred_away_win = a_win_pct
        
        # Normalizar para que sumen 100%
        total_1x2 = pred_home_win + pred_draw + pred_away_win
        if total_1x2 > 0:
            pred_home_win = (pred_home_win / total_1x2) * 100
            pred_draw = (pred_draw / total_1x2) * 100
            pred_away_win = (pred_away_win / total_1x2) * 100
        
        # Calcular cuotas 1X2
        odd_home_win = 100 / pred_home_win if pred_home_win > 0 else 0
        odd_draw = 100 / pred_draw if pred_draw > 0 else 0
        odd_away_win = 100 / pred_away_win if pred_away_win > 0 else 0
        
        # Calcular probabilidades de doble oportunidad
        pred_1x = pred_home_win + pred_draw
        pred_x2 = pred_draw + pred_away_win
        pred_12 = pred_home_win + pred_away_win
        
        # Calcular cuotas de doble oportunidad
        odd_1x = 100 / pred_1x if pred_1x > 0 else 0
        odd_x2 = 100 / pred_x2 if pred_x2 > 0 else 0
        odd_12 = 100 / pred_12 if pred_12 > 0 else 0
        
        # Calcular estadísticas de goles
        h_avg = stats.team_home_average_goals(home_team)
        a_avg = stats.team_away_average_goals(away_team)
        h_over_15 = stats.team_home_percentage_over_goals(home_team, 1)
        a_over_15 = stats.team_away_percentage_over_goals(away_team, 1)
        h_over_25 = stats.team_home_percentage_over_goals(home_team, 2)
        a_over_25 = stats.team_away_percentage_over_goals(away_team, 2)
        h_over_35 = stats.team_home_percentage_over_goals(home_team, 3)
        a_over_35 = stats.team_away_percentage_over_goals(away_team, 3)
        h_btts = stats.team_home_percentage_btts(home_team)
        a_btts = stats.team_away_percentage_btts(away_team)
        
        pred_avg_goals = (h_avg + a_avg) / 2
        pred_over_15 = (h_over_15 + a_over_15) / 2
        pred_over_25 = (h_over_25 + a_over_25) / 2
        pred_over_35 = (h_over_35 + a_over_35) / 2
        pred_under_35 = 100 - pred_over_35
        pred_btts = (h_btts + a_btts) / 2
        
        # Calcular cuotas de goles
        odd_over_15 = 100 / pred_over_15 if pred_over_15 > 0 else 0
        odd_over_25 = 100 / pred_over_25 if pred_over_25 > 0 else 0
        odd_under_35 = 100 / pred_under_35 if pred_under_35 > 0 else 0
        odd_btts = 100 / pred_btts if pred_btts > 0 else 0
        
        # Calcular probabilidades y cuotas combinadas
        prob_home_over25 = (pred_home_win / 100) * (pred_over_25 / 100) * 100
        prob_home_under25 = (pred_home_win / 100) * ((100 - pred_over_25) / 100) * 100
        prob_away_over25 = (pred_away_win / 100) * (pred_over_25 / 100) * 100
        prob_away_under25 = (pred_away_win / 100) * ((100 - pred_over_25) / 100) * 100
        prob_draw_over25 = (pred_draw / 100) * (pred_over_25 / 100) * 100
        prob_draw_under25 = (pred_draw / 100) * ((100 - pred_over_25) / 100) * 100
        
        odd_home_over25 = 100 / prob_home_over25 if prob_home_over25 > 0 else 0
        odd_home_under25 = 100 / prob_home_under25 if prob_home_under25 > 0 else 0
        odd_away_over25 = 100 / prob_away_over25 if prob_away_over25 > 0 else 0
        odd_away_under25 = 100 / prob_away_under25 if prob_away_under25 > 0 else 0
        odd_draw_over25 = 100 / prob_draw_over25 if prob_draw_over25 > 0 else 0
        odd_draw_under25 = 100 / prob_draw_under25 if prob_draw_under25 > 0 else 0
        
        # Determinar valor vs mercado (rangos típicos)
        # Mercado 1X2: Victoria Local/Visitante: 1.50-3.50, Empate: 2.80-4.50
        valor_home = "VALOR" if odd_home_win > 3.50 else "REVISAR" if odd_home_win > 2.50 else "NO"
        valor_draw = "VALOR" if odd_draw > 4.50 else "REVISAR" if odd_draw > 3.65 else "NO"
        valor_away = "VALOR" if odd_away_win > 3.50 else "REVISAR" if odd_away_win > 2.50 else "NO"
        
        # Doble Oportunidad: 1X/X2: 1.10-1.50, 12: 1.15-1.40
        valor_1x = "VALOR" if odd_1x > 1.50 else "REVISAR" if odd_1x > 1.30 else "NO"
        valor_x2 = "VALOR" if odd_x2 > 1.50 else "REVISAR" if odd_x2 > 1.30 else "NO"
        valor_12 = "VALOR" if odd_12 > 1.40 else "REVISAR" if odd_12 > 1.27 else "NO"
        
        # Crear registro para este partido
        match_data = {
            "Jornada": match_round,
            "Fecha": match_date,
            "Hora": match_time,
            "Local": home_team,
            "Visitante": away_team,
            
            # Probabilidades 1X2
            "Prob_Victoria_Local_%": round(pred_home_win, 2),
            "Prob_Empate_%": round(pred_draw, 2),
            "Prob_Victoria_Visitante_%": round(pred_away_win, 2),
            
            # Cuotas 1X2
            "Cuota_Victoria_Local": round(odd_home_win, 2),
            "Cuota_Empate": round(odd_draw, 2),
            "Cuota_Victoria_Visitante": round(odd_away_win, 2),
            
            # Valor 1X2
            "Valor_Victoria_Local": valor_home,
            "Valor_Empate": valor_draw,
            "Valor_Victoria_Visitante": valor_away,
            
            # Mercado típico 1X2
            "Mercado_Victoria_Local": "1.50-3.50",
            "Mercado_Empate": "2.80-4.50",
            "Mercado_Victoria_Visitante": "1.50-3.50",
            
            # Probabilidades Doble Oportunidad
            "Prob_1X_%": round(pred_1x, 2),
            "Prob_X2_%": round(pred_x2, 2),
            "Prob_12_%": round(pred_12, 2),
            
            # Cuotas Doble Oportunidad
            "Cuota_1X": round(odd_1x, 2),
            "Cuota_X2": round(odd_x2, 2),
            "Cuota_12": round(odd_12, 2),
            
            # Valor Doble Oportunidad
            "Valor_1X": valor_1x,
            "Valor_X2": valor_x2,
            "Valor_12": valor_12,
            
            # Mercado típico Doble Oportunidad
            "Mercado_1X": "1.10-1.50",
            "Mercado_X2": "1.10-1.50",
            "Mercado_12": "1.15-1.40",
            
            # Estadísticas de Goles
            "Goles_Esperados": round(pred_avg_goals, 2),
            "Prob_Over_1.5_%": round(pred_over_15, 2),
            "Prob_Over_2.5_%": round(pred_over_25, 2),
            "Prob_Under_3.5_%": round(pred_under_35, 2),
            "Prob_BTTS_%": round(pred_btts, 2),
            
            # Cuotas de Goles
            "Cuota_Over_1.5": round(odd_over_15, 2),
            "Cuota_Over_2.5": round(odd_over_25, 2),
            "Cuota_Under_3.5": round(odd_under_35, 2),
            "Cuota_BTTS": round(odd_btts, 2),
            
            # Mercados Combinados - Probabilidades
            "Prob_Local_Over2.5_%": round(prob_home_over25, 2),
            "Prob_Local_Under2.5_%": round(prob_home_under25, 2),
            "Prob_Empate_Over2.5_%": round(prob_draw_over25, 2),
            "Prob_Empate_Under2.5_%": round(prob_draw_under25, 2),
            "Prob_Visitante_Over2.5_%": round(prob_away_over25, 2),
            "Prob_Visitante_Under2.5_%": round(prob_away_under25, 2),
            
            # Mercados Combinados - Cuotas
            "Cuota_Local_Over2.5": round(odd_home_over25, 2),
            "Cuota_Local_Under2.5": round(odd_home_under25, 2),
            "Cuota_Empate_Over2.5": round(odd_draw_over25, 2),
            "Cuota_Empate_Under2.5": round(odd_draw_under25, 2),
            "Cuota_Visitante_Over2.5": round(odd_away_over25, 2),
            "Cuota_Visitante_Under2.5": round(odd_away_under25, 2),
        }
        
        all_odds_data.append(match_data)
    
    # Crear DataFrame con Polars
    odds_df = pl.DataFrame(all_odds_data)
    
    return odds_df


def main():
    """
    Función principal para extraer cuotas calculadas vs mercado
    """
    print("=" * 80)
    print("EXTRACTOR DE CUOTAS CALCULADAS VS MERCADO")
    print("=" * 80)
    print()
    
    # Ligas disponibles (puedes modificar esta lista)
    ligas = {
        "1": ("🇩🇪 Alemania - Bundesliga", "https://www.livefutbol.com/competition/co12/alemania-bundesliga/all-matches/"),
        "2": ("🇩🇪 Alemania - 2. Bundesliga", "https://www.livefutbol.com/competition/co3/alemania-2-bundesliga/all-matches/"),
        "3": ("🇪🇸 España - La Liga", "https://www.livefutbol.com/competition/co97/espana-primera-division/all-matches/"),
        "4": ("🇬🇧 Inglaterra - Premier League", "https://www.livefutbol.com/competition/co91/inglaterra-premier-league/all-matches/"),
        "5": ("🇮🇹 Italia - Serie A", "https://www.livefutbol.com/competition/co111/italia-serie-a/all-matches/"),
        "6": ("🇫🇷 Francia - Ligue 1", "https://www.livefutbol.com/competition/co71/francia-ligue-1/all-matches/"),
    }
    
    # Mostrar opciones
    print("Selecciona una liga:")
    for key, (name, _) in ligas.items():
        print(f"{key}. {name}")
    print()
    
    # Seleccionar liga
    choice = input("Ingresa el número de la liga (o presiona Enter para Bundesliga): ").strip()
    if not choice:
        choice = "1"
    
    if choice not in ligas:
        print(f"❌ Opción inválida. Usando Bundesliga por defecto.")
        choice = "1"
    
    liga_name, liga_url = ligas[choice]
    print(f"\n✅ Liga seleccionada: {liga_name}")
    print(f"🔗 URL: {liga_url}")
    print()
    
    # Extraer datos
    print("📥 Cargando datos de la liga...")
    extractor = CalendarExtractor(liga_url)
    extractor.fetch_and_parse()
    df = extractor.get_dataframe()
    print(f"✅ Datos cargados: {len(df)} partidos encontrados")
    print()
    
    # Calcular estadísticas
    print("📊 Calculando estadísticas...")
    stats = StatisticsCalculator(df)
    
    # Extraer cuotas
    print("💰 Extrayendo cuotas calculadas vs mercado...")
    odds_df = calculate_odds_comparison(df, stats)
    
    if odds_df is None or len(odds_df) == 0:
        print("❌ No se encontraron partidos próximos para analizar")
        return
    
    print(f"✅ Se analizaron {len(odds_df)} partidos próximos")
    print()
    
    # Guardar en CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    liga_slug = liga_name.split("-")[0].strip().replace(" ", "_").replace("🇩🇪", "").replace("🇪🇸", "").replace("🇬🇧", "").replace("🇮🇹", "").replace("🇫🇷", "").strip()
    
    csv_filename = f"cuotas_calculadas_{liga_slug}_{timestamp}.csv"
    excel_filename = f"cuotas_calculadas_{liga_slug}_{timestamp}.xlsx"
    
    # Guardar CSV
    odds_df.write_csv(csv_filename)
    print(f"✅ Datos guardados en CSV: {csv_filename}")
    
    # Intentar guardar en Excel (requiere openpyxl o xlsxwriter)
    try:
        odds_df.write_excel(excel_filename)
        print(f"✅ Datos guardados en Excel: {excel_filename}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar en Excel: {e}")
        print("   Instala 'openpyxl' o 'xlsxwriter' para exportar a Excel")
    
    print()
    print("=" * 80)
    print("RESUMEN DE COLUMNAS EXPORTADAS:")
    print("=" * 80)
    print("""
    📋 INFORMACIÓN DEL PARTIDO:
    - Jornada, Fecha, Hora, Local, Visitante
    
    ⚽ MERCADO 1X2:
    - Probabilidades: Prob_Victoria_Local_%, Prob_Empate_%, Prob_Victoria_Visitante_%
    - Cuotas Calculadas: Cuota_Victoria_Local, Cuota_Empate, Cuota_Victoria_Visitante
    - Análisis de Valor: Valor_Victoria_Local, Valor_Empate, Valor_Victoria_Visitante
    - Mercado Típico: Mercado_Victoria_Local, Mercado_Empate, Mercado_Victoria_Visitante
    
    🎲 DOBLE OPORTUNIDAD:
    - Probabilidades: Prob_1X_%, Prob_X2_%, Prob_12_%
    - Cuotas Calculadas: Cuota_1X, Cuota_X2, Cuota_12
    - Análisis de Valor: Valor_1X, Valor_X2, Valor_12
    - Mercado Típico: Mercado_1X, Mercado_X2, Mercado_12
    
    🎯 MERCADOS DE GOLES:
    - Goles Esperados
    - Probabilidades: Prob_Over_1.5_%, Prob_Over_2.5_%, Prob_Under_3.5_%, Prob_BTTS_%
    - Cuotas: Cuota_Over_1.5, Cuota_Over_2.5, Cuota_Under_3.5, Cuota_BTTS
    
    🔥 MERCADOS COMBINADOS (Resultado + Goles):
    - Probabilidades: Prob_Local_Over2.5_%, Prob_Local_Under2.5_%, etc.
    - Cuotas: Cuota_Local_Over2.5, Cuota_Local_Under2.5, etc.
    
    📊 ANÁLISIS DE VALOR:
    - VALOR = Cuota calculada superior al mercado típico (oportunidad)
    - REVISAR = Cuota en rango medio (analizar más)
    - NO = Cuota inferior al mercado (sin valor)
    """)
    print("=" * 80)
    print()
    print("✅ ¡Extracción completada exitosamente!")
    print()


if __name__ == "__main__":
    main()
