"""
EBIOS Risk Manager Calculator - Application Web Flask
Interface web pour construire des analyses EBIOS RM
Version: 1.0.0
Auteur: Ludovic Mouly - Cybersecurity Engineer
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import sys
import json
from datetime import datetime

PORT = int(os.environ.get('PORT', 8080))
DEBUG_MODE = os.environ.get('FLASK_ENV', 'production') != 'production'

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
    ebios_loader = EBIOSDataLoader('data/ebios_templates.json')
    print("✅ Templates EBIOS chargés")
except Exception as e:
    print(f"⚠️  Erreur chargement templates: {e}")
    ebios_loader = None

# === CONFIGURATION FLASK ===
app = Flask(__name__)
app.secret_key = 'ebios_secret_key_2026_change_in_production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['JSON_AS_ASCII'] = False

# === FILTRE JINJA2 POUR LES DATES ===
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y'):
    """Filtre Jinja2 pour formater les dates"""
    if value == 'now':
        return datetime.now().strftime(format)
    if isinstance(value, datetime):
        return value.strftime(format)
    return str(value)

# Ajouter la date actuelle au contexte global des templates
@app.context_processor
def inject_now():
    """Injecte la date actuelle dans tous les templates"""
    return {'now': datetime.now()}

# === HELPERS ===
def get_saved_analyses():
    """Liste les analyses sauvegardées"""
    analyses = []
    data_dir = 'data/assessments'
    
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('_atelier1.json')]
        for file in files:
            filepath = os.path.join(data_dir, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    analyses.append({
                        'filename': file.replace('_atelier1.json', ''),
                        'organisme': data.get('metadata', {}).get('organisme', 'N/A'),
                        'date': data.get('metadata', {}).get('date_debut', 'N/A')[:10],
                        'responsable': data.get('metadata', {}).get('responsable', 'N/A'),
                        'perimetre': data.get('metadata', {}).get('perimetre', 'N/A')
                    })
            except:
                continue
    
    return sorted(analyses, key=lambda x: x['date'], reverse=True)

# === ROUTES PRINCIPALES ===
@app.route('/')
def index():
    """Page d'accueil"""
    analyses = get_saved_analyses()
    return render_template('index.html', analyses=analyses)

@app.route('/dashboard')
def dashboard():
    """Tableau de bord des analyses"""
    analyses = get_saved_analyses()
    
    # Statistiques globales
    stats = {
        'total_analyses': len(analyses),
        'total_risques': 0,
        'risques_critiques': 0,
        'derniere_analyse': analyses[0]['date'] if analyses else 'N/A'
    }
    
    return render_template('dashboard.html', analyses=analyses, stats=stats)

# === ATELIER 1 - ROUTES ===
@app.route('/atelier1', methods=['GET', 'POST'])
def atelier1():
    """Atelier 1 - Cadrage et socle de sécurité"""
    if request.method == 'POST':
        # Sauvegarder dans la session
        session['atelier1'] = {
            'organisme': request.form.get('organisme'),
            'perimetre': request.form.get('perimetre'),
            'responsable': request.form.get('responsable'),
            'missions': request.form.getlist('mission_nom'),
            'missions_desc': request.form.getlist('mission_desc'),
            'missions_criticite': request.form.getlist('mission_criticite'),
            'valeurs': request.form.getlist('valeur_nom'),
            'valeurs_type': request.form.getlist('valeur_type'),
            'valeurs_d': request.form.getlist('valeur_d'),
            'valeurs_i': request.form.getlist('valeur_i'),
            'valeurs_c': request.form.getlist('valeur_c'),
            'valeurs_t': request.form.getlist('valeur_t')
        }
        
        # Créer l'objet Workshop1
        w1 = Workshop1()
        w1.init_study(
            session['atelier1']['organisme'],
            session['atelier1']['perimetre'],
            session['atelier1']['responsable']
        )
        
        # Ajouter les missions
        for i, nom in enumerate(session['atelier1']['missions']):
            if nom:
                w1.add_mission(
                    nom,
                    session['atelier1']['missions_desc'][i],
                    int(session['atelier1']['missions_criticite'][i])
                )
        
        # Ajouter les valeurs métier
        for i, nom in enumerate(session['atelier1']['valeurs']):
            if nom:
                w1.add_valeur_metier(
                    nom,
                    session['atelier1']['valeurs_type'][i],
                    {
                        'D': int(session['atelier1']['valeurs_d'][i]),
                        'I': int(session['atelier1']['valeurs_i'][i]),
                        'C': int(session['atelier1']['valeurs_c'][i]),
                        'T': int(session['atelier1']['valeurs_t'][i])
                    }
                )
        
        # Sauvegarder
        filename = session['atelier1']['organisme'].lower().replace(' ', '_').replace('-', '_')
        session['filename'] = filename
        w1.save(filename)
        
        flash('✅ Atelier 1 sauvegardé avec succès', 'success')
        return redirect(url_for('atelier2'))
    
    return render_template('atelier1.html')

# === ATELIER 2 - ROUTES ===
@app.route('/atelier2', methods=['GET', 'POST'])
def atelier2():
    """Atelier 2 - Sources de risque et objectifs visés"""
    if request.method == 'POST':
        w2 = Workshop2()
        
        # Sources de risque
        sr_noms = request.form.getlist('sr_nom')
        sr_types = request.form.getlist('sr_type')
        sr_ressources = request.form.getlist('sr_ressources')
        sr_determination = request.form.getlist('sr_determination')
        sr_competences = request.form.getlist('sr_competences')
        
        for i, nom in enumerate(sr_noms):
            if nom:
                w2.add_source_risque(
                    nom,
                    sr_types[i],
                    int(sr_ressources[i]),
                    int(sr_determination[i]),
                    int(sr_competences[i])
                )
        
        # Objectifs visés
        ov_noms = request.form.getlist('ov_nom')
        ov_desc = request.form.getlist('ov_desc')
        ov_impact = request.form.getlist('ov_impact')
        
        for i, nom in enumerate(ov_noms):
            if nom:
                w2.add_objectif_vise(nom, ov_desc[i], int(ov_impact[i]))
        
        # Cartographie SR×OV (si fournie)
        sr_ids = request.form.getlist('carto_sr')
        ov_ids = request.form.getlist('carto_ov')
        pertinences = request.form.getlist('carto_pertinence')
        
        for i, sr_id in enumerate(sr_ids):
            if sr_id and ov_ids[i]:
                w2.map_sr_to_ov(sr_id, ov_ids[i], int(pertinences[i]))
        
        # Générer scénarios
        w2.generate_scenarios_strategiques()
        
        # Sauvegarder
        filename = session.get('filename', 'analyse_ebios')
        w2.save(filename)
        
        flash('✅ Atelier 2 sauvegardé avec succès', 'success')
        return redirect(url_for('atelier5'))
    
    # Charger les types de sources depuis les templates
    types_sr = []
    if ebios_loader:
        sources = ebios_loader.get_sources_risque()
        types_sr = list(set([s['type'] for s in sources]))
    else:
        types_sr = ['APT', 'Cybercriminel organisé', 'Hacktiviste', 'Insider']
    
    return render_template('atelier2.html', types_sr=types_sr)

# === ATELIER 3 - ROUTES ===
@app.route('/atelier3', methods=['GET', 'POST'])
def atelier3():
    """Atelier 3 - Écosystème et parties prenantes"""
    if request.method == 'POST':
        w3 = Workshop3()
        
        # Parties prenantes
        pp_noms = request.form.getlist('pp_nom')
        pp_types = request.form.getlist('pp_type')
        pp_criticite = request.form.getlist('pp_criticite')
        pp_services = request.form.getlist('pp_services')
        pp_confiance = request.form.getlist('pp_confiance')
        pp_exposition = request.form.getlist('pp_exposition')
        
        for i, nom in enumerate(pp_noms):
            if nom:
                w3.add_partie_prenante(
                    nom,
                    pp_types[i],
                    int(pp_criticite[i]),
                    pp_services[i],
                    int(pp_confiance[i]),
                    int(pp_exposition[i])
                )
        
        # Biens supports
        bien_noms = request.form.getlist('bien_nom')
        bien_types = request.form.getlist('bien_type')
        bien_criticite = request.form.getlist('bien_criticite')
        bien_desc = request.form.getlist('bien_desc')
        
        for i, nom in enumerate(bien_noms):
            if nom:
                w3.add_bien_support(
                    nom,
                    bien_types[i],
                    int(bien_criticite[i]),
                    bien_desc[i]
                )
        
        # Sauvegarder
        filename = session.get('filename', 'analyse_ebios')
        w3.save(filename)
        
        flash('✅ Atelier 3 sauvegardé avec succès', 'success')
        return redirect(url_for('atelier4'))
    
    return render_template('atelier3.html')

# === ATELIER 4 - ROUTES ===
@app.route('/atelier4', methods=['GET', 'POST'])
def atelier4():
    """Atelier 4 - Scénarios opérationnels"""
    if request.method == 'POST':
        w4 = Workshop4()
        
        # Chemins d'attaque
        chemin_desc = request.form.getlist('chemin_desc')
        chemin_vraisemblance = request.form.getlist('chemin_vraisemblance')
        chemin_entree = request.form.getlist('chemin_entree')
        chemin_cible = request.form.getlist('chemin_cible')
        
        for i, desc in enumerate(chemin_desc):
            if desc:
                w4.add_chemin_attaque(
                    f"CA{i+1}",
                    desc,
                    int(chemin_vraisemblance[i]),
                    chemin_entree[i],
                    chemin_cible[i]
                )
        
        # Scénarios opérationnels
        scenario_noms = request.form.getlist('scenario_nom')
        scenario_gravite = request.form.getlist('scenario_gravite')
        scenario_deroulement = request.form.getlist('scenario_deroulement')
        scenario_mitre = request.form.getlist('scenario_mitre')
        scenario_ioc = request.form.getlist('scenario_ioc')
        
        for i, nom in enumerate(scenario_noms):
            if nom:
                w4.add_scenario_operationnel(
                    f"SO{i+1}",
                    nom,
                    int(scenario_gravite[i]),
                    scenario_deroulement[i],
                    scenario_mitre[i],
                    scenario_ioc[i]
                )
        
        # Sauvegarder
        filename = session.get('filename', 'analyse_ebios')
        w4.save(filename)
        
        flash('✅ Atelier 4 sauvegardé avec succès', 'success')
        return redirect(url_for('atelier5'))
    
    return render_template('atelier4.html')

# === ATELIER 5 - ROUTES ===
@app.route('/atelier5', methods=['GET', 'POST'])
def atelier5():
    """Atelier 5 - Traitement du risque"""
    if request.method == 'POST':
        w5 = Workshop5()
        
        # Risques
        risque_noms = request.form.getlist('risque_nom')
        risque_gravite = request.form.getlist('risque_gravite')
        risque_vraisemblance = request.form.getlist('risque_vraisemblance')
        risque_traitement = request.form.getlist('risque_traitement')
        
        for i, nom in enumerate(risque_noms):
            if nom:
                risque_id = f"R{i+1}"
                w5.add_risque(
                    risque_id,
                    nom,
                    int(risque_gravite[i]),
                    int(risque_vraisemblance[i]),
                    ""
                )
                w5.define_traitement(
                    risque_id,
                    risque_traitement[i],
                    "Traitement défini via interface web"
                )
        
        # Mesures
        mesure_noms = request.form.getlist('mesure_nom')
        mesure_type = request.form.getlist('mesure_type')
        mesure_cout = request.form.getlist('mesure_cout')
        
        for i, nom in enumerate(mesure_noms):
            if nom:
                w5.add_mesure_traitement(
                    nom,
                    mesure_type[i] if i < len(mesure_type) else "Préventif",
                    "Mesure de sécurité",
                    float(mesure_cout[i]) if mesure_cout[i] else 0,
                    0.7,
                    30,
                    "RSSI"
                )
        
        # Sauvegarder
        filename = session.get('filename', 'analyse_ebios')
        w5.save(filename)
        
        flash('✅ Atelier 5 sauvegardé avec succès', 'success')
        return redirect(url_for('visualisations', filename=filename))
    
    # Charger les mesures depuis templates
    mesures_templates = []
    if ebios_loader:
        mesures_templates = ebios_loader.get_mesures_securite()
    
    return render_template('atelier5.html', mesures_templates=mesures_templates)

# === VISUALISATIONS ===
@app.route('/visualisations/<filename>')
def visualisations(filename):
    """Page de visualisations et rapports"""
    try:
        # Charger Workshop2 pour scénarios
        w2 = Workshop2()
        w2.load(filename)
        
        # Charger Workshop5 pour risques
        w5 = Workshop5()
        try:
            w5.load(filename)
        except:
            w5 = None
        
        # Générer heatmap
        risks = []
        for scenario in w2.assessment.get('scenarios_strategiques', [])[:10]:
            risks.append({
                'gravite': scenario['gravite'],
                'vraisemblance': 3
            })
        
        heatmap_b64 = None
        if risks:
            try:
                heatmap_b64 = HeatmapGenerator.generate_risk_heatmap(risks)
            except Exception as e:
                print(f"Erreur génération heatmap: {e}")
        
        return render_template('visualisations.html', 
                             filename=filename,
                             heatmap=heatmap_b64,
                             scenarios=w2.assessment.get('scenarios_strategiques', []),
                             w5=w5)
    except Exception as e:
        flash(f'⚠️ Erreur chargement visualisations: {e}', 'error')
        return redirect(url_for('dashboard'))

# === API ENDPOINTS ===
@app.route('/api/templates/sources_risque')
def api_sources_risque():
    """API - Liste des sources de risque depuis templates"""
    if ebios_loader:
        sources = ebios_loader.get_sources_risque()
        return jsonify(sources)
    return jsonify([])

@app.route('/api/templates/mesures')
def api_mesures():
    """API - Liste des mesures de sécurité"""
    if ebios_loader:
        mesures = ebios_loader.get_mesures_securite()
        return jsonify(mesures)
    return jsonify([])

@app.route('/api/calculate_risk', methods=['POST'])
def api_calculate_risk():
    """API - Calcul du niveau de risque"""
    data = request.get_json()
    gravite = int(data.get('gravite', 1))
    vraisemblance = int(data.get('vraisemblance', 1))
    
    score, niveau = RiskCalculator.calculate_risk_level(gravite, vraisemblance)
    
    return jsonify({
        'score': score,
        'niveau': niveau,
        'gravite': gravite,
        'vraisemblance': vraisemblance
    })

@app.route('/api/analyse/<filename>/delete', methods=['POST'])
def api_delete_analyse(filename):
    """API - Supprimer une analyse"""
    try:
        data_dir = 'data/assessments'
        files_to_delete = [
            f"{filename}_atelier1.json",
            f"{filename}_atelier2.json",
            f"{filename}_atelier3.json",
            f"{filename}_atelier4.json",
            f"{filename}_atelier5.json"
        ]
        
        for file in files_to_delete:
            filepath = os.path.join(data_dir, file)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        return jsonify({'success': True, 'message': 'Analyse supprimée'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# === GESTION DES ERREURS ===
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# === LANCEMENT ===
if __name__ == '__main__':
    # Créer les répertoires nécessaires
    os.makedirs('data/assessments', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    print("\n" + "="*80)
    print("🛡️  EBIOS RISK MANAGER - WEB APPLICATION")
    print("="*80)
    print(f"\n✅ Serveur démarré sur http://0.0.0.0:{PORT}")
    print("📊 Interface web disponible")
    print("🎯 Ctrl+C pour arrêter")
    
    # Mode production : utiliser gunicorn (via Procfile)
    # Mode développement : Flask dev server
    if DEBUG_MODE:
        print("\n💡 Mode DÉVELOPPEMENT - Flask dev server")
        print("   Pour la production, utilisez: gunicorn app_web:app\n")
        app.run(debug=True, host='0.0.0.0', port=PORT)
    else:
        print("\n🚀 Mode PRODUCTION - Démarrage via Gunicorn")
        print("   Commande: gunicorn app_web:app\n")
        # Gunicorn sera lancé par le Procfile, pas ici

