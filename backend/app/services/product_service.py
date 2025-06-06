"""
Product data service - handles loading and filtering product data
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path

from app.models.product import Product, ProductCatalog
from app.core.config import settings


class ProductService:
    """Service for managing product data"""
    
    def __init__(self):
        self._products: Optional[List[Product]] = None
        self._products_by_id: Optional[Dict[str, Product]] = None
        self.data_file = Path(settings.DATA_DIR) / settings.PRODUCTS_FILE
    
    def _load_products(self) -> None:
        """Load products from JSON file"""
        if self._products is not None:
            return
            
        try:
            if not self.data_file.exists():
                raise FileNotFoundError(f"Product data file not found: {self.data_file}")
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            catalog = ProductCatalog(**data['product_catalog'])
            self._products = catalog.products
            self._products_by_id = {product.id: product for product in self._products}
            
        except Exception as e:
            raise RuntimeError(f"Failed to load product data: {str(e)}")
    
    def get_all_products(self) -> List[Product]:
        """Get all products"""
        self._load_products()
        return self._products.copy()
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a single product by ID"""
        self._load_products()
        return self._products_by_id.get(product_id)
    
    def filter_products(self, filters: Dict[str, Any]) -> List[Product]:
        """Filter products based on criteria"""
        self._load_products()
        filtered_products = self._products.copy()
        
        for key, value in filters.items():
            if key == "joint_type":
                filtered_products = [
                    p for p in filtered_products 
                    if value.lower() in p.joint_type.lower()
                ]
            elif key == "product_code":
                filtered_products = [
                    p for p in filtered_products 
                    if value.upper() in p.product_code.upper()
                ]
            elif key == "body_design":
                filtered_products = [
                    p for p in filtered_products 
                    if value.lower() in p.body_design.lower()
                ]
            elif key == "min_pressure":
                filtered_products = [
                    p for p in filtered_products 
                    if any(rating.psi >= value for rating in p.specifications.pressure_ratings)
                ]
            elif key == "max_pressure":
                filtered_products = [
                    p for p in filtered_products 
                    if any(rating.psi <= value for rating in p.specifications.pressure_ratings)
                ]
            elif key == "size":
                # Simple size filtering - could be enhanced
                filtered_products = [
                    p for p in filtered_products 
                    if value in p.specifications.size_range
                ]
        
        return filtered_products
    
    def get_product_codes(self) -> List[str]:
        """Get list of unique product codes"""
        self._load_products()
        return list(set(product.product_code for product in self._products))
    
    def get_joint_types(self) -> List[str]:
        """Get list of unique joint types"""
        self._load_products()
        return list(set(product.joint_type for product in self._products))
    
    def get_body_designs(self) -> List[str]:
        """Get list of unique body designs"""
        self._load_products()
        return list(set(product.body_design for product in self._products))


# Singleton instance
product_service = ProductService()