"""
Atelier 3 EBIOS RM : Scénarios stratégiques et cartographie de l'écosystème
"""
from typing import Dict, List, Tuple
import json
from datetime import datetime

class Workshop3:
    """Gestion de l'atelier 3 EBIOS RM"""
    
    def __init__(self):
        """Initialise l'atelier 3"""
        self.assessment = {
            'parties_prenantes': [],
            'ecosysteme': {},
            'scenarios_strategiques_enrichis': [],
            'chemins_attaque': []
        }
    
    def add_partie_prenante(self, nom: str, type_pp: str,
                           dependance: int, exposition: int,
                           confiance: int, maturite: int) -> Dict:
        """
        Ajoute une partie prenante de l'écosystème
        
        Args:
            nom: Nom de la partie prenante
            type_pp: Type (Client, Fournisseur, Partenaire, Autorité, etc.)
            dependance: Niveau de dépendance (1-4)
            exposition: Exposition de la PP au risque (1-4)
            confiance: Niveau de confiance accordé (1-4)
            maturite: Maturité cyber de la PP (1-4)
        
        Returns:
            La partie prenante créée
        """
        # Calculer un score de risque tiers
        score_risque = round((dependance + exposition - maturite) / 3, 1)
        
        pp = {
            'id': f"PP{len(self.assessment['parties_prenantes']) + 1}",
            'nom': nom,
            'type': type_pp,
            'evaluation': {
                'dependance': dependance,
                'exposition': exposition,
                'confiance': confiance,
                'maturite': maturite
            },
            'score_risque_tiers': score_risque,
            'niveau_criticite': self._get_criticite_level(score_risque)
        }
        
        self.assessment['parties_prenantes'].append(pp)
        return pp
    
    def _get_criticite_level(self, score: float) -> str:
        """Détermine le niveau de criticité d'une partie prenante"""
        if score <= 1.5:
            return "Faible"
        elif score <= 2.5:
            return "Modéré"
        elif score <= 3.5:
            return "Élevé"
        else:
            return "Critique"
    
    def map_ecosysteme(self, relations: List[Dict]) -> Dict:
        """
        Cartographie l'écosystème avec les relations
        
        Args:
            relations: Liste de relations {pp_id, type_relation, criticite}
        
        Returns:
            L'écosystème cartographié
        """
        self.assessment['ecosysteme'] = {
            'date_cartographie': datetime.now().isoformat(),
            'nombre_parties_prenantes': len(self.assessment['parties_prenantes']),
            'relations': relations,
            'points_entree': []
        }
        
        # Identifier les points d'entrée critiques
        for relation in relations:
            if relation.get('criticite', 0) >= 3:
                self.assessment['ecosysteme']['points_entree'].append({
                    'pp_id': relation['pp_id'],
                    'type': relation['type_relation'],
                    'criticite': relation['criticite']
                })
        
        return self.assessment['ecosysteme']
    
    def enrich_scenario_strategique(self, scenario_id: str,
                                    pp_ids: List[str],
                                    chemin_attaque: str) -> Dict:
        """
        Enrichit un scénario stratégique avec l'écosystème
        
        Args:
            scenario_id: ID du scénario stratégique (depuis atelier 2)
            pp_ids: IDs des parties prenantes impliquées
            chemin_attaque: Description du chemin d'attaque via l'écosystème
        
        Returns:
            Le scénario enrichi
        """
        # Récupérer les PP impliquées
        pp_impliquees = [
            pp for pp in self.assessment['parties_prenantes']
            if pp['id'] in pp_ids
        ]
        
        # Calculer la gravité enrichie
        gravite_ecosysteme = max(
            [pp['evaluation']['exposition'] for pp in pp_impliquees],
            default=0
        )
        
        scenario_enrichi = {
            'id': f"SSE{len(self.assessment['scenarios_strategiques_enrichis']) + 1}",
            'scenario_strategique_ref': scenario_id,
            'parties_prenantes_impliquees': pp_ids,
            'chemin_attaque': chemin_attaque,
            'gravite_ecosysteme': gravite_ecosysteme,
            'niveau_risque': self._calculate_risk_ecosystem(gravite_ecosysteme)
        }
        
        self.assessment['scenarios_strategiques_enrichis'].append(scenario_enrichi)
        return scenario_enrichi
    
    def _calculate_risk_ecosystem(self, gravite: int) -> str:
        """Calcule le niveau de risque en fonction de la gravité"""
        if gravite <= 1:
            return "Faible"
        elif gravite <= 2:
            return "Modéré"
        elif gravite <= 3:
            return "Élevé"
        else:
            return "Critique"
    
    def add_chemin_attaque(self, source_risque: str, 
                          objectif_vise: str,
                          etapes: List[Dict]) -> Dict:
        """
        Ajoute un chemin d'attaque détaillé via l'écosystème
        
        Args:
            source_risque: Source de risque
            objectif_vise: Objectif visé
            etapes: Liste d'étapes [{pp_id, action, technique}]
        
        Returns:
            Le chemin d'attaque créé
        """
        chemin = {
            'id': f"CA{len(self.assessment['chemins_attaque']) + 1}",
            'source_risque': source_risque,
            'objectif_vise': objectif_vise,
            'etapes': etapes,
            'nombre_etapes': len(etapes),
            'complexite': self._calculate_complexity(etapes)
        }
        
        self.assessment['chemins_attaque'].append(chemin)
        return chemin
    
    def _calculate_complexity(self, etapes: List[Dict]) -> str:
        """Calcule la complexité d'un chemin d'attaque"""
        nb_etapes = len(etapes)
        
        if nb_etapes <= 2:
            return "Faible"
        elif nb_etapes <= 4:
            return "Moyenne"
        else:
            return "Élevée"
    
    def get_parties_prenantes_critiques(self) -> List[Dict]:
        """Retourne les parties prenantes critiques"""
        return [
            pp for pp in self.assessment['parties_prenantes']
            if pp['niveau_criticite'] in ['Élevé', 'Critique']
        ]
    
    def get_points_entree_prioritaires(self) -> List[Dict]:
        """Retourne les points d'entrée prioritaires pour sécurisation"""
        if not self.assessment['ecosysteme']:
            return []
        
        return self.assessment['ecosysteme'].get('points_entree', [])
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques de l'atelier 3"""
        pp_critiques = self.get_parties_prenantes_critiques()
        
        return {
            'nb_parties_prenantes': len(self.assessment['parties_prenantes']),
            'nb_pp_critiques': len(pp_critiques),
            'nb_scenarios_enrichis': len(self.assessment['scenarios_strategiques_enrichis']),
            'nb_chemins_attaque': len(self.assessment['chemins_attaque']),
            'nb_points_entree': len(self.assessment['ecosysteme'].get('points_entree', []))
        }
    
    def save(self, filename: str) -> str:
        """Sauvegarde l'atelier 3"""
        import os
        os.makedirs('data/assessments', exist_ok=True)
        
        filepath = f"data/assessments/{filename}_atelier3.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.assessment, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load(self, filename: str) -> Dict:
        """Charge une évaluation existante"""
        filepath = f"data/assessments/{filename}_atelier3.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            self.assessment = json.load(f)
        
        return self.assessment
