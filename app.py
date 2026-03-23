"""
Pharma Knowledge Hub - Main Application
A comprehensive pharmaceutical knowledge portal with real-time data
"""
import streamlit as st
from streamlit_option_menu import option_menu
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import config

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "theme" not in st.session_state:
    st.session_state.theme = config.DEFAULT_THEME

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load custom CSS with theme
def load_css(theme):
    css_path = project_root / "styles" / "custom.css"
    if css_path.exists():
        with open(css_path) as f:
            css_content = f.read()
        
        # Apply theme-specific overrides
        if theme == "light":
            theme_override = """
            .main, [data-testid="stAppViewContainer"] {
                background-color: #F9FAFB !important;
                color: #1F2937 !important;
            }
            [data-testid="stSidebar"] {
                background-color: #FFFFFF !important;
            }
            .stMarkdown, p, span, div {
                color: #1F2937 !important;
            }
            """
            css_content += theme_override
        else:
            theme_override = """
            .main, [data-testid="stAppViewContainer"] {
                background-color: #0E1117 !important;
                color: #E5E7EB !important;
            }
            [data-testid="stSidebar"] {
                background-color: #1E1E2E !important;
            }
            """
            css_content += theme_override
        
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

load_css(st.session_state.theme)

# Main title with gradient
st.markdown(f"""
<h1 class="gradient-header" style="text-align: center; margin-bottom: 0.5rem;">
    {config.APP_ICON} {config.APP_TITLE}
</h1>
<p style="text-align: center; color: var(--text-secondary); margin-bottom: 2rem;">
    Your comprehensive pharmaceutical knowledge platform
</p>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Theme toggle at the top
    st.markdown("### ⚙️ Theme")
    
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("🌙 Dark", use_container_width=True, type="primary" if st.session_state.theme == "dark" else "secondary"):
            st.session_state.theme = "dark"
            st.rerun()
    
    with theme_col2:
        if st.button("☀️ Light", use_container_width=True, type="primary" if st.session_state.theme == "light" else "secondary"):
            st.session_state.theme = "light"
            st.rerun()
    
    st.markdown("---")
    
    # Navigation menu
    st.markdown("### 📋 Navigation")
    
    selected = option_menu(
        menu_title=None,
        options=[
            "Pharma News",
            "Research Papers",
            "Analytics",
            "Drug Info",
            "Clinical Trials",
            "Regulatory",
            "Company News",
            "Events",
            "Company Knowledge",
            "Chatbot"
        ],
        icons=[
            "newspaper",
            "journal-medical",
            "bar-chart-line",
            "capsule",
            "clipboard2-pulse",
            "shield-check",
            "building",
            "calendar-event",
            "building-check",
            "chat-dots"
        ],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important"},
            "icon": {"font-size": "1rem"},
            "nav-link": {
                "font-size": "0.95rem",
                "text-align": "left",
                "margin": "0.25rem 0",
                "padding": "0.6rem 1rem",
                "border-radius": "8px"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #6366F1, #8B5CF6)",
                "font-weight": "500"
            },
        }
    )

# Route to tabs (renamed from pages to avoid Streamlit auto-detection)
if selected == "Pharma News":
    from tabs import pharma_news
    pharma_news.show()
    
elif selected == "Research Papers":
    from tabs import research_papers
    research_papers.show()
    
elif selected == "Analytics":
    from tabs import analytics
    analytics.show()
    
elif selected == "Drug Info":
    from tabs import drug_info
    drug_info.show()
    
elif selected == "Clinical Trials":
    from tabs import clinical_trials
    clinical_trials.show()
    
elif selected == "Regulatory":
    from tabs import regulatory
    regulatory.show()
    
elif selected == "Company News":
    from tabs import company_news
    company_news.show()
    
elif selected == "Events":
    from tabs import events
    events.show()

elif selected == "Company Knowledge":
    from tabs import company_knowledge
    company_knowledge.show()
    
elif selected == "Chatbot":
    from tabs import chatbot
    chatbot.show()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); font-size: 0.85rem; padding: 1rem 0;">
    <p>
        Powered by NewsAPI, OpenFDA, ClinicalTrials.gov, PubMed & Groq AI<br>
        <em>Data is for informational purposes only. Always consult healthcare professionals.</em>
    </p>
</div>
""", unsafe_allow_html=True)
