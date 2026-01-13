"""
EBIOS Risk Manager Calculator - Application Interactive CLI
L'utilisateur construit son analyse EBIOS RM pas à pas via terminal
Version: 1.0.0
Auteur: Ludovic Mouly - Cybersecurity Engineer
"""
import os
import sys
import questionary
from questionary import Style
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.workshop1 import Workshop1
from modules.workshop2 import Workshop2
from modules.workshop3 import Workshop3
from modules.workshop4 import Workshop4
from modules.workshop5 import Workshop5
from modules.risk_calculator import RiskCalculator
from modules.heatmap_generator import HeatmapGenerator

try:
    from modules.ebios_data_loader import EBIOSDataLoader
    EBIOS_LOADER_AVAILABLE = True
except ImportError:
    EBIOS_LOADER_AVAILABLE = False

# Style personnalisé pour questionary
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])

def print_header(text: str):
    """Affiche un en-tête formaté"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_section(text: str):
    """Affiche une section formatée"""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)

def print_success(text: str):
    """Affiche un message de succès"""
    print(f"✅ {text}")

def print_info(text: str):
    """Affiche un message d'information"""
    print(f"ℹ️  {text}")

def atelier1_interactive():
    """Atelier 1 - Cadrage et socle de sécurité (interactif)"""
    print_header("🛡️  ATELIER 1 - CADRAGE ET SOCLE DE SÉCURITÉ")
    
    w1 = Workshop1()
    
    # === MÉTADONNÉES ===
    print("📋 Informations générales\n")
    organisme = questionary.text(
        "Nom de votre organisation:",
        style=custom_style
    ).ask()
    
    if not organisme:
        print("❌ Opération annulée")
        return None, None
    
    perimetre = questionary.text(
        "Périmètre de l'étude (ex: SI métier, application web...):",
        style=custom_style
    ).ask()
    
    responsable = questionary.text(
        "Responsable de l'étude (nom + fonction):",
        style=custom_style
    ).ask()
    
    w1.init_study(organisme, perimetre, responsable)
    print_success(f"Étude créée pour {organisme}\n")
    
    # === MISSIONS CRITIQUES ===
    print_section("🎯 Missions critiques")
    print("Les missions critiques représentent les activités essentielles de votre organisation.\n")
    
    add_missions = True
    while add_missions:
        nom_mission = questionary.text(
            "Nom de la mission critique:",
            style=custom_style
        ).ask()
        
        if not nom_mission:
            break
        
        desc_mission = questionary.text(
            "Description de la mission:",
            style=custom_style
        ).ask()
        
        criticite = questionary.select(
            "Niveau de criticité:",
            choices=[
                '1 - Négligeable',
                '2 - Limitée',
                '3 - Importante',
                '4 - Critique'
            ],
            style=custom_style
        ).ask()
        criticite_val = int(criticite.split(' - ')[0])
        
        w1.add_mission(nom_mission, desc_mission, criticite_val)
        print_success("Mission ajoutée\n")
        
        add_missions = questionary.confirm(
            "Ajouter une autre mission ?",
            default=True,
            style=custom_style
        ).ask()
    
    # === VALEURS MÉTIER ===
    print_section("💎 Valeurs métier")
    print("Les valeurs métier sont les actifs essentiels (données, services, processus).\n")
    
    add_valeurs = True
    while add_valeurs:
        nom_valeur = questionary.text(
            "Nom de la valeur métier (ex: Base de données clients):",
            style=custom_style
        ).ask()
        
        if not nom_valeur:
            break
        
        type_valeur = questionary.select(
            "Type de valeur métier:",
            choices=['Information', 'Service', 'Processus', 'Autre'],
            style=custom_style
        ).ask()
        
        print("\n📊 Évaluez la sensibilité DICT (1-4):")
        d = int(questionary.select("Disponibilité (D):", 
                 choices=['1', '2', '3', '4'], style=custom_style).ask())
        i = int(questionary.select("Intégrité (I):", 
                 choices=['1', '2', '3', '4'], style=custom_style).ask())
        c = int(questionary.select("Confidentialité (C):", 
                 choices=['1', '2', '3', '4'], style=custom_style).ask())
        t = int(questionary.select("Traçabilité (T):", 
                 choices=['1', '2', '3', '4'], style=custom_style).ask())
        
        w1.add_valeur_metier(nom_valeur, type_valeur, {'D': d, 'I': i, 'C': c, 'T': t})
        print_success("Valeur métier ajoutée\n")
        
        add_valeurs = questionary.confirm(
            "Ajouter une autre valeur métier ?",
            default=True,
            style=custom_style
        ).ask()
    
    # === ÉVÉNEMENTS REDOUTÉS ===
    print_section("⚠️  Événements redoutés")
    print("Les événements redoutés sont les incidents que vous craignez.\n")
    
    add_evenements = True
    while add_evenements:
        nom_er = questionary.text(
            "Nom de l'événement redouté (ex: Fuite de données):",
            style=custom_style
        ).ask()
        
        if not nom_er:
            break
        
        desc_er = questionary.text(
            "Description de l'événement:",
            style=custom_style
        ).ask()
        
        gravite_er = questionary.select(
            "Gravité de l'événement:",
            choices=[
                '1 - Négligeable',
                '2 - Limitée',
                '3 - Importante',
                '4 - Critique'
            ],
            style=custom_style
        ).ask()
        gravite_val = int(gravite_er.split(' - ')[0])
        
        w1.add_evenement_redoute(nom_er, desc_er, gravite_val, [])
        print_success("Événement redouté ajouté\n")
        
        add_evenements = questionary.confirm(
            "Ajouter un autre événement redouté ?",
            default=False,
            style=custom_style
        ).ask()
    
    # === SOCLE DE SÉCURITÉ ===
    print_section("🔒 Évaluation du socle de sécurité")
    evaluer_socle = questionary.confirm(
        "Voulez-vous évaluer votre socle de sécurité ?",
        default=True,
        style=custom_style
    ).ask()
    
    if evaluer_socle:
        domaines = [
            'Politique de sécurité',
            'Organisation',
            'Gestion des actifs',
            'Contrôle d\'accès',
            'Cryptographie',
            'Sécurité physique',
            'Sécurité opérationnelle',
            'Gestion des incidents',
            'Continuité d\'activité',
            'Conformité'
        ]
        
        print("\nÉvaluez chaque domaine de 0 à 100%:\n")
        for domaine in domaines:
            score = questionary.text(
                f"{domaine} - Conformité (0-100):",
                validate=lambda x: x.isdigit() and 0 <= int(x) <= 100,
                style=custom_style
            ).ask()
            w1.evaluate_socle(domaine, float(score))
        
        socle_stats = w1.get_socle_stats()
        print(f"\n✅ Conformité globale: {socle_stats['taux_conformite']}%")
    
    # === STATISTIQUES ===
    stats = w1.get_statistics()
    print_section("📊 Statistiques Atelier 1")
    print(f"Missions critiques: {stats['nb_missions']}")
    print(f"Valeurs métier: {stats['nb_valeurs_metier']}")
    print(f"Événements redoutés: {stats['nb_evenements_redoutes']}")
    print(f"Conformité socle: {stats['taux_conformite_socle']}%")
    
    # === SAUVEGARDE ===
    filename = questionary.text(
        "\nNom du fichier de sauvegarde (sans extension):",
        default=organisme.lower().replace(' ', '_'),
        style=custom_style
    ).ask()
    
    filepath = w1.save(filename)
    print_success(f"Atelier 1 sauvegardé: {filepath}")
    
    return w1, filename

def atelier2_interactive(filename):
    """Atelier 2 - Sources de risque et objectifs visés"""
    print_header("🎯 ATELIER 2 - SOURCES DE RISQUE ET OBJECTIFS VISÉS")
    
    w2 = Workshop2()
    
    # === SOURCES DE RISQUE ===
    print_section("🦹 Sources de risque")
    print("Identifiez les attaquants potentiels (cybercriminels, APT, hacktivistes...).\n")
    
    types_sr = [
        'APT (Advanced Persistent Threat)',
        'Cybercriminel organisé',
        'Hacktiviste',
        'Terroriste',
        'État-nation hostile',
        'Concurrent déloyal',
        'Insider malveillant',
        'Employé négligent',
        'Script kiddie'
    ]
    
    add_sr = True
    while add_sr:
        nom_sr = questionary.text(
            "Nom de la source de risque:",
            style=custom_style
        ).ask()
        
        if not nom_sr:
            break
        
        type_sr = questionary.select(
            "Type de source de risque:",
            choices=types_sr,
            style=custom_style
        ).ask()
        
        print("\n📊 Évaluez la capacité de la source (1-4):")
        ressources = int(questionary.select(
            "Ressources financières et matérielles:", 
            choices=['1 - Limitées', '2 - Moyennes', '3 - Importantes', '4 - Très importantes'],
            style=custom_style
        ).ask().split(' - ')[0])
        
        determination = int(questionary.select(
            "Détermination et motivation:", 
            choices=['1 - Faible', '2 - Moyenne', '3 - Forte', '4 - Très forte'],
            style=custom_style
        ).ask().split(' - ')[0])
        
        competences = int(questionary.select(
            "Compétences techniques:", 
            choices=['1 - Basiques', '2 - Intermédiaires', '3 - Avancées', '4 - Expert'],
            style=custom_style
        ).ask().split(' - ')[0])
        
        w2.add_source_risque(nom_sr, type_sr, ressources, determination, competences)
        
        # Afficher la capacité calculée
        sr_ajoutee = w2.assessment['sources_risque'][-1]
        print_success(f"Source ajoutée - Capacité globale: {sr_ajoutee['capacite_globale']}/4 ({sr_ajoutee['niveau']})\n")
        
        add_sr = questionary.confirm(
            "Ajouter une autre source de risque ?",
            default=True,
            style=custom_style
        ).ask()
    
    # === OBJECTIFS VISÉS ===
    print_section("🎯 Objectifs visés")
    print("Identifiez ce que les attaquants pourraient vouloir accomplir.\n")
    
    add_ov = True
    while add_ov:
        nom_ov = questionary.text(
            "Nom de l'objectif visé (ex: Vol de données, Ransomware...):",
            style=custom_style
        ).ask()
        
        if not nom_ov:
            break
        
        desc_ov = questionary.text(
            "Description de l'objectif:",
            style=custom_style
        ).ask()
        
        impact = questionary.select(
            "Impact potentiel:",
            choices=[
                '1 - Négligeable',
                '2 - Limité',
                '3 - Important',
                '4 - Critique'
            ],
            style=custom_style
        ).ask()
        impact_val = int(impact.split(' - ')[0])
        
        w2.add_objectif_vise(nom_ov, desc_ov, impact_val)
        print_success("Objectif visé ajouté\n")
        
        add_ov = questionary.confirm(
            "Ajouter un autre objectif visé ?",
            default=True,
            style=custom_style
        ).ask()
    
    # === CARTOGRAPHIE SR × OV ===
    print_section("🗺️  Cartographie SR × OV")
    print("Associez les sources de risque aux objectifs visés.\n")
    
    sources = w2.assessment['sources_risque']
    objectifs = w2.assessment['objectifs_vises']
    
    for sr in sources:
        print(f"\n🦹 Source: {sr['nom']}")
        ov_choices = [f"{ov['id']} - {ov['nom']}" for ov in objectifs]
        ov_choices.append("Passer à la source suivante")
        
        ov_selected = questionary.checkbox(
            "Sélectionnez les objectifs visés par cette source:",
            choices=ov_choices,
            style=custom_style
        ).ask()
        
        for ov_str in ov_selected:
            if "Passer" in ov_str:
                continue
            ov_id = ov_str.split(' - ')[0]
            pertinence = int(questionary.select(
                f"Pertinence de {sr['nom']} → {ov_str}:",
                choices=['1 - Faible', '2 - Moyenne', '3 - Forte', '4 - Très forte'],
                style=custom_style
            ).ask().split(' - ')[0])
            w2.map_sr_to_ov(sr['id'], ov_id, pertinence)
    
    # === GÉNÉRATION DES SCÉNARIOS ===
    print_section("📝 Génération des scénarios stratégiques")
    scenarios = w2.generate_scenarios_strategiques()
    print_success(f"{len(scenarios)} scénarios stratégiques générés")
    
    if scenarios:
        print("\n🔥 Top 5 des scénarios les plus critiques:")
        for i, scenario in enumerate(scenarios[:5], 1):
            print(f"\n{i}. [{scenario['niveau_risque']}] {scenario['source_risque']} → {scenario['objectif_vise']}")
            print(f"   Gravité: {scenario['gravite']}/4 | Pertinence: {scenario['pertinence']}/4")
    
    # === STATISTIQUES ===
    stats = w2.get_statistics()
    print_section("📊 Statistiques Atelier 2")
    print(f"Sources de risque: {stats['nb_sources_risque']}")
    print(f"Objectifs visés: {stats['nb_objectifs_vises']}")
    print(f"Scénarios stratégiques: {stats['nb_scenarios_strategiques']}")
    print(f"  • Critiques: {stats['scenarios_critiques']}")
    print(f"  • Élevés: {stats['scenarios_eleves']}")
    
    # === SAUVEGARDE ===
    filepath = w2.save(filename)
    print_success(f"Atelier 2 sauvegardé: {filepath}\n")
    
    return w2

def atelier5_interactive(filename):
    """Atelier 5 - Traitement du risque"""
    print_header("🛡️  ATELIER 5 - TRAITEMENT DU RISQUE")
    
    w5 = Workshop5()
    
    # === IDENTIFICATION DES RISQUES ===
    print_section("⚠️  Identification des risques")
    print("Identifiez les risques à traiter.\n")
    
    add_risques = True
    risque_count = 1
    
    while add_risques:
        nom_risque = questionary.text(
            "Nom du risque:",
            style=custom_style
        ).ask()
        
        if not nom_risque:
            break
        
        gravite = int(questionary.select(
            "Gravité:",
            choices=['1 - Négligeable', '2 - Limitée', '3 - Importante', '4 - Critique'],
            style=custom_style
        ).ask().split(' - ')[0])
        
        vraisemblance = int(questionary.select(
            "Vraisemblance:",
            choices=['1 - Improbable', '2 - Possible', '3 - Probable', '4 - Très probable'],
            style=custom_style
        ).ask().split(' - ')[0])
        
        w5.add_risque(f"R{risque_count}", nom_risque, gravite, vraisemblance, "")
        
        # Calculer et afficher le niveau
        score, niveau = RiskCalculator.calculate_risk_level(gravite, vraisemblance)
        print_success(f"Risque ajouté - Niveau: {niveau} ({score}/4)\n")
        
        # === OPTION DE TRAITEMENT ===
        option = questionary.select(
            "Option de traitement:",
            choices=['Atténuation', 'Évitement', 'Transfert', 'Acceptation'],
            style=custom_style
        ).ask()
        
        justif = questionary.text(
            "Justification du traitement:",
            style=custom_style
        ).ask()
        
        w5.define_traitement(f"R{risque_count}", option, justif)
        
        # === MESURE SI ATTÉNUATION ===
        if option == "Atténuation":
            ajouter_mesure = questionary.confirm(
                "Ajouter une mesure de sécurité ?",
                default=True,
                style=custom_style
            ).ask()
            
            if ajouter_mesure:
                nom_mesure = questionary.text(
                    "Nom de la mesure de sécurité:",
                    style=custom_style
                ).ask()
                
                cout = float(questionary.text(
                    "Coût estimé (€):",
                    validate=lambda x: x.replace('.', '').replace(',', '').isdigit(),
                    style=custom_style
                ).ask())
                
                efficacite = float(questionary.select(
                    "Efficacité estimée:",
                    choices=['0.3 - Faible', '0.5 - Moyenne', '0.7 - Bonne', '0.9 - Excellente'],
                    style=custom_style
                ).ask().split(' - ')[0])
                
                w5.add_mesure_traitement(
                    nom_mesure,
                    "Préventif",
                    "Mesure de sécurité",
                    cout,
                    efficacite,
                    30,
                    "RSSI"
                )
                w5.associate_mesure_to_risque(f"R{risque_count}", f"M{len(w5.assessment['mesures_traitement'])}")
                print_success("Mesure ajoutée et associée au risque\n")
        
        risque_count += 1
        
        add_risques = questionary.confirm(
            "Ajouter un autre risque ?",
            default=False,
            style=custom_style
        ).ask()
    
    # === STATISTIQUES ===
    stats = w5.get_statistics()
    print_section("📊 Statistiques Atelier 5")
    print(f"Risques identifiés: {stats['nb_risques_total']}")
    print(f"Risques critiques: {stats['nb_risques_critiques']}")
    print(f"Budget total: {stats['budget_total']:,.0f} €")
    print(f"Taux de traitement: {stats['taux_traitement']}%")
    
    # === SAUVEGARDE ===
    filepath = w5.save(filename)
    print_success(f"Atelier 5 sauvegardé: {filepath}\n")
    
    return w5

def main():
    """Application principale interactive"""
    print_header("🛡️  EBIOS RISK MANAGER - APPLICATION INTERACTIVE")
    print("Version 1.0.0 - CLI Interactive")
    print("Auteur: Ludovic Mouly - Cybersecurity Engineer")
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    
    action = questionary.select(
        "Que voulez-vous faire ?",
        choices=[
            'Nouvelle analyse EBIOS RM',
            'Charger une analyse existante',
            'Quitter'
        ],
        style=custom_style
    ).ask()
    
    if action == 'Quitter':
        print("\n👋 Au revoir !")
        return
    
    if action == 'Nouvelle analyse EBIOS RM':
        # === ATELIER 1 ===
        w1, filename = atelier1_interactive()
        
        if not filename:
            return
        
        # === CONTINUER AVEC ATELIER 2 ? ===
        continuer = questionary.confirm(
            "\nPasser à l'Atelier 2 (Sources de risque) ?",
            default=True,
            style=custom_style
        ).ask()
        
        if continuer:
            w2 = atelier2_interactive(filename)
            
            # === CONTINUER AVEC ATELIER 5 ? ===
            continuer5 = questionary.confirm(
                "\nPasser à l'Atelier 5 (Traitement du risque) ?",
                default=True,
                style=custom_style
            ).ask()
            
            if continuer5:
                w5 = atelier5_interactive(filename)
        
        # === RÉSUMÉ FINAL ===
        print_header("✅ ANALYSE EBIOS RM TERMINÉE")
        print(f"\n📁 Fichiers sauvegardés dans data/assessments/")
        print(f"🎯 Analyse complète: {filename}")
        print(f"\n💡 Conseil: Lancez 'python3 app_web.py' pour visualiser vos résultats dans le navigateur !\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Opération interrompue par l'utilisateur")
        sys.exit(0)
