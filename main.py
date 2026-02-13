# Add this near the top of analyze_with_deepseek to debug
import streamlit as st

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
        
        # Simpler prompt to test if API works at all
        prompt = f"""Analyze this website: {url}

First, tell me what type of website this is. Choose ONE category:
- E-commerce / Retail (online store selling products)
- Service Provider (consulting, agency, professional services)
- Content / Media (blog, news, magazine)
- Business Website (corporate site)

Then provide a JSON response with this exact structure:
{{
  "website_type": {{
    "type": "the category you chose",
    "industry": "specific industry (e.g., Footwear Retail, Digital Marketing, Tech News)",
    "description": "brief description"
  }},
  "ai_visibility_score": 65,
  "entity_score": 58,
  "entity_count": 24,
  "schema_score": 42,
  "schema_types": 3,
  "sge_score": 55,
  "ai_confidence": 70,
  "improvement_potential": 35,
  "platform_scores": {{
    "Google SGE": 62,
    "ChatGPT": 58,
    "Bard": 45
  }}
}}

Return ONLY valid JSON, no other text."""
        
        # Call DeepSeek API
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a website analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_text = result['choices'][0]['message']['content']
            
            # Show raw response for debugging (remove in production)
            with st.expander("🔍 DeepSeek API Raw Response (Debug)"):
                st.code(analysis_text, language="json")
            
            try:
                analysis_data = json.loads(analysis_text)
            except:
                analysis_data = {}
            
            # STRONG FORCED OVERRIDE - This will catch obvious misclassifications
            url_lower = url.lower()
            domain_lower = domain.lower()
            
            # FORCE E-COMMERCE classification for ANY store/shop/product website
            ecommerce_indicators = [
                'shoe', 'footwear', 'store', 'shop', 'product', 'buy', 'cart', 
                'checkout', 'retail', 'merch', 'merchandise', 'clothing', 
                'apparel', 'fashion', 'bag', 'accessory', 'electronics',
                'furniture', 'home', 'decor', 'beauty', 'cosmetic', 'toy',
                'book', 'amazon', 'etsy', 'ebay', 'walmart', 'target',
                'payless', 'zappos', 'nike', 'adidas', 'reebok', 'puma'
            ]
            
            # Check if this is CLEARLY an e-commerce site
            if any(kw in url_lower or kw in domain_lower for kw in ecommerce_indicators):
                # Force correct classification regardless of what API said
                analysis_data['website_type'] = {
                    'type': 'E-commerce / Retail',
                    'industry': 'Retail',
                    'description': f'online retail store selling products',
                    'entity_focus': ['Products', 'Brands', 'Categories', 'Reviews', 'Prices', 'Inventory', 'Shipping'],
                    'schema_priority': ['Product', 'Offer', 'Review', 'AggregateRating', 'Breadcrumb', 'Shipping']
                }
                st.info("🛍️ Detected e-commerce website - corrected classification")
            
            # ... rest of the code ...
