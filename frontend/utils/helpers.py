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
        <div style="
            background-color: #1e1e1e;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ff4b4b;
            margin-bottom: 15px;
        ">
            <h3 style="color: #ffffff; margin-top: 0;">{product['title']}</h3>
            <p style="color: #cccccc;">
                <strong>Code:</strong> {product['product_code']} | 
                <strong>Joint:</strong> {product['joint_type']} | 
                <strong>Design:</strong> {product['body_design']}
            </p>
            <p style="color: #cccccc;">
                <strong>Size Range:</strong> {product['specifications']['size_range']} | 
                <strong>Standard:</strong> {product['primary_standard']}
            </p>
        </div>
        """, unsafe_allow_html=True)


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
        confidence_color = "#00ff00" if suggestion['confidence'] > 0.8 else "#ffff00" if suggestion['confidence'] > 0.6 else "#ff8800"
        
        st.markdown(f"""
        <div style="
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            border-left: 3px solid {confidence_color};
        ">
            <h4 style="color: #ffffff; margin-top: 0;">#{i} - {suggestion['code']}</h4>
            <p style="color: #cccccc;">{suggestion['description']}</p>
            <p style="color: {confidence_color};">
                <strong>Confidence:</strong> {suggestion['confidence']:.1%}
            </p>
            <p style="color: #aaaaaa; font-size: 0.9em;">
                <strong>Reasoning:</strong> {suggestion.get('reasoning', 'No reasoning provided')}
            </p>
        </div>
        """, unsafe_allow_html=True)


def search_result_display(result: Dict[str, Any]) -> None:
    """Display search result with score"""
    product = result['product']
    score = result.get('score', 0)
    match_reason = result.get('match_reason', 'No match reason')
    
    score_color = "#00ff00" if score > 80 else "#ffff00" if score > 60 else "#ff8800"
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        create_product_card(product)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 20px;">
            <div style="
                background-color: {score_color};
                color: #000000;
                padding: 10px;
                border-radius: 50%;
                font-weight: bold;
                font-size: 1.2em;
                margin-bottom: 10px;
            ">
                {score:.0f}
            </div>
            <p style="color: #cccccc; font-size: 0.8em;">
                {match_reason}
            </p>
        </div>
        """, unsafe_allow_html=True)


def apply_dark_theme():
    """Apply dark theme CSS"""
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    .stSidebar {
        background-color: #1e1e1e;
    }
    
    .stSelectbox > div > div {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .stButton > button {
        background-color: #ff4b4b;
        color: #ffffff;
        border: none;
        border-radius: 5px;
    }
    
    .stButton > button:hover {
        background-color: #ff6b6b;
    }
    
    .stDataFrame {
        background-color: #1e1e1e;
    }
    
    .stExpander {
        background-color: #1e1e1e;
        border: 1px solid #404040;
    }
    
    .stAlert {
        background-color: #2d2d2d;
        border: 1px solid #404040;
    }
    
    h1, h2, h3 {
        color: #ffffff;
    }
    
    .highlight {
        background-color: #ff4b4b;
        color: #ffffff;
        padding: 2px 6px;
        border-radius: 3px;
    }
    </style>
    """, unsafe_allow_html=True)


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