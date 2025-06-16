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
    """Create a compact product card display"""
    st.markdown(f"""
    **{product['title']}**
    
    Code: {product['product_code']} | Joint: {product['joint_type']} | Design: {product['body_design']}
    
    Size Range: {product['specifications']['size_range']} | Standard: {product['primary_standard']}
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


def create_hts_display(suggestions: List[Dict[str, Any]], use_expanders: bool = True) -> None:
    """Display HTS code suggestions with optional expander usage"""
    if not suggestions:
        st.info("No HTS code suggestions available")
        return
    
    for i, suggestion in enumerate(suggestions, 1):
        confidence_level = "High" if suggestion['confidence'] > 0.8 else "Medium" if suggestion['confidence'] > 0.6 else "Low"
        
        if use_expanders:
            # Use expanders when not nested
            with st.expander(f"#{i} - {suggestion['code']} ({confidence_level} Confidence)"):
                st.write(f"**Description:** {suggestion['description']}")
                st.write(f"**Confidence:** {suggestion['confidence']:.1%}")
                st.write(f"**Reasoning:** {suggestion.get('reasoning', 'No reasoning provided')}")
        else:
            # Use containers when nested inside expanders
            with st.container(border=True):
                st.markdown(f"**#{i} - {suggestion['code']} ({confidence_level} Confidence)**")
                st.write(f"**Description:** {suggestion['description']}")
                st.write(f"**Confidence:** {suggestion['confidence']:.1%}")
                st.write(f"**Reasoning:** {suggestion.get('reasoning', 'No reasoning provided')}")


def create_hts_display_flat(suggestions: List[Dict[str, Any]]) -> None:
    """Display HTS code suggestions in flat format without expanders"""
    if not suggestions:
        st.info("No HTS code suggestions available")
        return
    
    for i, suggestion in enumerate(suggestions, 1):
        confidence_level = "High" if suggestion['confidence'] > 0.8 else "Medium" if suggestion['confidence'] > 0.6 else "Low"
        
        with st.container(border=True):
            st.markdown(f"**#{i} - {suggestion['code']} ({confidence_level} Confidence)**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Description:** {suggestion['description']}")
                st.write(f"**Confidence:** {suggestion['confidence']:.1%}")
            with col2:
                st.write(f"**Reasoning:** {suggestion.get('reasoning', 'No reasoning provided')}")


def search_result_display(result: Dict[str, Any]) -> None:
    """Display compact search result"""
    product = result['product']
    
    # Compact product display
    st.markdown(f"**{product['title']}**")
    st.caption(f"Code: {product['product_code']} | Joint: {product['joint_type']} | Design: {product['body_design']}")
    st.caption(f"Size Range: {product['specifications']['size_range']} | Standard: {product['primary_standard']}")


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