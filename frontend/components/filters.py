"""
Filter components for Streamlit frontend
"""

import streamlit as st
from typing import Dict, Any, Optional
from services.api_client import get_api_client
from utils.helpers import display_api_error


def advanced_filters_sidebar():
    """Advanced filtering sidebar"""
    st.sidebar.markdown("##Advanced Filters")
    
    api_client = get_api_client()
    filter_options = api_client.get_filter_options()
    
    filters = {}
    
    if filter_options["success"]:
        data = filter_options["data"]
        
        # Product specifications
        st.sidebar.markdown("### Product Specifications")
        
        # Product codes
        if data.get("product_codes"):
            selected_codes = st.sidebar.multiselect(
                "Product Codes",
                options=data["product_codes"],
                help="Filter by specific product codes"
            )
            if selected_codes:
                filters["product_codes"] = selected_codes
        
        # Joint types
        if data.get("joint_types"):
            selected_joints = st.sidebar.multiselect(
                "Joint Types",
                options=data["joint_types"],
                help="Filter by joint connection type"
            )
            if selected_joints:
                filters["joint_types"] = selected_joints
        
        # Body designs
        if data.get("body_designs"):
            selected_designs = st.sidebar.multiselect(
                "Body Designs",
                options=data["body_designs"],
                help="Filter by body design type"
            )
            if selected_designs:
                filters["body_designs"] = selected_designs
        
        # Technical specifications
        st.sidebar.markdown("### Technical Specifications")
        
        # Pressure range
        pressure_range = st.sidebar.slider(
            "Pressure Range (PSI)",
            min_value=0,
            max_value=500,
            value=(0, 500),
            step=25,
            help="Filter by pressure rating range"
        )
        if pressure_range != (0, 500):
            filters["min_pressure"] = pressure_range[0]
            filters["max_pressure"] = pressure_range[1]
        
        # Size options
        st.sidebar.markdown("### Size Specifications")
        size_input = st.sidebar.text_input(
            "Size Filter",
            placeholder="e.g., 6\", 24\", 2\" - 48\"",
            help="Filter by size specifications"
        )
        if size_input:
            filters["size"] = size_input
        
        # Certifications
        st.sidebar.markdown("### Certifications")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            nsf61_only = st.checkbox("NSF 61 Only")
            ul_listed_only = st.checkbox("UL Listed Only")
        
        with col2:
            fm_approved_only = st.checkbox("FM Approved Only")
            nsf372_only = st.checkbox("NSF 372 Only")
        
        if any([nsf61_only, ul_listed_only, fm_approved_only, nsf372_only]):
            filters["certifications"] = {
                "nsf61": nsf61_only,
                "ul_listed": ul_listed_only,
                "fm_approved": fm_approved_only,
                "nsf372": nsf372_only
            }
        
        # Clear filters
        if st.sidebar.button("Clear All Filters"):
            filters = {}
            st.rerun()
        
        # Filter summary
        if filters:
            st.sidebar.markdown("### Applied Filters")
            filter_count = len([f for f in filters.values() if f])
            st.sidebar.success(f"{filter_count} filters active")
    
    else:
        st.sidebar.error("Failed to load filter options")
        display_api_error(filter_options["error"])
    
    return filters


def quick_filters():
    """Quick filter buttons for common searches"""
    st.markdown("### Quick Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Mechanical Joint", use_container_width=True):
            return {"joint_type": "Mechanical Joint"}
    
    with col2:
        if st.button("Push-On Joint", use_container_width=True):
            return {"joint_type": "Push-On Joint"}
    
    with col3:
        if st.button("Flanged Joint", use_container_width=True):
            return {"joint_type": "Flanged Joint"}
    
    with col4:
        if st.button("High Pressure", use_container_width=True):
            return {"min_pressure": 300}
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Compact Design", use_container_width=True):
            return {"body_design": "Compact/Short Body"}
    
    with col2:
        if st.button("Full Body", use_container_width=True):
            return {"body_design": "Full Body"}
    
    with col3:
        if st.button("C153 Series", use_container_width=True):
            return {"product_code": "C153"}
    
    with col4:
        if st.button("C110 Series", use_container_width=True):
            return {"product_code": "C110"}
    
    return {}


def filter_results_display(filters: Dict[str, Any], total_results: int):
    """Display active filters and results count"""
    if not filters:
        return
    
    st.markdown("###Active Filters")
    
    filter_cols = st.columns(min(len(filters), 4))
    
    for i, (key, value) in enumerate(filters.items()):
        with filter_cols[i % 4]:
            if isinstance(value, list):
                st.info(f"**{key.replace('_', ' ').title()}:** {', '.join(value)}")
            elif isinstance(value, dict):
                st.info(f"**{key.replace('_', ' ').title()}:** Multiple")
            else:
                st.info(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.success(f"Found {total_results} products matching your filters")