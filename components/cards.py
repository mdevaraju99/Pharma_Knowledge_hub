"""
Reusable UI card components
"""
import streamlit as st
from typing import Optional


def kpi_card(label: str, value: str, icon: str = "📊"):
    """Display a KPI card with gradient styling"""
    st.markdown(f"""
    <div class="kpi-card fade-in">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def news_card(title: str, description: str, source: str, date: str, url: str):
    """Display a news article card"""
    st.markdown(f"""
    <div class="news-card fade-in">
        <div class="news-title">{title}</div>
        <div class="news-meta">
            <span style="color: #6366F1;">📰 {source}</span> • 
            <span>📅 {date}</span>
        </div>
        <div class="news-description">{description}</div>
        <div style="margin-top: 0.75rem;">
            <a href="{url}" target="_blank" style="font-size: 0.9rem;">
                Read more →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def paper_card(title: str, authors: str, journal: str, date: str, url: str):
    """Display a research paper card"""
    st.markdown(f"""
    <div class="news-card fade-in">
        <div class="news-title">{title}</div>
        <div class="news-meta">
            <span>👥 {authors}</span>
        </div>
        <div class="news-meta">
            <span style="color: #6366F1;">📚 {journal}</span> • 
            <span>📅 {date}</span>
        </div>
        <div style="margin-top: 0.75rem;">
            <a href="{url}" target="_blank" style="font-size: 0.9rem;">
                View on PubMed →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def event_card(name: str, date: str, location: str, event_type: str, url: str, description: Optional[str] = None):
    """Display an event card"""
    type_colors = {
        "hackathon": "#10B981",
        "conference": "#6366F1",
        "workshop": "#F59E0B"
    }
    color = type_colors.get(event_type.lower(), "#6366F1")
    
    desc_html = f'<div class="news-description">{description}</div>' if description else ''
    
    st.markdown(f"""
    <div class="news-card fade-in">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div class="news-title">{name}</div>
            <span class="badge" style="background: {color}20; color: {color}; border-color: {color}50;">
                {event_type.upper()}
            </span>
        </div>
        <div class="news-meta" style="margin-top: 0.5rem;">
            <span>📅 {date}</span> • <span>📍 {location}</span>
        </div>
        {desc_html}
        <div style="margin-top: 0.75rem;">
            <a href="{url}" target="_blank" style="font-size: 0.9rem;">
                Register / Learn More →
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def loading_skeleton():
    """Display a loading skeleton"""
    st.markdown("""
    <div class="news-card" style="animation: pulse 1.5s infinite;">
        <div style="height: 1.2rem; background: rgba(99, 102, 241, 0.1); border-radius: 4px; margin-bottom: 0.5rem;"></div>
        <div style="height: 0.9rem; background: rgba(99, 102, 241, 0.05); border-radius: 4px; width: 60%; margin-bottom: 0.5rem;"></div>
        <div style="height: 4rem; background: rgba(99, 102, 241, 0.05); border-radius: 4px;"></div>
    </div>
    """, unsafe_allow_html=True)
