"""
Utility functions and helpers
"""

import re
from typing import Any, Dict, List, Optional


def clean_query(query: str) -> str:
    """Clean and normalize search query"""
    # Remove extra whitespace
    query = re.sub(r'\s+', ' ', query.strip())
    
    # Remove special characters except quotes and hyphens
    query = re.sub(r'[^\w\s\-"\']', '', query)
    
    return query


def extract_size_from_query(query: str) -> Optional[str]:
    """Extract size specification from query"""
    # Look for patterns like 6", 12", 24"
    size_match = re.search(r'(\d+)["\']', query)
    if size_match:
        return size_match.group(1) + '"'
    
    # Look for patterns like 6 inch, 12 inches
    inch_match = re.search(r'(\d+)\s*inch', query, re.IGNORECASE)
    if inch_match:
        return inch_match.group(1) + '"'
    
    return None


def extract_pressure_from_query(query: str) -> Optional[int]:
    """Extract pressure specification from query"""
    # Look for patterns like 350 PSI, 250PSI
    pressure_match = re.search(r'(\d+)\s*psi', query, re.IGNORECASE)
    if pressure_match:
        return int(pressure_match.group(1))
    
    return None


def format_product_summary(product) -> str:
    """Create a brief product summary for display"""
    pressure_ranges = [f"{pr.sizes}: {pr.psi} PSI" for pr in product.specifications.pressure_ratings]
    pressure_text = ", ".join(pressure_ranges)
    
    return f"{product.title} | {product.specifications.size_range} | {pressure_text} | {product.joint_type}"


def validate_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean filter parameters"""
    valid_filters = {}
    
    if filters is None:
        return valid_filters
    
    # Validate joint_type
    if "joint_type" in filters and isinstance(filters["joint_type"], str):
        valid_filters["joint_type"] = filters["joint_type"].strip()
    
    # Validate product_code
    if "product_code" in filters and isinstance(filters["product_code"], str):
        valid_filters["product_code"] = filters["product_code"].strip().upper()
    
    # Validate body_design
    if "body_design" in filters and isinstance(filters["body_design"], str):
        valid_filters["body_design"] = filters["body_design"].strip()
    
    # Validate pressure ranges
    if "min_pressure" in filters:
        try:
            valid_filters["min_pressure"] = int(filters["min_pressure"])
        except (ValueError, TypeError):
            pass
    
    if "max_pressure" in filters:
        try:
            valid_filters["max_pressure"] = int(filters["max_pressure"])
        except (ValueError, TypeError):
            pass
    
    # Validate size
    if "size" in filters and isinstance(filters["size"], str):
        valid_filters["size"] = filters["size"].strip()
    
    return valid_filters


def generate_search_suggestions(query: str, products: List) -> List[str]:
    """Generate search suggestions based on available products"""
    suggestions = set()
    query_lower = query.lower()
    
    # Add matching product codes
    for product in products:
        if product.product_code.lower().startswith(query_lower):
            suggestions.add(product.product_code)
    
    # Add matching joint types
    for product in products:
        if product.joint_type.lower().startswith(query_lower):
            suggestions.add(product.joint_type)
    
    # Add matching keywords
    for product in products:
        for keyword in product.metadata.keywords:
            if keyword.lower().startswith(query_lower):
                suggestions.add(keyword)
    
    return sorted(list(suggestions))[:8]


def calculate_search_metrics(results: List, total_available: int) -> Dict[str, Any]:
    """Calculate search performance metrics"""
    return {
        "total_results": len(results),
        "total_available": total_available,
        "coverage_percentage": round((len(results) / total_available) * 100, 2) if total_available > 0 else 0,
        "average_score": round(sum(r.score for r in results if r.score) / len(results), 2) if results else 0
    }
