"""
Module de chargement des templates et données EBIOS RM
"""
import json
import os
from typing import Dict, List, Optional

class EBIOSDataLoader:
    """Chargeur de données EBIOS RM depuis JSON"""
    
    def __init__(self, templates_path: str = "data/ebios_templates.json"):
        """
        Initialise le chargeur
        
        Args:
            templates_path: Chemin vers le fichier JSON de templates
        """
        self.templates_path = templates_path
        self.data = {}
        self.load_templates()
    
    def load_templates(self):
        """Charge les templates depuis le fichier JSON"""
        if not os.path.exists(self.templates_path):
            raise FileNotFoundError(f"❌ Fichier {self.templates_path} introuvable")
        
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Templates EBIOS chargés depuis {self.templates_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"❌ JSON invalide: {e}")
        except Exception as e:
            raise Exception(f"❌ Erreur chargement templates: {e}")
    
    def get_all_data(self) -> Dict:
        """Retourne toutes les données chargées"""
        return self.data
    
    def get_gravite_scale(self, niveau: int) -> Optional[Dict]:
        """Retourne les détails d'un niveau de gravité"""
        echelles = self.data.get('echelles_gravite', [])
        for item in echelles:
            if item.get('niveau') == niveau:
                return item
        return None
    
    def get_all_gravite_scales(self) -> List[Dict]:
        """Retourne toutes les échelles de gravité"""
        return self.data.get('echelles_gravite', [])
    
    def get_sources_risque(self, type_sr: Optional[str] = None) -> List[Dict]:
        """
        Retourne les sources de risque (filtrées par type si spécifié)
        
        Args:
            type_sr: Type de source de risque (optionnel)
        
        Returns:
            Liste des sources de risque
        """
        sources = self.data.get('sources_risque', [])
        if type_sr:
            return [s for s in sources if s.get('type', '').lower() == type_sr.lower()]
        return sources
    
    def get_objectifs_vises(self) -> List[Dict]:
        """Retourne tous les objectifs visés"""
        return self.data.get('objectifs_vises', [])
    
    def get_objectif_vise_by_id(self, obj_id: str) -> Optional[Dict]:
        """Retourne un objectif visé par son ID"""
        objectifs = self.data.get('objectifs_vises', [])
        for obj in objectifs:
            if obj.get('id') == obj_id:
                return obj
        return None
    
    def get_mesures_securite(self, domaine: Optional[str] = None, 
                            type_mesure: Optional[str] = None) -> List[Dict]:
        """
        Retourne les mesures de sécurité (filtrées si spécifié)
        
        Args:
            domaine: Domaine de sécurité (optionnel)
            type_mesure: Type de mesure (Préventif, Détectif, Correctif) (optionnel)
        
        Returns:
            Liste des mesures de sécurité
        """
        mesures = self.data.get('mesures_securite', [])
        
        if domaine:
            mesures = [m for m in mesures if m.get('domaine', '').lower() == domaine.lower()]
        
        if type_mesure:
            mesures = [m for m in mesures if m.get('type', '').lower() == type_mesure.lower()]
        
        return mesures
    
    def get_mesure_by_id(self, mesure_id: str) -> Optional[Dict]:
        """Retourne une mesure par son ID"""
        mesures = self.data.get('mesures_securite', [])
        for mesure in mesures:
            if mesure.get('id') == mesure_id:
                return mesure
        return None
    
    def get_secteurs(self) -> List[Dict]:
        """Retourne tous les secteurs"""
        return self.data.get('secteurs', [])
    
    def get_secteur(self, nom_secteur: str) -> Optional[Dict]:
        """
        Retourne les informations d'un secteur
        
        Args:
            nom_secteur: Nom du secteur (insensible à la casse)
        
        Returns:
            Dictionnaire avec les infos du secteur ou None
        """
        secteurs = self.data.get('secteurs', [])
        for secteur in secteurs:
            if secteur.get('nom', '').lower() == nom_secteur.lower():
                return secteur
        return None
    
    def get_cas_usage_secteur(self, secteur: str) -> Optional[Dict]:
        """
        Retourne un cas d'usage complet pour un secteur
        Alias de get_secteur pour compatibilité
        """
        return self.get_secteur(secteur)
    
    def get_reglementations(self) -> List[Dict]:
        """Retourne toutes les réglementations"""
        return self.data.get('reglementations', [])
    
    def get_reglementation(self, nom_reg: str) -> Optional[Dict]:
        """
        Retourne les infos sur une réglementation
        
        Args:
            nom_reg: Nom de la réglementation (ex: RGPD, NIS2)
        
        Returns:
            Dictionnaire avec les infos de la réglementation
        """
        regs = self.data.get('reglementations', [])
        for reg in regs:
            if reg.get('nom', '').upper() == nom_reg.upper():
                return reg
        return None
    
    def get_kpis(self) -> List[Dict]:
        """Retourne les KPIs prédéfinis"""
        return self.data.get('kpis', [])
    
    def get_types_parties_prenantes(self) -> List[str]:
        """Retourne les types de parties prenantes"""
        return self.data.get('types_parties_prenantes', [])
    
    def get_techniques_mitre(self, tactic: Optional[str] = None) -> List[Dict]:
        """
        Retourne les techniques MITRE ATT&CK
        
        Args:
            tactic: Tactique MITRE (optionnel)
        
        Returns:
            Liste des techniques
        """
        techniques = self.data.get('mitre_techniques', [])
        if tactic:
            return [t for t in techniques if t.get('tactic', '').lower() == tactic.lower()]
        return techniques
    
    def search_templates(self, keyword: str) -> Dict:
        """
        Recherche un mot-clé dans tous les templates
        
        Args:
            keyword: Mot-clé à rechercher
        
        Returns:
            Dict avec les résultats par catégorie
        """
        keyword_lower = keyword.lower()
        results = {
            'sources_risque': [],
            'objectifs_vises': [],
            'mesures_securite': [],
            'secteurs': []
        }
        
        # Recherche dans sources de risque
        for sr in self.get_sources_risque():
            if keyword_lower in str(sr).lower():
                results['sources_risque'].append(sr)
        
        # Recherche dans objectifs
        for ov in self.get_objectifs_vises():
            if keyword_lower in str(ov).lower():
                results['objectifs_vises'].append(ov)
        
        # Recherche dans mesures
        for mesure in self.get_mesures_securite():
            if keyword_lower in str(mesure).lower():
                results['mesures_securite'].append(mesure)
        
        # Recherche dans secteurs
        for secteur in self.get_secteurs():
            if keyword_lower in str(secteur).lower():
                results['secteurs'].append(secteur)
        
        return results
    
    def get_statistics(self) -> Dict:
        """Retourne des statistiques sur les templates chargés"""
        return {
            'nb_sources_risque': len(self.get_sources_risque()),
            'nb_objectifs_vises': len(self.get_objectifs_vises()),
            'nb_mesures_securite': len(self.get_mesures_securite()),
            'nb_secteurs': len(self.get_secteurs()),
            'nb_reglementations': len(self.get_reglementations()),
            'nb_echelles_gravite': len(self.get_all_gravite_scales())
        }
