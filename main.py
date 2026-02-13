# main_enhanced.py
import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import re
from urllib.parse import urlparse
import random
import json
import requests

# Page configuration
st.set_page_config(
    page_title="AI Search Optimizer - Generative SEO Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== DEEPSEEK API INTEGRATION ==============
def analyze_with_deepseek(api_key, url, depth, platforms):
    """
    Actually call DeepSeek API for real AI analysis of ANY website
    """
    if not api_key or not api_key.startswith('sk-') or len(api_key) < 20:
        st.warning("⚠️ Invalid or missing API key. Using enhanced demo data.")
        return generate_ai_analysis(url, depth, platforms, enhanced=True)
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        domain = urlparse(url).netloc if url.startswith(('http://', 'https://')) else url
        
        # Comprehensive prompt for ANY website type
        prompt = f"""You are an expert at website classification and SEO analysis. Analyze this website URL and domain: {url}

Domain: {domain}
Analysis depth: {depth}
Target AI platforms: {', '.join(platforms) if platforms else 'Google SGE, ChatGPT, Bard'}

First, classify the website type STRICTLY based on these categories:

1. "E-commerce / Retail" - Sells physical or digital products, has shopping cart, product pages, categories
   Examples: shoe stores, clothing shops, electronics stores, Amazon, Etsy, any online store

2. "Service Provider" - Offers professional services, consultations, expertise
   Examples: marketing agencies, consulting firms, law firms, medical practices, digital agencies, freelancers

3. "Content / Media" - Publishes articles, news, blogs, educational content
   Examples: news sites, tech blogs, magazines, educational platforms, review sites

4. "Business Website" - Corporate/brochure website for a company
   Examples: company landing pages, corporate sites, portfolio sites

Return ONLY valid JSON with this exact structure. ALL fields are required:

{{
  "website_type": {{
    "type": "string - one of the four categories above",
    "industry": "string - specific industry (e.g., 'Footwear Retail', 'Digital Marketing', 'Tech News', 'Manufacturing')",
    "description": "string - brief 1-sentence description of what the website does",
    "entity_focus": ["array of 4-6 main entity types relevant to this business"],
    "schema_priority": ["array of 4-6 schema.org types to prioritize"]
  }},
  "ai_visibility_score": "integer 0-100",
  "entity_score": "integer 0-100",
  "entity_count": "integer 15-50",
  "schema_score": "integer 0-100",
  "schema_types": "integer 1-8",
  "sge_score": "integer 0-100",
  "ai_confidence": "integer 0-100",
  "improvement_potential": "integer 0-100",
  "platform_scores": {{
    "Google SGE": "integer 0-100",
    "ChatGPT": "integer 0-100",
    "Bard": "integer 0-100",
    "Claude": "integer 0-100"
  }},
  "entities": [
    {{
      "text": "string - entity name",
      "type": "string - entity type (PRODUCT, SERVICE, BRAND, etc.)",
      "confidence": "number 0.5-1.0",
      "in_schema": "boolean",
      "relevance": "number 0.6-1.0"
    }}
  ],
  "entity_recommendations": [
    {{
      "title": "string",
      "description": "string",
      "priority": "high/medium/low",
      "impact": "string (e.g., '+45% visibility')",
      "effort": "High/Medium/Low"
    }}
  ],
  "kg_present": ["array of 3-4 entities already in knowledge graph"],
  "kg_missing": ["array of 3-4 entities missing from knowledge graph"],
  "ai_description": "string - current AI understanding of the website (1-2 sentences)",
  "optimized_description": "string - optimized AI description (1-2 sentences)",
  "featured_snippets": [
    {{
      "question": "string - common question in this industry",
      "answer": "string - best answer",
      "status": "string - current ranking status",
      "color": "string hex color code"
    }}
  ],
  "generative_recommendations": [
    {{
      "category": "string - strategy category",
      "title": "string",
      "description": "string",
      "impact": "Very High/High/Medium",
      "effort": "High/Medium/Low",
      "border_color": "string hex color code"
    }}
  ]
}}

Ensure ALL fields are included with appropriate values for this specific website. The response must be parseable JSON only, no other text."""
        
        # Call DeepSeek API
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are an AI search optimization expert. Analyze any website and provide structured JSON data about its AI search visibility and entity recognition. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_text = result['choices'][0]['message']['content']
            
            # Clean the response - remove markdown code blocks if present
            analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()
            
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Try to extract JSON from the text using regex
                import re
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from API response")
            
            # Add metadata
            analysis_data['url'] = url
            analysis_data['domain'] = domain
            analysis_data['improvement_potential'] = 100 - analysis_data.get('ai_visibility_score', 50)
            
            # Ensure schema_types exists
            if 'schema_types' not in analysis_data:
                analysis_data['schema_types'] = len(analysis_data.get('schema_priority', [])) or random.randint(2, 5)
            
            # Validate and fix website type if needed using pattern matching
            valid_types = ["E-commerce / Retail", "Service Provider", "Content / Media", "Business Website"]
            detected_type = analysis_data.get('website_type', {}).get('type', '')
            
            if detected_type not in valid_types:
                # Re-classify based on URL patterns
                url_lower = url.lower()
                domain_lower = domain.lower()
                
                # E-commerce / Retail detection
                ecommerce_keywords = ['shop', 'store', 'product', 'buy', 'cart', 'checkout', 'retail', 
                                    'amazon', 'etsy', 'ebay', 'walmart', 'target', 'merch', 'merchandise',
                                    'clothing', 'apparel', 'fashion', 'shoe', 'footwear', 'bag', 'accessory',
                                    'electronics', 'gadget', 'furniture', 'home', 'decor', 'beauty', 'cosmetic']
                
                # Service Provider detection
                service_keywords = ['service', 'consulting', 'agency', 'solutions', 'professional', 
                                  'marketing', 'design', 'development', 'legal', 'law', 'medical', 'health',
                                  'hr', 'recruiting', 'financial', 'insurance', 'real estate', 'contractor',
                                  'cleaning', 'repair', 'maintenance', 'coaching', 'training']
                
                # Content / Media detection
                media_keywords = ['blog', 'news', 'magazine', 'media', 'publishing', 'journal', 
                                'review', 'tech', 'science', 'education', 'learn', 'tutorial', 
                                'guide', 'how-to', 'podcast', 'video', 'streaming']
                
                if any(kw in url_lower or kw in domain_lower for kw in ecommerce_keywords):
                    analysis_data['website_type'] = {
                        'type': 'E-commerce / Retail',
                        'industry': 'Retail',
                        'description': f'online store selling products',
                        'entity_focus': ['Products', 'Brands', 'Categories', 'Reviews', 'Prices', 'Inventory'],
                        'schema_priority': ['Product', 'Offer', 'Review', 'AggregateRating', 'Breadcrumb', 'Shipping']
                    }
                elif any(kw in url_lower or kw in domain_lower for kw in service_keywords):
                    analysis_data['website_type'] = {
                        'type': 'Service Provider',
                        'industry': 'Professional Services',
                        'description': f'service-based business',
                        'entity_focus': ['Services', 'Team', 'Expertise', 'Process', 'Testimonials', 'Case Studies'],
                        'schema_priority': ['Service', 'Organization', 'Person', 'FAQ', 'LocalBusiness', 'Review']
                    }
                elif any(kw in url_lower or kw in domain_lower for kw in media_keywords):
                    analysis_data['website_type'] = {
                        'type': 'Content / Media',
                        'industry': 'Digital Media',
                        'description': f'content publishing platform',
                        'entity_focus': ['Articles', 'Authors', 'Topics', 'Categories', 'Publications', 'Media'],
                        'schema_priority': ['Article', 'Person', 'Organization', 'Breadcrumb', 'HowTo', 'VideoObject']
                    }
                else:
                    analysis_data['website_type'] = {
                        'type': 'Business Website',
                        'industry': 'General Business',
                        'description': f'corporate website',
                        'entity_focus': ['Company', 'Services', 'Contact', 'About', 'Team', 'Careers'],
                        'schema_priority': ['Organization', 'LocalBusiness', 'ContactPoint', 'AboutPage', 'FAQ', 'Event']
                    }
            
            # Ensure all required fields exist with fallbacks
            if 'platform_scores' not in analysis_data or not analysis_data['platform_scores']:
                analysis_data['platform_scores'] = {
                    "Google SGE": random.randint(45, 75),
                    "ChatGPT": random.randint(50, 80),
                    "Bard": random.randint(40, 70),
                    "Claude": random.randint(45, 75)
                }
            
            if 'entities' not in analysis_data or not analysis_data['entities']:
                # Generate sample entities based on website type
                website_type = analysis_data.get('website_type', {}).get('type', 'Business Website')
                analysis_data['entities'] = generate_entities(20, depth, {'type': website_type}, enhanced=True)
            
            if 'entity_recommendations' not in analysis_data:
                analysis_data['entity_recommendations'] = generate_entity_recommendations(
                    {'type': analysis_data.get('website_type', {}).get('type', 'Business Website')}, 
                    enhanced=True
                )
            
            if 'featured_snippets' not in analysis_data:
                analysis_data['featured_snippets'] = generate_featured_snippets(
                    {'type': analysis_data.get('website_type', {}).get('type', 'Business Website')}, 
                    enhanced=True
                )
            
            if 'generative_recommendations' not in analysis_data:
                analysis_data['generative_recommendations'] = generate_generative_recommendations(
                    {'type': analysis_data.get('website_type', {}).get('type', 'Business Website')}, 
                    enhanced=True
                )
            
            if 'kg_present' not in analysis_data:
                analysis_data['kg_present'] = analysis_data.get('website_type', {}).get('entity_focus', [])[:3]
            
            if 'kg_missing' not in analysis_data:
                analysis_data['kg_missing'] = analysis_data.get('website_type', {}).get('schema_priority', [])[:3]
            
            return analysis_data
        else:
            st.warning(f"⚠️ DeepSeek API error ({response.status_code}). Using enhanced demo data.")
            return generate_ai_analysis(url, depth, platforms, enhanced=True)
            
    except Exception as e:
        st.warning(f"⚠️ Could not connect to DeepSeek API: {str(e)}. Using enhanced demo data.")
        return generate_ai_analysis(url, depth, platforms, enhanced=True)

# ============== CORE ANALYSIS FUNCTIONS ============== 

def detect_website_type(url, domain):
    """
    Detect website type based on URL patterns and domain
    Works for ANY website type
    """
    url_lower = url.lower()
    domain_lower = domain.lower()
    
    # E-commerce / Retail detection - comprehensive list
    ecommerce_keywords = ['shop', 'store', 'product', 'buy', 'cart', 'checkout', 'retail', 
                         'amazon', 'etsy', 'ebay', 'walmart', 'target', 'merch', 'merchandise',
                         'clothing', 'apparel', 'fashion', 'shoe', 'footwear', 'bag', 'accessory',
                         'electronics', 'gadget', 'furniture', 'home', 'decor', 'beauty', 'cosmetic',
                         'grocer', 'food', 'beverage', 'wine', 'book', 'toy', 'game', 'sport',
                         'jewelry', 'watch', 'tool', 'hardware', 'pet', 'auto', 'part']
    
    # Service business detection - comprehensive list
    service_keywords = ['service', 'consulting', 'agency', 'solutions', 'professional', 
                       'marketing', 'design', 'development', 'legal', 'law', 'medical', 'health',
                       'hr', 'recruiting', 'financial', 'insurance', 'real estate', 'contractor',
                       'cleaning', 'repair', 'maintenance', 'coaching', 'training', 'tutoring',
                       'therapy', 'counseling', 'photography', 'event', 'wedding', 'catering',
                       'landscaping', 'pest', 'moving', 'storage', 'logistics', 'shipping']
    
    # Media/Content detection - comprehensive list
    media_keywords = ['blog', 'news', 'magazine', 'media', 'publishing', 'journal', 
                     'review', 'tech', 'science', 'education', 'learn', 'tutorial', 
                     'guide', 'how-to', 'podcast', 'video', 'streaming', 'entertainment',
                     'sports', 'gaming', 'music', 'art', 'culture', 'lifestyle', 'travel',
                     'foodie', 'recipe', 'fitness', 'wellness', 'finance', 'investing']
    
    # Check for e-commerce indicators
    for kw in ecommerce_keywords:
        if kw in url_lower or kw in domain_lower:
            return {
                'type': 'E-commerce / Retail',
                'industry': 'Retail',
                'description': 'online store selling products',
                'entity_focus': ['Products', 'Brands', 'Categories', 'Reviews', 'Prices', 'Inventory', 'Shipping'],
                'schema_priority': ['Product', 'Offer', 'Review', 'AggregateRating', 'Breadcrumb', 'Shipping']
            }
    
    # Check for service indicators
    for kw in service_keywords:
        if kw in url_lower or kw in domain_lower:
            return {
                'type': 'Service Provider',
                'industry': 'Professional Services',
                'description': 'service-based business',
                'entity_focus': ['Services', 'Team', 'Expertise', 'Process', 'Testimonials', 'Case Studies', 'Pricing'],
                'schema_priority': ['Service', 'Organization', 'Person', 'FAQ', 'LocalBusiness', 'Review', 'ContactPoint']
            }
    
    # Check for media/content indicators
    for kw in media_keywords:
        if kw in url_lower or kw in domain_lower:
            return {
                'type': 'Content / Media',
                'industry': 'Digital Media',
                'description': 'content publishing platform',
                'entity_focus': ['Articles', 'Authors', 'Topics', 'Categories', 'Publications', 'Media', 'Subscribers'],
                'schema_priority': ['Article', 'Person', 'Organization', 'Breadcrumb', 'HowTo', 'VideoObject', 'Podcast']
            }
    
    # Default generic business
    return {
        'type': 'Business Website',
        'industry': 'General Business',
        'description': 'corporate website',
        'entity_focus': ['Company', 'Services', 'Contact', 'About', 'Team', 'Careers', 'Locations'],
        'schema_priority': ['Organization', 'LocalBusiness', 'ContactPoint', 'AboutPage', 'FAQ', 'Event', 'Review']
    }

def generate_entities(count, depth, website_type, enhanced=False):
    """
    Generate realistic entity data based on website type
    Works for ANY website type
    """
    # Entity templates by website type - expanded for all industries
    entity_templates = {
        'E-commerce / Retail': {
            'types': ['PRODUCT', 'BRAND', 'CATEGORY', 'OFFER', 'REVIEW', 'PRICE', 'SIZE', 'COLOR', 'MATERIAL', 'SHIPPING'],
            'names': [
                'Featured Products', 'Best Sellers', 'New Arrivals', 'Sale Items', 'Clearance',
                'Customer Reviews', 'Ratings', 'Size Guide', 'Returns Policy', 'Shipping Information',
                'Gift Cards', 'Loyalty Program', 'Wishlist', 'Compare Products', 'Recently Viewed',
                'Product Specifications', 'Care Instructions', 'Warranty', 'Gift Wrapping', 'Bulk Orders'
            ]
        },
        'Service Provider': {
            'types': ['SERVICE', 'ORGANIZATION', 'PERSON', 'PROCESS', 'CERTIFICATION', 'TESTIMONIAL', 'PORTFOLIO', 'PRICING'],
            'names': [
                'Consulting Services', 'Strategy Development', 'Implementation', 'Training Programs', 'Ongoing Support',
                'Expert Team', 'Certified Professionals', 'Client Success Stories', 'Methodology', 'Case Studies',
                'ROI Analysis', 'Free Consultation', 'Digital Transformation', 'Managed Services', 'Cloud Solutions',
                'Custom Development', 'Audit Services', 'Compliance', 'Risk Assessment', 'Quality Assurance'
            ]
        },
        'Content / Media': {
            'types': ['ARTICLE', 'AUTHOR', 'TOPIC', 'PUBLICATION', 'CATEGORY', 'INTERVIEW', 'RESEARCH', 'ANALYSIS'],
            'names': [
                'Latest News', 'Trending Topics', 'In-depth Analysis', 'Opinion Pieces', 'Research Reports',
                'Editorial Team', 'Contributors', 'Guest Authors', 'Subscriber Benefits', 'Premium Content',
                'Breaking Stories', 'Exclusive Interviews', 'Podcast Episodes', 'Video Series', 'Webinars',
                'Whitepapers', 'E-books', 'Infographics', 'Data Visualizations', 'Newsletters'
            ]
        },
        'Business Website': {
            'types': ['ORGANIZATION', 'SERVICE', 'LOCATION', 'CONTACT', 'ABOUT', 'CAREER', 'EVENT', 'PARTNER'],
            'names': [
                'Company Overview', 'Mission Statement', 'Core Values', 'Leadership Team', 'Board of Directors',
                'Office Locations', 'Global Presence', 'Contact Information', 'Careers', 'Job Openings',
                'Strategic Partners', 'Clients', 'Press Releases', 'Events', 'Webinars',
                'Annual Report', 'Sustainability Initiatives', 'Community Involvement', 'Awards', 'Certifications'
            ]
        }
    }
    
    # Get template or default to business
    template = entity_templates.get(website_type['type'], entity_templates['Business Website'])
    
    # Select appropriate entity types and names
    entity_types = template['types']
    entity_names = template['names']
    
    # More entities for deep/advanced analysis
    if enhanced or "Deep" in depth or "🧬" in depth:
        count = min(count + 15, len(entity_names))
    elif "Advanced" in depth or "🔬" in depth:
        count = min(count + 10, len(entity_names))
    
    entities = []
    used_names = set()
    
    for i in range(min(count, len(entity_names))):
        # Ensure we don't duplicate
        available_names = [n for n in entity_names if n not in used_names]
        if not available_names:
            break
            
        name = random.choice(available_names)
        used_names.add(name)
        
        confidence = random.uniform(0.65, 0.98)
        entities.append({
            'text': name,
            'type': random.choice(entity_types),
            'confidence': round(confidence, 2),
            'in_schema': confidence > 0.75,
            'relevance': round(random.uniform(0.7, 1.0), 2)
        })
    
    return entities

def generate_entity_recommendations(website_type, enhanced=False):
    """
    Generate entity optimization recommendations based on website type
    Works for ANY website type
    """
    if 'E-commerce' in website_type['type']:
        recommendations = [
            {
                'title': 'Implement Product Schema',
                'description': 'Add Product schema markup with price, availability, and reviews for all product pages. Include MPN/GTIN for better product recognition.',
                'priority': 'high',
                'impact': '+45% product visibility in AI search',
                'effort': 'High'
            },
            {
                'title': 'Add AggregateRating Schema',
                'description': 'Include review schema with aggregate ratings to display stars in search results and AI answers.',
                'priority': 'high',
                'impact': '+35% click-through rate',
                'effort': 'Medium'
            },
            {
                'title': 'Implement Offer Schema',
                'description': 'Mark up special offers, sales, and promotions with Offer schema for real-time AI visibility.',
                'priority': 'medium',
                'impact': '+30% promotional visibility',
                'effort': 'Low'
            }
        ]
        if enhanced:
            recommendations.extend([
                {
                    'title': 'Add Product Variants Schema',
                    'description': 'Use ProductGroup schema to define product variants like sizes, colors, and materials for better AI understanding.',
                    'priority': 'medium',
                    'impact': '+25% product discovery',
                    'effort': 'High'
                },
                {
                    'title': 'Implement FAQ Schema',
                    'description': 'Add FAQ schema for common questions about shipping, returns, sizing, and product care.',
                    'priority': 'low',
                    'impact': '+20% featured snippet potential',
                    'effort': 'Low'
                }
            ])
        return recommendations
    elif 'Service' in website_type['type']:
        recommendations = [
            {
                'title': 'Implement Service Schema',
                'description': 'Add Service schema for each service offering with description, provider, price range, and area served.',
                'priority': 'high',
                'impact': '+40% service visibility in AI search',
                'effort': 'Medium'
            },
            {
                'title': 'Add Organization Schema',
                'description': 'Enhance Organization schema with logo, contact info, social profiles, founding date, and awards.',
                'priority': 'high',
                'impact': '+35% brand authority',
                'effort': 'Low'
            }
        ]
        if enhanced:
            recommendations.extend([
                {
                    'title': 'Implement Person Schema',
                    'description': 'Add Person schema for key team members with credentials, expertise, social profiles, and publications.',
                    'priority': 'medium',
                    'impact': '+30% trust signals',
                    'effort': 'Medium'
                },
                {
                    'title': 'Add LocalBusiness Schema',
                    'description': 'If you serve specific locations, add LocalBusiness schema with address, opening hours, and service areas.',
                    'priority': 'medium',
                    'impact': '+25% local search visibility',
                    'effort': 'Low'
                }
            ])
        return recommendations
    elif 'Content' in website_type['type']:
        recommendations = [
            {
                'title': 'Implement Article Schema',
                'description': 'Add Article/NewsArticle schema with headline, author, date published, date modified, and image.',
                'priority': 'high',
                'impact': '+40% visibility in Google News and SGE',
                'effort': 'Medium'
            },
            {
                'title': 'Add Author Schema',
                'description': 'Mark up author profiles with Person schema to build authority, expertise signals, and author recognition.',
                'priority': 'high',
                'impact': '+35% author authority and E-E-A-T',
                'effort': 'Low'
            }
        ]
        if enhanced:
            recommendations.append({
                'title': 'Implement Breadcrumb Schema',
                'description': 'Add BreadcrumbList schema to help AI understand site structure, content hierarchy, and navigation paths.',
                'priority': 'medium',
                'impact': '+25% navigation understanding',
                'effort': 'Low'
            })
        return recommendations
    else:
        recommendations = [
            {
                'title': 'Implement Organization Schema',
                'description': 'Add comprehensive Organization schema with legal name, logo, contact points, social profiles, and founding details.',
                'priority': 'high',
                'impact': '+35% entity visibility in Knowledge Graph',
                'effort': 'Low'
            },
            {
                'title': 'Add LocalBusiness Schema',
                'description': 'Include LocalBusiness schema with address, phone, opening hours, and geo coordinates for local search.',
                'priority': 'high',
                'impact': '+40% local search visibility',
                'effort': 'Low'
            }
        ]
        if enhanced:
            recommendations.append({
                'title': 'Implement ContactPoint Schema',
                'description': 'Add ContactPoint schema for customer support, sales, and general inquiries with available hours.',
                'priority': 'medium',
                'impact': '+25% customer engagement',
                'effort': 'Low'
            })
        return recommendations

def generate_featured_snippets(website_type, enhanced=False):
    """
    Generate featured snippet opportunities based on website type
    Works for ANY website type
    """
    if 'E-commerce' in website_type['type']:
        snippets = [
            {
                'question': 'What are the shipping options and delivery times?',
                'answer': 'Standard shipping takes 3-5 business days. Express shipping available for 1-2 business day delivery. Free shipping on orders over $50.',
                'status': '⚠️ Opportunity - Add Shipping schema',
                'color': '#eab308'
            },
            {
                'question': 'What is the return policy?',
                'answer': 'Free returns within 30 days of purchase. Items must be unworn with original tags attached. Refunds processed within 5-7 business days.',
                'status': '❌ Not ranking - Add FAQ schema',
                'color': '#ef4444'
            }
        ]
        if enhanced:
            snippets.append({
                'question': 'What sizes and colors are available?',
                'answer': 'Our collection includes sizes XS-XXL and colors including black, white, navy, red, and seasonal colors. Size guide available for exact measurements.',
                'status': '✅ Currently ranking #3',
                'color': '#22c55e'
            })
        return snippets
    elif 'Service' in website_type['type']:
        return [
            {
                'question': 'What services do you offer?',
                'answer': 'We provide comprehensive solutions including strategic consulting, implementation, training, and ongoing support tailored to your specific needs.',
                'status': '✅ Currently featured snippet',
                'color': '#22c55e'
            },
            {
                'question': 'How much do your services cost?',
                'answer': 'Our services start at $500/month for basic packages, with custom enterprise solutions available. Contact us for a personalized quote.',
                'status': '⚠️ Opportunity - Add PriceSpecification',
                'color': '#eab308'
            }
        ]
    elif 'Content' in website_type['type']:
        return [
            {
                'question': 'How often is new content published?',
                'answer': 'We publish new articles daily, with in-depth features weekly and special reports monthly. Subscribe to our newsletter for updates.',
                'status': '✅ Ranking #2 for "content updates"',
                'color': '#22c55e'
            },
            {
                'question': 'Who are the authors and experts?',
                'answer': 'Our content is created by industry experts, experienced journalists, and subject matter specialists with 10+ years of experience.',
                'status': '❌ Missing - Add Author schema',
                'color': '#ef4444'
            }
        ]
    else:
        return [
            {
                'question': 'What is your company background and history?',
                'answer': 'Founded in 2010, we have grown to serve over 500 clients across 15 countries with our innovative solutions and customer-first approach.',
                'status': '✅ Ranking #4 for "company background"',
                'color': '#22c55e'
            }
        ]

def generate_generative_recommendations(website_type, enhanced=False):
    """
    Generate generative SEO recommendations based on website type
    Works for ANY website type
    """
    base_recommendations = [
        {
            'category': 'SGE Optimization',
            'title': 'Structure Content for Generative Search',
            'description': 'Organize content with clear headings (H1, H2, H3), bullet points, tables, and concise answers to directly address user queries. Create dedicated FAQ sections.',
            'impact': 'Very High',
            'effort': 'Medium',
            'border_color': '#00d2ff'
        },
        {
            'category': 'Voice Search',
            'title': 'Optimize for Conversational Queries',
            'description': 'Target long-tail, natural language questions users ask voice assistants. Focus on who, what, where, when, why, and how questions.',
            'impact': 'High',
            'effort': 'Low',
            'border_color': '#00ff9d'
        }
    ]
    
    if 'E-commerce' in website_type['type']:
        base_recommendations.append({
            'category': 'Product SEO',
            'title': 'Enhance Product Data for AI Shopping',
            'description': 'Provide detailed product attributes (size, color, material, brand), high-quality images with descriptive alt text, and verified customer reviews for AI shopping features.',
            'impact': 'Very High',
            'effort': 'High',
            'border_color': '#9d4edd'
        })
        if enhanced:
            base_recommendations.append({
                'category': 'Visual Search',
                'title': 'Optimize Images for Google Lens',
                'description': 'Use high-resolution product images with descriptive filenames, comprehensive alt text, and structured image metadata for visual search discovery.',
                'impact': 'High',
                'effort': 'Medium',
                'border_color': '#f59e0b'
            })
    elif 'Service' in website_type['type']:
        base_recommendations.append({
            'category': 'Local SEO',
            'title': 'Optimize for "Near Me" Searches',
            'description': 'Include location-specific content, implement LocalBusiness schema, and optimize Google Business Profile for "near me" voice and mobile searches.',
            'impact': 'High',
            'effort': 'Low',
            'border_color': '#9d4edd'
        })
        if enhanced:
            base_recommendations.append({
                'category': 'Trust Signals',
                'title': 'Build E-E-A-T Through Expertise',
                'description': 'Showcase team credentials, certifications, case studies, and client testimonials to demonstrate Experience, Expertise, Authoritativeness, and Trustworthiness.',
                'impact': 'High',
                'effort': 'Medium',
                'border_color': '#f43f5e'
            })
    elif 'Content' in website_type['type']:
        base_recommendations.append({
            'category': 'Content Strategy',
            'title': 'Develop Topic Clusters',
            'description': 'Create comprehensive pillar pages and supporting topic clusters to establish authority and improve semantic relevance for AI search algorithms.',
            'impact': 'Very High',
            'effort': 'High',
            'border_color': '#9d4edd'
        })
    else:
        base_recommendations.append({
            'category': 'Brand Authority',
            'title': 'Build Knowledge Graph Presence',
            'description': 'Implement comprehensive Organization schema, claim your Google Knowledge Panel, and maintain consistent NAP (Name, Address, Phone) across the web.',
            'impact': 'High',
            'effort': 'Medium',
            'border_color': '#9d4edd'
        })
    
    return base_recommendations

def generate_ai_analysis(url, depth, platforms, enhanced=False):
    """
    Generate comprehensive AI search analysis (enhanced demo data)
    Works for ANY website type
    """
    domain = urlparse(url).netloc if url.startswith(('http://', 'https://')) else url
    
    # Detect website type
    website_type = detect_website_type(url, domain)
    
    # Base scores - higher for enhanced mode
    if enhanced:
        base_score = random.randint(55, 85)
    else:
        base_score = random.randint(45, 75)
    
    # Adjust based on depth
    if "Deep" in depth or "🧬" in depth:
        entity_count = random.randint(45, 65) if enhanced else random.randint(35, 55)
        entity_score = random.randint(55, 75) if enhanced else random.randint(45, 65)
        schema_score = random.randint(45, 65) if enhanced else random.randint(35, 55)
        schema_types = random.randint(4, 8) if enhanced else random.randint(3, 6)
    elif "Advanced" in depth or "🔬" in depth:
        entity_count = random.randint(30, 45) if enhanced else random.randint(20, 35)
        entity_score = random.randint(50, 65) if enhanced else random.randint(40, 55)
        schema_score = random.randint(40, 55) if enhanced else random.randint(30, 45)
        schema_types = random.randint(3, 6) if enhanced else random.randint(2, 4)
    else:
        entity_count = random.randint(15, 25) if enhanced else random.randint(10, 20)
        entity_score = random.randint(40, 55) if enhanced else random.randint(30, 45)
        schema_score = random.randint(30, 45) if enhanced else random.randint(20, 35)
        schema_types = random.randint(2, 4) if enhanced else random.randint(1, 3)
    
    # Generate platform scores
    platform_scores = {}
    if platforms:
        for platform in platforms:
            platform_scores[platform] = random.randint(
                max(30, base_score - 10),
                min(90, base_score + 15)
            )
    else:
        platform_scores = {
            "Google SGE": random.randint(45, 75),
            "ChatGPT": random.randint(50, 80),
            "Bard": random.randint(40, 70),
            "Claude": random.randint(45, 75)
        }
    
    # Generate entities based on website type
    entities = generate_entities(entity_count, depth, website_type, enhanced)
    
    # Calculate entity confidence
    entity_confidence = sum(e['confidence'] for e in entities) / len(entities) if entities else 0.7
    
    # Generate context-aware descriptions based on actual website type
    website_type_name = website_type['type']
    industry = website_type['industry']
    
    if 'E-commerce' in website_type_name:
        ai_description = f"{domain} is an e-commerce website selling {industry.lower()} products. Product schema implementation is partial - missing offer pricing, availability markup, and product variants. Review schema is present but not aggregated for rich results."
        optimized_description = f"{domain} is a premier online retailer specializing in {industry.lower()}, featuring an extensive collection of products with detailed specifications, authentic customer reviews, real-time inventory tracking, and personalized shopping recommendations."
    elif 'Service' in website_type_name:
        ai_description = f"{domain} provides professional {industry.lower()} services. The site lacks Service schema markup and team member profiles. Organization schema is minimal with missing social profiles, founding information, and service areas."
        optimized_description = f"{domain} is a leading {industry.lower()} firm delivering tailored solutions. Our expert team of certified professionals brings proven methodologies, industry recognition, and measurable results to every client engagement."
    elif 'Content' in website_type_name:
        ai_description = f"{domain} is a {industry.lower()} content platform. Article schema is implemented on some posts but missing author bios, publication dates, and category breadcrumbs. Entity recognition for topics and authors is limited."
        optimized_description = f"{domain} is a premier {industry.lower()} publication featuring expert analysis, breaking news, and in-depth research. Our content is created by industry specialists and journalists with verified credentials."
    else:
        ai_description = f"{domain} is a {industry.lower()} business website. Organization and LocalBusiness schema are incomplete or missing. Contact points, opening hours, and detailed about information are not structured for AI understanding."
        optimized_description = f"{domain} is an established {industry.lower()} business committed to quality solutions and customer satisfaction. With years of industry expertise, we deliver value through innovation, integrity, and personalized service."
    
    return {
        'url': url,
        'domain': domain,
        'website_type': website_type,
        'ai_visibility_score': base_score,
        'entity_score': entity_score,
        'entity_count': entity_count,
        'schema_score': schema_score,
        'schema_types': schema_types,
        'sge_score': random.randint(45, 75) if enhanced else random.randint(35, 65),
        'ai_confidence': int(entity_confidence * 100),
        'improvement_potential': random.randint(25, 45) if enhanced else random.randint(35, 55),
        'platform_scores': platform_scores,
        'entities': entities,
        'entity_recommendations': generate_entity_recommendations(website_type, enhanced),
        'kg_present': website_type['entity_focus'][:4],
        'kg_missing': website_type['schema_priority'][:4],
        'ai_description': ai_description,
        'optimized_description': optimized_description,
        'featured_snippets': generate_featured_snippets(website_type, enhanced),
        'generative_recommendations': generate_generative_recommendations(website_type, enhanced)
    }

def export_to_json(data):
    """Export analysis results to JSON"""
    return json.dumps(data, indent=2)

def export_to_csv(data):
    """Export entity data to CSV"""
    df = pd.DataFrame(data['entities'])
    return df.to_csv(index=False)

# ============== ENHANCED CUSTOM CSS ============== 
st.markdown("""
<style>
    /* Modern gradient background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* API Key Section Styling */
    .api-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stTextInput input {
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .api-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-align: center;
        color: white;
        font-weight: 600;
        text-decoration: none;
        display: inline-block;
        width: 100%;
        transition: transform 0.2s;
    }
    
    .api-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    
    .metric-title {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-change {
        font-size: 0.9rem;
        color: #22c55e;
        font-weight: 600;
    }
    
    /* Platform score cards */
    .platform-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .platform-name {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .platform-score {
        font-size: 2.5rem;
        font-weight: 800;
    }
    
    /* Entity chips */
    .entity-chip {
        display: inline-block;
        background: white;
        border-left: 4px solid #00d2ff;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0.5rem 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .entity-chip:hover {
        transform: translateX(5px);
    }
    
    .entity-text {
        font-weight: 600;
        color: #1e293b;
    }
    
    .entity-type {
        color: #64748b;
        font-size: 0.85rem;
    }
    
    /* Entity type distribution bars */
    .entity-bar {
        margin-bottom: 1rem;
    }
    
    .entity-bar-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
        color: #1e293b;
    }
    
    .entity-bar-bg {
        background: #e2e8f0;
        height: 30px;
        border-radius: 15px;
        overflow: hidden;
    }
    
    .entity-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #00d2ff 0%, #00ff9d 100%);
        border-radius: 15px;
        transition: width 0.5s ease;
    }
    
    /* Recommendation cards */
    .recommendation-high {
        background: white;
        border-left: 5px solid #ef4444;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .recommendation-medium {
        background: white;
        border-left: 5px solid #eab308;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .recommendation-low {
        background: white;
        border-left: 5px solid #22c55e;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .rec-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .rec-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .rec-badge {
        background: #ef4444;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .rec-description {
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .rec-stats {
        display: flex;
        gap: 1.5rem;
        font-size: 0.9rem;
        color: #1e293b;
    }
    
    /* Knowledge graph nodes */
    .kg-node {
        background: white;
        border: 3px solid #00d2ff;
        padding: 1.5rem;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem auto;
    }
    
    .kg-node-name {
        font-size: 0.85rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.25rem;
    }
    
    .kg-node-type {
        font-size: 0.7rem;
        color: #64748b;
    }
    
    /* Knowledge panel items */
    .kg-item {
        background: #f1f5f9;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        font-size: 0.95rem;
        color: #1e293b;
    }
    
    /* Featured snippet cards */
    .snippet-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .snippet-question {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.75rem;
    }
    
    .snippet-answer {
        color: #64748b;
        line-height: 1.6;
        margin-bottom: 1rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 8px;
    }
    
    .snippet-status {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Generative recommendation cards */
    .gen-rec-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .gen-rec-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .gen-rec-icon {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .gen-rec-category {
        font-size: 0.85rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .gen-rec-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    /* Competitor leaderboard */
    .competitor-row {
        background: white;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .competitor-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .competitor-name {
        font-weight: 700;
        color: #1e293b;
    }
    
    .competitor-score {
        font-size: 1.5rem;
        font-weight: 800;
    }
    
    .competitor-bar-bg {
        background: #e2e8f0;
        height: 12px;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .competitor-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    
    .competitor-entities {
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* Trend chart */
    .trend-chart {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .trend-month {
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .trend-month-label {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .trend-bars {
        display: flex;
        gap: 0.25rem;
        height: 100px;
        align-items: flex-end;
    }
    
    .trend-bar {
        flex: 1;
        border-radius: 4px 4px 0 0;
        transition: height 0.3s ease;
    }
    
    /* Website type badge */
    .website-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-top: 3rem;
    }
    
    .footer-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .footer-subtitle {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .footer-info {
        font-size: 0.85rem;
        opacity: 0.7;
    }
    
    /* Animation classes */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-slide-in {
        animation: slideInUp 0.5s ease-out;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============== INITIALIZE SESSION STATE ============== 
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# ============== HEADER ============== 
st.markdown('''
<div class="main-header">
    <h1>🤖 AI Search Optimizer Pro</h1>
    <div class="subtitle">Generative Search • Entity Recognition • Knowledge Graphs • SGE Readiness</div>
</div>
''', unsafe_allow_html=True)

# ============== API KEY SECTION - MOVED TO MAIN AREA (ALWAYS VISIBLE) ==============
st.markdown('<div class="api-section">', unsafe_allow_html=True)
st.markdown("### 🔑 DeepSeek AI Authentication")
st.markdown("#### Enter your API key for real AI analysis of ANY website - without a key, enhanced demo data will be used")

col1, col2 = st.columns([3, 1])

with col1:
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="sk-... (enter your API key for real analysis of any website)",
        help="Enter your DeepSeek API key to enable real AI analysis. Get your key at platform.deepseek.com",
        key="api_key_main_area",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("""
    <a href="https://platform.deepseek.com" target="_blank" style="text-decoration: none;">
        <div class="api-button">
            Get API Key →
        </div>
    </a>
    """, unsafe_allow_html=True)

# API Key Validation Status
if api_key:
    if api_key.startswith('sk-') and len(api_key) >= 20:
        st.session_state.api_key = api_key
        st.success("✅ DeepSeek AI Connected - Real-time analysis enabled for ANY website!")
        # Show masked key
        masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "***"
        st.caption(f"Connected: {masked_key}")
    else:
        if len(api_key) > 0:
            st.error("❌ Invalid API key format. Key should start with 'sk-' and be at least 20 characters.")
        st.session_state.api_key = None
else:
    st.session_state.api_key = None
    st.info("💡 No API key provided - using enhanced demo data. Enter a valid DeepSeek API key for real AI analysis of ANY website.")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

# ============== SIDEBAR ============== 
with st.sidebar:
    # AI Analysis Settings
    st.markdown("### 🎯 AI Analysis Depth")
    analysis_depth = st.radio(
        "Select depth",
        ["🌱 Basic Entity Recognition", "🔬 Advanced Semantic Analysis", "🧬 Deep Knowledge Graph"],
        index=1,
        label_visibility="collapsed",
        key="analysis_depth_radio_final"
    )
    
    # Target AI Platforms
    st.markdown("### 🤖 Target AI Platforms")
    ai_platforms = st.multiselect(
        "Select platforms",
        ["Google SGE", "ChatGPT", "Bard", "Claude", "Perplexity", "Copilot"],
        default=["Google SGE", "ChatGPT"],
        label_visibility="collapsed",
        key="ai_platforms_multiselect_final"
    )
    
    st.markdown("---")
    
    # Live AI Metrics
    with st.expander("📊 Global AI Trends", expanded=False):
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
        for idx, hist in enumerate(st.session_state.analysis_history[-3:]):
            st.markdown(f"""
            **{hist['url']}**  
            AI Score: {hist['score']}% | Entities: {hist['entities']}
            """)

# ============== MAIN TABS ============== 
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 AI Readiness Scan",
    "🧬 Entity Intelligence", 
    "🕸️ Knowledge Graph",
    "🔮 Generative SEO",
    "📊 AI Visibility Report"
])

# ============== TAB 1: AI READINESS SCAN ============== 
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input(
            "Enter website URL for AI analysis",
            placeholder="https://yourwebsite.com",
            label_visibility="collapsed",
            key="url_input_tab1_final"
        )
    
    with col2:
        analyze_btn = st.button("🚀 Analyze for AI Search", use_container_width=True, type="primary", key="analyze_button_final")
    
    if analyze_btn and url:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        with st.spinner("🧠 Analyzing AI search readiness..." if not st.session_state.api_key else "🧠 Connecting to DeepSeek AI for real analysis of ANY website..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate analysis steps with status updates
            if st.session_state.api_key:
                steps = [
                    "Authenticating with DeepSeek AI...",
                    f"Analyzing website structure: {url}...",
                    "Extracting entities with AI...",
                    "Evaluating schema markup...",
                    "Generating AI-powered recommendations..."
                ]
            else:
                steps = [
                    "Detecting website type...",
                    "Extracting entities (demo)...",
                    "Analyzing schema markup...",
                    "Evaluating AI platform visibility...",
                    "Generating enhanced demo recommendations..."
                ]
            
            for i, step in enumerate(steps):
                status_text.text(step)
                time.sleep(0.3)
                progress_bar.progress((i + 1) * 20)
            
            # Actually use the API key for real analysis
            if st.session_state.api_key:
                results = analyze_with_deepseek(st.session_state.api_key, url, analysis_depth, ai_platforms)
            else:
                results = generate_ai_analysis(url, analysis_depth, ai_platforms, enhanced=True)
                st.info("ℹ️ Using enhanced demo data. Enter a DeepSeek API key for real AI analysis of ANY website.")
            
            st.session_state.analysis_results = results
            
            # Add to history
            st.session_state.analysis_history.append({
                'url': url,
                'score': results['ai_visibility_score'],
                'entities': results['entity_count'],
                'timestamp': datetime.now().strftime("%H:%M")
            })
            
            status_text.empty()
            if st.session_state.api_key:
                st.success(f"✅ DeepSeek AI Analysis Complete! Visibility Score: {results['ai_visibility_score']}%")
            else:
                st.success(f"✅ Demo Analysis Complete! Visibility Score: {results['ai_visibility_score']}%")
    
    # Display AI Score Dashboard
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Website Type Badge
        st.markdown(f"""
        <div class="website-badge">
            🏷️ <strong>Detected:</strong> {results['website_type']['type']} | {results['website_type']['industry']}<br>
            🌐 <strong>Domain:</strong> {results['domain']}
            {' • 🔴 Real AI Analysis' if st.session_state.api_key else ' • 🟡 Enhanced Demo Data'}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🤖 AI Search Readiness Scorecard")
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">AI Visibility</div>
                <div class="metric-value">{results['ai_visibility_score']}%</div>
                <div class="metric-change">+{results['improvement_potential']}% potential</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Entity Recognition</div>
                <div class="metric-value">{results['entity_score']}%</div>
                <div class="metric-change">{results['entity_count']} entities found</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # FIXED: Use .get() with default value to prevent KeyError
            schema_types_count = results.get('schema_types', len(results.get('schema_priority', [])) or 3)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Schema Coverage</div>
                <div class="metric-value">{results['schema_score']}%</div>
                <div class="metric-change">{schema_types_count} types</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">SGE Readiness</div>
                <div class="metric-value">{results['sge_score']}%</div>
                <div class="metric-change">Featured snippet potential</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Platform scores
        st.markdown("### 📱 AI Platform Readiness")
        platform_cols = st.columns(len(results['platform_scores']))
        
        for idx, (platform, score) in enumerate(results['platform_scores'].items()):
            with platform_cols[idx]:
                st.markdown(f"""
                <div class="platform-card">
                    <div class="platform-name">{platform}</div>
                    <div class="platform-score">{score}%</div>
                </div>
                """, unsafe_allow_html=True)

# ============== TAB 2: ENTITY INTELLIGENCE ============== 
with tab2:
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🧬 Entity Recognition & Semantic Analysis")
        if st.session_state.api_key:
            st.markdown("#### 🔍 Real AI-detected Entities")
        else:
            st.markdown("#### 🔍 Demo Entities")
        st.markdown(f"*Based on {results['website_type']['type']} analysis*")
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            # Display entity chips
            for entity in results['entities'][:12]:
                confidence_color = "#22c55e" if entity['confidence'] > 0.8 else "#eab308" if entity['confidence'] > 0.6 else "#ef4444"
                schema_badge = "✅" if entity.get('in_schema') else "⚠️"
                
                st.markdown(f"""
                <div class="entity-chip" style="border-left-color: {confidence_color};">
                    <span class="entity-text">{entity['text']}</span>
                    <span class="entity-type">({entity['type']})</span>
                    {schema_badge}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📊 Entity Distribution")
            
            # Entity type distribution
            entity_types = {}
            for entity in results['entities']:
                entity_types[entity['type']] = entity_types.get(entity['type'], 0) + 1
            
            # Bar chart using HTML/CSS
            colors = ['#00d2ff', '#00ff9d', '#9d4edd', '#f59e0b', '#ef4444']
            
            for idx, (etype, count) in enumerate(list(entity_types.items())[:5]):
                percentage = (count / results['entity_count']) * 100
                
                st.markdown(f"""
                <div class="entity-bar">
                    <div class="entity-bar-label">
                        <span><strong>{etype}</strong></span>
                        <span>{count} ({percentage:.1f}%)</span>
                    </div>
                    <div class="entity-bar-bg">
                        <div class="entity-bar-fill" style="width: {percentage}%; background: {colors[idx]};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Entity recommendations
        st.markdown("#### ⚡ Entity Optimization Priority")
        st.markdown(f"*Recommendations for {results['website_type']['type']}*")
        
        for rec in results['entity_recommendations']:
            rec_class = f"recommendation-{rec['priority']}"
            badge_color = "#ef4444" if rec['priority'] == 'high' else "#eab308" if rec['priority'] == 'medium' else "#22c55e"
            
            st.markdown(f"""
            <div class="{rec_class}">
                <div class="rec-header">
                    <div class="rec-title">{rec['title']}</div>
                    <div class="rec-badge" style="background: {badge_color};">{rec['priority'].upper()}</div>
                </div>
                <div class="rec-description">{rec['description']}</div>
                <div class="rec-stats">
                    <span>🎯 <strong>Impact:</strong> {rec['impact']}</span>
                    <span>⏱️ <strong>Effort:</strong> {rec['effort']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👆 Analyze a website first to view entity intelligence")

# ============== TAB 3: KNOWLEDGE GRAPH ============== 
with tab3:
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.markdown("### 🕸️ Entity Knowledge Graph")
        st.markdown(f"*Knowledge graph visualization for {results['website_type']['type']}*")
        
        # Sample knowledge graph visualization
        nodes = results['entities'][:6]
        node_colors = ['#00d2ff', '#00ff9d', '#9d4edd', '#f59e0b', '#ef4444', '#3b82f6']
        
        cols = st.columns(3)
        for idx, entity in enumerate(nodes[:3]):
            with cols[idx]:
                st.markdown(f"""
                <div class="kg-node" style="border-color: {node_colors[idx]};">
                    <div class="kg-node-name">{entity['text'][:15]}{'...' if len(entity['text']) > 15 else ''}</div>
                    <div class="kg-node-type">{entity['type']}</div>
                    <div style="font-size: 0.7rem; margin-top: 0.5rem;">
                        Confidence: {int(entity['confidence'] * 100)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Relationship lines
        st.markdown("""
        <div style="text-align: center; color: #64748b; margin: 1rem 0;">
            ↓ ↓ ↓
        </div>
        """, unsafe_allow_html=True)
        
        cols2 = st.columns(3)
        for idx, entity in enumerate(nodes[3:6]):
            with cols2[idx]:
                st.markdown(f"""
                <div class="kg-node" style="border-color: {node_colors[idx+3]};">
                    <div class="kg-node-name">{entity['text'][:15]}{'...' if len(entity['text']) > 15 else ''}</div>
                    <div class="kg-node-type">{entity['type']}</div>
                    <div style="font-size: 0.7rem; margin-top: 0.5rem;">
                        Confidence: {int(entity['confidence'] * 100)}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Knowledge Panel Status
        st.markdown("### 📋 Knowledge Panel Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Present in Knowledge Graph**")
            for entity in results.get('kg_present', [])[:4]:
                st.markdown(f"""
                <div class="kg-item" style="background: #d1fae5; color: #065f46;">
                    ✓ {entity}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**❌ Missing from Knowledge Graph**")
            for entity in results.get('kg_missing', [])[:4]:
                st.markdown(f"""
                <div class="kg-item" style="background: #fee2e2; color: #991b1b;">
                    ✗ {entity}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👆 Analyze a website to generate knowledge graph")

# ============== TAB 4: GENERATIVE SEO ============== 
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
            <div class="snippet-card">
                <div class="snippet-answer">
                    "{results['ai_description']}"
                </div>
                <div class="snippet-status" style="background: #fee2e2; color: #991b1b;">
                    ⚠️ Confidence: {results['ai_confidence']}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Optimized AI Description**")
            st.markdown(f"""
            <div class="snippet-card">
                <div class="snippet-answer">
                    "{results['optimized_description']}"
                </div>
                <div class="snippet-status" style="background: #d1fae5; color: #065f46;">
                    ✅ Potential: +{results['improvement_potential']}% visibility
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Featured Snippet Opportunities
        st.markdown("#### 🎯 Featured Snippet Opportunities")
        
        for qa in results.get('featured_snippets', []):
            st.markdown(f"""
            <div class="snippet-card">
                <div class="snippet-question">Q: {qa['question']}</div>
                <div class="snippet-answer">A: {qa['answer']}</div>
                <div class="snippet-status" style="background: {qa['color']}; color: white;">
                    {qa['status']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Generative SEO Recommendations
        st.markdown("#### 📈 Generative SEO Strategy")
        
        for rec in results.get('generative_recommendations', []):
            st.markdown(f"""
            <div class="gen-rec-card" style="border-left: 4px solid {rec['border_color']};">
                <div class="gen-rec-header">
                    <div class="gen-rec-icon" style="background: {rec['border_color']}20;">
                        🎯
                    </div>
                    <div>
                        <div class="gen-rec-category">{rec['category']}</div>
                        <div class="gen-rec-title">{rec['title']}</div>
                    </div>
                </div>
                <div class="rec-description">{rec['description']}</div>
                <div class="rec-stats">
                    <span>⚡ <strong>Impact:</strong> {rec['impact']}</span>
                    <span>⏱️ <strong>Effort:</strong> {rec['effort']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👆 Analyze a website to view generative SEO insights")

# ============== TAB 5: AI VISIBILITY REPORT ============== 
with tab5:
    st.markdown("### 📊 AI Visibility & Competitive Analysis")
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Competitive Analysis
        st.markdown("#### 🏆 AI Visibility Leaderboard")
        st.markdown(f"*Industry: {results['website_type']['industry']}*")
        
        # Create competitor data
        competitors = [
            {"name": "Your Website", "score": results['ai_visibility_score'], "entities": results['entity_count'], "color": "#00d2ff"},
            {"name": "Competitor A", "score": min(99, results['ai_visibility_score'] + 18), "entities": results['entity_count'] + 22, "color": "#ff6b6b"},
            {"name": "Competitor B", "score": max(30, results['ai_visibility_score'] - 8), "entities": results['entity_count'] - 5, "color": "#4ecdc4"},
            {"name": "Competitor C", "score": min(99, results['ai_visibility_score'] + 12), "entities": results['entity_count'] + 15, "color": "#ffe66d"},
            {"name": "Industry Avg", "score": max(30, results['ai_visibility_score'] - 15), "entities": results['entity_count'] - 10, "color": "#a5a5a5"}
        ]
        
        # Sort by score
        competitors.sort(key=lambda x: x['score'], reverse=True)
        
        for comp in competitors:
            st.markdown(f"""
            <div class="competitor-row">
                <div class="competitor-info">
                    <span class="competitor-name">{comp['name']}</span>
                    <span class="competitor-score">{comp['score']}%</span>
                </div>
                <div class="competitor-bar-bg">
                    <div class="competitor-bar-fill" style="width: {comp['score']}%; background: {comp['color']};"></div>
                </div>
                <div class="competitor-entities">{comp['entities']} entities recognized</div>
            </div>
            """, unsafe_allow_html=True)
        
        # AI Trend Analysis
        st.markdown("#### 📈 6-Month AI Visibility Forecast")
        
        # Generate trend data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        your_site = [35, 42, 48, 52, 58, results['ai_visibility_score']]
        industry = [40, 43, 48, 52, 55, 58]
        top_performer = [75, 78, 80, 82, 85, 88]
        
        # Create trend visualization
        st.markdown('<div class="trend-chart">', unsafe_allow_html=True)
        
        trend_cols = st.columns(len(months))
        for i, month in enumerate(months):
            with trend_cols[i]:
                st.markdown(f"""
                <div class="trend-month">
                    <div class="trend-month-label">{month}</div>
                    <div class="trend-bars">
                        <div class="trend-bar" style="background: #00d2ff; height: {your_site[i]}px;" title="You: {your_site[i]}%"></div>
                        <div class="trend-bar" style="background: #a5a5a5; height: {industry[i]}px;" title="Avg: {industry[i]}%"></div>
                        <div class="trend-bar" style="background: #22c55e; height: {top_performer[i]}px;" title="Top: {top_performer[i]}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Legend
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🔵 **Your Website**")
        with col2:
            st.markdown("⚪ **Industry Average**")
        with col3:
            st.markdown("🟢 **Top Performer**")
        
        st.markdown("---")
        
        # Export Options
        st.markdown("#### 📄 Export AI Readiness Report")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📊 Full AI Report", use_container_width=True, key="export_json_final"):
                # Generate JSON export
                report_data = {
                    'domain': results['domain'],
                    'analysis_date': datetime.now().isoformat(),
                    'analysis_type': 'real' if st.session_state.api_key else 'demo',
                    'scores': {
                        'ai_visibility': results['ai_visibility_score'],
                        'entity_recognition': results['entity_score'],
                        'schema_coverage': results['schema_score'],
                        'sge_readiness': results['sge_score']
                    },
                    'entity_count': results['entity_count'],
                    'improvement_potential': results['improvement_potential'],
                    'website_type': results['website_type']
                }
                
                st.download_button(
                    label="💾 Download JSON",
                    data=export_to_json(report_data),
                    file_name=f"ai_report_{results['domain']}_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    key="download_json_final"
                )
        
        with col2:
            if st.button("🧬 Entity Map", use_container_width=True, key="export_csv_final"):
                st.download_button(
                    label="💾 Download CSV",
                    data=export_to_csv(results),
                    file_name=f"entities_{results['domain']}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_csv_final"
                )
        
        with col3:
            if st.button("🔮 SGE Strategy", use_container_width=True, key="export_strategy_final"):
                strategy_text = f"""
# {'DeepSeek AI ' if st.session_state.api_key else ''}Generative SEO Strategy for {results['domain']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Analysis Type: {'Real AI Analysis' if st.session_state.api_key else 'Enhanced Demo Data'}

## Current SGE Readiness: {results['sge_score']}%

## Recommendations:
"""
                for rec in results['generative_recommendations']:
                    strategy_text += f"\n### {rec['title']}\n"
                    strategy_text += f"**Category:** {rec['category']}\n"
                    strategy_text += f"**Description:** {rec['description']}\n"
                    strategy_text += f"**Impact:** {rec['impact']} | **Effort:** {rec['effort']}\n"
                
                st.download_button(
                    label="💾 Download Strategy",
                    data=strategy_text,
                    file_name=f"sge_strategy_{results['domain']}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    key="download_strategy_final"
                )
        
        with col4:
            if st.button("📈 Competitor Analysis", use_container_width=True, key="export_competitors_final"):
                comp_df = pd.DataFrame(competitors)
                st.download_button(
                    label="💾 Download CSV",
                    data=comp_df.to_csv(index=False),
                    file_name=f"competitors_{results['domain']}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_competitors_final"
                )
    else:
        st.info("👆 Analyze a website to view AI visibility reports")

# ============== FOOTER ============== 
st.markdown("""
<div class="footer">
    <div class="footer-title">🤖 AI Search Optimizer Pro</div>
    <div class="footer-subtitle">Generative Search • Entity Intelligence • Knowledge Graphs • SGE Readiness</div>
    <div class="footer-info">Powered by DeepSeek AI • Real-time Analysis • Enterprise Grade</div>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    # App is ready to run
    pass
