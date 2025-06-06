"""
OpenAI service - handles AI-powered search and HTS code generation
"""

import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.product import Product, HTSCodeSuggestion, SearchResult
from app.core.security import get_openai_client
from app.services.product_service import product_service


class OpenAIService:
    """Service for OpenAI-powered features"""
    
    def __init__(self):
        self.product_service = product_service
    
    async def enhanced_search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Use OpenAI to enhance search with natural language understanding"""
        try:
            client = get_openai_client()
            
            # Get all products for context
            products = self.product_service.get_all_products()
            
            # Create a simplified product list for AI processing
            product_summaries = []
            for product in products:
                summary = {
                    "id": product.id,
                    "title": product.title,
                    "product_code": product.product_code,
                    "joint_type": product.joint_type,
                    "body_design": product.body_design,
                    "size_range": product.specifications.size_range,
                    "keywords": product.metadata.keywords[:5]  # Limit keywords
                }
                product_summaries.append(summary)
            
            # Create prompt for AI search
            prompt = f"""
            Given this user search query: "{query}"
            
            And this list of products: {json.dumps(product_summaries[:20])}  # Limit for token management
            
            Please identify the most relevant products and return a JSON array of product IDs ranked by relevance.
            Consider natural language patterns, synonyms, and intent.
            
            Return only a JSON array of product IDs, like: ["product-id-1", "product-id-2"]
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",  # Use cheaper model for search
                messages=[
                    {"role": "system", "content": "You are a product search assistant. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            try:
                product_ids = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback to extracting IDs from response
                product_ids = self._extract_product_ids(ai_response, products)
            
            # Build results
            results = []
            products_dict = {p.id: p for p in products}
            
            for i, product_id in enumerate(product_ids[:limit]):
                if product_id in products_dict:
                    results.append(SearchResult(
                        product=products_dict[product_id],
                        score=100 - (i * 5),  # Decreasing score by rank
                        match_reason="AI-enhanced match"
                    ))
            
            return results
            
        except Exception as e:
            print(f"OpenAI search error: {e}")
            # Fallback to basic search
            from app.services.search_service import search_service
            results, _ = search_service.search_products(query, limit)
            return results
    
    async def generate_hts_codes(self, product: Product) -> List[HTSCodeSuggestion]:
        """Generate HTS code suggestions for a product"""
        try:
            client = get_openai_client()
            
            # Create detailed product description for HTS analysis
            product_info = f"""
            Product: {product.title}
            Product Code: {product.product_code}
            Material: {product.specifications.material.type} ({product.specifications.material.standard})
            Joint Type: {product.joint_type}
            Body Design: {product.body_design}
            Size Range: {product.specifications.size_range}
            Primary Standard: {product.primary_standard}
            Application: Water and sewer pipe fittings
            Construction: {product.construction.lining}
            Coatings: Interior - {product.construction.coating.interior}, Exterior - {product.construction.coating.exterior}
            """
            
            prompt = f"""
            Based on the following product specification, suggest the most appropriate HTS (Harmonized Tariff Schedule) codes:

            {product_info}

            Please provide 2-3 HTS code suggestions with confidence levels and reasoning. Consider that this is:
            - A pipe fitting made of ductile iron
            - Used for water/sewer applications  
            - Manufactured to AWWA standards
            - Industrial/commercial grade product

            Return your response as a JSON array with this format:
            [
                {{
                    "code": "HTS.CODE.HERE",
                    "description": "Description of what this code covers",
                    "confidence": 0.85,
                    "reasoning": "Why this code is appropriate"
                }}
            ]
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o",  # Use more capable model for HTS codes
                messages=[
                    {"role": "system", "content": "You are an expert in HTS codes for industrial products. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            # Parse response
            ai_response = response.choices[0].message.content.strip()
            try:
                suggestions_data = json.loads(ai_response)
                suggestions = [HTSCodeSuggestion(**item) for item in suggestions_data]
                return suggestions
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse HTS response: {e}")
                return self._fallback_hts_codes(product)
                
        except Exception as e:
            print(f"OpenAI HTS generation error: {e}")
            return self._fallback_hts_codes(product)
    
    def _extract_product_ids(self, response: str, products: List[Product]) -> List[str]:
        """Extract product IDs from AI response as fallback"""
        product_ids = []
        for product in products:
            if product.id in response:
                product_ids.append(product.id)
        return product_ids[:10]
    
    def _fallback_hts_codes(self, product: Product) -> List[HTSCodeSuggestion]:
        """Provide fallback HTS codes when AI fails"""
        # Basic fallback based on product type
        if "ductile iron" in product.specifications.material.type.lower():
            return [
                HTSCodeSuggestion(
                    code="7307.99.1000",
                    description="Other tube or pipe fittings of iron or steel",
                    confidence=0.7,
                    reasoning="General category for iron pipe fittings"
                ),
                HTSCodeSuggestion(
                    code="8481.80.9090",
                    description="Other valves and similar articles",
                    confidence=0.5,
                    reasoning="Alternative classification for pipe connection components"
                )
            ]
        return []


# Singleton instance
openai_service = OpenAIService()