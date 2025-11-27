import streamlit as st
import google.generativeai as genai
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

st.set_page_config(page_title="Gazette EHPAD", page_icon="📰", layout="wide")

# Initialisation
if 'data' not in st.session_state:
    st.session_state.data = {
        'etablissement': '',
        'mois': datetime.now().strftime('%B %Y'),
        'edito_prompt': '', 'edito_text': '',
        'activites_prompt': '', 'activites_text': '',
        'planning_prompt': '', 'planning_text': '',
        'news_prompt': '', 'news_text': '',
        'memoire_prompt': '', 'memoire_text': '',
    }

def generate_text(prompt, context, etablissement, mois, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        full_prompt = f"""Tu es redacteur pour la gazette mensuelle d'un EHPAD ({etablissement or 'notre etablissement'}).

Contexte: {context}
Mois: {mois}

Instructions: {prompt}

Redige un texte chaleureux et bienveillant en francais simple, positif, de 2-4 paragraphes.
Reponds uniquement avec le texte, sans introduction."""

        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Erreur: {str(e)}"

def create_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=24, textColor=HexColor('#2D5A4A'), alignment=TA_CENTER, spaceAfter=5*mm)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=14, textColor=HexColor('#C9A962'), alignment=TA_CENTER, spaceAfter=10*mm)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, textColor=HexColor('#2D5A4A'), spaceBefore=8*mm, spaceAfter=4*mm)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=11, textColor=HexColor('#2C3E50'), alignment=TA_JUSTIFY, spaceAfter=3*mm, leading=16)
    
    story = []
    
    story.append(Paragraph(data['etablissement'] or "Notre EHPAD", title_style))
    story.append(Paragraph(f"La Gazette - {data['mois']}", subtitle_style))
    story.append(Paragraph("Editorial", section_style))
    story.append(Paragraph((data['edito_text'] or "...").replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    story.append(Paragraph("Les Activites du Mois", section_style))
    story.append(Paragraph((data['activites_text'] or "...").replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    story.append(Paragraph("Planning du Mois", section_style))
    story.append(Paragraph((data['planning_text'] or "...").replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Actualites", section_style))
    story.append(Paragraph((data['news_text'] or "...").replace('\n', '<br/>'), body_style))
    story.append(PageBreak())
    
    story.append(Paragraph("Chronique Memoire", section_style))
    story.append(Paragraph((data['memoire_text'] or "...").replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("Merci de votre lecture !", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=12, textColor=HexColor('#2D5A4A'), alignment=TA_CENTER)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Interface
st.title("Gazette EHPAD")
st.caption("Createur de gazette mensuelle avec IA")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Cle API Google Gemini", type="password", help="Obtenez-la sur aistudio.google.com")
    
    if api_key:
        st.success("Cle configuree")
    
    st.divider()
    
    page = st.radio("Section", ["Couverture", "Activites", "Planning", "Memoire", "Apercu"])
    
    st.divider()
    
    if st.button("Telecharger PDF"):
        pdf = create_pdf(st.session_state.data)
        st.download_button("Cliquez pour telecharger", pdf, "gazette.pdf", "application/pdf")

data = st.session_state.data

if page == "Couverture":
    st.header("Page 1 : Couverture")
    
    data['etablissement'] = st.text_input("Nom etablissement", value=data['etablissement'])
    data['mois'] = st.text_input("Mois", value=data['mois'])
    
    st.subheader("Editorial")
    data['edito_prompt'] = st.text_area("Decrivez ce que vous voulez", value=data['edito_prompt'], height=80, key="ep")
    
    if st.button("Generer editorial") and api_key and data['edito_prompt']:
        with st.spinner("Generation..."):
            data['edito_text'] = generate_text(data['edito_prompt'], "Editorial accueil", data['etablissement'], data['mois'], api_key)
    
    data['edito_text'] = st.text_area("Texte editorial", value=data['edito_text'], height=200, key="et")

elif page == "Activites":
    st.header("Page 2 : Activites")
    
    data['activites_prompt'] = st.text_area("Decrivez les activites du mois", value=data['activites_prompt'], height=80, key="ap")
    
    if st.button("Generer activites") and api_key and data['activites_prompt']:
        with st.spinner("Generation..."):
            data['activites_text'] = generate_text(data['activites_prompt'], "Recapitulatif activites", data['etablissement'], data['mois'], api_key)
    
    data['activites_text'] = st.text_area("Texte activites", value=data['activites_text'], height=200, key="at")

elif page == "Planning":
    st.header("Page 3 : Planning et Actualites")
    
    st.subheader("Planning")
    data['planning_prompt'] = st.text_area("Decrivez le planning", value=data['planning_prompt'], height=80, key="pp")
    
    if st.button("Generer planning") and api_key and data['planning_prompt']:
        with st.spinner("Generation..."):
            data['planning_text'] = generate_text(data['planning_prompt'], "Planning mensuel", data['etablissement'], data['mois'], api_key)
    
    data['planning_text'] = st.text_area("Texte planning", value=data['planning_text'], height=150, key="pt")
    
    st.subheader("Actualites")
    data['news_prompt'] = st.text_area("Decrivez les actualites", value=data['news_prompt'], height=80, key="np")
    
    if st.button("Generer actualites") and api_key and data['news_prompt']:
        with st.spinner("Generation..."):
            data['news_text'] = generate_text(data['news_prompt'], "Actualites etablissement", data['etablissement'], data['mois'], api_key)
    
    data['news_text'] = st.text_area("Texte actualites", value=data['news_text'], height=150, key="nt")

elif page == "Memoire":
    st.header("Page 4 : Chronique Memoire")
    st.info("Cette section rend hommage aux residents qui nous ont quittes.")
    
    data['memoire_prompt'] = st.text_area("Decrivez les personnes a honorer", value=data['memoire_prompt'], height=80, key="mp")
    
    if st.button("Generer hommage") and api_key and data['memoire_prompt']:
        with st.spinner("Generation..."):
            data['memoire_text'] = generate_text(data['memoire_prompt'], "Hommage bienveillant aux residents disparus", data['etablissement'], data['mois'], api_key)
    
    data['memoire_text'] = st.text_area("Texte hommage", value=data['memoire_text'], height=200, key="mt")

elif page == "Apercu":
    st.header("Apercu de la Gazette")
    
    st.subheader(data['etablissement'] or "Notre EHPAD")
    st.caption("La Gazette - " + data['mois'])
    
    st.write("**Editorial**")
    st.write(data['edito_text'] or "...")
    
    st.divider()
    
    st.write("**Activites du Mois**")
    st.write(data['activites_text'] or "...")
    
    st.divider()
    
    st.write("**Planning**")
    st.write(data['planning_text'] or "...")
    
    st.write("**Actualites**")
    st.write(data['news_text'] or "...")
    
    st.divider()
    
    st.write("**Chronique Memoire**")
    st.write(data['memoire_text'] or "...")

st.divider()
st.caption("Gazette EHPAD - Gratuit avec Google Gemini")
