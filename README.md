# EBIOS Risk Manager Calculator

Calculateur automatisé pour l'analyse de risques cyber selon la méthode EBIOS RM (ANSSI). Implémentation des 5 ateliers avec génération automatique de rapports et matrices de risques.

## Fonctionnalités

### Atelier 1 - Périmètre & Socle de sécurité
Définition du périmètre, des parties prenantes et des missions critiques. Calcul automatisé de la gravité des événements redoutés (ER) et des impacts DICT (Disponibilité, Intégrité, Confidentialité, Traçabilité).

### Atelier 2 - Origines du risque
Identification et scoring des sources de risque (SR) et des objectifs visés (OV) avec matrice de croisement SR × OV. Scoring de pertinence et priorisation automatique des couples SR/OV pour générer les scénarios stratégiques.

### Atelier 3 - Écosystème et parties prenantes
Cartographie des parties prenantes, identification des biens supports et évaluation de leur criticité dans l'écosystème.

### Atelier 4 - Scénarios opérationnels
Modélisation détaillée des chemins d'attaque opérationnels (points d'entrée, cibles, déroulement). Référencement des techniques selon MITRE ATT&CK, ajout d'IoC et priorisation des risques opérationnels.

### Atelier 5 - Traitement des risques
Définition des stratégies de traitement (accepter, éviter, réduire, transférer) et association de mesures de sécurité. Calcul des risques résiduels, estimation des coûts et génération d'un plan d'action priorisé par niveau de risque.

## Livrables générés

- Cartographie des risques sous forme de heatmap 4×4 Gravité/Vraisemblance
- Matrices SR/OV, listes de scénarios stratégiques et opérationnels avec leurs scores et niveaux de criticité
- Export d'analyses EBIOS RM structurées (JSON) pour archivage ou réutilisation
- Plan de traitement des risques consolidé avec mesures priorisées, responsables et indicateurs de suivi

## Architecture technique

Application web Flask avec interface responsive. Persistance des données en JSON. Génération de heatmaps via matplotlib. API REST pour intégrations tierces.

## Structure modulaire
```
modules/
├── workshop1.py          # Atelier 1 - Cadrage
├── workshop2.py          # Atelier 2 - Sources de risque
├── workshop3.py          # Atelier 3 - Écosystème
├── workshop4.py          # Atelier 4 - Scénarios opérationnels
├── workshop5.py          # Atelier 5 - Traitement
├── risk_calculator.py    # Moteur de calcul des risques
├── heatmap_generator.py  # Génération des visualisations
└── ebios_data_loader.py  # Chargement des référentiels
```

## Référentiels intégrés

- Échelles de gravité et vraisemblance 1-4
- Sources de risque types (APT, cybercriminels, hacktivistes, insiders)
- Objectifs visés types (vol de données, sabotage, ransomware)
- Mesures de sécurité ISO 27001:2022
- Framework MITRE ATT&CK pour le référencement des techniques d'attaque

## API REST
```
GET  /api/templates/sources_risque    # Liste des sources de risque
GET  /api/templates/mesures           # Liste des mesures de sécurité
POST /api/calculate_risk              # Calcul du niveau de risque
POST /api/analyse/<filename>/delete   # Suppression d'une analyse
```

## Conformité

Méthode EBIOS Risk Manager conforme aux préconisations ANSSI. Compatible avec les exigences ISO 27001, RGPD, NIS2, DORA et LPM.

## Auteur

Ludovic Mouly - Cybersecurity Engineer

## Version

1.0.0
