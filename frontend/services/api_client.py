"""
API client for communicating with FastAPI backend
"""

import requests
import streamlit as st
from typing import Dict, List, Optional, Any
from config.settings import settings


class APIClient:
    """Client for FastAPI backend communication"""
    
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.timeout = settings.API_TIMEOUT
        self.session = requests.Session()
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and errors"""
        try:
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 404:
                return {"success": False, "error": "Resource not found"}
            elif response.status_code == 422:
                return {"success": False, "error": "Invalid request data"}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    # Products API
    def get_products(self, limit: Optional[int] = None, **filters) -> Dict[str, Any]:
        """Get all products with optional filtering"""
        params = {}
        if limit:
            params["limit"] = limit
        params.update(filters)
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/products/",
                params=params,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Get single product by ID"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/products/{product_id}",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_product_summary(self, product_id: str) -> Dict[str, Any]:
        """Get product summary"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/products/{product_id}/summary",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_filter_options(self) -> Dict[str, Any]:
        """Get available filter options"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/products/filters/options",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def compare_products(self, product_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple products"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/products/compare",
                json=product_ids,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Search API
    def search_products(self, query: str, enhanced: bool = False, limit: int = 10, **filters) -> Dict[str, Any]:
        """Search products"""
        params = {
            "q": query,
            "enhanced": enhanced,
            "limit": limit
        }
        params.update(filters)
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/search/",
                params=params,
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_search_suggestions(self, query: str, limit: int = 8) -> Dict[str, Any]:
        """Get search suggestions"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/search/suggestions",
                params={"q": query, "limit": limit},
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_similar_products(self, product_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get similar products"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/search/similar/{product_id}",
                params={"limit": limit},
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # HTS Codes API
    def get_hts_codes(self, product_id: str) -> Dict[str, Any]:
        """Get HTS codes for product"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/hts-codes/{product_id}",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def validate_hts_code(self, hts_code: str) -> Dict[str, Any]:
        """Validate HTS code format"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/hts-codes/validate/{hts_code}",
                timeout=self.timeout
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Health Check
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return self._handle_response(response)
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
@st.cache_resource
def get_api_client():
    """Get cached API client instance"""
    return APIClient()