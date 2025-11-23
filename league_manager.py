import json
import os
from typing import List, Dict, Optional

class LeagueManager:
    """Gestor de ligas para el dashboard de pronósticos"""
    
    def __init__(self, config_file: str = "leagues_config.json"):
        self.config_file = config_file
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Crear archivo de configuración si no existe"""
        if not os.path.exists(self.config_file):
            default_leagues = {
                "leagues": [
                    {
                        "id": "liga_esp",
                        "name": "Liga Española",
                        "url": "https://www.livefutbol.com/espana/laliga/calendario/"
                    },
                    {
                        "id": "premier",
                        "name": "Premier League",
                        "url": "https://www.livefutbol.com/inglaterra/premier-league/calendario/"
                    },
                    {
                        "id": "serie_a",
                        "name": "Serie A",
                        "url": "https://www.livefutbol.com/italia/serie-a/calendario/"
                    },
                    {
                        "id": "bundesliga",
                        "name": "Bundesliga",
                        "url": "https://www.livefutbol.com/alemania/bundesliga/calendario/"
                    },
                    {
                        "id": "ligue1",
                        "name": "Ligue 1",
                        "url": "https://www.livefutbol.com/francia/ligue-1/calendario/"
                    }
                ]
            }
            self._save_config(default_leagues)
    
    def _load_config(self) -> Dict:
        """Cargar configuración desde JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {"leagues": []}
    
    def _save_config(self, config: Dict):
        """Guardar configuración a JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_all_leagues(self) -> List[Dict]:
        """Obtener todas las ligas"""
        config = self._load_config()
        return config.get("leagues", [])
    
    def get_league_by_id(self, league_id: str) -> Optional[Dict]:
        """Obtener liga por ID"""
        leagues = self.get_all_leagues()
        for league in leagues:
            if league.get("id") == league_id:
                return league
        return None
    
    def add_league(self, name: str, url: str) -> bool:
        """Agregar nueva liga"""
        try:
            config = self._load_config()
            
            # Generar ID único
            league_id = name.lower().replace(" ", "_").replace("á", "a").replace("é", "e")\
                           .replace("í", "i").replace("ó", "o").replace("ú", "u")
            
            # Verificar si ya existe
            for league in config["leagues"]:
                if league["id"] == league_id:
                    return False  # Ya existe
            
            # Agregar nueva liga
            new_league = {
                "id": league_id,
                "name": name,
                "url": url
            }
            config["leagues"].append(new_league)
            
            self._save_config(config)
            return True
        except Exception as e:
            print(f"Error adding league: {e}")
            return False
    
    def delete_league(self, league_id: str) -> bool:
        """Eliminar liga por ID"""
        try:
            config = self._load_config()
            original_count = len(config["leagues"])
            
            config["leagues"] = [l for l in config["leagues"] if l.get("id") != league_id]
            
            if len(config["leagues"]) < original_count:
                self._save_config(config)
                return True
            return False
        except Exception as e:
            print(f"Error deleting league: {e}")
            return False
    
    def update_league(self, league_id: str, name: str = None, url: str = None) -> bool:
        """Actualizar liga existente"""
        try:
            config = self._load_config()
            
            for league in config["leagues"]:
                if league["id"] == league_id:
                    if name:
                        league["name"] = name
                    if url:
                        league["url"] = url
                    self._save_config(config)
                    return True
            
            return False
        except Exception as e:
            print(f"Error updating league: {e}")
            return False
    
    def get_leagues_dict(self) -> Dict[str, str]:
        """Obtener diccionario de ligas {nombre: url}"""
        leagues = self.get_all_leagues()
        return {league["name"]: league["url"] for league in leagues}
