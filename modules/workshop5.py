"""
Atelier 5 EBIOS RM : Traitement du risque et plan d'action
"""
from typing import Dict, List, Optional
import json
from datetime import datetime

class Workshop5:
    """Gestion de l'atelier 5 EBIOS RM - Traitement du risque"""
    
    def __init__(self):
        """Initialise l'atelier 5"""
        self.assessment = {
            'risques': [],
            'mesures_traitement': [],
            'plan_traitement': [],
            'risques_residuels': [],
            'risques_acceptes': [],
            'budget_estime': 0.0,
            'kpis': []
        }
    
    def add_risque(self, risque_id: str, nom: str, 
                   gravite: int, vraisemblance: int,
                   scenario_ref: str) -> Dict:
        """
        Ajoute un risque à traiter
        
        Args:
            risque_id: Identifiant unique du risque
            nom: Nom/description du risque
            gravite: Gravité (1-4)
            vraisemblance: Vraisemblance (1-4)
            scenario_ref: Référence au scénario (atelier 2/3/4)
        
        Returns:
            Le risque ajouté
        """
        # Calculer le score de risque (matrice EBIOS RM)
        score_brut = self._calculate_risk_score(gravite, vraisemblance)
        
        risque = {
            'id': risque_id,
            'nom': nom,
            'gravite': gravite,
            'vraisemblance': vraisemblance,
            'score_brut': score_brut,
            'niveau_brut': self._get_risk_level(score_brut),
            'scenario_reference': scenario_ref,
            'statut': 'Non traité',
            'option_traitement': None,
            'mesures_associees': [],
            'date_identification': datetime.now().isoformat()
        }
        
        self.assessment['risques'].append(risque)
        return risque
    
    def _calculate_risk_score(self, gravite: int, vraisemblance: int) -> int:
        """Calcule le score de risque selon la matrice EBIOS RM"""
        # Matrice 4x4 EBIOS RM
        matrice = [
            [1, 1, 2, 2],  # Gravité 1
            [1, 2, 2, 3],  # Gravité 2
            [2, 2, 3, 4],  # Gravité 3
            [2, 3, 4, 4]   # Gravité 4
        ]
        
        return matrice[gravite - 1][vraisemblance - 1]
    
    def _get_risk_level(self, score: int) -> str:
        """Détermine le niveau de risque"""
        if score == 1:
            return "Faible"
        elif score == 2:
            return "Acceptable"
        elif score == 3:
            return "Modéré"
        elif score == 4:
            return "Critique"
        else:
            return "Indéterminé"
    
    def define_traitement(self, risque_id: str, option: str,
                          justification: str) -> Dict:
        """
        Définit l'option de traitement pour un risque
        
        Args:
            risque_id: ID du risque
            option: Option choisie (Atténuation, Transfert, Évitement, Acceptation)
            justification: Justification de la décision
        
        Returns:
            Le risque mis à jour
        """
        options_valides = ['Atténuation', 'Transfert', 'Évitement', 'Acceptation']
        
        if option not in options_valides:
            raise ValueError(f"Option invalide. Options valides: {options_valides}")
        
        risque = next((r for r in self.assessment['risques'] 
                      if r['id'] == risque_id), None)
        
        if not risque:
            raise ValueError(f"Risque {risque_id} non trouvé")
        
        risque['option_traitement'] = option
        risque['justification'] = justification
        risque['statut'] = 'Stratégie définie'
        risque['date_decision'] = datetime.now().isoformat()
        
        return risque
    
    def add_mesure_traitement(self, nom: str, type_mesure: str,
                             description: str, cout_estime: float,
                             efficacite: float, delai_mise_en_oeuvre: int,
                             responsable: str) -> Dict:
        """
        Ajoute une mesure de traitement
        
        Args:
            nom: Nom de la mesure
            type_mesure: Type (Préventif, Détectif, Correctif, Dissuasif)
            description: Description détaillée
            cout_estime: Coût estimé en euros
            efficacite: Efficacité estimée (0.0 à 1.0)
            delai_mise_en_oeuvre: Délai en jours
            responsable: Responsable de la mise en œuvre
        
        Returns:
            La mesure créée
        """
        if not 0.0 <= efficacite <= 1.0:
            raise ValueError("L'efficacité doit être entre 0.0 et 1.0")
        
        mesure = {
            'id': f"M{len(self.assessment['mesures_traitement']) + 1}",
            'nom': nom,
            'type': type_mesure,
            'description': description,
            'cout_estime': cout_estime,
            'efficacite': efficacite,
            'delai_mise_en_oeuvre': delai_mise_en_oeuvre,
            'responsable': responsable,
            'statut': 'Planifiée',
            'risques_couverts': [],
            'date_creation': datetime.now().isoformat()
        }
        
        self.assessment['mesures_traitement'].append(mesure)
        self.assessment['budget_estime'] += cout_estime
        
        return mesure
    
    def associate_mesure_to_risque(self, risque_id: str, mesure_id: str) -> bool:
        """
        Associe une mesure à un risque
        
        Args:
            risque_id: ID du risque
            mesure_id: ID de la mesure
        
        Returns:
            True si l'association a réussi
        """
        risque = next((r for r in self.assessment['risques'] 
                      if r['id'] == risque_id), None)
        mesure = next((m for m in self.assessment['mesures_traitement'] 
                      if m['id'] == mesure_id), None)
        
        if not risque or not mesure:
            return False
        
        if mesure_id not in risque['mesures_associees']:
            risque['mesures_associees'].append(mesure_id)
        
        if risque_id not in mesure['risques_couverts']:
            mesure['risques_couverts'].append(risque_id)
        
        return True
    
    def calculate_risque_residuel(self, risque_id: str) -> Dict:
        """
        Calcule le risque résiduel après application des mesures
        
        Args:
            risque_id: ID du risque
        
        Returns:
            Dict avec le risque résiduel calculé
        """
        risque = next((r for r in self.assessment['risques'] 
                      if r['id'] == risque_id), None)
        
        if not risque:
            raise ValueError(f"Risque {risque_id} non trouvé")
        
        # Récupérer les mesures associées
        mesures = [
            m for m in self.assessment['mesures_traitement']
            if m['id'] in risque['mesures_associees']
        ]
        
        if not mesures:
            # Pas de mesures = risque résiduel = risque brut
            risque_residuel = {
                'risque_id': risque_id,
                'score_brut': risque['score_brut'],
                'score_residuel': risque['score_brut'],
                'niveau_residuel': risque['niveau_brut'],
                'reduction': 0.0,
                'mesures_appliquees': []
            }
        else:
            # Calculer l'efficacité combinée
            efficacite_totale = min(0.95, sum(m['efficacite'] for m in mesures))
            
            # Réduction du score
            reduction = risque['score_brut'] * efficacite_totale
            score_residuel = max(1, round(risque['score_brut'] - reduction))
            
            risque_residuel = {
                'risque_id': risque_id,
                'score_brut': risque['score_brut'],
                'score_residuel': score_residuel,
                'niveau_residuel': self._get_risk_level(score_residuel),
                'reduction': round(reduction, 2),
                'reduction_pct': round((reduction / risque['score_brut']) * 100, 1),
                'mesures_appliquees': [m['id'] for m in mesures],
                'date_calcul': datetime.now().isoformat()
            }
        
        # Ajouter ou mettre à jour dans la liste des risques résiduels
        existing = next((r for r in self.assessment['risques_residuels'] 
                        if r['risque_id'] == risque_id), None)
        
        if existing:
            self.assessment['risques_residuels'].remove(existing)
        
        self.assessment['risques_residuels'].append(risque_residuel)
        
        return risque_residuel
    
    def accept_risque(self, risque_id: str, acceptant: str,
                     justification: str) -> Dict:
        """
        Formalise l'acceptation d'un risque
        
        Args:
            risque_id: ID du risque accepté
            acceptant: Nom de la personne/entité acceptant le risque
            justification: Justification de l'acceptation
        
        Returns:
            La déclaration d'acceptation
        """
        risque = next((r for r in self.assessment['risques'] 
                      if r['id'] == risque_id), None)
        
        if not risque:
            raise ValueError(f"Risque {risque_id} non trouvé")
        
        # Calculer le risque résiduel
        risque_res = self.calculate_risque_residuel(risque_id)
        
        acceptation = {
            'risque_id': risque_id,
            'nom_risque': risque['nom'],
            'score_residuel': risque_res['score_residuel'],
            'niveau_residuel': risque_res['niveau_residuel'],
            'acceptant': acceptant,
            'justification': justification,
            'date_acceptation': datetime.now().isoformat(),
            'date_revue': self._calculate_review_date(risque_res['score_residuel']),
            'conditions': []
        }
        
        self.assessment['risques_acceptes'].append(acceptation)
        
        # Mettre à jour le statut du risque
        risque['statut'] = 'Accepté'
        
        return acceptation
    
    def _calculate_review_date(self, score_residuel: int) -> str:
        """Détermine la fréquence de revue selon le score résiduel"""
        from datetime import timedelta
        
        today = datetime.now()
        
        if score_residuel >= 3:
            # Risques modérés/critiques: revue trimestrielle
            next_review = today + timedelta(days=90)
        else:
            # Risques faibles: revue annuelle
            next_review = today + timedelta(days=365)
        
        return next_review.isoformat()
    
    def create_plan_traitement(self) -> Dict:
        """
        Crée le plan de traitement des risques (PTR)
        
        Returns:
            Le plan de traitement complet
        """
        # Prioriser les mesures
        mesures_prioritaires = sorted(
            self.assessment['mesures_traitement'],
            key=lambda m: (len(m['risques_couverts']), -m['cout_estime']),
            reverse=True
        )
        
        plan = {
            'date_creation': datetime.now().isoformat(),
            'budget_total': self.assessment['budget_estime'],
            'nombre_mesures': len(self.assessment['mesures_traitement']),
            'nombre_risques': len(self.assessment['risques']),
            'phases': self._create_phases(mesures_prioritaires),
            'timeline': self._create_timeline(mesures_prioritaires),
            'responsabilites': self._extract_responsabilites(),
            'criteres_succes': self._define_success_criteria()
        }
        
        self.assessment['plan_traitement'] = plan
        
        return plan
    
    def _create_phases(self, mesures: List[Dict]) -> List[Dict]:
        """Crée les phases du plan de traitement"""
        phases = [
            {'nom': 'Phase 1 - Urgences (0-3 mois)', 'mesures': []},
            {'nom': 'Phase 2 - Court terme (3-6 mois)', 'mesures': []},
            {'nom': 'Phase 3 - Moyen terme (6-12 mois)', 'mesures': []}
        ]
        
        for mesure in mesures:
            delai = mesure['delai_mise_en_oeuvre']
            
            if delai <= 90:
                phases[0]['mesures'].append(mesure['id'])
            elif delai <= 180:
                phases[1]['mesures'].append(mesure['id'])
            else:
                phases[2]['mesures'].append(mesure['id'])
        
        return phases
    
    def _create_timeline(self, mesures: List[Dict]) -> List[Dict]:
        """Crée la timeline du plan"""
        timeline = []
        
        for mesure in mesures[:10]:  # Top 10 des mesures
            timeline.append({
                'mesure_id': mesure['id'],
                'nom': mesure['nom'],
                'debut_prevu': datetime.now().isoformat(),
                'fin_prevue': self._calculate_end_date(mesure['delai_mise_en_oeuvre']),
                'responsable': mesure['responsable']
            })
        
        return timeline
    
    def _calculate_end_date(self, delai_jours: int) -> str:
        """Calcule la date de fin prévue"""
        from datetime import timedelta
        
        end_date = datetime.now() + timedelta(days=delai_jours)
        return end_date.isoformat()
    
    def _extract_responsabilites(self) -> Dict:
        """Extrait les responsabilités (matrice RACI)"""
        responsables = {}
        
        for mesure in self.assessment['mesures_traitement']:
            resp = mesure['responsable']
            if resp not in responsables:
                responsables[resp] = {
                    'mesures_responsable': [],
                    'budget_total': 0.0
                }
            
            responsables[resp]['mesures_responsable'].append(mesure['id'])
            responsables[resp]['budget_total'] += mesure['cout_estime']
        
        return responsables
    
    def _define_success_criteria(self) -> List[str]:
        """Définit les critères de succès du plan"""
        return [
            "Réduction de 50% des risques critiques dans les 6 mois",
            "100% des mesures Phase 1 implémentées dans les 3 mois",
            "Taux de conformité au socle de sécurité > 80%",
            "0 risque critique résiduel accepté",
            "Budget respecté à +/- 10%"
        ]
    
    def add_kpi(self, nom: str, description: str, 
                formule: str, objectif: str, 
                frequence_mesure: str) -> Dict:
        """
        Ajoute un KPI de suivi
        
        Args:
            nom: Nom du KPI
            description: Description
            formule: Formule de calcul
            objectif: Valeur cible
            frequence_mesure: Fréquence de mesure
        
        Returns:
            Le KPI créé
        """
        kpi = {
            'id': f"KPI{len(self.assessment['kpis']) + 1}",
            'nom': nom,
            'description': description,
            'formule': formule,
            'objectif': objectif,
            'frequence_mesure': frequence_mesure,
            'responsable_mesure': '',
            'valeur_actuelle': None,
            'historique': []
        }
        
        self.assessment['kpis'].append(kpi)
        return kpi
    
    def get_statistics(self) -> Dict:
        """Retourne les statistiques de l'atelier 5"""
        risques_critiques = [r for r in self.assessment['risques'] 
                            if r['niveau_brut'] == 'Critique']
        
        risques_traites = [r for r in self.assessment['risques'] 
                          if r['option_traitement'] is not None]
        
        # Répartition par option
        options_count = {}
        for risque in risques_traites:
            option = risque['option_traitement']
            options_count[option] = options_count.get(option, 0) + 1
        
        # Calcul ROI global
        risques_evites = sum(
            r['score_brut'] - res['score_residuel']
            for res in self.assessment['risques_residuels']
            for r in self.assessment['risques']
            if r['id'] == res['risque_id']
        )
        
        roi = 0.0
        if self.assessment['budget_estime'] > 0:
            roi = (risques_evites * 10000 - self.assessment['budget_estime']) / self.assessment['budget_estime']
        
        return {
            'nb_risques_total': len(self.assessment['risques']),
            'nb_risques_critiques': len(risques_critiques),
            'nb_risques_traites': len(risques_traites),
            'nb_mesures': len(self.assessment['mesures_traitement']),
            'nb_risques_acceptes': len(self.assessment['risques_acceptes']),
            'budget_total': self.assessment['budget_estime'],
            'repartition_options': options_count,
            'roi_estime': round(roi, 2),
            'taux_traitement': round((len(risques_traites) / max(1, len(self.assessment['risques']))) * 100, 1)
        }
    
    def get_dashboard_summary(self) -> Dict:
        """Retourne un résumé pour le tableau de bord"""
        stats = self.get_statistics()
        
        # Top 5 des risques résiduels
        top_residuels = sorted(
            self.assessment['risques_residuels'],
            key=lambda x: x['score_residuel'],
            reverse=True
        )[:5]
        
        # Mesures les plus efficaces
        top_mesures = sorted(
            self.assessment['mesures_traitement'],
            key=lambda x: (len(x['risques_couverts']), x['efficacite']),
            reverse=True
        )[:5]
        
        return {
            'statistiques': stats,
            'top_risques_residuels': top_residuels,
            'top_mesures': top_mesures,
            'plan_status': 'Défini' if self.assessment['plan_traitement'] else 'Non défini'
        }
    
    def validate_assessment(self) -> Dict:
        """Valide la complétude de l'atelier 5"""
        errors = []
        warnings = []
        
        # Vérifications obligatoires
        if len(self.assessment['risques']) == 0:
            errors.append("Aucun risque identifié")
        
        risques_non_traites = [r for r in self.assessment['risques'] 
                               if r['option_traitement'] is None]
        if risques_non_traites:
            warnings.append(f"{len(risques_non_traites)} risques sans option de traitement définie")
        
        if len(self.assessment['mesures_traitement']) == 0:
            warnings.append("Aucune mesure de traitement définie")
        
        if not self.assessment['plan_traitement']:
            warnings.append("Plan de traitement non créé")
        
        # Vérifier les risques critiques
        risques_critiques_non_traites = [
            r for r in self.assessment['risques']
            if r['niveau_brut'] == 'Critique' and r['option_traitement'] is None
        ]
        
        if risques_critiques_non_traites:
            errors.append(f"{len(risques_critiques_non_traites)} risques critiques non traités")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def save(self, filename: str) -> str:
        """Sauvegarde l'atelier 5"""
        import os
        os.makedirs('data/assessments', exist_ok=True)
        
        filepath = f"data/assessments/{filename}_atelier5.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.assessment, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load(self, filename: str) -> Dict:
        """Charge une évaluation existante"""
        filepath = f"data/assessments/{filename}_atelier5.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            self.assessment = json.load(f)
        
        return self.assessment
    
    def export_ptr_excel(self, filename: str) -> str:
        """
        Exporte le Plan de Traitement des Risques en Excel
        
        Args:
            filename: Nom du fichier de sortie
        
        Returns:
            Chemin du fichier Excel généré
        """
        import pandas as pd
        import os
        
        # Préparer les données pour Excel
        risques_df = pd.DataFrame(self.assessment['risques'])
        mesures_df = pd.DataFrame(self.assessment['mesures_traitement'])
        residuels_df = pd.DataFrame(self.assessment['risques_residuels'])
        
        # Sauvegarder en Excel
        os.makedirs('data/assessments', exist_ok=True)
        filepath = f"data/assessments/{filename}_PTR.xlsx"
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            risques_df.to_excel(writer, sheet_name='Risques', index=False)
            mesures_df.to_excel(writer, sheet_name='Mesures', index=False)
            residuels_df.to_excel(writer, sheet_name='Risques Résiduels', index=False)
        
        return filepath
    
    def __str__(self) -> str:
        """Représentation string de l'atelier 5"""
        stats = self.get_statistics()
        return f"""
Atelier 5 EBIOS RM - Plan de Traitement des Risques
====================================================
Risques identifiés: {stats['nb_risques_total']}
  - Critiques: {stats['nb_risques_critiques']}
  - Traités: {stats['nb_risques_traites']}
  - Acceptés: {stats['nb_risques_acceptes']}

Mesures de traitement: {stats['nb_mesures']}
Budget total: {stats['budget_total']:,.2f} €
ROI estimé: {stats['roi_estime']}

Taux de traitement: {stats['taux_traitement']}%
"""
