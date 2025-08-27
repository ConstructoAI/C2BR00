"""
Module de création de soumissions budgétaires pour Construction Héritage
Basé sur le template TEMPLATE_SOUM_BIG_R03.html
"""

import streamlit as st
import json
import uuid
from datetime import datetime, date
import sqlite3
import os

# Configuration de la compagnie
COMPANY_INFO = {
    'name': 'Construction Héritage',
    'address': '129 Rue Poirier',
    'city': 'Saint-Jean-sur-Richelieu (Québec) J3B 4E9',
    'phone': '438.524.9193',
    'cell': '514.983.7492',
    'email': 'info@constructionheritage.ca',
    'rbq': '5788-9784-01',
    'neq': '1163835623',
    'tps': '850370164RT0001',
    'tvq': '1212199610TQ0002'
}

# Catégories de travaux
CATEGORIES = {
    '0': {
        'name': '0.0 - Travaux Préparatoires et Démolition',
        'items': [
            {'id': '0-1', 'title': 'Permis et études', 
             'description': 'Permis de construction, étude géotechnique, certificat de localisation'},
            {'id': '0-2', 'title': 'Démolition et décontamination',
             'description': 'Démolition structures existantes, décontamination si applicable'},
            {'id': '0-3', 'title': 'Préparation du terrain',
             'description': 'Déboisement, nivellement, services temporaires'}
        ]
    },
    '1': {
        'name': '1.0 - Fondation, Infrastructure et Services',
        'items': [
            {'id': '1-1', 'title': 'Excavation et remblai',
             'description': 'Excavation générale, remblai granulaire compacté'},
            {'id': '1-2', 'title': 'Fondation complète',
             'description': 'Béton 30 MPA, armature, coffrage, isolation'},
            {'id': '1-3', 'title': 'Drainage et imperméabilisation',
             'description': 'Drain français, membrane, pompe de puisard'},
            {'id': '1-4', 'title': 'Raccordements et services',
             'description': 'Égout, aqueduc, pluvial, système septique si applicable'}
        ]
    },
    '2': {
        'name': '2.0 - Structure et Charpente',
        'items': [
            {'id': '2-1', 'title': 'Charpente de bois',
             'description': 'Murs extérieurs et intérieurs, planchers, toiture'},
            {'id': '2-2', 'title': 'Poutrelles et colonnes',
             'description': 'Système de poutrelles, colonnes d\'acier si requis'},
            {'id': '2-3', 'title': 'Plancher de béton',
             'description': 'Dalle structurale, finition, durcisseur'}
        ]
    },
    '3': {
        'name': '3.0 - Enveloppe Extérieure',
        'items': [
            {'id': '3-1', 'title': 'Toiture',
             'description': 'Bardeaux architecturaux, membrane, ventilation'},
            {'id': '3-2', 'title': 'Revêtement extérieur',
             'description': 'Parement, fourrures, pare-air'},
            {'id': '3-3', 'title': 'Portes et fenêtres',
             'description': 'Portes, fenêtres Energy Star, installation'},
            {'id': '3-4', 'title': 'Balcons et terrasses',
             'description': 'Structure, revêtement, garde-corps'}
        ]
    },
    '4': {
        'name': '4.0 - Systèmes Mécaniques et Électriques',
        'items': [
            {'id': '4-1', 'title': 'Plomberie complète',
             'description': 'Tuyauterie, fixtures, chauffe-eau'},
            {'id': '4-2', 'title': 'Chauffage et climatisation',
             'description': 'Système CVAC, thermostats, ventilation'},
            {'id': '4-3', 'title': 'Électricité complète',
             'description': 'Panneau, filage, prises, luminaires'},
            {'id': '4-4', 'title': 'Systèmes spécialisés',
             'description': 'Alarme, centrale, aspirateur, domotique'}
        ]
    },
    '5': {
        'name': '5.0 - Isolation et Étanchéité',
        'items': [
            {'id': '5-1', 'title': 'Isolation thermique',
             'description': 'Laine, uréthane, pare-vapeur'},
            {'id': '5-2', 'title': 'Insonorisation',
             'description': 'Isolation acoustique, barres résilientes'},
            {'id': '5-3', 'title': 'Étanchéité à l\'air',
             'description': 'Scellement, test infiltrométrie'}
        ]
    },
    '6': {
        'name': '6.0 - Finitions Intérieures',
        'items': [
            {'id': '6-1', 'title': 'Gypse et plafonds',
             'description': 'Gypse, joints, texture, plafonds suspendus'},
            {'id': '6-2', 'title': 'Revêtements de plancher',
             'description': 'Bois franc, céramique, vinyle, tapis'},
            {'id': '6-3', 'title': 'Armoires et vanités',
             'description': 'Cuisine, salles de bain, rangements'},
            {'id': '6-4', 'title': 'Peinture et finition',
             'description': 'Apprêt, peinture, teinture, vernis'},
            {'id': '6-5', 'title': 'Escaliers et rampes',
             'description': 'Escaliers, mains courantes, garde-corps'}
        ]
    },
    '7': {
        'name': '7.0 - Aménagement Extérieur et Garage',
        'items': [
            {'id': '7-1', 'title': 'Terrassement et pavage',
             'description': 'Nivellement, gazon, entrée pavée/asphalte'},
            {'id': '7-2', 'title': 'Garage',
             'description': 'Structure, dalle, porte, finition'},
            {'id': '7-3', 'title': 'Aménagement paysager',
             'description': 'Plantation, murets, éclairage'},
            {'id': '7-4', 'title': 'Clôtures et portails',
             'description': 'Clôture, portail, intimité'}
        ]
    }
}

def create_soumission_form():
    """Crée le formulaire de soumission interactif"""
    
    st.markdown("""
    <style>
        .soumission-header {
            background: linear-gradient(135deg, #374151 0%, #4b5563 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .category-section {
            background: #f9fafb;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #4b5563;
        }
        .item-row {
            padding: 0.5rem;
            margin: 0.5rem 0;
            background: white;
            border-radius: 4px;
        }
        .total-box {
            background: linear-gradient(135deg, #f9fafb 0%, #e5e7eb 100%);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #4b5563;
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialiser session state pour la soumission
    if 'soumission_data' not in st.session_state:
        st.session_state.soumission_data = {
            'numero': generate_numero_soumission(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'client': {},
            'projet': {},
            'items': {},
            'totaux': {},
            'conditions': [],
            'exclusions': []
        }
    
    st.markdown('<div class="soumission-header">', unsafe_allow_html=True)
    st.title("🏗️ CRÉATION DE SOUMISSION BUDGÉTAIRE")
    st.markdown("### Construction Héritage")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs pour organiser le formulaire
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Informations", "🏗️ Travaux", "💰 Récapitulatif", "💾 Actions"])
    
    with tab1:
        st.markdown("### Informations du projet")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Information client")
            st.session_state.soumission_data['client']['nom'] = st.text_input(
                "Nom du client", 
                value=st.session_state.soumission_data['client'].get('nom', '')
            )
            st.session_state.soumission_data['client']['adresse'] = st.text_input(
                "Adresse",
                value=st.session_state.soumission_data['client'].get('adresse', '')
            )
            st.session_state.soumission_data['client']['ville'] = st.text_input(
                "Ville",
                value=st.session_state.soumission_data['client'].get('ville', '')
            )
            st.session_state.soumission_data['client']['code_postal'] = st.text_input(
                "Code postal",
                value=st.session_state.soumission_data['client'].get('code_postal', '')
            )
            st.session_state.soumission_data['client']['telephone'] = st.text_input(
                "Téléphone",
                value=st.session_state.soumission_data['client'].get('telephone', '')
            )
            st.session_state.soumission_data['client']['courriel'] = st.text_input(
                "Courriel",
                value=st.session_state.soumission_data['client'].get('courriel', '')
            )
        
        with col2:
            st.markdown("#### 🏠 Information projet")
            st.session_state.soumission_data['projet']['nom'] = st.text_input(
                "Nom du projet",
                value=st.session_state.soumission_data['projet'].get('nom', '')
            )
            st.session_state.soumission_data['projet']['adresse'] = st.text_input(
                "Adresse du projet",
                value=st.session_state.soumission_data['projet'].get('adresse', '')
            )
            st.session_state.soumission_data['projet']['type'] = st.selectbox(
                "Type de construction",
                ["Résidentielle", "Commerciale", "Rénovation", "Agrandissement"]
            )
            col_a, col_b = st.columns(2)
            with col_a:
                st.session_state.soumission_data['projet']['superficie'] = st.number_input(
                    "Superficie (pi²)",
                    min_value=0,
                    value=st.session_state.soumission_data['projet'].get('superficie', 0)
                )
            with col_b:
                st.session_state.soumission_data['projet']['etages'] = st.number_input(
                    "Nombre d'étages",
                    min_value=1,
                    max_value=5,
                    value=st.session_state.soumission_data['projet'].get('etages', 1)
                )
            
            date_debut = st.date_input(
                "Date de début prévue",
                value=date.today()
            )
            # Convertir la date en string pour éviter les problèmes de sérialisation
            st.session_state.soumission_data['projet']['date_debut'] = date_debut.isoformat()
            st.session_state.soumission_data['projet']['duree'] = st.text_input(
                "Durée estimée",
                value=st.session_state.soumission_data['projet'].get('duree', '3-4 mois')
            )
    
    with tab2:
        st.markdown("### Détails des travaux")
        
        # Style pour les tableaux
        st.markdown("""
        <style>
            .stNumberInput > div > div > input {
                text-align: right;
            }
            .category-header {
                background: #f0f2f6;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .item-table {
                width: 100%;
                margin: 10px 0;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Mode admin pour calculs automatiques
        admin_mode = st.checkbox("Calcul automatique du total (Quantité × Coût unitaire)", value=True)
        
        # Pour chaque catégorie
        for cat_id, category in CATEGORIES.items():
            with st.expander(f"**{category['name']}**", expanded=False):
                
                # Header du tableau
                col_headers = st.columns([3.5, 1, 1.5, 1.5, 0.5])
                with col_headers[0]:
                    st.markdown("**Description**")
                with col_headers[1]:
                    st.markdown("**Quantité**")
                with col_headers[2]:
                    st.markdown("**Coût unitaire**")
                with col_headers[3]:
                    st.markdown("**Total**")
                with col_headers[4]:
                    st.markdown("**×**")
                
                st.markdown("---")
                
                category_total = 0
                
                for item in category['items']:
                    item_key = f"{cat_id}_{item['id']}"
                    
                    # Colonnes pour chaque ligne d'item
                    col1, col2, col3, col4, col5 = st.columns([3.5, 1, 1.5, 1.5, 0.5])
                    
                    with col1:
                        st.markdown(f"**{item['title']}**")
                        st.caption(item['description'])
                    
                    with col2:
                        qty = st.number_input(
                            "Quantité",
                            min_value=0.0,
                            value=st.session_state.soumission_data['items'].get(item_key, {}).get('quantite', 1.0),
                            step=1.0,
                            key=f"qty_{item_key}",
                            label_visibility="collapsed"
                        )
                    
                    with col3:
                        unit_price = st.number_input(
                            "Coût unitaire",
                            min_value=0.0,
                            value=st.session_state.soumission_data['items'].get(item_key, {}).get('prix_unitaire', 0.0),
                            format="%.2f",
                            step=100.0,
                            key=f"unit_{item_key}",
                            label_visibility="collapsed"
                        )
                    
                    # Calcul du montant total
                    if admin_mode:
                        amount = qty * unit_price
                        with col4:
                            st.markdown(f"<div style='text-align: right; font-weight: bold; padding: 8px; background: #f0f2f6; border-radius: 4px;'>${amount:,.2f}</div>", unsafe_allow_html=True)
                    else:
                        with col4:
                            amount = st.number_input(
                                "Total",
                                min_value=0.0,
                                value=st.session_state.soumission_data['items'].get(item_key, {}).get('montant', 0.0),
                                format="%.2f",
                                step=100.0,
                                key=f"amount_{item_key}",
                                label_visibility="collapsed"
                            )
                    
                    with col5:
                        # Bouton pour effacer la ligne
                        if st.button("🗑️", key=f"del_{item_key}", help="Effacer cette ligne"):
                            qty = 0
                            unit_price = 0
                            amount = 0
                    
                    # Sauvegarder les données de l'item
                    st.session_state.soumission_data['items'][item_key] = {
                        'titre': item['title'],
                        'description': item['description'],
                        'quantite': qty,
                        'prix_unitaire': unit_price,
                        'montant': amount
                    }
                    
                    category_total += amount
                    
                    # Ligne de séparation subtile
                    st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
                
                # Afficher le sous-total de la catégorie
                st.markdown("---")
                st.markdown(f"<div style='text-align: right; font-size: 1.1em; font-weight: bold; color: #4b5563;'>Sous-total de la catégorie: ${category_total:,.2f}</div>", unsafe_allow_html=True)
        
        # Paramètres des taux
        st.markdown("### ⚙️ Paramètres des taux")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            profit = st.slider("Profit (%)", 0, 50, 15) / 100
        with col2:
            admin = st.slider("Administration (%)", 0, 10, 3) / 100
        with col3:
            contingency = st.slider("Contingences (%)", 0, 25, 12) / 100
        
        st.session_state.soumission_data['taux'] = {
            'profit': profit,
            'admin': admin,
            'contingency': contingency
        }
    
    with tab3:
        st.markdown("### 📊 Récapitulatif financier")
        
        # Calculer les totaux
        total_travaux = sum(
            item.get('montant', 0) 
            for item in st.session_state.soumission_data['items'].values()
        )
        
        taux = st.session_state.soumission_data.get('taux', {
            'admin': 0.03,
            'contingency': 0.12,
            'profit': 0.15
        })
        
        admin_amount = total_travaux * taux['admin']
        contingency_amount = total_travaux * taux['contingency']
        profit_amount = total_travaux * taux['profit']
        
        sous_total = total_travaux + admin_amount + contingency_amount + profit_amount
        
        tps = sous_total * 0.05
        tvq = sous_total * 0.09975
        
        total_final = sous_total + tps + tvq
        
        # Sauvegarder les totaux
        st.session_state.soumission_data['totaux'] = {
            'travaux': total_travaux,
            'administration': admin_amount,
            'contingences': contingency_amount,
            'profit': profit_amount,
            'sous_total': sous_total,
            'tps': tps,
            'tvq': tvq,
            'total': total_final
        }
        
        # Style pour le tableau récapitulatif
        st.markdown("""
        <style>
            .recap-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            .recap-table td {
                padding: 10px;
                border-bottom: 1px solid #e5e7eb;
            }
            .recap-table .label {
                font-weight: 600;
                color: #4b5563;
            }
            .recap-table .value {
                text-align: right;
                font-weight: 500;
            }
            .recap-table .category-row {
                background: #f9fafb;
            }
            .recap-table .subtotal-row {
                background: #f0f2f6;
                font-weight: bold;
            }
            .recap-table .total-row {
                background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%);
                color: white;
                font-size: 1.2em;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Affichage du récapitulatif avec colonnes Streamlit
        st.markdown("#### Détail par catégorie")
        
        # Récap par catégorie
        for cat_id, category in CATEGORIES.items():
            cat_total = sum(
                item.get('montant', 0) 
                for key, item in st.session_state.soumission_data['items'].items()
                if key.startswith(cat_id + "_")
            )
            if cat_total > 0:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{category['name']}**")
                with col2:
                    st.write(f"**${cat_total:,.2f}**")
        
        st.markdown("---")
        st.markdown("#### Calcul du total")
        
        # Total des travaux
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Total des travaux**")
        with col2:
            st.markdown(f"**${total_travaux:,.2f}**")
        
        # Frais supplémentaires
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Administration ({taux['admin']*100:.0f}%)")
        with col2:
            st.write(f"${admin_amount:,.2f}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Contingences ({taux['contingency']*100:.0f}%)")
        with col2:
            st.write(f"${contingency_amount:,.2f}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Profit ({taux['profit']*100:.0f}%)")
        with col2:
            st.write(f"${profit_amount:,.2f}")
        
        st.markdown("---")
        
        # Sous-total avant taxes
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("**Sous-total avant taxes**")
        with col2:
            st.markdown(f"**${sous_total:,.2f}**")
        
        # Taxes
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("TPS (5%)")
        with col2:
            st.write(f"${tps:,.2f}")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write("TVQ (9.975%)")
        with col2:
            st.write(f"${tvq:,.2f}")
        
        st.markdown("---")
        
        # Total final avec style
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4b5563 0%, #6b7280 100%); 
                    color: white; 
                    padding: 15px; 
                    border-radius: 8px; 
                    margin: 20px 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;">
            <span style="font-size: 1.5em; font-weight: bold;">TOTAL FINAL</span>
            <span style="font-size: 1.8em; font-weight: bold;">${total_final:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Graphique de répartition
        if total_travaux > 0:
            st.markdown("### 📈 Répartition des coûts")
            
            import plotly.graph_objects as go
            
            # Données pour le graphique
            labels = []
            values = []
            
            for cat_id, category in CATEGORIES.items():
                cat_total = sum(
                    item.get('montant', 0) 
                    for key, item in st.session_state.soumission_data['items'].items()
                    if key.startswith(cat_id + "_")
                )
                if cat_total > 0:
                    labels.append(category['name'].split(' - ')[1])
                    values.append(cat_total)
            
            # Créer le graphique en secteurs
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values,
                hole=.3,
                marker=dict(colors=['#4b5563', '#6b7280', '#9ca3af', '#d1d5db', '#e5e7eb', '#f3f4f6', '#f9fafb', '#374151'])
            )])
            
            fig.update_layout(
                height=400,
                showlegend=True,
                font=dict(size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Conditions et exclusions
        st.markdown("### 📝 Conditions")
        conditions = st.text_area(
            "Conditions de la soumission",
            value="• Cette soumission est valide pour 30 jours\n• Prix sujet à changement selon les conditions du site\n• 50% d'acompte requis à la signature du contrat",
            height=100
        )
        st.session_state.soumission_data['conditions'] = conditions.split('\n')
        
        st.markdown("### ⚠️ Exclusions")
        exclusions = st.text_area(
            "Exclusions de la soumission",
            value="• Décontamination (si applicable)\n• Mobilier et électroménagers\n• Aménagement paysager (sauf si spécifié)",
            height=100
        )
        st.session_state.soumission_data['exclusions'] = exclusions.split('\n')
    
    with tab4:
        st.markdown("### 💾 Actions sur la soumission")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Sauvegarder", use_container_width=True, type="primary"):
                if save_soumission():
                    st.success("✅ Soumission sauvegardée avec succès!")
                    st.balloons()
                else:
                    st.error("❌ Erreur lors de la sauvegarde")
        
        with col2:
            if st.button("📄 Générer PDF", use_container_width=True):
                with st.spinner("Génération du document en cours..."):
                    file_path = generate_pdf()
                    if file_path:
                        # Lire le fichier généré
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        
                        # Déterminer le type de fichier et le MIME type
                        if file_path.endswith('.pdf'):
                            mime_type = "application/pdf"
                            file_ext = ".pdf"
                        else:
                            # C'est un HTML
                            mime_type = "text/html"
                            file_ext = ".html"
                        
                        # Bouton de téléchargement
                        st.download_button(
                            label="📥 Télécharger le document",
                            data=file_content,
                            file_name=f"soumission_{st.session_state.soumission_data['numero']}{file_ext}",
                            mime=mime_type,
                            help="Cliquez pour télécharger la soumission"
                        )
                        
                        if file_ext == ".html":
                            st.info("""
                            💡 **Document HTML généré avec succès!**
                            
                            Pour créer un PDF :
                            1. Cliquez sur "📥 Télécharger le document"
                            2. Ouvrez le fichier HTML dans votre navigateur
                            3. Appuyez sur Ctrl+P (ou Cmd+P sur Mac)
                            4. Choisissez "Enregistrer en PDF" comme imprimante
                            5. Cliquez sur "Enregistrer"
                            
                            Le document est déjà formaté pour une impression parfaite!
                            """)
                        
                        # Nettoyer le fichier temporaire
                        try:
                            os.remove(file_path)
                        except:
                            pass
        
        with col3:
            if st.button("🔄 Nouvelle soumission", use_container_width=True):
                st.session_state.soumission_data = {
                    'numero': generate_numero_soumission(),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'client': {},
                    'projet': {},
                    'items': {},
                    'totaux': {},
                    'conditions': [],
                    'exclusions': []
                }
                st.rerun()
        
        # Afficher les informations de la soumission
        st.markdown("### 📋 Informations de la soumission")
        st.info(f"""
        **Numéro:** {st.session_state.soumission_data['numero']}  
        **Date:** {st.session_state.soumission_data['date']}  
        **Client:** {st.session_state.soumission_data['client'].get('nom', 'Non défini')}  
        **Projet:** {st.session_state.soumission_data['projet'].get('nom', 'Non défini')}  
        **Total:** ${st.session_state.soumission_data['totaux'].get('total', 0):,.2f}
        """)

def generate_numero_soumission():
    """Génère un numéro de soumission unique"""
    year = datetime.now().year
    # Créer le dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)
    # Obtenir le dernier numéro de soumissions_heritage
    conn_heritage = sqlite3.connect('data/soumissions_heritage.db')
    cursor_heritage = conn_heritage.cursor()
    cursor_heritage.execute('''
        CREATE TABLE IF NOT EXISTS soumissions_heritage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor_heritage.execute(f"SELECT numero FROM soumissions_heritage WHERE numero LIKE '{year}-%' ORDER BY numero DESC LIMIT 1")
    heritage_result = cursor_heritage.fetchone()
    conn_heritage.close()
    
    # Obtenir le dernier numéro de soumissions_multi pour éviter les doublons
    max_num = 0
    
    try:
        conn_multi = sqlite3.connect('data/soumissions_multi.db')
        cursor_multi = conn_multi.cursor()
        cursor_multi.execute(f"SELECT numero_soumission FROM soumissions WHERE numero_soumission LIKE '{year}-%' ORDER BY numero_soumission DESC LIMIT 1")
        multi_result = cursor_multi.fetchone()
        conn_multi.close()
        
        if multi_result:
            # Extraire le numéro
            multi_num = int(multi_result[0].split('-')[1])
            max_num = max(max_num, multi_num)
    except:
        pass
    
    if heritage_result:
        # Extraire le numéro
        heritage_num = int(heritage_result[0].split('-')[1])
        max_num = max(max_num, heritage_num)
    
    # Retourner le prochain numéro disponible
    return f"{year}-{str(max_num + 1).zfill(3)}"

def save_soumission():
    """Sauvegarde la soumission dans la base de données"""
    try:
        # Créer le dossier data s'il n'existe pas
        os.makedirs('data', exist_ok=True)
        
        conn = sqlite3.connect('data/soumissions_heritage.db')
        cursor = conn.cursor()
        
        # Vérifier si la table existe et obtenir sa structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='soumissions_heritage'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Vérifier les colonnes existantes
            cursor.execute("PRAGMA table_info(soumissions_heritage)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Si les colonnes nécessaires n'existent pas, recréer la table
            required_columns = ['numero', 'client_nom', 'projet_nom', 'montant_total', 'data', 'token', 'lien_public']
            if not all(col in columns for col in required_columns):
                # Sauvegarder les données existantes si possible
                try:
                    cursor.execute("SELECT * FROM soumissions_heritage")
                    old_data = cursor.fetchall()
                except:
                    old_data = []
                
                # Supprimer et recréer la table
                cursor.execute("DROP TABLE IF EXISTS soumissions_heritage")
                cursor.execute('''
                    CREATE TABLE soumissions_heritage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero TEXT UNIQUE,
                        client_nom TEXT,
                        projet_nom TEXT,
                        montant_total REAL,
                        data TEXT,
                        statut TEXT DEFAULT 'en_attente',
                        token TEXT UNIQUE,
                        lien_public TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        else:
            # Créer la table si elle n'existe pas
            cursor.execute('''
                CREATE TABLE soumissions_heritage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT UNIQUE,
                    client_nom TEXT,
                    projet_nom TEXT,
                    montant_total REAL,
                    data TEXT,
                    statut TEXT DEFAULT 'en_attente',
                    token TEXT UNIQUE,
                    lien_public TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Préparer les données pour la sérialisation JSON
        # Copier les données pour éviter de modifier l'original
        data_to_save = st.session_state.soumission_data.copy()
        
        # Convertir les dates en string si elles existent
        if 'projet' in data_to_save and 'date_debut' in data_to_save['projet']:
            if hasattr(data_to_save['projet']['date_debut'], 'isoformat'):
                data_to_save['projet']['date_debut'] = data_to_save['projet']['date_debut'].isoformat()
        
        # Sauvegarder la soumission
        data_json = json.dumps(data_to_save, ensure_ascii=False, default=str)
        
        # Générer un token unique
        import uuid
        token = str(uuid.uuid4())
        lien_public = f"http://localhost:8501/?token={token}&type=heritage"
        
        cursor.execute('''
            INSERT OR REPLACE INTO soumissions_heritage 
            (numero, client_nom, projet_nom, montant_total, data, token, lien_public, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            st.session_state.soumission_data['numero'],
            st.session_state.soumission_data['client'].get('nom', ''),
            st.session_state.soumission_data['projet'].get('nom', ''),
            st.session_state.soumission_data['totaux'].get('total', 0),
            data_json,
            token,
            lien_public
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return False

def generate_pdf():
    """Génère un PDF de la soumission"""
    try:
        # Générer le contenu HTML formaté
        html_content = generate_html_for_pdf()
        
        # Pour l'instant, on génère toujours un HTML
        # (pdfkit nécessite wkhtmltopdf qui doit être installé séparément)
        import tempfile
        html_file = tempfile.mktemp(suffix='.html')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file
        
    except Exception as e:
        st.error(f"Erreur lors de la génération du document : {str(e)}")
        return None

def generate_html_for_pdf():
    """Génère un HTML formaté pour conversion en PDF"""
    data = st.session_state.soumission_data
    
    # Calculer les totaux pour affichage
    total_travaux = sum(
        item.get('montant', 0) 
        for item in data['items'].values()
    )
    
    # Style CSS pour le PDF
    html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Soumission """ + data['numero'] + """</title>
        <style>
            @page {
                size: letter;
                margin: 0.75in;
            }
            
            body {
                font-family: Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.4;
                color: #333;
                margin: 0;
                padding: 0;
            }
            
            .header {
                text-align: center;
                border-bottom: 3px solid #4b5563;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }
            
            .header h1 {
                color: #4b5563;
                margin: 0;
                font-size: 24pt;
            }
            
            .header h2 {
                color: #6b7280;
                margin: 5px 0;
                font-size: 18pt;
            }
            
            .header p {
                margin: 5px 0;
                color: #666;
            }
            
            .info-section {
                margin-bottom: 25px;
                padding: 15px;
                background: #f9fafb;
                border-left: 4px solid #4b5563;
            }
            
            .info-section h3 {
                color: #4b5563;
                margin: 0 0 10px 0;
                font-size: 14pt;
            }
            
            .info-section p {
                margin: 5px 0;
                font-size: 11pt;
            }
            
            .info-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 25px;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                page-break-inside: avoid;
            }
            
            th {
                background: #4b5563;
                color: white;
                padding: 10px;
                text-align: left;
                font-size: 11pt;
            }
            
            td {
                padding: 8px 10px;
                border-bottom: 1px solid #e5e7eb;
                font-size: 10pt;
            }
            
            tr:nth-child(even) {
                background: #f9fafb;
            }
            
            .category-header {
                background: #e5e7eb;
                font-weight: bold;
                font-size: 12pt;
            }
            
            .category-header td {
                padding: 12px 10px;
                border-bottom: 2px solid #9ca3af;
            }
            
            .text-right {
                text-align: right;
            }
            
            .text-center {
                text-align: center;
            }
            
            .total-section {
                margin-top: 30px;
                padding: 20px;
                background: #f0f2f6;
                border: 2px solid #4b5563;
                page-break-inside: avoid;
            }
            
            .total-row {
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                font-size: 11pt;
            }
            
            .total-row.final {
                font-size: 16pt;
                font-weight: bold;
                color: #4b5563;
                border-top: 2px solid #4b5563;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            .conditions {
                margin-top: 30px;
                padding: 15px;
                background: #fef3c7;
                border: 1px solid #f59e0b;
            }
            
            .conditions h4 {
                color: #d97706;
                margin: 0 0 10px 0;
            }
            
            .conditions ul {
                margin: 5px 0 5px 20px;
                padding: 0;
            }
            
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #4b5563;
                text-align: center;
                font-size: 9pt;
                color: #666;
            }
            
            .company-info {
                margin-top: 20px;
                padding: 10px;
                background: #f9fafb;
                font-size: 9pt;
            }
            
            @media print {
                .page-break {
                    page-break-before: always;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SOUMISSION BUDGÉTAIRE</h1>
            <h2>Construction Héritage</h2>
            <p>Numéro: """ + data['numero'] + """ | Date: """ + data['date'] + """</p>
        </div>
        
        <div class="info-grid">
            <div class="info-section">
                <h3>👤 Informations Client</h3>
                <p><strong>Nom:</strong> """ + data['client'].get('nom', 'N/A') + """</p>
                <p><strong>Adresse:</strong> """ + data['client'].get('adresse', 'N/A') + """</p>
                <p><strong>Ville:</strong> """ + data['client'].get('ville', 'N/A') + """ """ + data['client'].get('code_postal', '') + """</p>
                <p><strong>Téléphone:</strong> """ + data['client'].get('telephone', 'N/A') + """</p>
                <p><strong>Courriel:</strong> """ + data['client'].get('courriel', 'N/A') + """</p>
            </div>
            
            <div class="info-section">
                <h3>🏗️ Informations Projet</h3>
                <p><strong>Nom du projet:</strong> """ + data['projet'].get('nom', 'N/A') + """</p>
                <p><strong>Adresse:</strong> """ + data['projet'].get('adresse', 'N/A') + """</p>
                <p><strong>Type:</strong> """ + str(data['projet'].get('type', 'N/A')) + """</p>
                <p><strong>Superficie:</strong> """ + str(data['projet'].get('superficie', 0)) + """ pi²</p>
                <p><strong>Étages:</strong> """ + str(data['projet'].get('etages', 1)) + """</p>
                <p><strong>Début prévu:</strong> """ + str(data['projet'].get('date_debut', 'N/A')) + """</p>
                <p><strong>Durée estimée:</strong> """ + data['projet'].get('duree', 'N/A') + """</p>
            </div>
        </div>
        
        <h3 style="color: #4b5563; margin-top: 30px;">Détails des travaux</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 50%;">Description</th>
                    <th style="width: 10%;" class="text-center">Quantité</th>
                    <th style="width: 20%;" class="text-right">Coût unitaire</th>
                    <th style="width: 20%;" class="text-right">Total</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Ajouter les items par catégorie
    for cat_id, category in CATEGORIES.items():
        cat_total = sum(
            item.get('montant', 0) 
            for key, item in data['items'].items()
            if key.startswith(cat_id + "_")
        )
        
        if cat_total > 0:
            html += f"""
                <tr class="category-header">
                    <td colspan="4">{category['name']}</td>
                </tr>
            """
            
            for key, item in data['items'].items():
                if key.startswith(cat_id + "_") and item.get('montant', 0) > 0:
                    html += f"""
                    <tr>
                        <td>
                            <strong>{item['titre']}</strong><br>
                            <small style="color: #666;">{item['description']}</small>
                        </td>
                        <td class="text-center">{item.get('quantite', 1):.1f}</td>
                        <td class="text-right">${item.get('prix_unitaire', 0):,.2f}</td>
                        <td class="text-right"><strong>${item.get('montant', 0):,.2f}</strong></td>
                    </tr>
                    """
            
            html += f"""
                <tr style="background: #e5e7eb;">
                    <td colspan="3" class="text-right"><strong>Sous-total {category['name'].split(' - ')[1]}:</strong></td>
                    <td class="text-right"><strong>${cat_total:,.2f}</strong></td>
                </tr>
            """
    
    # Section des totaux
    html += f"""
            </tbody>
        </table>
        
        <div class="total-section">
            <h3 style="color: #4b5563; margin: 0 0 15px 0;">Récapitulatif financier</h3>
            <div class="total-row">
                <span>Total des travaux:</span>
                <span>${data['totaux'].get('travaux', 0):,.2f}</span>
            </div>
            <div class="total-row">
                <span>Administration ({data['taux'].get('admin', 0.03)*100:.0f}%):</span>
                <span>${data['totaux'].get('administration', 0):,.2f}</span>
            </div>
            <div class="total-row">
                <span>Contingences ({data['taux'].get('contingency', 0.12)*100:.0f}%):</span>
                <span>${data['totaux'].get('contingences', 0):,.2f}</span>
            </div>
            <div class="total-row">
                <span>Profit ({data['taux'].get('profit', 0.15)*100:.0f}%):</span>
                <span>${data['totaux'].get('profit', 0):,.2f}</span>
            </div>
            <hr style="margin: 10px 0;">
            <div class="total-row">
                <span><strong>Sous-total avant taxes:</strong></span>
                <span><strong>${data['totaux'].get('sous_total', 0):,.2f}</strong></span>
            </div>
            <div class="total-row">
                <span>TPS (5%):</span>
                <span>${data['totaux'].get('tps', 0):,.2f}</span>
            </div>
            <div class="total-row">
                <span>TVQ (9.975%):</span>
                <span>${data['totaux'].get('tvq', 0):,.2f}</span>
            </div>
            <div class="total-row final">
                <span>TOTAL FINAL:</span>
                <span>${data['totaux'].get('total', 0):,.2f}</span>
            </div>
        </div>
    """
    
    # Conditions et exclusions
    if data.get('conditions'):
        html += """
        <div class="conditions">
            <h4>📝 Conditions</h4>
            <ul>
        """
        for condition in data['conditions']:
            if condition.strip():
                html += f"<li>{condition}</li>"
        html += "</ul></div>"
    
    if data.get('exclusions'):
        html += """
        <div class="conditions" style="background: #fee2e2; border-color: #ef4444;">
            <h4 style="color: #dc2626;">⚠️ Exclusions</h4>
            <ul>
        """
        for exclusion in data['exclusions']:
            if exclusion.strip():
                html += f"<li>{exclusion}</li>"
        html += "</ul></div>"
    
    # Footer avec informations de l'entreprise
    html += f"""
        <div class="footer">
            <div class="company-info">
                <strong>Construction Héritage</strong><br>
                129 Rue Poirier, Saint-Jean-sur-Richelieu (Québec) J3B 4E9<br>
                Tél: 438.524.9193 | Cell: 514.983.7492<br>
                info@constructionheritage.ca<br>
                RBQ: 5788-9784-01 | NEQ: 1163835623
            </div>
            <p style="margin-top: 20px;">
                Cette soumission est valide pour 30 jours à partir de la date d'émission.<br>
                Merci de votre confiance!
            </p>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_html():
    """Génère le HTML de la soumission basé sur le template"""
    # Charger le template original et le modifier avec les données
    with open('TEMPLATE_SOUM_BIG_R03.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Pour l'instant on retourne un HTML simple
    # TODO: Implémenter la génération complète basée sur le template
    
    data = st.session_state.soumission_data
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Soumission {data['numero']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .section {{ margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #4b5563; color: white; }}
            .total {{ font-weight: bold; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>SOUMISSION BUDGÉTAIRE</h1>
            <h2>Construction Héritage</h2>
            <p>Numéro: {data['numero']} | Date: {data['date']}</p>
        </div>
        
        <div class="section">
            <h3>Client</h3>
            <p>{data['client'].get('nom', '')}<br>
            {data['client'].get('adresse', '')}<br>
            {data['client'].get('ville', '')} {data['client'].get('code_postal', '')}</p>
        </div>
        
        <div class="section">
            <h3>Projet</h3>
            <p>{data['projet'].get('nom', '')}<br>
            {data['projet'].get('adresse', '')}<br>
            Type: {data['projet'].get('type', '')}</p>
        </div>
        
        <div class="section">
            <h3>Détails des travaux</h3>
            <table>
                <tr><th>Description</th><th>Montant</th></tr>
    """
    
    # Ajouter les items
    for key, item in data['items'].items():
        if item['montant'] > 0:
            html += f"""
                <tr>
                    <td>{item['titre']}</td>
                    <td>${item['montant']:,.2f}</td>
                </tr>
            """
    
    # Ajouter les totaux
    html += f"""
            </table>
        </div>
        
        <div class="section">
            <h3>Récapitulatif</h3>
            <table>
                <tr><td>Total des travaux</td><td>${data['totaux']['travaux']:,.2f}</td></tr>
                <tr><td>Administration</td><td>${data['totaux']['administration']:,.2f}</td></tr>
                <tr><td>Contingences</td><td>${data['totaux']['contingences']:,.2f}</td></tr>
                <tr><td>Profit</td><td>${data['totaux']['profit']:,.2f}</td></tr>
                <tr><td>Sous-total</td><td>${data['totaux']['sous_total']:,.2f}</td></tr>
                <tr><td>TPS (5%)</td><td>${data['totaux']['tps']:,.2f}</td></tr>
                <tr><td>TVQ (9.975%)</td><td>${data['totaux']['tvq']:,.2f}</td></tr>
                <tr class="total"><td>TOTAL FINAL</td><td>${data['totaux']['total']:,.2f}</td></tr>
            </table>
        </div>
    </body>
    </html>
    """
    
    return html

def show_soumission_heritage():
    """Fonction principale pour afficher le module de soumission"""
    create_soumission_form()

def get_saved_submission_html(submission_id):
    """Récupère le HTML d'une soumission sauvegardée"""
    try:
        conn = sqlite3.connect('data/soumissions_heritage.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT data FROM soumissions_heritage 
            WHERE id = ?
        ''', (submission_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            # Charger les données dans session state temporairement
            import streamlit as st
            data = json.loads(result[0])
            
            # S'assurer que soumission_data existe dans session_state
            if 'soumission_data' not in st.session_state:
                st.session_state.soumission_data = {}
            
            # Restaurer les données dans session_state
            st.session_state.soumission_data = data
            for key, value in data.items():
                st.session_state[key] = value
            
            # Générer le HTML avec les données restaurées
            return generate_html()
        return None
        
    except Exception as e:
        print(f"Erreur récupération soumission: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    st.set_page_config(
        page_title="Soumission - Construction Héritage",
        page_icon="🏗️",
        layout="wide"
    )
    show_soumission_heritage()