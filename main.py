# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from bs4 import BeautifulSoup
import validators
import time
from datetime import datetime
import json
import re
import hashlib
from urllib.parse import urlparse, urljoin
import streamlit.components.v1 as components
import altair as alt
from PIL import Image
import io
import spacy
from typing import Dict, List, Any
import networkx as nx
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="WebAnalyzer Pro - AI Search & Generative SEO Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main styling */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 0 10px rgba(0,255,255,0.3);
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #a0a0c0;
        margin-bottom: 2rem;
    }
    
    .ai-score-card {
        background: rgba(10, 25, 47, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 255, 0.2);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 0 20px rgba(0,255,255,0.1);
    }
    
    .entity-card {
        background: rgba(20, 30, 50, 0.8);
        border: 1px solid #00d2ff;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    
    .recommendation-card {
        background: rgba(30, 40, 60, 0.9);
        padding: 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #00d2ff;
        color: white;
    }
    
    .knowledge-graph {
        background: rgba(10, 25, 47, 0.9);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(0, 210, 255, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        transition: all 0.3s ease;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(45deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'entity_cache' not in st.session_state:
    st.session_state.entity_cache = {}

# Header with AI focus
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    st.markdown('<p class="main-header">🤖 WebAnalyzer Pro: AI Search Suite</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Optimize for Generative Search • Entity Recognition • AI Visibility • Knowledge Graphs</p>', 
                unsafe_allow_html=True)

# Sidebar - AI Configuration
with st.sidebar:
    st.markdown("### 🧠 DeepSeek AI Integration")
    
    with st.expander("AI Configuration", expanded=True):
        api_key = st.text_input(
            "DeepSeek API Key",
            type="password",
            placeholder="sk-...",
            help="Enable AI-powered entity extraction and generative search optimization"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ AI Enhancement Active")
    
    st.markdown("---")
    
    # AI Search Settings
    st.markdown("### 🎯 AI Search Optimization")
    
    optimization_goals = st.multiselect(
        "AI Visibility Goals",
        ["Generative Search", "Voice Search", "AI Assistants", "Knowledge Panels", "Featured Snippets"],
        default=["Generative Search", "AI Assistants"],
        help="Select AI platforms to optimize for"
    )
    
    entity_depth = st.select_slider(
        "Entity Recognition Depth",
        options=["Basic", "Advanced", "Deep Learning"],
        value="Advanced",
        help="Deep analysis includes semantic relationships and entity graphs"
    )
    
    st.markdown("---")
    
    # AI Metrics
    st.markdown("### 📊 AI Visibility Score")
    
    # Mock AI metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("AI Readiness", "72%", "+8%")
        st.metric("Entity Coverage", "45%", "+12%")
    with col2:
        st.metric("Schema Score", "68%", "+5%")
        st.metric("NLP Friendliness", "81%", "+15%")
    
    st.markdown("---")
    
    # Recent AI Analyses
    st.markdown("### 🕒 AI Search History")
    ai_analyses = [
        {"url": "example.com", "score": 92, "entities": 24},
        {"url": "shop.com", "score": 78, "entities": 18},
        {"url": "blog.org", "score": 88, "entities": 31}
    ]
    
    for analysis in ai_analyses:
        st.markdown(f"""
        - **{analysis['url']}**  
          AI Score: {analysis['score']}% | Entities: {analysis['entities']}
        """)

# Main tabs with AI focus
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🎯 AI Search Analysis", "🧬 Entity Recognition", "📊 Knowledge Graph", 
     "🔮 Generative SEO", "📈 AI Visibility Report"]
)

# Tab 1: AI Search Analysis
with tab1:
    st.markdown("### 🔍 AI-Powered Website Analysis")
    
    # Input section with AI focus
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input(
            "Enter website URL for AI analysis",
            placeholder="https://example.com",
            label_visibility="collapsed"
        )
    with col2:
        analyze_button = st.button("🚀 Analyze for AI Search", type="primary", use_container_width=True)
    
    # AI Analysis Dashboard
    if analyze_button:
        if not url or not validators.url(url):
            st.error("❌ Please enter a valid URL")
        else:
            with st.spinner("🧠 Analyzing AI search readiness..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.02)
                    progress_bar.progress(i + 1)
                
                # Perform AI-focused analysis
                results = analyze_ai_readiness(url, optimization_goals, entity_depth)
                st.session_state.analysis_results = results
                
                # Display AI Score Dashboard
                st.markdown("### 🤖 AI Search Readiness Score")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="ai-score-card">
                        <h3 style='color: #00d2ff; margin:0;'>AI Visibility</h3>
                        <p class="metric-value">{results['ai_visibility_score']}%</p>
                        <p style='color: #a0a0c0;'>Generative Search Ready</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="ai-score-card">
                        <h3 style='color: #00d2ff; margin:0;'>Entity Density</h3>
                        <p class="metric-value">{results['entity_score']}%</p>
                        <p style='color: #a0a0c0;'>{results['entity_count']} Entities Found</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="ai-score-card">
                        <h3 style='color: #00d2ff; margin:0;'>Schema Coverage</h3>
                        <p class="metric-value">{results['schema_score']}%</p>
                        <p style='color: #a0a0c0;'>{results['schema_types']} Types</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="ai-score-card">
                        <h3 style='color: #00d2ff; margin:0;'>NLP Readiness</h3>
                        <p class="metric-value">{results['nlp_score']}%</p>
                        <p style='color: #a0a0c0;'>Semantic Clarity</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Generative Search Optimization
                if st.session_state.api_key:
                    with st.spinner("🤖 Generating AI search recommendations..."):
                        enhanced_results = enhance_generative_search(results, st.session_state.api_key)
                        st.session_state.analysis_results = enhanced_results
                        st.success("✅ Generative search optimization complete!")

    # Display AI recommendations if available
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🎯 Generative Search Optimization")
        
        # AI Answer Optimization
        st.markdown("#### 📝 AI Answer Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Featured Snippet Potential**")
            snippet_score = results.get('featured_snippet_score', 65)
            st.progress(snippet_score/100)
            st.caption(f"{snippet_score}% - {'High' if snippet_score > 70 else 'Medium' if snippet_score > 40 else 'Low'} potential")
            
            # Question optimization
            st.markdown("**Common Questions Answered**")
            for question in results.get('answered_questions', []):
                st.markdown(f"✅ {question}")
        
        with col2:
            st.markdown("**Voice Search Optimization**")
            voice_score = results.get('voice_search_score', 58)
            st.progress(voice_score/100)
            st.caption(f"{voice_score}% - Natural language processing")
            
            # Conversational keywords
            st.markdown("**Conversational Keywords**")
            for kw in results.get('conversational_keywords', [])[:5]:
                st.markdown(f"🎤 {kw}")

# Tab 2: Entity Recognition
with tab2:
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🧬 Entity Recognition & Semantic Analysis")
        
        # Entity Overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📊 Entity Distribution")
            
            if 'entities' in results:
                entity_types = [e['type'] for e in results['entities']]
                entity_counts = Counter(entity_types)
                
                entity_df = pd.DataFrame({
                    'Entity Type': list(entity_counts.keys()),
                    'Count': list(entity_counts.values())
                })
                
                fig = px.pie(entity_df, values='Count', names='Entity Type',
                           title='Entity Type Distribution',
                           color_discrete_sequence=px.colors.sequential.Plasma)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏷️ Top Entities")
            
            for entity in results.get('entities', [])[:10]:
                confidence = entity.get('confidence', 0.85)
                st.markdown(f"""
                <div class="entity-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #00d2ff; font-weight: bold;">{entity['text']}</span>
                        <span style="color: #a0a0c0;">{entity['type']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span style="color: #888;">Confidence: {confidence:.1%}</span>
                        <span style="color: {'#28a745' if entity.get('in_schema') else '#ffc107'};">
                            {'✅ Schema' if entity.get('in_schema') else '⚠️ Missing Schema'}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("#### 🔍 Entity Relationships")
            
            # Semantic relationship strength
            st.markdown("**Semantic Connectivity**")
            semantic_score = results.get('semantic_connectivity', 62)
            st.progress(semantic_score/100)
            st.caption(f"{semantic_score}% - Entity relationships")
            
            # Missing entity types
            st.markdown("**Missing Entity Types**")
            missing_entities = [
                "Organization Schema",
                "Product Schema",
                "Event Schema",
                "Review Schema"
            ]
            
            for entity in missing_entities[:results.get('missing_entities_count', 3)]:
                st.markdown(f"❌ {entity}")
        
        # Entity SEO Recommendations
        st.markdown("#### ⚡ Entity Optimization Recommendations")
        
        for rec in results.get('entity_recommendations', []):
            priority_color = {
                'high': '#dc3545',
                'medium': '#ffc107',
                'low': '#28a745'
            }.get(rec['priority'], '#00d2ff')
            
            st.markdown(f"""
            <div class="recommendation-card" style="border-left-color: {priority_color};">
                <h4 style='color: {priority_color}; margin: 0;'>{rec['title']}</h4>
                <p style='margin: 0.5rem 0 0 0; color: #ccc;'>{rec['description']}</p>
                <span style='font-size: 0.8rem; color: #00d2ff;'>
                    🎯 Impact: {rec.get('impact', 'High')} | Priority: {rec['priority']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.info("👆 Analyze a website to view entity recognition insights")

# Tab 3: Knowledge Graph
with tab3:
    if st.session_state.analysis_results:
        st.markdown("### 🔮 Knowledge Graph Visualization")
        
        results = st.session_state.analysis_results
        
        # Knowledge Graph Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Knowledge Panel Score", f"{results.get('kg_score', 58)}%", "+12%")
        with col2:
            st.metric("Entity Relationships", results.get('entity_relationships', 24), "+5")
        with col3:
            st.metric("WikiData Matches", results.get('wikidata_matches', 8), "+3")
        with col4:
            st.metric("Google KG Matches", results.get('google_kg_matches', 12), "+4")
        
        # Knowledge Graph Visualization
        st.markdown("#### 🕸️ Entity Knowledge Graph")
        
        # Create sample knowledge graph
        if 'entities' in results:
            # Create graph
            G = nx.Graph()
            
            # Add nodes
            for entity in results['entities'][:8]:
                G.add_node(entity['text'], type=entity['type'])
            
            # Add edges (relationships)
            relationships = results.get('entity_relationships_list', [])
            for rel in relationships[:12]:
                G.add_edge(rel['source'], rel['target'], weight=rel.get('weight', 0.5))
            
            # Convert to plotly
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            edge_trace = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_trace.append(
                    go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(width=1, color='rgba(0,210,255,0.3)'),
                        hoverinfo='none'
                    )
                )
            
            node_trace = go.Scatter(
                x=[], y=[], mode='markers+text',
                text=[], textposition="top center",
                marker=dict(
                    size=30,
                    color='rgba(0,210,255,0.8)',
                    line=dict(color='white', width=1)
                ),
                hoverinfo='text'
            )
            
            for node in G.nodes():
                x, y = pos[node]
                node_trace['x'] += tuple([x])
                node_trace['y'] += tuple([y])
                node_trace['text'] += tuple([node])
            
            fig = go.Figure(data=edge_trace + [node_trace],
                          layout=go.Layout(
                              title='Entity Knowledge Graph',
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20, l=5, r=5, t=40),
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              height=500,
                              paper_bgcolor='rgba(10,25,47,0.9)',
                              plot_bgcolor='rgba(10,25,47,0.9)'
                          ))
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Knowledge Panel Optimization
        st.markdown("#### 📋 Knowledge Panel Optimization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Present in Knowledge Graph**")
            for entity in results.get('kg_present', [])[:5]:
                st.markdown(f"- {entity}")
        
        with col2:
            st.markdown("**❌ Missing from Knowledge Graph**")
            for entity in results.get('kg_missing', [])[:5]:
                st.markdown(f"- {entity}")
        
    else:
        st.info("👆 Analyze a website to generate knowledge graph")

# Tab 4: Generative SEO
with tab4:
    st.markdown("### 🔮 Generative Search Optimization")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # AI Answer Generation
        st.markdown("#### 🤖 How AI Will Describe Your Website")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current AI Understanding**")
            st.info(results.get('ai_description', "No AI description available"))
            
            st.markdown("**AI Confidence**")
            st.progress(results.get('ai_confidence', 65)/100)
            st.caption(f"{results.get('ai_confidence', 65)}% confidence in understanding")
        
        with col2:
            st.markdown("**Optimized AI Description**")
            st.success(results.get('optimized_description', "Add schema markup to improve AI understanding"))
            
            st.markdown("**Improvement Potential**")
            st.progress(results.get('improvement_potential', 35)/100)
            st.caption(f"+{results.get('improvement_potential', 35)}% with recommendations")
        
        # Generative Search Features
        st.markdown("#### 🎯 Generative Search Features")
        
        features = results.get('generative_features', {})
        
        feature_cols = st.columns(3)
        
        with feature_cols[0]:
            st.markdown("**Direct Answers**")
            st.metric("Q&A Pairs", features.get('qa_pairs', 0), "+3")
            st.metric("FAQ Schema", "✅" if features.get('faq_schema') else "❌")
        
        with feature_cols[1]:
            st.markdown("**Rich Results**")
            st.metric("How-to Schema", features.get('howto_count', 0), "+2")
            st.metric("Recipe Schema", features.get('recipe_count', 0))
        
        with feature_cols[2]:
            st.markdown("**AI Readiness**")
            st.metric("NLP Score", f"{features.get('nlp_score', 62)}%", "+8%")
            st.metric("Semantic Score", f"{features.get('semantic_score', 55)}%", "+12%")
        
        # Generative Search Recommendations
        st.markdown("#### 📈 Generative SEO Recommendations")
        
        for rec in results.get('generative_recommendations', []):
            st.markdown(f"""
            <div class="recommendation-card">
                <div style="display: flex; align-items: center;">
                    <span style="background: #00d2ff; padding: 5px 10px; border-radius: 5px; margin-right: 10px; font-size: 0.8rem;">
                        {rec.get('category', 'AI')}
                    </span>
                    <h4 style='color: white; margin: 0;'>{rec['title']}</h4>
                </div>
                <p style='margin: 0.5rem 0 0 0; color: #ccc;'>{rec['description']}</p>
                <div style="display: flex; margin-top: 10px;">
                    <span style="color: #00d2ff; margin-right: 20px;">📊 Impact: {rec.get('impact', 'High')}</span>
                    <span style="color: #a0a0c0;">⏱️ Effort: {rec.get('effort', 'Medium')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.info("👆 Analyze a website to view generative SEO insights")

# Tab 5: AI Visibility Report
with tab5:
    st.markdown("### 📈 AI Visibility & Competitive Analysis")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # AI Visibility Dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 AI Platform Readiness")
            
            platforms = {
                "Google SGE": results.get('sge_score', 58),
                "ChatGPT": results.get('chatgpt_score', 62),
                "Bard": results.get('bard_score', 55),
                "Claude": results.get('claude_score', 48),
                "Perplexity": results.get('perplexity_score', 52)
            }
            
            platform_df = pd.DataFrame({
                'Platform': list(platforms.keys()),
                'Score': list(platforms.values())
            })
            
            fig = px.bar(platform_df, x='Platform', y='Score',
                        title='AI Platform Readiness Scores',
                        color='Score',
                        color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏆 Competitor AI Visibility")
            
            competitors = results.get('competitor_ai_scores', [
                {"name": "competitor1.com", "ai_score": 82, "entities": 45},
                {"name": "competitor2.com", "ai_score": 74, "entities": 38},
                {"name": "competitor3.com", "ai_score": 68, "entities": 32},
                {"name": "Your Site", "ai_score": results['ai_visibility_score'], "entities": results['entity_count']}
            ])
            
            comp_df = pd.DataFrame(competitors)
            comp_df = comp_df.sort_values('ai_score', ascending=True)
            
            fig = px.bar(comp_df, y='name', x='ai_score',
                        title='AI Visibility Competitive Analysis',
                        orientation='h',
                        color='ai_score',
                        color_continuous_scale='plasma')
            st.plotly_chart(fig, use_container_width=True)
        
        # AI Search Trends
        st.markdown("#### 📊 AI Search Trend Analysis")
        
        trend_data = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Your Site': [45, 52, 58, 62, 68, results['ai_visibility_score']],
            'Industry Avg': [40, 43, 48, 52, 55, 58],
            'Top Performer': [75, 78, 80, 82, 85, 88]
        })
        
        fig = px.line(trend_data, x='Month', y=['Your Site', 'Industry Avg', 'Top Performer'],
                     title='AI Visibility Trends',
                     markers=True)
        fig.update_layout(hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # Export AI Report
        st.markdown("#### 📄 Export AI Visibility Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 AI Readiness Report", use_container_width=True):
                st.success("AI Readiness Report generated!")
        
        with col2:
            if st.button("🔮 Generative SEO Plan", use_container_width=True):
                st.success("Generative SEO Strategy exported!")
        
        with col3:
            if st.button("🧬 Entity Map", use_container_width=True):
                st.success("Entity Relationship Map exported!")
        
    else:
        st.info("👆 Analyze a website to view AI visibility reports")

# AI Analysis Functions
def analyze_ai_readiness(url: str, optimization_goals: List[str], entity_depth: str) -> Dict[str, Any]:
    """
    Comprehensive AI search readiness analysis
    """
    domain = urlparse(url).netloc
    
    # Mock AI-focused analysis results
    results = {
        'url': url,
        'domain': domain,
        'ai_visibility_score': np.random.randint(55, 85),
        'entity_score': np.random.randint(40, 80),
        'entity_count': np.random.randint(15, 50),
        'schema_score': np.random.randint(35, 75),
        'schema_types': np.random.randint(2, 8),
        'nlp_score': np.random.randint(50, 90),
        'featured_snippet_score': np.random.randint(40, 80),
        'voice_search_score': np.random.randint(45, 75),
        'semantic_connectivity': np.random.randint(45, 85),
        'kg_score': np.random.randint(40, 75),
        'entity_relationships': np.random.randint(15, 40),
        'wikidata_matches': np.random.randint(3, 15),
        'google_kg_matches': np.random.randint(5, 20),
        'ai_confidence': np.random.randint(55, 80),
        'improvement_potential': np.random.randint(25, 45),
        
        # AI Platform Scores
        'sge_score': np.random.randint(45, 75),
        'chatgpt_score': np.random.randint(50, 80),
        'bard_score': np.random.randint(40, 70),
        'claude_score': np.random.randint(35, 65),
        'perplexity_score': np.random.randint(40, 70),
        
        # Entities with enhanced metadata
        'entities': generate_mock_entities(entity_depth),
        
        # Entity relationships for knowledge graph
        'entity_relationships_list': generate_entity_relationships(),
        
        # Answered questions for featured snippets
        'answered_questions': [
            "What is your main product/service?",
            "How does your solution work?",
            "What makes you different?",
            "Where do you operate?",
            "Who is your target audience?"
        ],
        
        # Conversational keywords for voice search
        'conversational_keywords': [
            "how to improve website SEO",
            "best local SEO services",
            "why choose our solution",
            "where to find professional SEO",
            "when to update website content"
        ],
        
        # Knowledge Graph presence
        'kg_present': ['Company', 'Product', 'Service'],
        'kg_missing': ['Founder', 'Awards', 'Partnerships'],
        
        # AI description
        'ai_description': f"A website providing {domain} services with focus on SEO and digital marketing. Content quality is moderate with some structured data.",
        'optimized_description': f"{domain} is a leading provider of comprehensive SEO and digital marketing solutions, specializing in AI-driven optimization and generative search readiness.",
        
        # Generative features
        'generative_features': {
            'qa_pairs': np.random.randint(0, 8),
            'faq_schema': np.random.choice([True, False]),
            'howto_count': np.random.randint(0, 5),
            'recipe_count': np.random.randint(0, 3),
            'nlp_score': np.random.randint(45, 85),
            'semantic_score': np.random.randint(40, 80)
        },
        
        # Entity optimization recommendations
        'entity_recommendations': [
            {
                'title': 'Implement Organization Schema',
                'description': 'Add structured data for your organization to improve entity recognition',
                'priority': 'high',
                'impact': '+35% entity visibility'
            },
            {
                'title': 'Enhance Product Entities',
                'description': 'Add Product schema markup for main offerings',
                'priority': 'high',
                'impact': '+40% product visibility in AI search'
            },
            {
                'title': 'Add Person Entities',
                'description': 'Mark up key team members and leadership',
                'priority': 'medium',
                'impact': '+25% trust signals'
            },
            {
                'title': 'Implement FAQ Schema',
                'description': 'Add FAQ structured data for common questions',
                'priority': 'medium',
                'impact': '+30% featured snippet potential'
            }
        ],
        
        # Generative SEO recommendations
        'generative_recommendations': [
            {
                'category': 'Generative Search',
                'title': 'Optimize for Conversational Queries',
                'description': 'Structure content to answer natural language questions directly',
                'impact': 'High',
                'effort': 'Medium'
            },
            {
                'category': 'AI Assistant',
                'title': 'Enhance Entity Relationships',
                'description': 'Create clear semantic relationships between entities',
                'impact': 'High',
                'effort': 'High'
            },
            {
                'category': 'Voice Search',
                'title': 'Add Long-tail Question Content',
                'description': 'Target specific questions users ask voice assistants',
                'impact': 'Medium',
                'effort': 'Low'
            }
        ],
        
        # Missing entities count
        'missing_entities_count': np.random.randint(2, 6)
    }
    
    # Add depth-specific enhancements
    if entity_depth == "Deep Learning":
        results['entity_count'] = np.random.randint(40, 80)
        results['entity_relationships'] = np.random.randint(30, 60)
        results['semantic_connectivity'] = np.random.randint(60, 90)
        results['wikidata_matches'] = np.random.randint(10, 25)
        results['google_kg_matches'] = np.random.randint(15, 30)
    
    return results

def generate_mock_entities(depth: str) -> List[Dict[str, Any]]:
    """
    Generate mock entities for demonstration
    """
    base_entities = [
        {'text': 'SEO Services', 'type': 'SERVICE', 'confidence': 0.95, 'in_schema': False},
        {'text': 'Digital Marketing', 'type': 'INDUSTRY', 'confidence': 0.92, 'in_schema': False},
        {'text': 'Google', 'type': 'ORGANIZATION', 'confidence': 0.88, 'in_schema': False},
        {'text': 'Website Traffic', 'type': 'METRIC', 'confidence': 0.85, 'in_schema': False},
        {'text': 'Keyword Research', 'type': 'PROCESS', 'confidence': 0.82, 'in_schema': False},
        {'text': 'Content Strategy', 'type': 'PROCESS', 'confidence': 0.80, 'in_schema': False},
        {'text': 'Link Building', 'type': 'TECHNIQUE', 'confidence': 0.78, 'in_schema': False},
        {'text': 'Analytics', 'type': 'TOOL', 'confidence': 0.75, 'in_schema': False},
        {'text': 'Conversion Rate', 'type': 'METRIC', 'confidence': 0.72, 'in_schema': False},
        {'text': 'Mobile Optimization', 'type': 'TECHNIQUE', 'confidence': 0.70, 'in_schema': False},
    ]
    
    if depth == "Advanced":
        base_entities.extend([
            {'text': 'Local SEO', 'type': 'SERVICE', 'confidence': 0.68, 'in_schema': True},
            {'text': 'E-commerce', 'type': 'INDUSTRY', 'confidence': 0.65, 'in_schema': False},
            {'text': 'WordPress', 'type': 'PLATFORM', 'confidence': 0.62, 'in_schema': False},
            {'text': 'Page Speed', 'type': 'METRIC', 'confidence': 0.60, 'in_schema': False},
        ])
    
    if depth == "Deep Learning":
        base_entities.extend([
            {'text': 'Schema Markup', 'type': 'TECHNIQUE', 'confidence': 0.58, 'in_schema': True},
            {'text': 'Voice Search', 'type': 'TECHNOLOGY', 'confidence': 0.55, 'in_schema': False},
            {'text': 'AI Content', 'type': 'SERVICE', 'confidence': 0.52, 'in_schema': False},
            {'text': 'BERT Algorithm', 'type': 'TECHNOLOGY', 'confidence': 0.50, 'in_schema': False},
            {'text': 'Featured Snippets', 'type': 'FEATURE', 'confidence': 0.48, 'in_schema': True},
            {'text': 'Knowledge Graph', 'type': 'FEATURE', 'confidence': 0.45, 'in_schema': False},
        ])
    
    return base_entities

def generate_entity_relationships() -> List[Dict[str, str]]:
    """
    Generate mock entity relationships
    """
    relationships = [
        {'source': 'SEO Services', 'target': 'Keyword Research', 'weight': 0.9},
        {'source': 'SEO Services', 'target': 'Content Strategy', 'weight': 0.8},
        {'source': 'SEO Services', 'target': 'Link Building', 'weight': 0.7},
        {'source': 'Digital Marketing', 'target': 'SEO Services', 'weight': 0.9},
        {'source': 'Digital Marketing', 'target': 'Content Strategy', 'weight': 0.6},
        {'source': 'Google', 'target': 'Analytics', 'weight': 0.8},
        {'source': 'Google', 'target': 'Page Speed', 'weight': 0.7},
        {'source': 'Website Traffic', 'target': 'Conversion Rate', 'weight': 0.8},
        {'source': 'Mobile Optimization', 'target': 'Page Speed', 'weight': 0.7},
        {'source': 'E-commerce', 'target': 'Local SEO', 'weight': 0.5},
        {'source': 'WordPress', 'target': 'SEO Services', 'weight': 0.6},
        {'source': 'Schema Markup', 'target': 'Featured Snippets', 'weight': 0.8},
    ]
    
    return relationships

def enhance_generative_search(results: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Enhance analysis with generative search optimization
    """
    # Mock DeepSeek generative enhancement
    results['generative_recommendations'].insert(0, {
        'category': 'DeepSeek AI',
        'title': 'Optimize for SGE (Search Generative Experience)',
        'description': 'Structure content to appear in AI-generated answers. Focus on clear definitions, step-by-step guides, and comparative analysis.',
        'impact': 'Very High',
        'effort': 'Medium'
    })
    
    # Add AI answer optimization
    results['ai_answer_potential'] = {
        'question_coverage': '65%',
        'answer_quality': '72%',
        'recommended_questions': [
            'How does your SEO service compare to competitors?',
            'What makes your approach unique?',
            'How quickly can you improve rankings?'
        ]
    }
    
    # Add entity confidence scores
    for entity in results['entities']:
        if entity.get('in_schema'):
            entity['ai_confidence'] = min(0.95, entity['confidence'] * 1.2)
    
    # Update AI visibility scores with generative focus
    results['sge_score'] = min(85, results.get('sge_score', 50) + 15)
    results['ai_visibility_score'] = min(90, results.get('ai_visibility_score', 60) + 8)
    
    return results

if __name__ == "__main__":
    # Note: For spaCy integration in production, uncomment:
    # try:
    #     nlp = spacy.load("en_core_web_lg")
    # except:
    #     st.warning("Install spaCy model: python -m spacy download en_core_web_lg")
    pass
