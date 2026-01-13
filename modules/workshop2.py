"""
Atelier 2 EBIOS RM : Sources de risque et objectifs visés
"""
from typing import Dict, List, Tuple
import json
from datetime import datetime

class Workshop2:
    """Gestion de l'atelier 2 EBIOS RM"""
    
    def __init__(self):
        """Initialise l'atelier 2"""
        self.assessment = {
            'sources_risque': [],
            'objectifs_vises': [],
            'cartographie_sr_ov': [],
            'scenarios_strategiques': []
        }
    
    def add_source_risque(self, nom: str, type_sr: str,
                          ressources: int, determination: int,
                          competences: int) -> Dict:
        """
        Ajoute une source de risque
        
        Args:
            nom: Nom de la source de risque
            type_sr: Type (État-nation, Cybercriminel, Hacktiviste, etc.)
            ressources: Niveau de ressources (1-4)
            determination: Niveau de détermination (1-4)
            competences: Niveau de compétences techniques (1-4)
        
        Returns:
            La source de risque créée
        """
        if not all(1 <= x <= 4 for x in [ressources, determination, competences]):
            raise ValueError("Les niveaux doivent être entre 1 et 4")
        
        capacite_globale = round((ressources + determination + competences) / 3, 1)
        
        sr = {
            'id': f"SR{len(self.assessment['sources_risque']) + 1}",
            'nom': nom,
            'type': type_sr,
            'caracteristiques': {
                'ressources': ressources,
                'determination': determination,
                'competences': competences
            },
            'capacite_globale': capacite_globale,
            'niveau': self._get_capacite_level(capacite_globale)
        }
        
        self.assessment['sources_risque'].append(sr)
        return sr
    
    def _get_capacite_level(self, capacite: float) -> str:
        """Détermine le niveau de capacité"""
        if capacite <= 1.5:
            return "Faible"
        elif capacite <= 2.5:
            return "Moyen"
        elif capacite <= 3.5:
            return "Fort"
        else:
            return "Très fort"
    
    def add_objectif_vise(self, nom: str, description: str,
                          impact_potentiel: int) -> Dict:
        """
        Ajoute un objectif visé
        
        Args:
            nom: Nom de l'objectif visé
            description: Description
            impact_potentiel: Impact potentiel si atteint (1-4)
        
        Returns:
            L'objectif visé créé
        """
        if not 1 <= impact_potentiel <= 4:
            raise ValueError("L'impact potentiel doit être entre 1 et 4")
        
        ov = {
            'id': f"OV{len(self.assessment['objectifs_vises']) + 1}",
            'nom': nom,
            'description': description,
            'impact_potentiel': impact_potentiel
        }
        
        self.assessment['objectifs_vises'].append(ov)
        return ov
    
    def map_sr_to_ov(self, sr_id: str, ov_id: str,
                     pertinence: int) -> Dict:
        """
        Cartographie SR × OV
        
        Args:
            sr_id: ID de la source de risque
            ov_id: ID de l'objectif visé
            pertinence: Pertinence de la relation (1-4)
        
        Returns:
            La relation créée
        """
        if not 1 <= pertinence <= 4:
            raise ValueError("La pertinence doit être entre 1 et 4")
        
        # Trouver SR et OV
        sr = next((s for s in self.assessment['sources_risque'] 
                  if s['id'] == sr_id), None)
        ov = next((o for o in self.assessment['objectifs_vises'] 
                  if o['id'] == ov_id), None)
        
        if not sr or not ov:
            return {}
        
        # Calculer la gravité du scénario stratégique
        gravite_scenario = self._calculate_gravite(
            sr['capacite_globale'],
            ov['impact_potentiel'],
            pertinence
        )
        
        relation = {
            'sr_id': sr_id,
            'ov_id': ov_id,
            'pertinence': pertinence,
            'gravite_scenario': gravite_scenario
        }
        
        self.assessment['cartographie_sr_ov'].append(relation)
        return relation
    
    def _calculate_gravite(self, capacite_sr: float, 
                          impact_ov: int, pertinence: int) -> int:
        """
        Calcule la gravité d'un scénario stratégique
        
        Formule EBIOS RM: combinaison de la capacité SR, impact OV et pertinence
        Résultat normalisé sur échelle 1-4
        """
        # Score pondéré: capacité × pertinence × impact
        score = (capacite_sr * pertinence * impact_ov) / 10
        
        # Normaliser sur échelle 1-4
        if score <= 1.5:
            return 1
        elif score <= 2.5:
            return 2
        elif score <= 3.5:
            return 3
        else:
            return 4
    
    def generate_scenarios_strategiques(self) -> List[Dict]:
        """
        Génère les scénarios stratégiques à partir de la cartographie
        
        Returns:
            Liste des scénarios stratégiques
        """
        self.assessment['scenarios_strategiques'] = []
        
        for relation in self.assessment['cartographie_sr_ov']:
            sr = next((s for s in self.assessment['sources_risque'] 
                      if s['id'] == relation['sr_id']), None)
            ov = next((o for o in self.assessment['objectifs_vises'] 
                      if o['id'] == relation['ov_id']), None)
            
            if sr and ov:
                scenario = {
                    'id': f"SS{len(self.assessment['scenarios_strategiques']) + 1}",
                    'source_risque': sr['nom'],
                    'source_risque_type': sr['type'],
                    'objectif_vise': ov['nom'],
                    'objectif_description': ov['description'],
                    'gravite': relation['gravite_scenario'],
                    'niveau_risque': self._get_risk_level(relation['gravite_scenario']),
                    'pertinence': relation['pertinence'],
                    'capacite_sr': sr['capacite_globale'],
                    'impact_ov': ov['impact_potentiel']
                }
                
                self.assessment['scenarios_strategiques'].append(scenario)
        
        # Trier par gravité décroissante
        self.assessment['scenarios_strategiques'].sort(
            key=lambda x: x['gravite'], reverse=True
        )
        
        return self.assessment['scenarios_strategiques']
    
    def _get_risk_level(self, gravite: int) -> str:
        """Détermine le niveau de risque"""
        levels = {1: "Faible", 2: "Modéré", 3: "Élevé", 4: "Critique"}
        return levels.get(gravite, "Indéterminé")
    
    def get_top_scenarios(self, n: int = 5) -> List[Dict]:
        """
        Retourne les n scénarios les plus graves
        
        Args:
            n: Nombre de scénarios à retourner
        
        Returns:
            Liste des n scénarios les plus critiques
        """
        if not self.assessment['scenarios_strategiques']:
            self.generate_scenarios_strategiques()
        
        return self.assessment['scenarios_strategiques'][:n]
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques de l'atelier 2"""
        if not self.assessment['scenarios_strategiques']:
            self.generate_scenarios_strategiques()
        
        total_scenarios = len(self.assessment['scenarios_strategiques'])
        
        # Compter par gravité
        gravite_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for scenario in self.assessment['scenarios_strategiques']:
            gravite_counts[scenario['gravite']] += 1
        
        return {
            'nb_sources_risque': len(self.assessment['sources_risque']),
            'nb_objectifs_vises': len(self.assessment['objectifs_vises']),
            'nb_scenarios_strategiques': total_scenarios,
            'repartition_gravite': gravite_counts,
            'scenarios_critiques': gravite_counts[4],
            'scenarios_eleves': gravite_counts[3],
            'scenarios_moderes': gravite_counts[2],
            'scenarios_faibles': gravite_counts[1]
        }
    
    def get_source_risque(self, sr_id: str) -> Dict:
        """Récupère une source de risque par son ID"""
        return next((s for s in self.assessment['sources_risque'] 
                    if s['id'] == sr_id), None)
    
    def get_objectif_vise(self, ov_id: str) -> Dict:
        """Récupère un objectif visé par son ID"""
        return next((o for o in self.assessment['objectifs_vises'] 
                    if o['id'] == ov_id), None)
    
    def get_scenarios_by_source(self, sr_id: str) -> List[Dict]:
        """Récupère tous les scénarios liés à une source de risque"""
        if not self.assessment['scenarios_strategiques']:
            self.generate_scenarios_strategiques()
        
        sr = self.get_source_risque(sr_id)
        if not sr:
            return []
        
        return [
            s for s in self.assessment['scenarios_strategiques']
            if s['source_risque'] == sr['nom']
        ]
    
    def get_scenarios_by_objectif(self, ov_id: str) -> List[Dict]:
        """Récupère tous les scénarios liés à un objectif visé"""
        if not self.assessment['scenarios_strategiques']:
            self.generate_scenarios_strategiques()
        
        ov = self.get_objectif_vise(ov_id)
        if not ov:
            return []
        
        return [
            s for s in self.assessment['scenarios_strategiques']
            if s['objectif_vise'] == ov['nom']
        ]
    
    def export_matrix_data(self) -> Dict:
        """
        Exporte les données pour génération de matrice SR×OV
        
        Returns:
            Dict avec sources, objectifs et cartographie
        """
        return {
            'sources': self.assessment['sources_risque'],
            'objectifs': self.assessment['objectifs_vises'],
            'cartographie': self.assessment['cartographie_sr_ov']
        }
    
    def get_summary(self) -> Dict:
        """Retourne un résumé complet de l'atelier 2"""
        stats = self.get_statistics()
        top_scenarios = self.get_top_scenarios(3)
        
        return {
            'statistiques': stats,
            'top_scenarios': top_scenarios,
            'taux_couverture_sr': self._calculate_coverage_rate('sources'),
            'taux_couverture_ov': self._calculate_coverage_rate('objectifs')
        }
    
    def _calculate_coverage_rate(self, type_entity: str) -> float:
        """
        Calcule le taux de couverture des SR ou OV dans la cartographie
        
        Args:
            type_entity: 'sources' ou 'objectifs'
        
        Returns:
            Taux de couverture en pourcentage
        """
        if type_entity == 'sources':
            total = len(self.assessment['sources_risque'])
            covered_ids = set(r['sr_id'] for r in self.assessment['cartographie_sr_ov'])
        else:  # objectifs
            total = len(self.assessment['objectifs_vises'])
            covered_ids = set(r['ov_id'] for r in self.assessment['cartographie_sr_ov'])
        
        if total == 0:
            return 0.0
        
        return round((len(covered_ids) / total) * 100, 1)
    
    def validate_assessment(self) -> Dict:
        """
        Valide la complétude de l'atelier 2
        
        Returns:
            Dict avec statut de validation et messages
        """
        errors = []
        warnings = []
        
        # Vérifications obligatoires
        if len(self.assessment['sources_risque']) == 0:
            errors.append("Aucune source de risque définie")
        
        if len(self.assessment['objectifs_vises']) == 0:
            errors.append("Aucun objectif visé défini")
        
        if len(self.assessment['cartographie_sr_ov']) == 0:
            errors.append("Aucune cartographie SR×OV réalisée")
        
        # Avertissements
        if len(self.assessment['sources_risque']) < 3:
            warnings.append("Moins de 3 sources de risque (recommandé: 3-7)")
        
        if len(self.assessment['objectifs_vises']) < 3:
            warnings.append("Moins de 3 objectifs visés (recommandé: 3-10)")
        
        cov_sr = self._calculate_coverage_rate('sources')
        if cov_sr < 80:
            warnings.append(f"Couverture des sources de risque faible: {cov_sr}%")
        
        cov_ov = self._calculate_coverage_rate('objectifs')
        if cov_ov < 80:
            warnings.append(f"Couverture des objectifs visés faible: {cov_ov}%")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def save(self, filename: str) -> str:
        """Sauvegarde l'atelier 2"""
        import os
        os.makedirs('data/assessments', exist_ok=True)
        
        filepath = f"data/assessments/{filename}_atelier2.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.assessment, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load(self, filename: str) -> Dict:
        """Charge une évaluation existante"""
        filepath = f"data/assessments/{filename}_atelier2.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            self.assessment = json.load(f)
        
        return self.assessment
    
    def __str__(self) -> str:
        """Représentation string de l'atelier 2"""
        stats = self.get_statistics()
        return f"""
Atelier 2 EBIOS RM
==================
Sources de risque: {stats['nb_sources_risque']}
Objectifs visés: {stats['nb_objectifs_vises']}
Scénarios stratégiques: {stats['nb_scenarios_strategiques']}
  - Critiques: {stats['scenarios_critiques']}
  - Élevés: {stats['scenarios_eleves']}
  - Modérés: {stats['scenarios_moderes']}
  - Faibles: {stats['scenarios_faibles']}
"""
