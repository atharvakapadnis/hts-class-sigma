"""
Search service - handles product search functionality
"""

import re
import time
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

from app.models.product import Product, SearchResult
from app.services.product_service import product_service


class SearchService:
    """Service for searching products"""
    
    def __init__(self):
        self.product_service = product_service
    
    def search_products(self, query: str, limit: int = 10, filters: Dict[str, Any] = None) -> Tuple[List[SearchResult], int]:
        """
        Search products using keyword matching and similarity scoring
        Returns (results, search_time_ms)
        """
        start_time = time.time()
        
        # Get all products or filtered subset
        if filters:
            products = self.product_service.filter_products(filters)
        else:
            products = self.product_service.get_all_products()
        
        # Perform search
        scored_results = []
        query_lower = query.lower().strip()
        
        for product in products:
            score, match_reason = self._calculate_relevance_score(product, query_lower)
            if score > 0:
                scored_results.append(SearchResult(
                    product=product,
                    score=score,
                    match_reason=match_reason
                ))
        
        # Sort by score (descending) and limit results
        scored_results.sort(key=lambda x: x.score, reverse=True)
        limited_results = scored_results[:limit]
        
        search_time_ms = int((time.time() - start_time) * 1000)
        
        return limited_results, search_time_ms
    
    def _calculate_relevance_score(self, product: Product, query: str) -> Tuple[float, str]:
        """Calculate relevance score for a product against a query"""
        score = 0.0
        match_reasons = []
        
        # Exact title match (highest priority)
        if query in product.title.lower():
            score += 100
            match_reasons.append("title match")
        
        # Product code match (high priority)
        if query in product.product_code.lower():
            score += 90
            match_reasons.append("product code match")
        
        # Joint type match
        if query in product.joint_type.lower():
            score += 80
            match_reasons.append("joint type match")
        
        # Body design match
        if query in product.body_design.lower():
            score += 70
            match_reasons.append("body design match")
        
        # Keywords match
        for keyword in product.metadata.keywords:
            if query in keyword.lower():
                score += 60
                match_reasons.append("keyword match")
                break
        
        # Search text match
        if query in product.metadata.search_text.lower():
            score += 50
            match_reasons.append("description match")
        
        # Standard match
        if query in product.primary_standard.lower():
            score += 40
            match_reasons.append("standard match")
        
        # Fuzzy matching for similar terms
        similarity = self._fuzzy_match(query, product.title.lower())
        if similarity > 0.6:
            score += similarity * 30
            match_reasons.append("fuzzy match")
        
        # Special handling for common terms
        score += self._handle_special_terms(query, product)
        
        match_reason = ", ".join(match_reasons) if match_reasons else "no match"
        
        return score, match_reason
    
    def _fuzzy_match(self, query: str, text: str) -> float:
        """Calculate fuzzy string similarity"""
        return SequenceMatcher(None, query, text).ratio()
    
    def _handle_special_terms(self, query: str, product: Product) -> float:
        """Handle special search terms and synonyms"""
        bonus_score = 0.0
        
        # Size-related queries
        if re.search(r'\d+["\']', query):  # Matches patterns like 6", 12"
            size_match = re.search(r'(\d+)["\']', query)
            if size_match:
                size = size_match.group(1)
                if size in product.specifications.size_range:
                    bonus_score += 25
        
        # Pressure-related queries
        pressure_terms = ['pressure', 'psi', 'high pressure', 'low pressure']
        if any(term in query for term in pressure_terms):
            bonus_score += 15
        
        # Material-related queries
        material_terms = ['ductile iron', 'iron', 'metal']
        if any(term in query for term in material_terms):
            if any(term in product.specifications.material.type.lower() for term in material_terms):
                bonus_score += 20
        
        # Application-related queries
        app_terms = ['water', 'sewer', 'pipe', 'fitting']
        if any(term in query for term in app_terms):
            if any(term in product.metadata.search_text.lower() for term in app_terms):
                bonus_score += 15
        
        return bonus_score
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = set()
        partial_lower = partial_query.lower()
        
        products = self.product_service.get_all_products()
        
        for product in products:
            # Add matching keywords
            for keyword in product.metadata.keywords:
                if keyword.lower().startswith(partial_lower):
                    suggestions.add(keyword)
            
            # Add product codes
            if product.product_code.lower().startswith(partial_lower):
                suggestions.add(product.product_code)
            
            # Add joint types
            if product.joint_type.lower().startswith(partial_lower):
                suggestions.add(product.joint_type)
        
        return sorted(list(suggestions))[:10]


# Singleton instance
search_service = SearchService()