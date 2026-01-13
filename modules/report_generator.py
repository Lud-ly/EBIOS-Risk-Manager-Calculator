"""
Module de génération de rapports EBIOS RM
"""
from fpdf import FPDF
from typing import Dict, List
from datetime import datetime
import os

class EBIOSReportGenerator(FPDF):
    """Générateur de rapports PDF EBIOS RM"""
    
    def header(self):
        """En-tête du PDF"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Rapport EBIOS Risk Manager', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        """Pied de page du PDF"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def chapter_title(self, title: str):
        """Titre de chapitre"""
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1)
        self.ln(2)
    
    def chapter_body(self, body: str):
        """Corps de chapitre"""
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

class EBIOSReportWriter:
    """Écrivain de rapport EBIOS RM complet"""
    
    def __init__(self, metadata: Dict, workshop_data: Dict):
        """
        Initialise le générateur de rapport
        
        Args:
            metadata: Métadonnées de l'étude
            workshop_data: Données des 5 ateliers
        """
        self.metadata = metadata
        self.data = workshop_data
        self.pdf = EBIOSReportGenerator()
    
    def generate_report(self, filename: str) -> str:
        """
        Génère le rapport PDF complet
        
        Returns:
            Chemin du fichier généré
        """
        self.pdf.add_page()
        
        # Page de garde
        self._generate_cover_page()
        
        # Synthèse exécutive
        self.pdf.add_page()
        self._generate_executive_summary()
        
        # Atelier 1
        self.pdf.add_page()
        self._generate_workshop1_report()
        
        # Atelier 2
        self.pdf.add_page()
        self._generate_workshop2_report()
        
        # Atelier 3 (si disponible)
        if self.data.get('workshop3'):
            self.pdf.add_page()
            self._generate_workshop3_report()
        
        # Atelier 4 (si disponible)
        if self.data.get('workshop4'):
            self.pdf.add_page()
            self._generate_workshop4_report()
        
        # Synthèse des risques
        self.pdf.add_page()
        self._generate_risk_synthesis()
        
        # Plan de traitement
        self.pdf.add_page()
        self._generate_treatment_plan()
        
        # Sauvegarder
        os.makedirs('data/assessments', exist_ok=True)
        filepath = f"data/assessments/{filename}_rapport.pdf"
        self.pdf.output(filepath)
        
        return filepath
    
    def _generate_cover_page(self):
        """Génère la page de garde"""
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 60, '', 0, 1)  # Espace
        self.pdf.cell(0, 15, 'EBIOS Risk Manager', 0, 1, 'C')
        
        self.pdf.set_font('Arial', 'B', 18)
        self.pdf.cell(0, 10, 'Analyse de Risques Cyber', 0, 1, 'C')
        
        self.pdf.ln(20)
        
        self.pdf.set_font('Arial', '', 14)
        self.pdf.cell(0, 10, f"Organisation: {self.metadata.get('organisme', 'N/A')}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Périmètre: {self.metadata.get('perimetre', 'N/A')}", 0, 1, 'C')
        self.pdf.cell(0, 10, f"Date: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, 'C')
        
        self.pdf.ln(40)
        
        self.pdf.set_font('Arial', 'I', 10)
        self.pdf.cell(0, 10, 'Confidentiel - Usage interne uniquement', 0, 1, 'C')
    
    def _generate_executive_summary(self):
        """Génère la synthèse exécutive"""
        self.pdf.chapter_title('1. Synthèse Exécutive')
        
        summary = f"""
Cette analyse de risques a été conduite selon la méthodologie EBIOS Risk Manager (ANSSI 2018).

Périmètre: {self.metadata.get('perimetre', 'N/A')}
Responsable: {self.metadata.get('responsable', 'N/A')}

L'étude a permis d'identifier les risques cyber majeurs pesant sur l'organisation et de 
définir un plan de traitement adapté.
"""
        
        self.pdf.chapter_body(summary)
    
    def _generate_workshop1_report(self):
        """Génère le rapport de l'atelier 1"""
        self.pdf.chapter_title('2. Atelier 1 - Cadrage et Socle de Sécurité')
        
        w1 = self.data.get('workshop1', {})
        
        body = f"""
Missions critiques identifiées: {len(w1.get('missions', []))}
Valeurs métier: {len(w1.get('valeurs_metier', []))}
Biens supports: {len(w1.get('biens_supports', []))}
Événements redoutés: {len(w1.get('evenements_redoutes', []))}

Taux de conformité du socle de sécurité: {w1.get('socle_securite', {}).get('taux_conformite', 0)}%
"""
        
        self.pdf.chapter_body(body)
    
    def _generate_workshop2_report(self):
        """Génère le rapport de l'atelier 2"""
        self.pdf.chapter_title('3. Atelier 2 - Sources de Risque et Objectifs Visés')
        
        w2 = self.data.get('workshop2', {})
        
        body = f"""
Sources de risque identifiées: {len(w2.get('sources_risque', []))}
Objectifs visés: {len(w2.get('objectifs_vises', []))}
Scénarios stratégiques: {len(w2.get('scenarios_strategiques', []))}
"""
        
        self.pdf.chapter_body(body)
        
        # Top scénarios
        scenarios = w2.get('scenarios_strategiques', [])[:5]
        if scenarios:
            self.pdf.set_font('Arial', 'B', 12)
            self.pdf.cell(0, 8, 'Top 5 des scénarios critiques:', 0, 1)
            self.pdf.set_font('Arial', '', 10)
            
            for i, scenario in enumerate(scenarios, 1):
                self.pdf.cell(0, 6, f"{i}. [{scenario['niveau_risque']}] {scenario['source_risque']} -> {scenario['objectif_vise']}", 0, 1)
    
    def _generate_workshop3_report(self):
        """Génère le rapport de l'atelier 3"""
        self.pdf.chapter_title('4. Atelier 3 - Écosystème et Parties Prenantes')
        
        w3 = self.data.get('workshop3', {})
        
        body = f"""
Parties prenantes cartographiées: {len(w3.get('parties_prenantes', []))}
Parties prenantes critiques: {len([pp for pp in w3.get('parties_prenantes', []) if pp.get('niveau_criticite') in ['Élevé', 'Critique']])}
Points d'entrée identifiés: {len(w3.get('ecosysteme', {}).get('points_entree', []))}
"""
        
        self.pdf.chapter_body(body)
    
    def _generate_workshop4_report(self):
        """Génère le rapport de l'atelier 4"""
        self.pdf.chapter_title('5. Atelier 4 - Scénarios Opérationnels')
        
        w4 = self.data.get('workshop4', {})
        
        stats = w4.get('statistics', {})
        
        body = f"""
Scénarios opérationnels détaillés: {stats.get('nb_scenarios_operationnels', 0)}
Actions élémentaires (TTP): {stats.get('nb_actions_elementaires', 0)}
Mesures de sécurité existantes: {stats.get('nb_mesures_existantes', 0)}

Taux de couverture: {stats.get('taux_couverture', 0)}%
Gaps identifiés: {stats.get('nb_gaps', 0)}
"""
        
        self.pdf.chapter_body(body)
    
    def _generate_risk_synthesis(self):
        """Génère la synthèse des risques"""
        self.pdf.chapter_title('6. Synthèse des Risques')
        
        w4 = self.data.get('workshop4', {})
        risques = w4.get('synthese_risques', [])
        
        if risques:
            body = f"Nombre total de risques: {len(risques)}\n\n"
            
            # Répartition par niveau
            niveaux = {}
            for risque in risques:
                niveau = risque['niveau']
                niveaux[niveau] = niveaux.get(niveau, 0) + 1
            
            body += "Répartition par niveau:\n"
            for niveau, count in sorted(niveaux.items(), key=lambda x: x[1], reverse=True):
                body += f"  - {niveau}: {count}\n"
            
            self.pdf.chapter_body(body)
    
    def _generate_treatment_plan(self):
        """Génère le plan de traitement"""
        self.pdf.chapter_title('7. Plan de Traitement des Risques')
        
        body = """
Ce plan de traitement doit être défini en atelier 5 avec la direction et les responsables métier.

Les options de traitement sont:
- Atténuation (réduction du risque)
- Transfert (assurance, externalisation)
- Évitement (abandon de l'activité à risque)
- Acceptation (risque assumé)

Les risques critiques et élevés doivent être traités en priorité.
"""
        
        self.pdf.chapter_body(body)

def generate_full_report(metadata: Dict, workshop_data: Dict, filename: str) -> str:
    """
    Fonction helper pour générer un rapport complet
    
    Args:
        metadata: Métadonnées de l'étude
        workshop_data: Données des ateliers
        filename: Nom du fichier de sortie
    
    Returns:
        Chemin du fichier généré
    """
    writer = EBIOSReportWriter(metadata, workshop_data)
    return writer.generate_report(filename)
