"""
Tabs Package - Exports all tab modules
"""
from . import analytics
from . import chatbot
from . import clinical_trials
from . import company_knowledge
from . import company_news
from . import drug_info
from . import events
from . import pharma_news
from . import regulatory
from . import research_papers

__all__ = [
    'analytics',
    'chatbot',
    'clinical_trials',
    'company_knowledge',
    'company_news',
    'drug_info',
    'events',
    'pharma_news',
    'regulatory',
    'research_papers'
]
