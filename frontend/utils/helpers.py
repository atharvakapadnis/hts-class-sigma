"""
Utility functions for Streamlit frontend
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional


def display_api_error(error_msg: str):
    """Display API error message"""
    st.error(f"API Error: {error_msg}")
    
    if "Connection" in error_msg or "timeout" in error_msg.lower():
        st.info("Make sure the backend server is running on http://localhost:8000")


def format_pressure_ratings(pressure_ratings: List[Dict]) -> str:
    """Format pressure ratings for display"""
    if not pressure_ratings:
        return "N/A"
    
    ratings = []
    for rating in pressure_ratings:
        ratings.append(f"{rating['sizes']}: {rating['psi']} PSI")
    
    return " | ".join(ratings)


def format_deflection_limits(deflection_limits: List[Dict]) -> str:
    """Format deflection limits for display"""
    if not deflection_limits:
        return "N/A"
    
    limits = []
    for limit in deflection_limits:
        limit_str = f"{limit['sizes']}: {limit['max_degrees']}°"
        if limit.get('note'):
            limit_str += f" ({limit['note']})"
        limits.append(limit_str)
    
    return " | ".join(limits)


def create_product_card(product: Dict[str, Any]) -> None:
    """Create a product card display"""
    with st.container():
        st.markdown(f"""
        ### {product['title']}
        
        **Code:** {product['product_code']} | **Joint:** {product['joint_type']} | **Design:** {product['body_design']}
        
        **Size Range:** {product['specifications']['size_range']} | **Standard:** {product['primary_standard']}
        """)


def create_specifications_table(product: Dict[str, Any]) -> pd.DataFrame:
    """Create specifications table for product"""
    specs = product['specifications']
    
    data = {
        'Specification': [
            'Size Range',
            'Material Type',
            'Material Standard',
            'Pressure Ratings',
            'Deflection Limits',
            'Joint Type',
            'Body Design',
            'Primary Standard'
        ],
        'Value': [
            specs['size_range'],
            specs['material']['type'],
            specs['material']['standard'],
            format_pressure_ratings(specs['pressure_ratings']),
            format_deflection_limits(specs['deflection_limits']),
            product['joint_type'],
            product['body_design'],
            product['primary_standard']
        ]
    }
    
    return pd.DataFrame(data)


def create_hts_display(suggestions: List[Dict[str, Any]]) -> None:
    """Display HTS code suggestions"""
    if not suggestions:
        st.info("No HTS code suggestions available")
        return
    
    for i, suggestion in enumerate(suggestions, 1):
        confidence_level = "High" if suggestion['confidence'] > 0.8 else "Medium" if suggestion['confidence'] > 0.6 else "Low"
        
        with st.expander(f"#{i} - {suggestion['code']} ({confidence_level} Confidence)"):
            st.write(f"**Description:** {suggestion['description']}")
            st.write(f"**Confidence:** {suggestion['confidence']:.1%}")
            st.write(f"**Reasoning:** {suggestion.get('reasoning', 'No reasoning provided')}")


def search_result_display(result: Dict[str, Any]) -> None:
    """Display search result with score - FIXED VERSION"""
    product = result['product']
    score = result.get('score', 0)
    match_reason = result.get('match_reason', 'No match reason')
    
    # Display product card
    create_product_card(product)
    
    # Display match information below the card
    if score:
        st.caption(f"**Match Score:** {score:.0f} | **Reason:** {match_reason}")


def show_loading():
    """Show loading spinner"""
    return st.spinner("Loading...")


def pagination_controls(total_items: int, items_per_page: int, current_page: int) -> int:
    """Create pagination controls"""
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    if total_pages <= 1:
        return current_page
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("First", disabled=current_page <= 1):
            return 1
    
    with col2:
        if st.button("Prev", disabled=current_page <= 1):
            return current_page - 1
    
    with col3:
        st.write(f"Page {current_page} of {total_pages} ({total_items} items)")
    
    with col4:
        if st.button("Next", disabled=current_page >= total_pages):
            return current_page + 1
    
    with col5:
        if st.button("Last", disabled=current_page >= total_pages):
            return total_pages
    
    return current_page