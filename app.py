import streamlit as st
import anthropic
from datetime import datetime
import locale
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import base64
from PIL import Image as PILImage

# Configuration de la page
st.set_page_config(
    page_title="Gazette EHPAD",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2D5A4A 0%, #4A7C6B 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white !important;
        margin: 0;
    }
    .main-header p {
        opacity: 0.9;
        margin: 0.5rem 0 0 0;
    }
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #C9A962 0%, #B8983D 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #B8983D 0%, #A68732 100%);
    }
    .preview-page {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #eee;
    }
    .gazette-title {
        font-family: Georgia, serif;
        color: #2D5A4A;
        text-align: center;
        border-bottom: 3px solid #2D5A4A;
        padding-bottom: 0.5rem;
    }
    .section-title {
        font-family: Georgia, serif;
        color: #2D5A4A;
        border-left: 4px solid #C9A962;
        padding-left: 1rem;
        margin: 1.5rem 0 1rem 0;
    }
    .memory-section {
        background: linear-gradient(135deg, #F5F0E8 0%, #EDE5D8 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'gazette_data' not in st.session_state:
    # Essayer d'obtenir le mois en français
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        mois_actuel = datetime.now().strftime('%B %Y').capitalize()
    except:
        mois_actuel = datetime.now().strftime('%B %Y')
    
    st.session_state.gazette_data = {
        'etablissement': '',
        'mois': mois_actuel,
        'edito_prompt': '',
        'edito_text': '',
        'cover_photos': [],
        'activites_prompt': '',
        'activites_text': '',
        'activites_photos': [],
        'planning_prompt': '',
        'planning_text': '',
        'news_prompt': '',
        'news_text': '',
        'memoire_prompt': '',
        'memoire_text': '',
        'memoire_photos': []
    }

def generate_text(prompt: str, context: str, etablissement: str, mois: str) -> str:
    """Génère du texte via l'API Anthropic."""
    try:
        client = anthropic.Anthropic(api_key=st.session_state.api_key)
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{
                "role": "user",
                "content": f"""Tu es rédacteur pour la gazette mensuelle d'un EHPAD ({etablissement or 'notre établissement'}).

Contexte: {context}
Mois: {mois}

Instructions: {prompt}

Rédige un texte chaleureux et bienveillant:
- Français simple et accessible
- Positif et valorisant pour les résidents et le personnel
- Adapté aux familles et résidents
- 2-4 paragraphes

Réponds uniquement avec le texte, sans introduction ni commentaire."""
            }]
        )
        
        return message.content[0].text
    except Exception as e:
        st.error(f"Erreur lors de la génération : {str(e)}")
        return ""

def create_pdf():
    """Génère le PDF de la gazette."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'GazetteTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#2D5A4A'),
        alignment=TA_CENTER,
        spaceAfter=5*mm
    )
    
    subtitle_style = ParagraphStyle(
        'GazetteSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=HexColor('#C9A962'),
        alignment=TA_CENTER,
        spaceAfter=10*mm
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2D5A4A'),
        spaceBefore=8*mm,
        spaceAfter=4*mm,
        leftIndent=10,
        borderLeftWidth=3,
        borderLeftColor=HexColor('#C9A962')
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#2C3E50'),
        alignment=TA_JUSTIFY,
        spaceAfter=3*mm,
        leading=16
    )
    
    memory_style = ParagraphStyle(
        'MemoryText',
        parent=body_style,
        fontName='Helvetica-Oblique',
        backColor=HexColor('#F5F0E8')
    )
    
    story = []
    data = st.session_state.gazette_data
    
    # Page 1 - Couverture & Éditorial
    story.append(Paragraph(data['etablissement'] or "Notre EHPAD", title_style))
    story.append(Paragraph(f"La Gazette — {data['mois']}", subtitle_style))
    story.append(Spacer(1, 5*mm))
    
    # Photos de couverture
    if data['cover_photos']:
        for photo in data['cover_photos'][:2]:
            try:
                img = Image(BytesIO(photo), width=80*mm, height=50*mm)
                story.append(img)
                story.append(Spacer(1, 3*mm))
            except:
                pass
    
    story.append(Paragraph("Éditorial", section_style))
    story.append(Paragraph(data['edito_text'] or "Votre éditorial apparaîtra ici...", body_style))
    story.append(PageBreak())
    
    # Page 2 - Activités
    story.append(Paragraph("Les Activités du Mois", section_style))
    
    if data['activites_photos']:
        for photo in data['activites_photos'][:4]:
            try:
                img = Image(BytesIO(photo), width=70*mm, height=45*mm)
                story.append(img)
                story.append(Spacer(1, 2*mm))
            except:
                pass
    
    story.append(Paragraph(data['activites_text'] or "Le récapitulatif des activités apparaîtra ici...", body_style))
    story.append(PageBreak())
    
    # Page 3 - Planning & News
    story.append(Paragraph("Planning du Mois", section_style))
    story.append(Paragraph(data['planning_text'] or "Le planning apparaîtra ici...", body_style))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Actualités", section_style))
    story.append(Paragraph(data['news_text'] or "Les actualités apparaîtront ici...", body_style))
    story.append(PageBreak())
    
    # Page 4 - Chronique Mémoire
    story.append(Paragraph("🕯️ Chronique Mémoire", section_style))
    
    if data['memoire_photos']:
        for photo in data['memoire_photos'][:2]:
            try:
                img = Image(BytesIO(photo), width=60*mm, height=40*mm)
                story.append(img)
                story.append(Spacer(1, 2*mm))
            except:
                pass
    
    story.append(Paragraph(data['memoire_text'] or "La chronique mémoire apparaîtra ici...", memory_style))
    story.append(Spacer(1, 10*mm))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#FFFFFF'),
        alignment=TA_CENTER,
        backColor=HexColor('#2D5A4A')
    )
    story.append(Paragraph("Merci de votre lecture ! À très bientôt.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# === INTERFACE PRINCIPALE ===

# Header
st.markdown("""
<div class="main-header">
    <h1>📰 Gazette EHPAD</h1>
    <p>Créateur de gazette mensuelle pour votre établissement</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = st.text_input(
        "Clé API Anthropic",
        type="password",
        help="Obtenez votre clé sur console.anthropic.com"
    )
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ Clé API configurée")
    
    st.divider()
    
    st.header("📋 Navigation")
    page = st.radio(
        "Choisir une section",
        ["1️⃣ Couverture & Éditorial", "2️⃣ Activités", "3️⃣ Planning & Actualités", "4️⃣ Chronique Mémoire", "👁️ Aperçu & Export"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.header("💾 Export")
    if st.button("📄 Générer le PDF", use_container_width=True):
        with st.spinner("Génération du PDF..."):
            pdf_buffer = create_pdf()
            st.download_button(
                label="⬇️ Télécharger le PDF",
                data=pdf_buffer,
                file_name=f"gazette-{st.session_state.gazette_data['mois'].replace(' ', '-')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# Contenu principal selon la page sélectionnée
data = st.session_state.gazette_data

if "Couverture" in page:
    st.header("1️⃣ Couverture & Éditorial")
    
    col1, col2 = st.columns(2)
    with col1:
        data['etablissement'] = st.text_input(
            "🏠 Nom de l'établissement",
            value=data['etablissement'],
            placeholder="Ex: Résidence Les Jardins de Marie"
        )
    with col2:
        data['mois'] = st.text_input(
            "📅 Mois de la gazette",
            value=data['mois'],
            placeholder="Ex: Novembre 2024"
        )
    
    st.subheader("📷 Photos de couverture")
    uploaded_cover = st.file_uploader(
        "Ajouter des photos",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="cover_upload"
    )
    if uploaded_cover:
        data['cover_photos'] = [f.read() for f in uploaded_cover]
        st.success(f"✅ {len(uploaded_cover)} photo(s) ajoutée(s)")
        cols = st.columns(min(len(uploaded_cover), 4))
        for i, photo in enumerate(uploaded_cover):
            with cols[i % 4]:
                st.image(photo, use_container_width=True)
    
    st.subheader("✍️ Éditorial")
    data['edito_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['edito_prompt'],
        placeholder="Ex: Parler de l'arrivée de l'automne, remercier l'équipe soignante, annoncer les fêtes de fin d'année...",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✨ Générer", key="gen_edito", disabled=not api_key or not data['edito_prompt']):
            with st.spinner("Génération en cours..."):
                data['edito_text'] = generate_text(
                    data['edito_prompt'],
                    "Éditorial de la gazette - texte d'accueil chaleureux",
                    data['etablissement'],
                    data['mois']
                )
    
    data['edito_text'] = st.text_area(
        "Texte de l'éditorial (modifiable)",
        value=data['edito_text'],
        height=200
    )

elif "Activités" in page:
    st.header("2️⃣ Activités du Mois")
    
    st.subheader("📷 Photos des activités")
    uploaded_activites = st.file_uploader(
        "Ajouter des photos",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="activites_upload"
    )
    if uploaded_activites:
        data['activites_photos'] = [f.read() for f in uploaded_activites]
        st.success(f"✅ {len(uploaded_activites)} photo(s) ajoutée(s)")
        cols = st.columns(min(len(uploaded_activites), 4))
        for i, photo in enumerate(uploaded_activites):
            with cols[i % 4]:
                st.image(photo, use_container_width=True)
    
    st.subheader("✍️ Récapitulatif des activités")
    data['activites_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['activites_prompt'],
        placeholder="Ex: Ce mois-ci nous avons fait un atelier pâtisserie (tarte aux pommes), de la gym douce tous les lundis, une sortie au marché, la visite des enfants de l'école maternelle...",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✨ Générer", key="gen_activites", disabled=not api_key or not data['activites_prompt']):
            with st.spinner("Génération en cours..."):
                data['activites_text'] = generate_text(
                    data['activites_prompt'],
                    "Récapitulatif des activités du mois - mettre en valeur les moments partagés",
                    data['etablissement'],
                    data['mois']
                )
    
    data['activites_text'] = st.text_area(
        "Texte des activités (modifiable)",
        value=data['activites_text'],
        height=200
    )

elif "Planning" in page:
    st.header("3️⃣ Planning & Actualités")
    
    st.subheader("📅 Planning du mois prochain")
    data['planning_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['planning_prompt'],
        placeholder="Ex: Lundi: gym douce 10h, Mardi: atelier mémoire 14h, Mercredi: chorale 15h, Jeudi: loto 14h30, Vendredi: art-thérapie 10h...",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✨ Générer", key="gen_planning", disabled=not api_key or not data['planning_prompt']):
            with st.spinner("Génération en cours..."):
                data['planning_text'] = generate_text(
                    data['planning_prompt'],
                    "Planning des activités du mois prochain",
                    data['etablissement'],
                    data['mois']
                )
    
    data['planning_text'] = st.text_area(
        "Texte du planning (modifiable)",
        value=data['planning_text'],
        height=150
    )
    
    st.divider()
    
    st.subheader("📢 Actualités de l'établissement")
    data['news_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['news_prompt'],
        placeholder="Ex: Nouvelle kinésithérapeute Mme Martin, travaux terminés au salon, menu spécial Noël le 25, anniversaires du mois: Mme Dupont (92 ans), M. Bernard (85 ans)...",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✨ Générer", key="gen_news", disabled=not api_key or not data['news_prompt']):
            with st.spinner("Génération en cours..."):
                data['news_text'] = generate_text(
                    data['news_prompt'],
                    "Actualités générales de l'établissement - informations pratiques",
                    data['etablissement'],
                    data['mois']
                )
    
    data['news_text'] = st.text_area(
        "Texte des actualités (modifiable)",
        value=data['news_text'],
        height=150
    )

elif "Mémoire" in page:
    st.header("4️⃣ Chronique Mémoire")
    
    st.info("🕯️ Cette section rend hommage avec délicatesse aux résidents qui nous ont quittés.")
    
    st.subheader("📷 Photos souvenirs")
    uploaded_memoire = st.file_uploader(
        "Ajouter des photos",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="memoire_upload"
    )
    if uploaded_memoire:
        data['memoire_photos'] = [f.read() for f in uploaded_memoire]
        st.success(f"✅ {len(uploaded_memoire)} photo(s) ajoutée(s)")
        cols = st.columns(min(len(uploaded_memoire), 4))
        for i, photo in enumerate(uploaded_memoire):
            with cols[i % 4]:
                st.image(photo, use_container_width=True)
    
    st.subheader("✍️ Texte d'hommage")
    data['memoire_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['memoire_prompt'],
        placeholder="Ex: Ce mois-ci, nous avons dit au revoir à M. Robert (aimait jardiner, ancien instituteur, toujours souriant) et Mme Jeanne (passionnée de tricot, aimait raconter des histoires)...",
        height=100
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("✨ Générer", key="gen_memoire", disabled=not api_key or not data['memoire_prompt']):
            with st.spinner("Génération en cours..."):
                data['memoire_text'] = generate_text(
                    data['memoire_prompt'],
                    "Chronique Mémoire - hommage subtil et bienveillant aux résidents qui nous ont quittés, célébrer leur mémoire avec dignité et chaleur",
                    data['etablissement'],
                    data['mois']
                )
    
    data['memoire_text'] = st.text_area(
        "Texte de la chronique (modifiable)",
        value=data['memoire_text'],
        height=200
    )

elif "Aperçu" in page:
    st.header("👁️ Aperçu de la Gazette")
    
    # Page 1
    st.markdown(f"""
    <div class="preview-page">
        <h1 class="gazette-title">{data['etablissement'] or 'Notre EHPAD'}</h1>
        <p style="text-align: center; color: #C9A962; font-size: 1.1rem;">La Gazette — {data['mois']}</p>
        <h2 class="section-title">Éditorial</h2>
        <p style="text-align: justify; line-height: 1.7;">{data['edito_text'] or '<em>Votre éditorial apparaîtra ici...</em>'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Page 2
    st.markdown(f"""
    <div class="preview-page">
        <h2 class="section-title">Les Activités du Mois</h2>
        <p style="text-align: justify; line-height: 1.7;">{data['activites_text'] or '<em>Le récapitulatif apparaîtra ici...</em>'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Page 3
    st.markdown(f"""
    <div class="preview-page">
        <h2 class="section-title">Planning du Mois</h2>
        <p style="text-align: justify; line-height: 1.7;">{data['planning_text'] or '<em>Le planning apparaîtra ici...</em>'}</p>
        <h2 class="section-title">Actualités</h2>
        <p style="text-align: justify; line-height: 1.7;">{data['news_text'] or '<em>Les actualités apparaîtront ici...</em>'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Page 4
    st.markdown(f"""
    <div class="preview-page">
        <div class="memory-section">
            <h2 style="color: #2D5A4A; font-family: Georgia, serif;">🕯️ Chronique Mémoire</h2>
            <p style="font-style: italic; line-height: 1.8;">{data['memoire_text'] or '<em>La chronique mémoire apparaîtra ici...</em>'}</p>
        </div>
        <div style="background: linear-gradient(135deg, #2D5A4A, #4A7C6B); color: white; text-align: center; padding: 1rem; border-radius: 8px; margin-top: 1.5rem;">
            <p style="font-family: Georgia, serif; font-size: 1.1rem; margin: 0;">Merci de votre lecture !</p>
            <p style="opacity: 0.9; margin: 0.3rem 0 0 0;">À très bientôt pour un nouveau numéro</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>📰 Gazette EHPAD — Créé avec ❤️ pour faciliter la communication en EHPAD</p>",
    unsafe_allow_html=True
)
