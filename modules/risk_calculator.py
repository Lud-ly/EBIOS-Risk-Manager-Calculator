"""
Module de calcul de risques EBIOS RM
"""
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

class RiskCalculator:
    """Calculateur de risques selon EBIOS RM"""
    
    # Matrice de risque EBIOS RM (Gravité × Vraisemblance)
    RISK_MATRIX = np.array([
        [1, 1, 2, 2],  # Gravité 1
        [1, 2, 2, 3],  # Gravité 2
        [2, 2, 3, 4],  # Gravité 3
        [2, 3, 4, 4]   # Gravité 4
    ])
    
    @staticmethod
    def calculate_risk_level(gravite: int, vraisemblance: int) -> Tuple[int, str]:
        """
        Calcule le niveau de risque selon la matrice EBIOS RM
        
        Args:
            gravite: Gravité (1-4)
            vraisemblance: Vraisemblance (1-4)
        
        Returns:
            (score, niveau) où score est 1-4 et niveau est Faible/Acceptable/Modéré/Critique
        """
        if not (1 <= gravite <= 4 and 1 <= vraisemblance <= 4):
            raise ValueError("Gravité et vraisemblance doivent être entre 1 et 4")
        
        score = RiskCalculator.RISK_MATRIX[gravite - 1][vraisemblance - 1]
        
        levels = {
            1: "Faible",
            2: "Acceptable", 
            3: "Modéré",
            4: "Critique"
        }
        
        return score, levels[score]
    
    @staticmethod
    def calculate_risk_score_extended(gravite: int, vraisemblance: int) -> Dict:
        """
        Calcule le score de risque avec informations détaillées
        
        Args:
            gravite: Gravité (1-4)
            vraisemblance: Vraisemblance (1-4)
        
        Returns:
            Dict avec score, niveau, priorité et recommandation
        """
        score, niveau = RiskCalculator.calculate_risk_level(gravite, vraisemblance)
        
        # Déterminer la priorité
        if score == 4:
            priorite = 0  # Urgent
            action = "Traiter immédiatement"
            delai = "< 1 mois"
        elif score == 3:
            priorite = 1  # Haute
            action = "Traiter en priorité"
            delai = "< 3 mois"
        elif score == 2:
            priorite = 2  # Moyenne
            action = "Surveiller et planifier"
            delai = "< 6 mois"
        else:
            priorite = 3  # Basse
            action = "Acceptation possible"
            delai = "< 12 mois ou accepter"
        
        return {
            'score': score,
            'niveau': niveau,
            'gravite': gravite,
            'vraisemblance': vraisemblance,
            'priorite': priorite,
            'action_recommandee': action,
            'delai_recommande': delai
        }
    
    @staticmethod
    def calculate_residual_risk(risque_initial: int, 
                               efficacite_mesures: float) -> Tuple[int, str, float]:
        """
        Calcule le risque résiduel après application de mesures
        
        Args:
            risque_initial: Niveau de risque initial (1-4)
            efficacite_mesures: Efficacité des mesures (0.0 à 1.0)
        
        Returns:
            (score_residuel, niveau, reduction_pct)
        """
        if not 0.0 <= efficacite_mesures <= 1.0:
            raise ValueError("L'efficacité doit être entre 0.0 et 1.0")
        
        if not 1 <= risque_initial <= 4:
            raise ValueError("Le risque initial doit être entre 1 et 4")
        
        # Réduction du risque proportionnelle à l'efficacité
        reduction = risque_initial * efficacite_mesures
        risque_residuel = max(1, round(risque_initial - reduction))
        
        levels = {1: "Faible", 2: "Acceptable", 3: "Modéré", 4: "Critique"}
        reduction_pct = (reduction / risque_initial) * 100
        
        return risque_residuel, levels[risque_residuel], round(reduction_pct, 1)
    
    @staticmethod
    def calculate_roi_measure(cout_mesure: float, risque_evite: int,
                             cout_incident_estime: float) -> Dict:
        """
        Calcule le ROI d'une mesure de sécurité
        
        Args:
            cout_mesure: Coût de la mesure (€)
            risque_evite: Niveau de risque évité (1-4)
            cout_incident_estime: Coût estimé de l'incident (€)
        
        Returns:
            Dict avec ROI, break-even et recommandation
        """
        # Gain estimé = risque évité × coût incident
        gain_estime = (risque_evite / 4.0) * cout_incident_estime
        
        # ROI = (Gain - Coût) / Coût
        if cout_mesure > 0:
            roi = ((gain_estime - cout_mesure) / cout_mesure) * 100
        else:
            roi = float('inf')
        
        # Break-even (en années)
        if cout_mesure > 0 and gain_estime > 0:
            break_even = cout_mesure / gain_estime
        else:
            break_even = float('inf')
        
        # Recommandation
        if roi > 100:
            recommandation = "Investissement fortement recommandé"
        elif roi > 0:
            recommandation = "Investissement rentable"
        elif roi > -50:
            recommandation = "Investissement marginal"
        else:
            recommandation = "Investissement non rentable"
        
        return {
            'cout_mesure': cout_mesure,
            'gain_estime': gain_estime,
            'roi_pct': round(roi, 2),
            'break_even_years': round(break_even, 2),
            'recommandation': recommandation
        }
    
    @staticmethod
    def prioritize_risks(risks: List[Dict]) -> pd.DataFrame:
        """
        Priorise une liste de risques
        
        Args:
            risks: Liste de dicts avec 'id', 'gravite', 'vraisemblance'
        
        Returns:
            DataFrame pandas trié par priorité décroissante
        """
        if not risks:
            return pd.DataFrame()
        
        df = pd.DataFrame(risks)
        
        # Calculer le score de risque pour chaque ligne
        df['score_risque'] = df.apply(
            lambda row: RiskCalculator.calculate_risk_level(
                int(row['gravite']), int(row['vraisemblance'])
            )[0], axis=1
        )
        
        df['niveau_risque'] = df.apply(
            lambda row: RiskCalculator.calculate_risk_level(
                int(row['gravite']), int(row['vraisemblance'])
            )[1], axis=1
        )
        
        # Calculer la priorité (0 = le plus urgent)
        priorite_map = {'Critique': 0, 'Modéré': 1, 'Acceptable': 2, 'Faible': 3}
        df['priorite_num'] = df['niveau_risque'].map(priorite_map)
        
        # Trier par score décroissant, puis par gravité
        df = df.sort_values(['score_risque', 'gravite'], ascending=[False, False])
        df['priorite'] = range(1, len(df) + 1)
        
        return df
    
    @staticmethod
    def calculate_global_risk_exposure(risks: List[Dict]) -> Dict:
        """
        Calcule l'exposition globale au risque d'une organisation
        
        Args:
            risks: Liste de risques avec gravite et vraisemblance
        
        Returns:
            Dict avec statistiques d'exposition globale
        """
        if not risks:
            return {
                'exposition_globale': 0,
                'niveau': 'Aucun',
                'nb_risques_total': 0,
                'repartition': {},
                'risques_critiques_pct': 0
            }
        
        total_score = 0
        repartition = {'Critique': 0, 'Modéré': 0, 'Acceptable': 0, 'Faible': 0}
        
        for risk in risks:
            score, niveau = RiskCalculator.calculate_risk_level(
                risk['gravite'], risk['vraisemblance']
            )
            total_score += score
            repartition[niveau] += 1
        
        exposition_moyenne = round(total_score / len(risks), 2)
        
        # Déterminer le niveau global d'exposition
        if exposition_moyenne >= 3.5:
            niveau_global = "Critique"
        elif exposition_moyenne >= 2.5:
            niveau_global = "Élevé"
        elif exposition_moyenne >= 1.5:
            niveau_global = "Modéré"
        else:
            niveau_global = "Faible"
        
        risques_critiques_pct = round((repartition['Critique'] / len(risks)) * 100, 1)
        
        return {
            'exposition_globale': exposition_moyenne,
            'niveau': niveau_global,
            'nb_risques_total': len(risks),
            'repartition': repartition,
            'risques_critiques_pct': risques_critiques_pct,
            'score_total': total_score
        }
    
    @staticmethod
    def calculate_ale(sle: float, aro: float) -> Dict:
        """
        Calcule l'Annual Loss Expectancy (ALE)
        
        ALE = SLE × ARO
        SLE = Single Loss Expectancy (coût d'un incident)
        ARO = Annual Rate of Occurrence (fréquence annuelle)
        
        Args:
            sle: Coût d'un incident unique (€)
            aro: Taux d'occurrence annuel (ex: 0.1 = 1 fois tous les 10 ans)
        
        Returns:
            Dict avec ALE et interprétation
        """
        ale = sle * aro
        
        # Interprétation
        if ale > 100000:
            interpretation = "Risque financier majeur - Traitement prioritaire"
        elif ale > 50000:
            interpretation = "Risque financier significatif - Traitement recommandé"
        elif ale > 10000:
            interpretation = "Risque financier modéré - Surveillance nécessaire"
        else:
            interpretation = "Risque financier faible - Acceptation possible"
        
        return {
            'sle': sle,
            'aro': aro,
            'ale': round(ale, 2),
            'ale_mensuelle': round(ale / 12, 2),
            'interpretation': interpretation
        }
    
    @staticmethod
    def compare_scenarios(scenario1: Dict, scenario2: Dict) -> Dict:
        """
        Compare deux scénarios de risque
        
        Args:
            scenario1: {'nom': str, 'gravite': int, 'vraisemblance': int}
            scenario2: {'nom': str, 'gravite': int, 'vraisemblance': int}
        
        Returns:
            Comparaison des deux scénarios
        """
        score1, niveau1 = RiskCalculator.calculate_risk_level(
            scenario1['gravite'], scenario1['vraisemblance']
        )
        score2, niveau2 = RiskCalculator.calculate_risk_level(
            scenario2['gravite'], scenario2['vraisemblance']
        )
        
        if score1 > score2:
            plus_critique = scenario1['nom']
            difference = score1 - score2
        elif score2 > score1:
            plus_critique = scenario2['nom']
            difference = score2 - score1
        else:
            plus_critique = "Équivalents"
            difference = 0
        
        return {
            'scenario1': {
                'nom': scenario1['nom'],
                'score': score1,
                'niveau': niveau1
            },
            'scenario2': {
                'nom': scenario2['nom'],
                'score': score2,
                'niveau': niveau2
            },
            'plus_critique': plus_critique,
            'difference': difference
        }
    
    @staticmethod
    def calculate_composite_risk(risques_lies: List[Dict]) -> Dict:
        """
        Calcule le risque composite pour des risques interdépendants
        
        Args:
            risques_lies: Liste de risques avec gravite, vraisemblance et poids
        
        Returns:
            Risque composite calculé
        """
        if not risques_lies:
            return {'score': 0, 'niveau': 'Aucun'}
        
        total_poids = sum(r.get('poids', 1) for r in risques_lies)
        score_composite = 0
        
        for risque in risques_lies:
            score, _ = RiskCalculator.calculate_risk_level(
                risque['gravite'], risque['vraisemblance']
            )
            poids = risque.get('poids', 1)
            score_composite += score * (poids / total_poids)
        
        score_composite = round(score_composite)
        
        levels = {1: "Faible", 2: "Acceptable", 3: "Modéré", 4: "Critique"}
        niveau_composite = levels.get(score_composite, "Indéterminé")
        
        return {
            'score_composite': score_composite,
            'niveau_composite': niveau_composite,
            'nb_risques_lies': len(risques_lies)
        }
