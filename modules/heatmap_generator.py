"""
Module de génération de cartographies de risques (heatmaps)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from typing import List, Dict
import io
import base64

class HeatmapGenerator:
    """Générateur de heatmaps EBIOS RM"""
    
    # Couleurs selon EBIOS RM
    COLORS = {
        1: '#90EE90',  # Vert - Faible
        2: '#FFFF00',  # Jaune - Acceptable
        3: '#FFA500',  # Orange - Modéré
        4: '#FF0000'   # Rouge - Critique
    }
    
    @staticmethod
    def generate_risk_heatmap(risks: List[Dict], title: str = "Cartographie des Risques EBIOS RM") -> str:
        """
        Génère une heatmap des risques avec positionnement
        
        Args:
            risks: Liste de risques avec 'gravite' et 'vraisemblance'
            title: Titre du graphique
        
        Returns:
            Image base64 de la heatmap
        """
        # Créer une matrice 4x4 pour compter les risques
        heatmap_data = np.zeros((4, 4))
        
        # Compter les risques par case
        for risk in risks:
            g = risk['gravite'] - 1
            v = risk['vraisemblance'] - 1
            heatmap_data[3 - g][v] += 1  # Inverser Y pour avoir gravité croissante vers le haut
        
        # Créer la figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Matrice de risque EBIOS RM pour les couleurs
        risk_matrix = np.array([
            [1, 1, 2, 2],
            [1, 2, 2, 3],
            [2, 2, 3, 4],
            [2, 3, 4, 4]
        ])
        
        # Inverser pour l'affichage (gravité croissante vers le haut)
        risk_matrix_display = np.flipud(risk_matrix)
        
        # Créer une colormap personnalisée
        from matplotlib.colors import ListedColormap
        colors_list = [HeatmapGenerator.COLORS[i] for i in [1, 2, 3, 4]]
        cmap = ListedColormap(colors_list)
        
        # Afficher la matrice de base
        im = ax.imshow(risk_matrix_display, cmap=cmap, alpha=0.3, vmin=1, vmax=4)
        
        # Ajouter les annotations (nombre de risques)
        for i in range(4):
            for j in range(4):
                count = int(heatmap_data[i, j])
                if count > 0:
                    # Couleur du texte selon le fond
                    risk_level = risk_matrix_display[i, j]
                    text_color = 'white' if risk_level >= 3 else 'black'
                    
                    ax.text(j, i, str(count), ha="center", va="center",
                           color=text_color, fontsize=20, fontweight='bold')
        
        # Labels des axes
        vraisemblance_labels = ['Peu\nprobable\n(1)', 'Possible\n(2)', 
                               'Probable\n(3)', 'Très\nprobable\n(4)']
        gravite_labels = ['Critique\n(4)', 'Importante\n(3)', 
                         'Limitée\n(2)', 'Négligeable\n(1)']
        
        ax.set_xticks(np.arange(4))
        ax.set_yticks(np.arange(4))
        ax.set_xticklabels(vraisemblance_labels, fontsize=11)
        ax.set_yticklabels(gravite_labels, fontsize=11)
        
        # Labels des axes principaux
        ax.set_xlabel('Vraisemblance', fontsize=14, fontweight='bold')
        ax.set_ylabel('Gravité', fontsize=14, fontweight='bold')
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Grille
        ax.set_xticks(np.arange(4) - 0.5, minor=True)
        ax.set_yticks(np.arange(4) - 0.5, minor=True)
        ax.grid(which="minor", color="black", linestyle='-', linewidth=2)
        ax.tick_params(which="minor", size=0)
        
        # Légende
        legend_elements = [
            mpatches.Patch(facecolor=HeatmapGenerator.COLORS[1], label='Faible (1)'),
            mpatches.Patch(facecolor=HeatmapGenerator.COLORS[2], label='Acceptable (2)'),
            mpatches.Patch(facecolor=HeatmapGenerator.COLORS[3], label='Modéré (3)'),
            mpatches.Patch(facecolor=HeatmapGenerator.COLORS[4], label='Critique (4)')
        ]
        ax.legend(handles=legend_elements, loc='upper left', 
                 bbox_to_anchor=(1.05, 1), fontsize=10)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_sr_ov_matrix(cartographie: List[Dict], 
                              sources: List[Dict], 
                              objectifs: List[Dict]) -> str:
        """
        Génère une matrice Sources de Risque × Objectifs Visés
        
        Args:
            cartographie: Relations SR-OV avec pertinence
            sources: Liste des sources de risque
            objectifs: Liste des objectifs visés
        
        Returns:
            Image base64 de la matrice
        """
        if not sources or not objectifs:
            # Retourner une image vide avec message
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=16, color='gray')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
        
        # Créer la matrice
        matrix = np.zeros((len(sources), len(objectifs)))
        
        for relation in cartographie:
            sr_idx = next((i for i, s in enumerate(sources) 
                          if s['id'] == relation['sr_id']), None)
            ov_idx = next((i for i, o in enumerate(objectifs) 
                          if o['id'] == relation['ov_id']), None)
            
            if sr_idx is not None and ov_idx is not None:
                matrix[sr_idx][ov_idx] = relation.get('pertinence', 0)
        
        # Créer la figure
        fig, ax = plt.subplots(figsize=(max(14, len(objectifs) * 1.5), 
                                        max(10, len(sources) * 0.8)))
        
        # Labels
        sr_labels = [f"{s['nom'][:30]}..." if len(s['nom']) > 30 else s['nom'] 
                    for s in sources]
        ov_labels = [f"{o['nom'][:35]}..." if len(o['nom']) > 35 else o['nom'] 
                    for o in objectifs]
        
        # Heatmap avec seaborn
        sns.heatmap(matrix, annot=True, fmt='.0f', cmap='YlOrRd', 
                   xticklabels=ov_labels, yticklabels=sr_labels,
                   linewidths=0.5, linecolor='gray', ax=ax,
                   cbar_kws={'label': 'Pertinence (1-4)'},
                   vmin=0, vmax=4)
        
        ax.set_xlabel('Objectifs Visés', fontsize=13, fontweight='bold')
        ax.set_ylabel('Sources de Risque', fontsize=13, fontweight='bold')
        ax.set_title('Matrice SR × OV - EBIOS RM Atelier 2', 
                    fontsize=15, fontweight='bold', pad=15)
        
        plt.xticks(rotation=45, ha='right', fontsize=10)
        plt.yticks(rotation=0, fontsize=10)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_risk_evolution(historical_data: List[Dict]) -> str:
        """
        Génère un graphique d'évolution des risques dans le temps
        
        Args:
            historical_data: Liste de {date, nb_critiques, nb_eleves, nb_moderes, nb_faibles}
        
        Returns:
            Image base64 du graphique
        """
        if not historical_data:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Aucune donnée historique', 
                   ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
        
        # Préparer les données
        dates = [d['date'] for d in historical_data]
        critiques = [d.get('nb_critiques', 0) for d in historical_data]
        eleves = [d.get('nb_eleves', 0) for d in historical_data]
        moderes = [d.get('nb_moderes', 0) for d in historical_data]
        faibles = [d.get('nb_faibles', 0) for d in historical_data]
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 7))
        
        x = range(len(dates))
        
        ax.plot(x, critiques, marker='o', linewidth=2, color='#FF0000', label='Critiques')
        ax.plot(x, eleves, marker='s', linewidth=2, color='#FFA500', label='Élevés')
        ax.plot(x, moderes, marker='^', linewidth=2, color='#FFFF00', label='Modérés')
        ax.plot(x, faibles, marker='d', linewidth=2, color='#90EE90', label='Faibles')
        
        ax.set_xlabel('Période', fontsize=12, fontweight='bold')
        ax.set_ylabel('Nombre de risques', fontsize=12, fontweight='bold')
        ax.set_title('Évolution des Risques dans le Temps', fontsize=14, fontweight='bold')
        
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right')
        
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_risk_distribution_pie(risks: List[Dict]) -> str:
        """
        Génère un pie chart de la distribution des risques
        
        Args:
            risks: Liste de risques avec gravite et vraisemblance
        
        Returns:
            Image base64 du pie chart
        """
        from modules.risk_calculator import RiskCalculator
        
        if not risks:
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(0.5, 0.5, 'Aucun risque', 
                   ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
        
        # Compter par niveau
        repartition = {'Critique': 0, 'Modéré': 0, 'Acceptable': 0, 'Faible': 0}
        
        for risk in risks:
            _, niveau = RiskCalculator.calculate_risk_level(
                risk['gravite'], risk['vraisemblance']
            )
            repartition[niveau] += 1
        
        # Filtrer les niveaux avec 0 risques
        labels = []
        sizes = []
        colors_list = []
        
        color_map = {
            'Critique': '#FF0000',
            'Modéré': '#FFA500',
            'Acceptable': '#FFFF00',
            'Faible': '#90EE90'
        }
        
        for niveau in ['Critique', 'Modéré', 'Acceptable', 'Faible']:
            if repartition[niveau] > 0:
                labels.append(f"{niveau}\n({repartition[niveau]})")
                sizes.append(repartition[niveau])
                colors_list.append(color_map[niveau])
        
        # Créer le pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_list,
                                           autopct='%1.1f%%', startangle=90,
                                           textprops={'fontsize': 12, 'fontweight': 'bold'})
        
        ax.set_title('Distribution des Risques par Niveau', 
                    fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_domain_bar_chart(domain_scores: Dict[str, float]) -> str:
        """
        Génère un bar chart des scores par domaine
        
        Args:
            domain_scores: Dict {domaine: score_pourcentage}
        
        Returns:
            Image base64 du bar chart
        """
        if not domain_scores:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Aucun score de domaine', 
                   ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()
            
            return image_base64
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, max(6, len(domain_scores) * 0.5)))
        
        domains = list(domain_scores.keys())
        scores = list(domain_scores.values())
        
        # Couleurs selon le score
        colors = []
        for score in scores:
            if score >= 80:
                colors.append('#90EE90')  # Vert
            elif score >= 60:
                colors.append('#FFFF00')  # Jaune
            elif score >= 40:
                colors.append('#FFA500')  # Orange
            else:
                colors.append('#FF0000')  # Rouge
        
        bars = ax.barh(domains, scores, color=colors, alpha=0.7, edgecolor='black')
        
        # Ligne de référence 80%
        ax.axvline(x=80, color='green', linestyle='--', linewidth=2, 
                  label='Objectif (80%)')
        
        ax.set_xlabel('Score (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Domaines', fontsize=12, fontweight='bold')
        ax.set_title('Score de Conformité par Domaine', 
                    fontsize=14, fontweight='bold')
        ax.set_xlim(0, 100)
        
        # Ajouter les valeurs sur les barres
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height()/2, 
                   f'{score:.1f}%', ha='left', va='center', fontsize=10)
        
        ax.legend()
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return image_base64
