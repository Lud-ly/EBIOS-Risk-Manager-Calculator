"""
Atelier 4 EBIOS RM : Scénarios opérationnels et modes opératoires
"""
from typing import Dict, List, Tuple
import json
from datetime import datetime

class Workshop4:
    """Gestion de l'atelier 4 EBIOS RM"""
    
    def __init__(self):
        """Initialise l'atelier 4"""
        self.assessment = {
            'scenarios_operationnels': [],
            'actions_elementaires': [],
            'mesures_existantes': [],
            'synthese_risques': []
        }
    
    def add_scenario_operationnel(self, scenario_strategique_id: str,
                                  nom: str, description: str,
                                  actions: List[str]) -> Dict:
        """
        Ajoute un scénario opérationnel
        
        Args:
            scenario_strategique_id: Référence au scénario stratégique (atelier 2/3)
            nom: Nom du scénario opérationnel
            description: Description technique
            actions: Liste d'actions élémentaires (IDs)
        
        Returns:
            Le scénario opérationnel créé
        """
        so = {
            'id': f"SO{len(self.assessment['scenarios_operationnels']) + 1}",
            'scenario_strategique_ref': scenario_strategique_id,
            'nom': nom,
            'description': description,
            'actions_elementaires': actions,
            'vraisemblance': 0,  # À calculer
            'date_creation': datetime.now().isoformat()
        }
        
        self.assessment['scenarios_operationnels'].append(so)
        return so
    
    def add_action_elementaire(self, nom: str, technique_mitre: str,
                              difficulte: int, detectabilite: int) -> Dict:
        """
        Ajoute une action élémentaire (TTP MITRE ATT&CK)
        
        Args:
            nom: Nom de l'action
            technique_mitre: Référence MITRE ATT&CK (ex: T1566 - Phishing)
            difficulte: Difficulté d'exécution (1-4)
            detectabilite: Facilité de détection (1-4, 4=facile à détecter)
        
        Returns:
            L'action élémentaire créée
        """
        action = {
            'id': f"AE{len(self.assessment['actions_elementaires']) + 1}",
            'nom': nom,
            'technique_mitre': technique_mitre,
            'difficulte': difficulte,
            'detectabilite': detectabilite,
            'vraisemblance_action': self._calculate_vraisemblance_action(difficulte, detectabilite)
        }
        
        self.assessment['actions_elementaires'].append(action)
        return action
    
    def _calculate_vraisemblance_action(self, difficulte: int, detectabilite: int) -> int:
        """
        Calcule la vraisemblance d'une action élémentaire
        
        Formule: (5 - difficulté + (5 - détectabilité)) / 2
        Plus c'est facile et difficile à détecter, plus c'est vraisemblable
        """
        score = ((5 - difficulte) + (5 - detectabilite)) / 2
        
        # Normaliser sur échelle 1-4
        if score <= 1.5:
            return 1
        elif score <= 2.5:
            return 2
        elif score <= 3.5:
            return 3
        else:
            return 4
    
    def calculate_vraisemblance_scenario(self, scenario_id: str) -> int:
        """
        Calcule la vraisemblance d'un scénario opérationnel
        
        Basé sur la moyenne des vraisemblances des actions élémentaires
        """
        scenario = next(
            (s for s in self.assessment['scenarios_operationnels'] 
             if s['id'] == scenario_id), None
        )
        
        if not scenario:
            return 0
        
        # Récupérer les actions du scénario
        actions = [
            a for a in self.assessment['actions_elementaires']
            if a['id'] in scenario['actions_elementaires']
        ]
        
        if not actions:
            return 0
        
        # Moyenne des vraisemblances
        avg_vraisemblance = sum(a['vraisemblance_action'] for a in actions) / len(actions)
        
        # Arrondir à l'échelle 1-4
        vraisemblance = round(avg_vraisemblance)
        
        # Mettre à jour le scénario
        scenario['vraisemblance'] = vraisemblance
        
        return vraisemblance
    
    def add_mesure_existante(self, nom: str, type_mesure: str,
                            efficacite: float, couverture: List[str]) -> Dict:
        """
        Ajoute une mesure de sécurité existante
        
        Args:
            nom: Nom de la mesure
            type_mesure: Type (Préventif, Détectif, Correctif)
            efficacite: Efficacité estimée (0.0 à 1.0)
            couverture: Liste d'IDs d'actions couvertes
        
        Returns:
            La mesure créée
        """
        mesure = {
            'id': f"ME{len(self.assessment['mesures_existantes']) + 1}",
            'nom': nom,
            'type': type_mesure,
            'efficacite': efficacite,
            'actions_couvertes': couverture
        }
        
        self.assessment['mesures_existantes'].append(mesure)
        return mesure
    
    def synthetize_risks(self, gravite_base: int) -> List[Dict]:
        """
        Synthétise les risques finaux (Gravité × Vraisemblance)
        
        Args:
            gravite_base: Gravité de base (depuis ateliers précédents)
        
        Returns:
            Liste des risques synthétisés
        """
        self.assessment['synthese_risques'] = []
        
        for scenario in self.assessment['scenarios_operationnels']:
            if scenario['vraisemblance'] == 0:
                self.calculate_vraisemblance_scenario(scenario['id'])
            
            # Calculer le risque brut
            risque_brut = gravite_base * scenario['vraisemblance']
            
            # Calculer le risque résiduel avec mesures existantes
            reduction = self._calculate_risk_reduction(scenario['actions_elementaires'])
            risque_residuel = max(1, round(risque_brut * (1 - reduction)))
            
            risque = {
                'scenario_id': scenario['id'],
                'nom': scenario['nom'],
                'gravite': gravite_base,
                'vraisemblance': scenario['vraisemblance'],
                'risque_brut': risque_brut,
                'risque_residuel': risque_residuel,
                'niveau': self._get_risk_level(risque_residuel),
                'reduction_pct': round(reduction * 100, 1)
            }
            
            self.assessment['synthese_risques'].append(risque)
        
        # Trier par risque résiduel décroissant
        self.assessment['synthese_risques'].sort(
            key=lambda x: x['risque_residuel'], reverse=True
        )
        
        return self.assessment['synthese_risques']
    
    def _calculate_risk_reduction(self, action_ids: List[str]) -> float:
        """Calcule la réduction de risque apportée par les mesures existantes"""
        if not self.assessment['mesures_existantes']:
            return 0.0
        
        # Compter les actions couvertes
        actions_couvertes = set()
        efficacite_totale = 0.0
        
        for mesure in self.assessment['mesures_existantes']:
            for action_id in action_ids:
                if action_id in mesure['actions_couvertes']:
                    actions_couvertes.add(action_id)
                    efficacite_totale += mesure['efficacite']
        
        if not actions_couvertes:
            return 0.0
        
        # Moyenne de l'efficacité pondérée par la couverture
        couverture_pct = len(actions_couvertes) / len(action_ids) if action_ids else 0
        efficacite_moyenne = efficacite_totale / len(actions_couvertes)
        
        return min(0.9, couverture_pct * efficacite_moyenne)  # Max 90% réduction
    
    def _get_risk_level(self, score: int) -> str:
        """Détermine le niveau de risque"""
        if score <= 2:
            return "Faible"
        elif score <= 4:
            return "Acceptable"
        elif score <= 8:
            return "Modéré"
        elif score <= 12:
            return "Élevé"
        else:
            return "Critique"
    
    def get_gaps(self) -> List[Dict]:
        """Identifie les actions non couvertes par des mesures"""
        gaps = []
        
        actions_couvertes = set()
        for mesure in self.assessment['mesures_existantes']:
            actions_couvertes.update(mesure['actions_couvertes'])
        
        for action in self.assessment['actions_elementaires']:
            if action['id'] not in actions_couvertes:
                gaps.append({
                    'action_id': action['id'],
                    'nom': action['nom'],
                    'technique_mitre': action['technique_mitre'],
                    'vraisemblance': action['vraisemblance_action']
                })
        
        return gaps
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques de l'atelier 4"""
        gaps = self.get_gaps()
        
        risques_critiques = [
            r for r in self.assessment['synthese_risques']
            if r['niveau'] == 'Critique'
        ]
        
        return {
            'nb_scenarios_operationnels': len(self.assessment['scenarios_operationnels']),
            'nb_actions_elementaires': len(self.assessment['actions_elementaires']),
            'nb_mesures_existantes': len(self.assessment['mesures_existantes']),
            'nb_gaps': len(gaps),
            'nb_risques_critiques': len(risques_critiques),
            'taux_couverture': round((1 - len(gaps) / max(1, len(self.assessment['actions_elementaires']))) * 100, 1)
        }
    
    def save(self, filename: str) -> str:
        """Sauvegarde l'atelier 4"""
        import os
        os.makedirs('data/assessments', exist_ok=True)
        
        filepath = f"data/assessments/{filename}_atelier4.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.assessment, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load(self, filename: str) -> Dict:
        """Charge une évaluation existante"""
        filepath = f"data/assessments/{filename}_atelier4.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            self.assessment = json.load(f)
        
        return self.assessment
