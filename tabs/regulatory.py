"""
Regulatory Updates Page
"""
import streamlit as st
from utils.data_fetchers import fetch_regulatory_updates
from utils.formatters import format_date


def show():
    st.markdown('<h2 class="gradient-header">🛡️ Regulatory Updates</h2>', unsafe_allow_html=True)
    st.markdown("FDA enforcement actions, recalls, and safety alerts")
    
    # Fetch regulatory data
    with st.spinner("🔍 Fetching FDA updates..."):
        updates = fetch_regulatory_updates(limit=20)
    
    if not updates:
        st.warning("⚠️ No regulatory updates found.")
        return
    
    st.success(f"✅ Found {len(updates)} recent updates")
    
    # Filter by classification
    classifications = ["All"] + sorted(list(set([u.get("classification", "N/A") for u in updates])))
    selected_class = st.selectbox("Filter by Classification", classifications)
    
    # Filter updates
    if selected_class != "All":
        filtered_updates = [u for u in updates if u.get("classification") == selected_class]
    else:
        filtered_updates = updates
    
    # Display updates
    for update in filtered_updates:
        classification = update.get("classification", "N/A")
        
        # Color code by classification
        if classification == "Class I":
            color = "#EF4444"  # Red - most serious
        elif classification == "Class II":
            color = "#F59E0B"  # Orange - moderate
        elif classification == "Class III":
            color = "#10B981"  # Green - least serious
        else:
            color = "#6366F1"  # Blue - unknown
        
        st.markdown(f"""
        <div class="news-card fade-in">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div class="news-title">{update.get('product', 'N/A')}</div>
                <span class="badge" style="background: {color}20; color: {color}; border-color: {color}50;">
                    {classification}
                </span>
            </div>
            <div class="news-meta" style="margin-top: 0.5rem;">
                <span>🏢 {update.get('company', 'N/A')}</span> • 
                <span>📅 {update.get('date', 'N/A')}</span>
            </div>
            <div class="news-description" style="margin-top: 0.75rem;">
                <strong>Reason for Recall:</strong> {update.get('reason', 'N/A')}
            </div>
            <div class="news-meta" style="margin-top: 0.5rem;">
                <span class="badge" style="background: rgba(99, 102, 241, 0.1);">
                    Status: {update.get('status', 'N/A')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Classification legend
    with st.expander("ℹ️ Classification Guide"):
        st.markdown("""
        - **Class I**: Dangerous or defective products that could cause serious health problems or death
        - **Class II**: Products that might cause temporary health problems or slight threat of serious nature
        - **Class III**: Products unlikely to cause adverse health reactions but violate FDA regulations
        """)
    
    # Refresh button
    if st.button("🔄 Refresh Updates", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
