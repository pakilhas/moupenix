import json
import os

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".moupenix_config.json")

DEFAULT_CONFIG = {
    "scale": 1.0,               # Escala geral (0.5 a 2.5)
    "speed_stretch": 1.5,       # Quanto estica com velocidade (0 a 3.0)
    "click_stretch": 1.4,       # Quanto estica ao segurar clique (1.0 a 2.5)
    "elasticity": 0.25,         # Velocidade de recuperação elástica (0.1 a 0.6)
    "jiggle_amount": 1.0,       # Intensidade da inércia/rebolado dos testículos
    "particles_enabled": True,  # Gotículas/efeito ao soltar clique
    "sound_effects": False,     # Efeitos sonoros cômicos ao soltar clique
    "autostart": False,         # Iniciar automaticamente com o Windows
    "theme": "Berinjela (Eggplant)", # Tema padrão cômico e seguro para GitHub
    "hide_native_cursor": False # Tentar ocultar cursor original via Win32
}

THEMES = {
    "Berinjela (Eggplant)": {
        "shaft": "#6A1B9A",
        "head": "#8E24AA",
        "outline": "#2E0854",
        "vein": "#43A047",
        "particle": "#E1BEE7",
        "wrinkle": "#4A148C"
    },
    "Cartoon Rosa": {
        "shaft": "#FFAEC9",
        "head": "#FF6B8B",
        "outline": "#4A1525",
        "vein": "#9932CC",
        "particle": "#FFFFFF",
        "wrinkle": "#C77D98"
    },
    "Tom de Pele": {
        "shaft": "#F5C396",
        "head": "#E5887B",
        "outline": "#572F18",
        "vein": "#4682B4",
        "particle": "#FFF5EE",
        "wrinkle": "#C49A74"
    },
    "Dourado Luxo": {
        "shaft": "#FFD700",
        "head": "#FFA500",
        "outline": "#5C4033",
        "vein": "#FFF8DC",
        "particle": "#FFFFE0",
        "wrinkle": "#C6A300"
    },
    "Cyber Neon": {
        "shaft": "#00F5D4",
        "head": "#7B2CBF",
        "outline": "#0B090A",
        "vein": "#F72585",
        "particle": "#4CC9F0",
        "wrinkle": "#00BB9E"
    },
    "Alien Verde": {
        "shaft": "#70E000",
        "head": "#38B000",
        "outline": "#004B23",
        "vein": "#FF5400",
        "particle": "#CCFF33",
        "wrinkle": "#4F9D00"
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(data)
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception:
        pass

