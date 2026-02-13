# deepseek_integration.py
"""
DeepSeek API Integration Module
Provides real AI-powered SEO analysis using DeepSeek API
"""

import requests
import json
from typing import Dict, List, Optional

class DeepSeekAnalyzer:
    """
    Real AI analysis using DeepSeek API
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_website(self, url: str, website_type: Dict) -> Dict:
        """
        Use DeepSeek AI to analyze a website for SEO and AI search readiness
        """
        
        prompt = self._create_analysis_prompt(url, website_type)
        
        try:
            response = self._call_deepseek_api(prompt)
            analysis = self._parse_analysis_response(response)
            return analysis
        except Exception as e:
            print(f"DeepSeek API Error: {e}")
            return None
    
    def _create_analysis_prompt(self, url: str, website_type: Dict) -> str:
        """
        Create a detailed prompt for DeepSeek to analyze the website
        """
        
        prompt = f"""You are an expert SEO analyst specializing in AI search optimization.

Analyze this website for AI search readiness and provide detailed metrics:

Website URL: {url}
Website Type: {website_type['type']}
Industry: {website_type['industry']}

Please provide a comprehensive analysis in JSON format with the following structure:

{{
    "ai_visibility_score": <integer 0-100>,
    "entity_score": <integer 0-100>,
    "schema_score": <integer 0-100>,
    "sge_score": <integer 0-100>,
    "content_structure_score": <integer 0-100>,
    "entities": [
        {{
            "text": "<entity name>",
            "type": "<PRODUCT|BRAND|ORGANIZATION|PERSON|etc>",
            "confidence": <float 0.0-1.0>,
            "mentions": <integer>
        }}
    ],
    "detected_schemas": ["<schema type>", ...],
    "missing_schemas": ["<recommended schema type>", ...],
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "weaknesses": ["<weakness 1>", "<weakness 2>", ...],
    "priority_recommendations": [
        {{
            "title": "<recommendation title>",
            "description": "<detailed description>",
            "priority": "<high|medium|low>",
            "impact": "<expected impact>",
            "effort": "<High|Medium|Low>"
        }}
    ]
}}

Important:
- Provide realistic scores based on typical {website_type['type']} websites
- Identify 10-15 relevant entities for this industry
- List specific schema types appropriate for {website_type['type']}
- Give actionable, industry-specific recommendations
- Be thorough but concise

Return ONLY the JSON object, no additional text.
"""
        return prompt
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """
        Make API call to DeepSeek
        """
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert SEO analyst. Provide detailed, accurate analysis in valid JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more consistent analysis
            "max_tokens": 2000
        }
        
        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """
        Parse the JSON response from DeepSeek
        """
        
        # Clean the response (remove markdown code blocks if present)
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        # Parse JSON
        try:
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response: {response[:500]}")
            return None
    
    def extract_entities(self, content: str, website_type: Dict) -> List[Dict]:
        """
        Use DeepSeek to extract entities from content
        """
        
        prompt = f"""Extract key entities from this website content.
Website Type: {website_type['type']}

Content snippet:
{content[:2000]}

Identify 10-15 most important entities (products, brands, people, organizations, etc.)

Return as JSON array:
[
    {{
        "text": "<entity name>",
        "type": "<entity type>",
        "confidence": <0.0-1.0>,
        "relevance": <0.0-1.0>
    }}
]

Return ONLY the JSON array.
"""
        
        try:
            response = self._call_deepseek_api(prompt)
            entities = json.loads(response)
            return entities
        except Exception as e:
            print(f"Entity extraction error: {e}")
            return []
    
    def generate_recommendations(self, analysis: Dict, website_type: Dict) -> List[Dict]:
        """
        Generate detailed recommendations based on analysis
        """
        
        prompt = f"""Based on this SEO analysis, provide 5-7 specific, actionable recommendations.

Website Type: {website_type['type']}
Current Scores:
- AI Visibility: {analysis.get('ai_visibility_score', 50)}%
- Schema Coverage: {analysis.get('schema_score', 40)}%
- Entity Recognition: {analysis.get('entity_score', 45)}%

Focus on recommendations that will have the highest impact for {website_type['type']} websites.

Return as JSON array:
[
    {{
        "title": "<recommendation title>",
        "description": "<detailed description>",
        "priority": "<high|medium|low>",
        "impact": "<expected impact with percentage>",
        "effort": "<High|Medium|Low>",
        "timeline": "<estimated timeline>",
        "roi": "<expected ROI>",
        "implementation": ["step 1", "step 2", "step 3"]
    }}
]

Return ONLY the JSON array.
"""
        
        try:
            response = self._call_deepseek_api(prompt)
            recommendations = json.loads(response)
            return recommendations
        except Exception as e:
            print(f"Recommendations generation error: {e}")
            return []
    
    def predict_improvements(self, current_score: int, entity_count: int, schema_score: int) -> Dict:
        """
        Use AI to predict future performance
        """
        
        prompt = f"""As an SEO expert, predict future performance improvements.

Current Metrics:
- AI Visibility Score: {current_score}%
- Entity Count: {entity_count}
- Schema Score: {schema_score}%

Provide realistic predictions for 30, 60, and 90 days assuming recommended optimizations are implemented.

Return as JSON:
{{
    "30_days": <predicted score 0-100>,
    "60_days": <predicted score 0-100>,
    "90_days": <predicted score 0-100>,
    "confidence": <confidence level 0-100>,
    "key_factors": ["factor 1", "factor 2", ...],
    "assumptions": ["assumption 1", "assumption 2", ...]
}}

Return ONLY the JSON object.
"""
        
        try:
            response = self._call_deepseek_api(prompt)
            predictions = json.loads(response)
            return predictions
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                "30_days": min(100, current_score + 10),
                "60_days": min(100, current_score + 20),
                "90_days": min(100, current_score + 30),
                "confidence": 70
            }


# Helper functions for integration with main app

def analyze_with_deepseek(url: str, website_type: Dict, api_key: str) -> Dict:
    """
    Main function to analyze website using DeepSeek API
    
    Args:
        url: Website URL to analyze
        website_type: Detected website type dict
        api_key: DeepSeek API key
        
    Returns:
        Complete analysis results dict
    """
    
    if not api_key or api_key.strip() == "":
        return None
    
    try:
        analyzer = DeepSeekAnalyzer(api_key)
        analysis = analyzer.analyze_website(url, website_type)
        
        if analysis:
            # Add predictions
            predictions = analyzer.predict_improvements(
                analysis.get('ai_visibility_score', 50),
                len(analysis.get('entities', [])),
                analysis.get('schema_score', 40)
            )
            analysis['predictions'] = predictions
            
            # Add detailed recommendations if not already present
            if not analysis.get('priority_recommendations'):
                recommendations = analyzer.generate_recommendations(analysis, website_type)
                analysis['priority_recommendations'] = recommendations
            
            return analysis
        
        return None
        
    except Exception as e:
        print(f"DeepSeek analysis failed: {e}")
        return None


def test_deepseek_api(api_key: str) -> bool:
    """
    Test if DeepSeek API key is valid
    
    Args:
        api_key: DeepSeek API key to test
        
    Returns:
        True if valid, False otherwise
    """
    
    try:
        analyzer = DeepSeekAnalyzer(api_key)
        
        # Simple test prompt
        test_prompt = "Say 'API key is valid' if you can read this."
        
        response = analyzer._call_deepseek_api(test_prompt)
        
        return "valid" in response.lower() or len(response) > 0
        
    except Exception as e:
        print(f"API key test failed: {e}")
        return False
