"""
Configuration globale pour EBIOS Risk Manager Calculator
"""
import os
from pathlib import Path

# Répertoires
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
ASSESSMENTS_DIR = DATA_DIR / 'assessments'
TEMPLATES_DIR = DATA_DIR

# Fichiers
EBIOS_TEMPLATES_FILE = TEMPLATES_DIR / 'ebios_templates_complete.json'

# Créer les répertoires s'ils n'existent pas
ASSESSMENTS_DIR.mkdir(parents=True, exist_ok=True)

# Configuration des échelles EBIOS RM
GRAVITE_SCALE = {
    1: "Négligeable",
    2: "Limitée",
    3: "Importante",
    4: "Critique"
}

VRAISEMBLANCE_SCALE = {
    1: "Peu probable",
    2: "Possible",
    3: "Probable",
    4: "Très probable"
}

# Matrice de risque (Gravité × Vraisemblance)
RISK_MATRIX = [
    [1, 1, 2, 2],  # Gravité 1
    [1, 2, 2, 3],  # Gravité 2
    [2, 2, 3, 4],  # Gravité 3
    [2, 3, 4, 4]   # Gravité 4
]

# Seuils d'acceptation
RISK_ACCEPTANCE_THRESHOLDS = {
    'acceptable': 4,
    'tolerable_max': 8,
    'inacceptable_min': 9
}

# Couleurs pour les visualisations
RISK_COLORS = {
    'Faible': '#90EE90',
    'Acceptable': '#C8E6C9',
    'Modéré': '#FFFF00',
    'Élevé': '#FFA500',
    'Critique': '#FF0000'
}

# Configuration PDF
PDF_CONFIG = {
    'font': 'Arial',
    'font_size': 11,
    'line_height': 6
}

# Métadonnées
APP_NAME = "EBIOS Risk Manager Calculator"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Ludovic Mouly"
METHODOLOGY = "EBIOS Risk Manager 2018"
