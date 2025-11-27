import streamlit as st
import anthropic
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

# Configuration de la page
st.set_page_config(
    page_title="Gazette EHPAD",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de l'état de session
if 'gazette_data' not in st.session_state:
    mois_actuel = datetime.now().strftime('%B %Y').capitalize()
    
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

if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

def generate_text(prompt: str, context: str, etablissement: str, mois: str) -> str:
    """Génère du texte via l'API Anthropic."""
    if not st.session_state.api_key:
        st.error("Veuillez entrer votre clé API Anthropic dans la barre latérale.")
        return ""
    
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
    except anthropic.AuthenticationError:
        st.error("Clé API invalide. Vérifiez votre clé Anthropic.")
        return ""
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
        spaceAfter=4*mm
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
        fontName='Helvetica-Oblique'
    )
    
    story = []
    data = st.session_state.gazette_data
    
    # Page 1 - Couverture & Éditorial
    story.append(Paragraph(data['etablissement'] or "Notre EHPAD", title_style))
    story.append(Paragraph(f"La Gazette — {data['mois']}", subtitle_style))
    story.append(Spacer(1, 5*mm))
    
    if data['cover_photos']:
        for photo in data['cover_photos'][:2]:
            try:
                img = Image(BytesIO(photo), width=80*mm, height=50*mm)
                story.append(img)
                story.append(Spacer(1, 3*mm))
            except:
                pass
    
    story.append(Paragraph("Éditorial", section_style))
    edito = data['edito_text'] or "Votre éditorial apparaîtra ici..."
    story.append(Paragraph(edito.replace('\n', '<br/>'), body_style))
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
    
    activites = data['activites_text'] or "Le récapitulatif des activités apparaîtra ici..."
    story.append(Paragraph(activites.replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    # Page 3 - Planning & News
    story.append(Paragraph("Planning du Mois", section_style))
    planning = data['planning_text'] or "Le planning apparaîtra ici..."
    story.append(Paragraph(planning.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Actualités", section_style))
    news = data['news_text'] or "Les actualités apparaîtront ici..."
    story.append(Paragraph(news.replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    # Page 4 - Chronique Mémoire
    story.append(Paragraph("Chronique Mémoire", section_style))
    
    if data['memoire_photos']:
        for photo in data['memoire_photos'][:2]:
            try:
                img = Image(BytesIO(photo), width=60*mm, height=40*mm)
                story.append(img)
                story.append(Spacer(1, 2*mm))
            except:
                pass
    
    memoire = data['memoire_text'] or "La chronique mémoire apparaîtra ici..."
    story.append(Paragraph(memoire.replace('\n', '<br/>'), memory_style))
    story.append(Spacer(1, 10*mm))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#2D5A4A'),
        alignment=TA_CENTER
    )
    story.append(Paragraph("Merci de votre lecture ! À très bientôt.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# === INTERFACE PRINCIPALE ===

# Header
st.title("📰 Gazette EHPAD")
st.caption("Créateur de gazette mensuelle pour votre établissement")

st.divider()

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key_input = st.text_input(
        "Clé API Anthropic",
        type="password",
        value=st.session_state.api_key,
        help="Obtenez votre clé sur console.anthropic.com"
    )
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ Clé API configurée")
    
    st.divider()
    
    st.header("📋 Navigation")
    page = st.radio(
        "Choisir une section",
        ["1 - Couverture et Éditorial", "2 - Activités", "3 - Planning et Actualités", "4 - Chronique Mémoire", "5 - Aperçu et Export"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    st.header("💾 Export PDF")
    if st.button("📄 Générer le PDF", use_container_width=True):
        with st.spinner("Génération du PDF..."):
            try:
                pdf_buffer = create_pdf()
                st.download_button(
                    label="⬇️ Télécharger le PDF",
                    data=pdf_buffer,
                    file_name=f"gazette-{st.session_state.gazette_data['mois'].replace(' ', '-')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erreur PDF : {str(e)}")

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
            photo.seek(0)
            with cols[i % 4]:
                st.image(photo, use_container_width=True)
    
    st.subheader("✍️ Éditorial")
    data['edito_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['edito_prompt'],
        placeholder="Ex: Parler de l'arrivée de l'automne, remercier l'équipe soignante, annoncer les fêtes de fin d'année...",
        height=100
    )
    
    if st.button("✨ Générer l'éditorial", key="gen_edito", disabled=not st.session_state.api_key or not data['edito_prompt']):
        with st.spinner("Génération en cours..."):
            result = generate_text(
                data['edito_prompt'],
                "Éditorial de la gazette - texte d'accueil chaleureux",
                data['etablissement'],
                data['mois']
            )
            if result:
                data['edito_text'] = result
                st.rerun()
    
    data['edito_text'] = st.text_area(
        "Texte de l'éditorial (modifiable)",
        value=data['edito_text'],
        height=200,
        key="edito_text_area"
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
            photo.seek(0)
            with cols[i % 4]:
                st.image(photo, use_container_width=True)
    
    st.subheader("✍️ Récapitulatif des activités")
    data['activites_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['activites_prompt'],
        placeholder="Ex: Ce mois-ci nous avons fait un atelier pâtisserie (tarte aux pommes), de la gym douce tous les lundis, une sortie au marché...",
        height=100
    )
    
    if st.button("✨ Générer le récapitulatif", key="gen_activites", disabled=not st.session_state.api_key or not data['activites_prompt']):
        with st.spinner("Génération en cours..."):
            result = generate_text(
                data['activites_prompt'],
                "Récapitulatif des activités du mois - mettre en valeur les moments partagés",
                data['etablissement'],
                data['mois']
            )
            if result:
                data['activites_text'] = result
                st.rerun()
    
    data['activites_text'] = st.text_area(
        "Texte des activités (modifiable)",
        value=data['activites_text'],
        height=200,
        key="activites_text_area"
    )

elif "Planning" in page:
    st.header("3️⃣ Planning & Actualités")
    
    st.subheader("📅 Planning du mois prochain")
    data['planning_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['planning_prompt'],
        placeholder="Ex: Lundi: gym douce 10h, Mardi: atelier mémoire 14h, Mercredi: chorale 15h...",
        height=100
    )
    
    if st.button("✨ Générer le planning", key="gen_planning", disabled=not st.session_state.api_key or not data['planning_prompt']):
        with st.spinner("Génération en cours..."):
            result = generate_text(
                data['planning_prompt'],
                "Planning des activités du mois prochain",
                data['etablissement'],
                data['mois']
            )
            if result:
                data['planning_text'] = result
                st.rerun()
    
    data['planning_text'] = st.text_area(
        "Texte du planning (modifiable)",
        value=data['planning_text'],
        height=150,
        key="planning_text_area"
    )
    
    st.divider()
    
    st.subheader("📢 Actualités de l'établissement")
    data['news_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['news_prompt'],
        placeholder="Ex: Nouvelle kinésithérapeute Mme Martin, travaux terminés au salon, anniversaires du mois...",
        height=100
    )
    
    if st.button("✨ Générer les actualités", key="gen_news", disabled=not st.session_state.api_key or not data['news_prompt']):
        with st.spinner("Génération en cours..."):
            result = generate_text(
                data['news_prompt'],
                "Actualités générales de l'établissement - informations pratiques",
                data['etablissement'],
                data['mois']
            )
            if result:
                data['news_text'] = result
                st.rerun()
    
    data['news_text'] = st.text_area(
        "Texte des actualités (modifiable)",
        value=data['news_text'],
        height=150,
        key="news_text_area"
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
            photo.seek(0)
            with cols[i % 4]:
                st.image(photo, use_container_width=True)
    
    st.subheader("✍️ Texte d'hommage")
    data['memoire_prompt'] = st.text_area(
        "Instructions pour la génération",
        value=data['memoire_prompt'],
        placeholder="Ex: Ce mois-ci, nous avons dit au revoir à M. Robert (aimait jardiner, ancien instituteur) et Mme Jeanne (passionnée de tricot)...",
        height=100
    )
    
    if st.button("✨ Générer l'hommage", key="gen_memoire", disabled=not st.session_state.api_key or not data['memoire_prompt']):
        with st.spinner("Génération en cours..."):
            result = generate_text(
                data['memoire_prompt'],
                "Chronique Mémoire - hommage subtil et bienveillant aux résidents qui nous ont quittés",
                data['etablissement'],
                data['mois']
            )
            if result:
                data['memoire_text'] = result
                st.rerun()
    
    data['memoire_text'] = st.text_area(
        "Texte de la chronique (modifiable)",
        value=data['memoire_text'],
        height=200,
        key="memoire_text_area"
    )

elif "Aperçu" in page:
    st.header("👁️ Aperçu de la Gazette")
    
    # Page 1
    st.subheader(f"📄 Page 1 : Couverture")
    with st.container(border=True):
        st.markdown(f"### {data['etablissement'] or 'Notre EHPAD'}")
        st.caption(f"La Gazette — {data['mois']}")
        if data['cover_photos']:
            cols = st.columns(2)
            for i, photo in enumerate(data['cover_photos'][:2]):
                with cols[i]:
                    st.image(photo, use_container_width=True)
        st.markdown("#### Éditorial")
        st.write(data['edito_text'] or "_Votre éditorial apparaîtra ici..._")
    
    # Page 2
    st.subheader("📄 Page 2 : Activités")
    with st.container(border=True):
        st.markdown("#### Les Activités du Mois")
        if data['activites_photos']:
            cols = st.columns(4)
            for i, photo in enumerate(data['activites_photos'][:4]):
                with cols[i % 4]:
                    st.image(photo, use_container_width=True)
        st.write(data['activites_text'] or "_Le récapitulatif apparaîtra ici..._")
    
    # Page 3
    st.subheader("📄 Page 3 : Planning & Actualités")
    with st.container(border=True):
        st.markdown("#### Planning du Mois")
        st.write(data['planning_text'] or "_Le planning apparaîtra ici..._")
        st.markdown("#### Actualités")
        st.write(data['news_text'] or "_Les actualités apparaîtront ici..._")
    
    # Page 4
    st.subheader("📄 Page 4 : Chronique Mémoire")
    with st.container(border=True):
        st.markdown("#### 🕯️ Chronique Mémoire")
        if data['memoire_photos']:
            cols = st.columns(2)
            for i, photo in enumerate(data['memoire_photos'][:2]):
                with cols[i]:
                    st.image(photo, use_container_width=True)
        st.write(f"_{data['memoire_text'] or 'La chronique mémoire apparaîtra ici...'}_")
        
        st.success("**Merci de votre lecture !** À très bientôt pour un nouveau numéro.")

# Footer
st.divider()
st.caption("📰 Gazette EHPAD — Créé avec ❤️ pour faciliter la communication en EHPAD")
