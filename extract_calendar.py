import requests
from bs4 import BeautifulSoup
import polars as pl
from datetime import datetime

class CalendarExtractor:
    def __init__(self, url):
        self.url = url
        self.data = []

    def fetch_and_parse(self):
        print(f"Fetching {self.url}...")
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to fetch URL: {response.status_code}")
            return

        soup = BeautifulSoup(response.content, 'html.parser')
        
        container = soup.find('div', class_='module-gameplan')
        if not container:
            print("Could not find module-gameplan container")
            return

        wrapper = container.find('div', recursive=False)
        if not wrapper:
            print("Could not find wrapper div")
            return

        current_round = None
        
        for child in wrapper.find_all(recursive=False):
            classes = child.get('class', [])
            
            if 'round-head' in classes:
                current_round = child.get_text(strip=True)
                
            elif 'match' in classes:
                self._process_match(child, current_round)

    def _process_match(self, child, current_round):
        datetime_str = child.get('data-datetime')
        date_val = None
        time_val = None
        
        if datetime_str:
            try:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                date_val = dt.strftime('%Y-%m-%d')
                time_val = dt.strftime('%H:%M')
            except ValueError:
                pass
        
        if not time_val:
            time_div = child.find('div', class_='match-time')
            if time_div:
                time_val = time_div.get_text(strip=True)

        home_div = child.find('div', class_='team-name-home')
        away_div = child.find('div', class_='team-name-away')
        
        home_team = home_div.get_text(strip=True) if home_div else "Unknown"
        away_team = away_div.get_text(strip=True) if away_div else "Unknown"
        
        result_div = child.find('div', class_='match-result')
        score_text = result_div.get_text(strip=True) if result_div else None
        
        home_goals = None
        away_goals = None

        if score_text and ":" in score_text and score_text != "-:-":
            try:
                parts = score_text.split(":")
                if len(parts) == 2:
                    home_goals = int(parts[0])
                    away_goals = int(parts[1])
            except ValueError:
                pass

        self.data.append({
            "Jornada": current_round,
            "Fecha": date_val,
            "Hora": time_val,
            "Local": home_team,
            "Visita": away_team,
            "GA": home_goals,
            "GC": away_goals
        })

    def get_dataframe(self):
        if not self.data:
            return pl.DataFrame()
        return pl.DataFrame(self.data)

    def save_to_csv(self, output_file="calendario_liga.csv"):
        df = self.get_dataframe()
        if df.is_empty():
            print("No match data found.")
            return

        print(f"Extracted {len(df)} matches.")
        print(df.head())
        
        df.write_csv(output_file)
        print(f"Saved to {output_file}")

    def run(self):
        self.fetch_and_parse()
        self.save_to_csv()

class StatisticsCalculator:
    def __init__(self, df):
        self.df = df

    def count_played_matches(self):
        played = self.df.filter(pl.col("GA").is_not_null())
        return len(played)

    def count_upcoming_matches(self):
        upcoming = self.df.filter(pl.col("GA").is_null())
        return len(upcoming)

    def percentage_played(self):
        total = len(self.df)
        if total == 0:
            return 0.0
        played = self.count_played_matches()
        return (played / total) * 100

    def average_goals_per_match(self):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        if len(played_matches) == 0:
            return 0.0
        total_goals = (played_matches["GA"] + played_matches["GC"]).sum()
        return total_goals / len(played_matches)

    def percentage_over_goals(self, threshold=0):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        if len(played_matches) == 0:
            return 0.0
        total_goals = played_matches["GA"] + played_matches["GC"]
        matches_over = played_matches.filter(total_goals > threshold)
        return (len(matches_over) / len(played_matches)) * 100

    def percentage_under_goals(self, threshold=5):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        if len(played_matches) == 0:
            return 0.0
        total_goals = played_matches["GA"] + played_matches["GC"]
        matches_under = played_matches.filter(total_goals < threshold)
        return (len(matches_under) / len(played_matches)) * 100

    def percentage_exact_goals(self, exact=0):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        if len(played_matches) == 0:
            return 0.0
        total_goals = played_matches["GA"] + played_matches["GC"]
        matches_exact = played_matches.filter(total_goals == exact)
        return (len(matches_exact) / len(played_matches)) * 100

    def percentage_both_teams_score(self):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        if len(played_matches) == 0:
            return 0.0
        both_score = played_matches.filter((pl.col("GA") > 0) & (pl.col("GC") > 0))
        return (len(both_score) / len(played_matches)) * 100

    def get_team_matches(self, team_name):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        team_matches = played_matches.filter(
            (pl.col("Local").str.contains(team_name)) | 
            (pl.col("Visita").str.contains(team_name))
        )
        return team_matches

    def team_count_matches(self, team_name):
        team_matches = self.get_team_matches(team_name)
        return len(team_matches)

    def team_average_goals(self, team_name):
        team_matches = self.get_team_matches(team_name)
        if len(team_matches) == 0:
            return 0.0
        total_goals = (team_matches["GA"] + team_matches["GC"]).sum()
        return total_goals / len(team_matches)

    def team_percentage_over_goals(self, team_name, threshold=0):
        team_matches = self.get_team_matches(team_name)
        if len(team_matches) == 0:
            return 0.0
        total_goals = team_matches["GA"] + team_matches["GC"]
        matches_over = team_matches.filter(total_goals > threshold)
        return (len(matches_over) / len(team_matches)) * 100

    def team_percentage_under_goals(self, team_name, threshold=5):
        team_matches = self.get_team_matches(team_name)
        if len(team_matches) == 0:
            return 0.0
        total_goals = team_matches["GA"] + team_matches["GC"]
        matches_under = team_matches.filter(total_goals < threshold)
        return (len(matches_under) / len(team_matches)) * 100

    def team_percentage_btts(self, team_name):
        team_matches = self.get_team_matches(team_name)
        if len(team_matches) == 0:
            return 0.0
        both_score = team_matches.filter((pl.col("GA") > 0) & (pl.col("GC") > 0))
        return (len(both_score) / len(team_matches)) * 100

    def get_all_teams(self):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        home_teams = played_matches["Local"].unique().to_list()
        away_teams = played_matches["Visita"].unique().to_list()
        all_teams = sorted(list(set(home_teams + away_teams)))
        return all_teams

    def get_team_home_matches(self, team_name):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        home_matches = played_matches.filter(pl.col("Local").str.contains(team_name))
        return home_matches

    def get_team_away_matches(self, team_name):
        played_matches = self.df.filter(pl.col("GA").is_not_null())
        away_matches = played_matches.filter(pl.col("Visita").str.contains(team_name))
        return away_matches

    def team_home_count_matches(self, team_name):
        return len(self.get_team_home_matches(team_name))

    def team_away_count_matches(self, team_name):
        return len(self.get_team_away_matches(team_name))

    def team_home_average_goals(self, team_name):
        home_matches = self.get_team_home_matches(team_name)
        if len(home_matches) == 0:
            return 0.0
        total_goals = (home_matches["GA"] + home_matches["GC"]).sum()
        return total_goals / len(home_matches)

    def team_away_average_goals(self, team_name):
        away_matches = self.get_team_away_matches(team_name)
        if len(away_matches) == 0:
            return 0.0
        total_goals = (away_matches["GA"] + away_matches["GC"]).sum()
        return total_goals / len(away_matches)

    def team_home_percentage_over_goals(self, team_name, threshold=0):
        home_matches = self.get_team_home_matches(team_name)
        if len(home_matches) == 0:
            return 0.0
        total_goals = home_matches["GA"] + home_matches["GC"]
        matches_over = home_matches.filter(total_goals > threshold)
        return (len(matches_over) / len(home_matches)) * 100

    def team_away_percentage_over_goals(self, team_name, threshold=0):
        away_matches = self.get_team_away_matches(team_name)
        if len(away_matches) == 0:
            return 0.0
        total_goals = away_matches["GA"] + away_matches["GC"]
        matches_over = away_matches.filter(total_goals > threshold)
        return (len(matches_over) / len(away_matches)) * 100

    def team_home_percentage_btts(self, team_name):
        home_matches = self.get_team_home_matches(team_name)
        if len(home_matches) == 0:
            return 0.0
        both_score = home_matches.filter((pl.col("GA") > 0) & (pl.col("GC") > 0))
        return (len(both_score) / len(home_matches)) * 100

    def team_away_percentage_btts(self, team_name):
        away_matches = self.get_team_away_matches(team_name)
        if len(away_matches) == 0:
            return 0.0
        both_score = away_matches.filter((pl.col("GA") > 0) & (pl.col("GC") > 0))
        return (len(both_score) / len(away_matches)) * 100

    def team_home_percentage_wins(self, team_name):
        """Porcentaje de victorias como local"""
        home_matches = self.get_team_home_matches(team_name)
        if len(home_matches) == 0:
            return 0.0
        wins = home_matches.filter(pl.col("GA") > pl.col("GC"))
        return (len(wins) / len(home_matches)) * 100

    def team_home_percentage_draws(self, team_name):
        """Porcentaje de empates como local"""
        home_matches = self.get_team_home_matches(team_name)
        if len(home_matches) == 0:
            return 0.0
        draws = home_matches.filter(pl.col("GA") == pl.col("GC"))
        return (len(draws) / len(home_matches)) * 100

    def team_home_percentage_losses(self, team_name):
        """Porcentaje de derrotas como local"""
        home_matches = self.get_team_home_matches(team_name)
        if len(home_matches) == 0:
            return 0.0
        losses = home_matches.filter(pl.col("GA") < pl.col("GC"))
        return (len(losses) / len(home_matches)) * 100

    def team_away_percentage_wins(self, team_name):
        """Porcentaje de victorias como visitante"""
        away_matches = self.get_team_away_matches(team_name)
        if len(away_matches) == 0:
            return 0.0
        wins = away_matches.filter(pl.col("GC") > pl.col("GA"))
        return (len(wins) / len(away_matches)) * 100

    def team_away_percentage_draws(self, team_name):
        """Porcentaje de empates como visitante"""
        away_matches = self.get_team_away_matches(team_name)
        if len(away_matches) == 0:
            return 0.0
        draws = away_matches.filter(pl.col("GA") == pl.col("GC"))
        return (len(draws) / len(away_matches)) * 100

    def team_away_percentage_losses(self, team_name):
        """Porcentaje de derrotas como visitante"""
        away_matches = self.get_team_away_matches(team_name)
        if len(away_matches) == 0:
            return 0.0
        losses = away_matches.filter(pl.col("GC") < pl.col("GA"))
        return (len(losses) / len(away_matches)) * 100

    def get_upcoming_matches(self):
        upcoming = self.df.filter(pl.col("GA").is_null())
        return upcoming

    def get_team_upcoming_matches(self, team_name):
        upcoming = self.get_upcoming_matches()
        team_upcoming = upcoming.filter(
            (pl.col("Local").str.contains(team_name)) | 
            (pl.col("Visita").str.contains(team_name))
        )
        return team_upcoming

    def get_head_to_head_upcoming(self, team1, team2):
        upcoming = self.get_upcoming_matches()
        h2h = upcoming.filter(
            ((pl.col("Local").str.contains(team1)) & (pl.col("Visita").str.contains(team2))) |
            ((pl.col("Local").str.contains(team2)) & (pl.col("Visita").str.contains(team1)))
        )
        return h2h

    def get_all_rounds(self):
        rounds = self.df["Jornada"].unique().to_list()
        rounds = [r for r in rounds if r is not None]
        return sorted(rounds)

    def get_matches_by_round(self, round_name):
        matches = self.df.filter(pl.col("Jornada") == round_name)
        return matches

if __name__ == "__main__":
    main()