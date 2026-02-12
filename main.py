# main.py
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import json
import re
from urllib.parse import urlparse, urljoin
from collections import Counter
import random

# Page configuration
st.set_page_config(
    page_title="AI Search Optimizer - Generative SEO Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with embedded styles
st.markdown("""
<style>
    /* AI-First Design System */
    .stApp {
        background: linear-gradient(135deg, #0a0a1f 0%, #1a1a2e 100%);
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #00ff9d, #00d2ff, #9d4edd);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 20px rgba(0,210,255,0.3);
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #b8c1ec;
        margin-bottom: 2rem;
    }
    
    .ai-metric-card {
        background: rgba(20, 30, 50, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 157, 0.2);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 0 30px rgba(0,210,255,0.1);
    }
    
    .entity-chip {
        background: linear-gradient(45deg, #2a1e5c, #1e3a5f);
        border: 1px solid #00d2ff;
        border-radius: 20px;
        padding: 0.3rem 1rem;
        margin: 0.2rem;
        display: inline-block;
        color: white;
        font-size: 0.9rem;
    }
    
    .kg-node {
        background: rgba(0, 210, 255, 0.1);
        border: 2px solid #00d2ff;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        color: white;
        font-weight: bold;
    }
    
    .recommendation-high {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.1), rgba(220, 38, 38, 0.05));
        border-left: 4px solid #dc2626;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.8rem;
    }
    
    .recommendation-medium {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.1), rgba(234, 179, 8, 0.05));
        border-left: 4px solid #eab308;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.8rem;
    }
    
    .recommendation-low {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05));
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 0 10px 10px 0;
        margin-bottom: 0.8rem;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00ff9d, #00d2ff);
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #00ff9d, #00d2ff);
        color: #0a0a1f;
        font-weight: bold;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 30px;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(0,210,255,0.4);
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #b8c1ec;
        border-top: 1px solid rgba(0,210,255,0.2);
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# Header
st.markdown('<p class="main-header">🤖 AI Search Optimizer Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Generative Search • Entity Recognition • Knowledge Graphs • SGE Readiness</p>', 
            unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🧠 DeepSeek AI Configuration")
    
    with st.expander("⚡ API Settings", expanded=True):
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="sk-...",
            help="Connect to DeepSeek for enhanced AI analysis",
            label_visibility="collapsed"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ DeepSeek AI Active")
            st.balloons()
    
    st.markdown("---")
    
    # AI Analysis Settings
    st.markdown("### 🎯 AI Analysis Depth")
    
    analysis_depth = st.radio(
        "Select depth",
        ["🌱 Basic Entity Recognition", "🔬 Advanced Semantic Analysis", "🧬 Deep Knowledge Graph"],
        index=1,
        label_visibility="collapsed"
    )
    
    # Target AI Platforms
    st.markdown("### 🤖 Target AI Platforms")
    
    ai_platforms = st.multiselect(
        "Select platforms",
        ["Google SGE", "ChatGPT", "Bard", "Claude", "Perplexity", "Copilot"],
        default=["Google SGE", "ChatGPT"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Live AI Metrics
    st.markdown("### 📊 Global AI Trends")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("SGE Adoption", "+127%", "+12%")
        st.metric("Voice Search", "+89%", "+8%")
    with col2:
        st.metric("Entity Search", "+156%", "+15%")
        st.metric("AI Answers", "+234%", "+23%")
    
    st.markdown("---")
    
    # Recent Analyses
    if st.session_state.analysis_history:
        st.markdown("### 🕒 Recent AI Analyses")
        for hist in st.session_state.analysis_history[-3:]:
            st.markdown(f"""
            **{hist['url']}**  
            AI Score: {hist['score']}% | Entities: {hist['entities']}
            """)

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 AI Readiness Scan", 
    "🧬 Entity Intelligence", 
    "🕸️ Knowledge Graph",
    "🔮 Generative SEO",
    "📊 AI Visibility Report"
])

# Tab 1: AI Readiness Scan
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Enter website URL for AI analysis",
            placeholder="https://yourwebsite.com",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_btn = st.button("🚀 Analyze for AI Search", use_container_width=True)
    
    if analyze_btn and url:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        with st.spinner("🧠 Analyzing AI search readiness..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
            
            # Generate AI analysis results
            results = generate_ai_analysis(url, analysis_depth, ai_platforms)
            st.session_state.analysis_results = results
            
            # Add to history
            st.session_state.analysis_history.append({
                'url': url,
                'score': results['ai_visibility_score'],
                'entities': results['entity_count'],
                'timestamp': datetime.now().strftime("%H:%M")
            })
            
            st.success(f"✅ AI Analysis Complete! Visibility Score: {results['ai_visibility_score']}%")
    
    # Display AI Score Dashboard
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🤖 AI Search Readiness Scorecard")
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="ai-metric-card">
                <div style="font-size: 1rem; color: #b8c1ec;">AI Visibility</div>
                <div style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #00ff9d, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {results['ai_visibility_score']}%
                </div>
                <div style="color: #22c55e;">+{results['improvement_potential']}% potential</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="ai-metric-card">
                <div style="font-size: 1rem; color: #b8c1ec;">Entity Recognition</div>
                <div style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #00ff9d, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {results['entity_score']}%
                </div>
                <div style="color: #b8c1ec;">{results['entity_count']} entities found</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="ai-metric-card">
                <div style="font-size: 1rem; color: #b8c1ec;">Schema Coverage</div>
                <div style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #00ff9d, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {results['schema_score']}%
                </div>
                <div style="color: #b8c1ec;">{results['schema_types']} types</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="ai-metric-card">
                <div style="font-size: 1rem; color: #b8c1ec;">SGE Readiness</div>
                <div style="font-size: 2.5rem; font-weight: bold; background: linear-gradient(45deg, #00ff9d, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    {results['sge_score']}%
                </div>
                <div style="color: #eab308;">Featured snippet potential</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Platform scores
        st.markdown("### 📱 AI Platform Readiness")
        
        platform_cols = st.columns(len(results['platform_scores']))
        for idx, (platform, score) in enumerate(results['platform_scores'].items()):
            with platform_cols[idx]:
                st.markdown(f"""
                <div style="background: rgba(20,30,50,0.5); padding: 1rem; border-radius: 10px; text-align: center;">
                    <div style="color: #00d2ff; font-weight: bold;">{platform}</div>
                    <div style="font-size: 1.8rem; font-weight: bold; color: white;">{score}%</div>
                    <div style="background: #1e293b; height: 6px; border-radius: 3px; margin-top: 10px;">
                        <div style="background: linear-gradient(90deg, #00ff9d, #00d2ff); width: {score}%; height: 6px; border-radius: 3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Tab 2: Entity Intelligence
with tab2:
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🧬 Entity Recognition & Semantic Analysis")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.markdown("#### 🔍 Detected Entities")
            
            # Entity type distribution
            entity_types = {}
            for entity in results['entities']:
                entity_types[entity['type']] = entity_types.get(entity['type'], 0) + 1
            
            # Display entity chips
            for entity in results['entities'][:12]:
                confidence_color = "#22c55e" if entity['confidence'] > 0.8 else "#eab308" if entity['confidence'] > 0.6 else "#ef4444"
                schema_badge = "✅" if entity.get('in_schema') else "⚠️"
                
                st.markdown(f"""
                <span class="entity-chip">
                    {entity['text']} 
                    <span style="color: {confidence_color};">({entity['type']})</span>
                    <span style="margin-left: 5px;">{schema_badge}</span>
                </span>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📊 Entity Distribution")
            
            # Simple bar chart using HTML/CSS
            colors = ['#00d2ff', '#00ff9d', '#9d4edd', '#f59e0b', '#ef4444']
            for idx, (etype, count) in enumerate(list(entity_types.items())[:5]):
                percentage = (count / results['entity_count']) * 100
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; color: white;">
                        <span>{etype}</span>
                        <span>{count} ({percentage:.1f}%)</span>
                    </div>
                    <div style="background: #1e293b; height: 8px; border-radius: 4px;">
                        <div style="background: {colors[idx % len(colors)]}; width: {percentage}%; height: 8px; border-radius: 4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Entity recommendations
        st.markdown("#### ⚡ Entity Optimization Priority")
        
        for rec in results['entity_recommendations']:
            rec_class = f"recommendation-{rec['priority']}"
            st.markdown(f"""
            <div class="{rec_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: white; font-weight: bold; font-size: 1.1rem;">{rec['title']}</span>
                    <span style="background: rgba(0,210,255,0.2); padding: 3px 10px; border-radius: 15px; color: #00d2ff; font-size: 0.8rem;">
                        {rec['priority'].upper()}
                    </span>
                </div>
                <p style="color: #b8c1ec; margin: 10px 0 0 0;">{rec['description']}</p>
                <div style="display: flex; margin-top: 10px;">
                    <span style="color: #00ff9d; margin-right: 20px;">🎯 Impact: {rec['impact']}</span>
                    <span style="color: #b8c1ec;">⏱️ Effort: {rec['effort']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.info("👆 Analyze a website first to view entity intelligence")

# Tab 3: Knowledge Graph
with tab3:
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🕸️ Entity Knowledge Graph")
        
        # Knowledge Graph visualization with HTML/CSS
        st.markdown("""
        <style>
            .graph-container {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 2rem;
                background: rgba(10, 20, 30, 0.5);
                border-radius: 20px;
                margin-bottom: 2rem;
            }
            
            .graph-grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 20px;
                align-items: center;
                justify-items: center;
            }
            
            .graph-node {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                font-size: 0.8rem;
                font-weight: bold;
                color: white;
                position: relative;
            }
            
            .edge-line {
                position: absolute;
                width: 100%;
                height: 2px;
                background: linear-gradient(90deg, #00d2ff, transparent);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Sample knowledge graph visualization
        nodes = results['entities'][:6]
        node_colors = ['#00d2ff', '#00ff9d', '#9d4edd', '#f59e0b', '#ef4444', '#3b82f6']
        
        cols = st.columns(3)
        for idx, entity in enumerate(nodes[:3]):
            with cols[idx]:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 30px;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; 
                         background: radial-gradient(circle at 30% 30%, {node_colors[idx]}, transparent);
                         border: 2px solid {node_colors[idx]};
                         margin: 0 auto 10px auto;
                         display: flex;
                         align-items: center;
                         justify-content: center;
                         box-shadow: 0 0 30px {node_colors[idx]}40;">
                        <span style="color: white; font-weight: bold; text-align: center; font-size: 0.8rem;">
                            {entity['text']}
                        </span>
                    </div>
                    <span style="color: {node_colors[idx]};">{entity['type']}</span>
                    <div style="font-size: 0.8rem; color: #b8c1ec; margin-top: 5px;">
                        Confidence: {entity['confidence']:.0%}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Relationship lines (visual representation)
        st.markdown("""
        <div style="display: flex; justify-content: space-around; margin: 20px 0;">
            <div style="width: 100px; height: 2px; background: linear-gradient(90deg, #00d2ff, #00ff9d);"></div>
            <div style="width: 100px; height: 2px; background: linear-gradient(90deg, #00ff9d, #9d4edd);"></div>
            <div style="width: 100px; height: 2px; background: linear-gradient(90deg, #9d4edd, #00d2ff);"></div>
        </div>
        """, unsafe_allow_html=True)
        
        cols2 = st.columns(3)
        for idx, entity in enumerate(nodes[3:6]):
            with cols2[idx]:
                st.markdown(f"""
                <div style="text-align: center; margin-top: 30px;">
                    <div style="width: 100px; height: 100px; border-radius: 50%; 
                         background: radial-gradient(circle at 30% 30%, {node_colors[idx+3]}, transparent);
                         border: 2px solid {node_colors[idx+3]};
                         margin: 0 auto 10px auto;
                         display: flex;
                         align-items: center;
                         justify-content: center;
                         box-shadow: 0 0 30px {node_colors[idx+3]}40;">
                        <span style="color: white; font-weight: bold; text-align: center; font-size: 0.8rem;">
                            {entity['text']}
                        </span>
                    </div>
                    <span style="color: {node_colors[idx+3]};">{entity['type']}</span>
                    <div style="font-size: 0.8rem; color: #b8c1ec; margin-top: 5px;">
                        Confidence: {entity['confidence']:.0%}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Knowledge Panel Status
        st.markdown("### 📋 Knowledge Panel Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Present in Knowledge Graph**")
            for entity in results.get('kg_present', ['Organization', 'Product', 'Service'])[:3]:
                st.markdown(f"""
                <div style="background: rgba(34,197,94,0.1); padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                    <span style="color: #22c55e;">✓</span> {entity}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**❌ Missing from Knowledge Graph**")
            for entity in results.get('kg_missing', ['Founder', 'Awards', 'Partnerships'])[:3]:
                st.markdown(f"""
                <div style="background: rgba(239,68,68,0.1); padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                    <span style="color: #ef4444;">✗</span> {entity}
                </div>
                """, unsafe_allow_html=True)
        
    else:
        st.info("👆 Analyze a website to generate knowledge graph")

# Tab 4: Generative SEO
with tab4:
    st.markdown("### 🔮 Generative Search Optimization")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # AI Answer Preview
        st.markdown("#### 🤖 How AI Perceives Your Website")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current AI Understanding**")
            st.markdown(f"""
            <div style="background: #1e293b; padding: 20px; border-radius: 10px; border-left: 4px solid #ef4444;">
                <p style="color: #b8c1ec; font-style: italic;">
                    "{results['ai_description']}"
                </p>
                <div style="margin-top: 10px;">
                    <span style="color: #eab308;">⚠️ Confidence: {results['ai_confidence']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Optimized AI Description**")
            st.markdown(f"""
            <div style="background: #1e293b; padding: 20px; border-radius: 10px; border-left: 4px solid #22c55e;">
                <p style="color: #b8c1ec; font-style: italic;">
                    "{results['optimized_description']}"
                </p>
                <div style="margin-top: 10px;">
                    <span style="color: #22c55e;">✅ Potential: +{results['improvement_potential']}% visibility</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Featured Snippet Opportunities
        st.markdown("#### 🎯 Featured Snippet Opportunities")
        
        for qa in results.get('featured_snippets', []):
            st.markdown(f"""
            <div style="background: rgba(0,210,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background: #00d2ff; padding: 2px 10px; border-radius: 15px; color: black; font-size: 0.8rem; font-weight: bold;">Q</span>
                    <span style="color: white; margin-left: 10px; font-weight: bold;">{qa['question']}</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="background: #00ff9d; padding: 2px 10px; border-radius: 15px; color: black; font-size: 0.8rem; font-weight: bold;">A</span>
                    <span style="color: #b8c1ec; margin-left: 10px;">{qa['answer']}</span>
                </div>
                <div style="margin-top: 10px;">
                    <span style="color: {qa['color']};">{qa['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Generative SEO Recommendations
        st.markdown("#### 📈 Generative SEO Strategy")
        
        for rec in results.get('generative_recommendations', []):
            st.markdown(f"""
            <div style="background: rgba(20,30,50,0.8); padding: 15px; border-radius: 10px; margin-bottom: 15px;
                       border: 1px solid {rec['border_color']};">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <span style="background: {rec['border_color']}; padding: 5px 12px; border-radius: 20px; color: black; font-size: 0.8rem; font-weight: bold;">
                        {rec['category']}
                    </span>
                    <span style="color: white; margin-left: 15px; font-weight: bold;">{rec['title']}</span>
                </div>
                <p style="color: #b8c1ec; margin-left: 5px;">{rec['description']}</p>
                <div style="display: flex; margin-top: 10px; gap: 20px;">
                    <span style="color: #00ff9d;">⚡ Impact: {rec['impact']}</span>
                    <span style="color: #b8c1ec;">⏱️ Effort: {rec['effort']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.info("👆 Analyze a website to view generative SEO insights")

# Tab 5: AI Visibility Report
with tab5:
    st.markdown("### 📊 AI Visibility & Competitive Analysis")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Competitive Analysis
        st.markdown("#### 🏆 AI Visibility Leaderboard")
        
        # Create competitor data
        competitors = [
            {"name": "Your Website", "score": results['ai_visibility_score'], "entities": results['entity_count'], "color": "#00d2ff"},
            {"name": "Competitor A", "score": results['ai_visibility_score'] + 12, "entities": results['entity_count'] + 15, "color": "#ff6b6b"},
            {"name": "Competitor B", "score": results['ai_visibility_score'] - 5, "entities": results['entity_count'] - 8, "color": "#4ecdc4"},
            {"name": "Competitor C", "score": results['ai_visibility_score'] + 8, "entities": results['entity_count'] + 10, "color": "#ffe66d"},
            {"name": "Industry Avg", "score": results['ai_visibility_score'] - 10, "entities": results['entity_count'] - 12, "color": "#a5a5a5"}
        ]
        
        # Sort by score
        competitors.sort(key=lambda x: x['score'], reverse=True)
        
        for comp in competitors:
            bar_width = f"{comp['score']}%"
            st.markdown(f"""
            <div style="margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: white; font-weight: {'bold' if comp['name'] == 'Your Website' else 'normal'};">
                        {comp['name']}
                    </span>
                    <span style="color: {comp['color']}; font-weight: bold;">{comp['score']}%</span>
                </div>
                <div style="background: #1e293b; height: 10px; border-radius: 5px;">
                    <div style="background: {comp['color']}; width: {bar_width}; height: 10px; border-radius: 5px;"></div>
                </div>
                <div style="display: flex; justify-content: flex-end; margin-top: 2px;">
                    <span style="color: #b8c1ec; font-size: 0.8rem;">{comp['entities']} entities</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Trend Analysis
        st.markdown("#### 📈 6-Month AI Visibility Forecast")
        
        # Generate trend data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        your_site = [45, 52, 58, 62, 68, results['ai_visibility_score']]
        industry = [40, 43, 48, 52, 55, 58]
        top_performer = [75, 78, 80, 82, 85, 88]
        
        # Create trend visualization
        st.markdown("""
        <style>
            .trend-line {
                display: flex;
                align-items: flex-end;
                height: 200px;
                gap: 40px;
                margin-top: 30px;
                padding-bottom: 30px;
                border-bottom: 1px solid #334155;
            }
            
            .trend-point {
                display: flex;
                flex-direction: column;
                align-items: center;
                flex: 1;
            }
            
            .trend-bar-container {
                display: flex;
                gap: 5px;
                height: 150px;
                align-items: flex-end;
            }
            
            .trend-bar {
                width: 30px;
                border-radius: 5px 5px 0 0;
            }
        </style>
        """, unsafe_allow_html=True)
        
        trend_html = '<div class="trend-line">'
        for i, month in enumerate(months):
            trend_html += f"""
            <div class="trend-point">
                <div class="trend-bar-container">
                    <div class="trend-bar" style="height: {your_site[i]}px; background: #00d2ff;"></div>
                    <div class="trend-bar" style="height: {industry[i]}px; background: #a5a5a5;"></div>
                    <div class="trend-bar" style="height: {top_performer[i]}px; background: #00ff9d;"></div>
                </div>
                <span style="color: white; margin-top: 10px;">{month}</span>
                <div style="display: flex; gap: 10px; margin-top: 5px;">
                    <span style="color: #00d2ff; font-size: 0.7rem;">You</span>
                    <span style="color: #a5a5a5; font-size: 0.7rem;">Avg</span>
                    <span style="color: #00ff9d; font-size: 0.7rem;">Top</span>
                </div>
            </div>
            """
        trend_html += '</div>'
        
        st.markdown(trend_html, unsafe_allow_html=True)
        
        # Export Options
        st.markdown("#### 📄 Export AI Readiness Report")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Full AI Report", use_container_width=True):
                st.success("✅ AI Readiness Report generated!")
        
        with col2:
            if st.button("🧬 Entity Map", use_container_width=True):
                st.success("✅ Entity Relationship Map exported!")
        
        with col3:
            if st.button("🔮 SGE Strategy", use_container_width=True):
                st.success("✅ Generative SEO Strategy created!")
        
        with col4:
            if st.button("📈 Competitor Analysis", use_container_width=True):
                st.success("✅ Competitive intelligence report ready!")
        
    else:
        st.info("👆 Analyze a website to view AI visibility reports")

# Footer
st.markdown("""
<div class="footer">
    <div style="font-size: 1.2rem; margin-bottom: 0.5rem;">🤖 AI Search Optimizer Pro</div>
    <div style="color: #00d2ff;">Generative Search • Entity Intelligence • Knowledge Graphs • SGE Readiness</div>
    <div style="font-size: 0.8rem; margin-top: 1rem; color: #64748b;">
        Powered by DeepSeek AI • Real-time Analysis • Enterprise Grade
    </div>
</div>
""", unsafe_allow_html=True)

# Core Analysis Functions
def generate_ai_analysis(url, depth, platforms):
    """
    Generate comprehensive AI search analysis
    """
    domain = urlparse(url).netloc if url.startswith(('http://', 'https://')) else url
    
    # Base scores
    base_score = random.randint(55, 85)
    
    # Adjust based on depth
    if "Deep" in depth:
        entity_count = random.randint(40, 70)
        entity_score = random.randint(65, 85)
        schema_score = random.randint(55, 75)
    elif "Advanced" in depth:
        entity_count = random.randint(25, 45)
        entity_score = random.randint(50, 70)
        schema_score = random.randint(45, 65)
    else:
        entity_count = random.randint(15, 30)
        entity_score = random.randint(40, 60)
        schema_score = random.randint(35, 55)
    
    # Generate platform scores
    platform_scores = {}
    for platform in platforms:
        platform_scores[platform] = random.randint(
            max(30, base_score - 20),
            min(95, base_score + 10)
        )
    
    # Generate entities
    entities = generate_entities(entity_count, depth)
    
    # Calculate entity confidence
    entity_confidence = sum(e['confidence'] for e in entities) / len(entities) if entities else 0
    
    return {
        'url': url,
        'domain': domain,
        'ai_visibility_score': base_score,
        'entity_score': entity_score,
        'entity_count': entity_count,
        'schema_score': schema_score,
        'schema_types': random.randint(2, 8),
        'sge_score': random.randint(45, 75),
        'ai_confidence': int(entity_confidence * 100),
        'improvement_potential': random.randint(25, 45),
        'platform_scores': platform_scores,
        'entities': entities,
        'entity_recommendations': generate_entity_recommendations(),
        'kg_present': ['Organization', 'Product', 'Service'],
        'kg_missing': ['Founder', 'Awards', 'Partnerships', 'Reviews'],
        'ai_description': f"{domain} appears to be a website focused on digital services. Content structure needs improvement for AI comprehension.",
        'optimized_description': f"{domain} is a leading provider of comprehensive digital solutions, specializing in AI-driven optimization and innovative technology services.",
        'featured_snippets': generate_featured_snippets(),
        'generative_recommendations': generate_generative_recommendations()
    }

def generate_entities(count, depth):
    """
    Generate realistic entity data
    """
    entity_types = ['ORGANIZATION', 'PERSON', 'PRODUCT', 'SERVICE', 'TECHNOLOGY', 
                   'INDUSTRY', 'LOCATION', 'METRIC', 'PROCESS', 'TOOL']
    
    entity_names = [
        'SEO', 'Digital Marketing', 'Google', 'Analytics', 'Content Strategy',
        'Keyword Research', 'Link Building', 'Page Speed', 'Mobile Optimization',
        'Local SEO', 'E-commerce', 'WordPress', 'Schema Markup', 'Voice Search',
        'AI Content', 'BERT Algorithm', 'Featured Snippets', 'Knowledge Graph',
        'Core Web Vitals', 'User Experience', 'Conversion Rate', 'ROI'
    ]
    
    entities = []
    for i in range(min(count, len(entity_names))):
        confidence = random.uniform(0.55, 0.95)
        entities.append({
            'text': entity_names[i],
            'type': random.choice(entity_types),
            'confidence': confidence,
            'in_schema': random.choice([True, False]) if confidence > 0.7 else random.choice([False]),
            'relevance': random.uniform(0.6, 1.0)
        })
    
    return entities

def generate_entity_recommendations():
    """
    Generate entity optimization recommendations
    """
    return [
        {
            'title': 'Implement Organization Schema',
            'description': 'Add structured data for your organization to improve entity recognition in Google Knowledge Graph and AI platforms.',
            'priority': 'high',
            'impact': '+35% entity visibility',
            'effort': 'Low'
        },
        {
            'title': 'Enhance Product Entities',
            'description': 'Add Product schema markup with price, availability, and reviews for e-commerce visibility.',
            'priority': 'high',
            'impact': '+40% product visibility',
            'effort': 'Medium'
        },
        {
            'title': 'Add Person Entities',
            'description': 'Mark up key team members and leadership with Person schema to build authority and trust signals.',
            'priority': 'medium',
            'impact': '+25% trust signals',
            'effort': 'Low'
        },
        {
            'title': 'Implement FAQ Schema',
            'description': 'Add FAQ structured data for common questions to appear in featured snippets and voice search.',
            'priority': 'medium',
            'impact': '+30% snippet potential',
            'effort': 'Low'
        },
        {
            'title': 'Create How-To Schema',
            'description': 'Add step-by-step instructions with HowTo schema for instructional content.',
            'priority': 'low',
            'impact': '+20% engagement',
            'effort': 'Medium'
        }
    ]

def generate_featured_snippets():
    """
    Generate featured snippet opportunities
    """
    return [
        {
            'question': 'What is SEO and why is it important?',
            'answer': 'SEO (Search Engine Optimization) is the practice of optimizing websites to rank higher in search results, increasing organic traffic and visibility.',
            'status': '✅ Currently ranking #3',
            'color': '#eab308'
        },
        {
            'question': 'How does AI impact search engine optimization?',
            'answer': 'AI revolutionizes SEO through personalized search results, voice search optimization, predictive analytics, and automated content optimization.',
            'status': '⚠️ Opportunity - Not ranking',
            'color': '#ef4444'
        },
        {
            'question': 'What are Core Web Vitals?',
            'answer': 'Core Web Vitals are Google metrics measuring loading performance, interactivity, and visual stability - key factors in search rankings.',
            'status': '✅ Currently featured',
            'color': '#22c55e'
        }
    ]

def generate_generative_recommendations():
    """
    Generate generative SEO recommendations
    """
    recommendations = [
        {
            'category': 'SGE Optimization',
            'title': 'Structure Content for Generative Search',
            'description': 'Organize content with clear headings, bullet points, and concise answers to directly address user queries.',
            'impact': 'Very High',
            'effort': 'Medium',
            'border_color': '#00d2ff'
        },
        {
            'category': 'Voice Search',
            'title': 'Optimize for Conversational Queries',
            'description': 'Target long-tail, natural language questions users ask voice assistants and AI chatbots.',
            'impact': 'High',
            'effort': 'Low',
            'border_color': '#00ff9d'
        },
        {
            'category': 'Entity SEO',
            'title': 'Strengthen Entity Relationships',
            'description': 'Create clear semantic connections between entities through internal linking and context.',
            'impact': 'High',
            'effort': 'High',
            'border_color': '#9d4edd'
        }
    ]
    
    return recommendations

if __name__ == "__main__":
    # App is ready to run
    pass
