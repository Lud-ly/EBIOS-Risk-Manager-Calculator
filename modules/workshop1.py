"""
Atelier 1 EBIOS RM : Cadrage et socle de sécurité
"""
from typing import Dict, List
import json
from datetime import datetime

class Workshop1:
    """Gestion de l'atelier 1 EBIOS RM"""
    
    def __init__(self):
        """Initialise l'atelier 1"""
        self.study = {
            'metadata': {},
            'missions': [],
            'valeurs_metier': [],
            'biens_supports': [],
            'evenements_redoutes': [],
            'socle_securite': {}
        }
    
    def init_study(self, nom_organisme: str, perimetre: str, responsable: str) -> Dict:
        """
        Initialise une nouvelle étude EBIOS RM
        
        Args:
            nom_organisme: Nom de l'organisation
            perimetre: Périmètre de l'étude
            responsable: Responsable de l'étude
        
        Returns:
            Métadonnées de l'étude
        """
        self.study['metadata'] = {
            'organisme': nom_organisme,
            'perimetre': perimetre,
            'responsable': responsable,
            'date_debut': datetime.now().isoformat(),
            'version': '1.0'
        }
        return self.study['metadata']
    
    def add_mission(self, nom: str, description: str, criticite: int) -> bool:
        """
        Ajoute une mission critique
        
        Args:
            nom: Nom de la mission
            description: Description
            criticite: Niveau de criticité (1-4)
        
        Returns:
            True si ajouté avec succès
        """
        if not 1 <= criticite <= 4:
            raise ValueError("La criticité doit être entre 1 et 4")
        
        mission = {
            'id': f"M{len(self.study['missions']) + 1}",
            'nom': nom,
            'description': description,
            'criticite': criticite
        }
        
        self.study['missions'].append(mission)
        return True
    
    def add_valeur_metier(self, nom: str, type_valeur: str, 
                          sensibilite: Dict[str, int]) -> bool:
        """
        Ajoute une valeur métier avec sa sensibilité DICT
        
        Args:
            nom: Nom de la valeur métier
            type_valeur: Type (Information, Service, etc.)
            sensibilite: Dict avec D, I, C, T (1-4 chacun)
        
        Returns:
            True si ajouté avec succès
        """
        for cle in ['D', 'I', 'C', 'T']:
            if cle not in sensibilite:
                raise ValueError(f"La clé {cle} est manquante dans la sensibilité")
            if not 1 <= sensibilite[cle] <= 4:
                raise ValueError(f"La sensibilité {cle} doit être entre 1 et 4")
        
        niveau_max = max(sensibilite.values())
        
        valeur = {
            'id': f"VM{len(self.study['valeurs_metier']) + 1}",
            'nom': nom,
            'type': type_valeur,
            'sensibilite': sensibilite,
            'niveau_max': niveau_max
        }
        
        self.study['valeurs_metier'].append(valeur)
        return True
    
    def add_bien_support(self, nom: str, type_bien: str, 
                        valeurs_supportees: List[str]) -> bool:
        """
        Ajoute un bien support
        
        Args:
            nom: Nom du bien support
            type_bien: Type (SI, Personnel, Local, etc.)
            valeurs_supportees: Liste des IDs de valeurs métier supportées
        
        Returns:
            True si ajouté avec succès
        """
        bien = {
            'id': f"BS{len(self.study['biens_supports']) + 1}",
            'nom': nom,
            'type': type_bien,
            'valeurs_supportees': valeurs_supportees
        }
        
        self.study['biens_supports'].append(bien)
        return True
    
    def add_evenement_redoute(self, nom: str, description: str,
                              gravite: int, biens_impactes: List[str]) -> bool:
        """
        Ajoute un événement redouté
        
        Args:
            nom: Nom de l'événement redouté
            description: Description de l'événement
            gravite: Gravité (1-4)
            biens_impactes: Liste des IDs des biens supports impactés
        
        Returns:
            True si ajouté avec succès
        """
        if not 1 <= gravite <= 4:
            raise ValueError("La gravité doit être entre 1 et 4")
        
        evenement = {
            'id': f"ER{len(self.study['evenements_redoutes']) + 1}",
            'nom': nom,
            'description': description,
            'gravite': gravite,
            'biens_impactes': biens_impactes
        }
        
        self.study['evenements_redoutes'].append(evenement)
        return True
    
    def evaluate_socle(self, domaine: str, score: float) -> bool:
        """
        Évalue un domaine du socle de sécurité
        
        Args:
            domaine: Nom du domaine (ex: "Contrôle d'accès")
            score: Score de conformité (0-100)
        
        Returns:
            True si évalué avec succès
        """
        if not 0 <= score <= 100:
            raise ValueError("Le score doit être entre 0 et 100")
        
        self.study['socle_securite'][domaine] = score
        return True
    
    def get_socle_stats(self) -> Dict:
        """Retourne les statistiques du socle de sécurité"""
        if not self.study['socle_securite']:
            return {
                'taux_conformite': 0,
                'domaines_critiques': 0,
                'domaines_conformes': 0
            }
        
        scores = list(self.study['socle_securite'].values())
        taux_moyen = sum(scores) / len(scores)
        
        domaines_critiques = sum(1 for s in scores if s < 60)
        domaines_conformes = sum(1 for s in scores if s >= 80)
        
        return {
            'taux_conformite': round(taux_moyen, 1),
            'domaines_critiques': domaines_critiques,
            'domaines_conformes': domaines_conformes
        }
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques globales de l'atelier 1"""
        socle_stats = self.get_socle_stats()
        
        return {
            'nb_missions': len(self.study['missions']),
            'nb_valeurs_metier': len(self.study['valeurs_metier']),
            'nb_biens_supports': len(self.study['biens_supports']),
            'nb_evenements_redoutes': len(self.study['evenements_redoutes']),
            'taux_conformite_socle': socle_stats['taux_conformite']
        }
    
    def save(self, filename: str) -> str:
        """Sauvegarde l'étude dans un fichier JSON"""
        import os
        os.makedirs('data/assessments', exist_ok=True)
        
        filepath = f"data/assessments/{filename}_atelier1.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.study, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load(self, filename: str) -> Dict:
        """Charge une étude depuis un fichier JSON"""
        filepath = f"data/assessments/{filename}_atelier1.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            self.study = json.load(f)
        
        return self.study
