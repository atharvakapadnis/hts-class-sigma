"""
Search components for Streamlit frontend
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from services.api_client import get_api_client
from utils.helpers import display_api_error, search_result_display, show_loading

def search_interface():
    """Main search interface"""
    st.title("Product Search")

    # Search input
    col1, col2 = st.columns([3,1])

    with col1:
        search_query = st.text_input(
            "Search Products....",
            placeholder = "e.g., mechanical joint, C153, high pressure fittings",
            help="Search by product name, code, joint type, or specifications"
        )

    with col2: 
        enhanced_search = st.checkbox(
            "AI Enhanced",
            value = False,
            help = "Use AI for natural language search"
        )

    # Search filters in sidebar
    with st.sidebar:
        st.header("🔧 Search Filters")
        
        # Get filter options
        api_client = get_api_client()
        filter_options = api_client.get_filter_options()
        
        filters = {}
        
        if filter_options["success"]:
            data = filter_options["data"]
            
            # Product Code filter
            if data.get("product_codes"):
                selected_code = st.selectbox(
                    "Product Code",
                    ["All"] + data["product_codes"]
                )
                if selected_code != "All":
                    filters["product_code"] = selected_code
            
            # Joint Type filter
            if data.get("joint_types"):
                selected_joint = st.selectbox(
                    "Joint Type",
                    ["All"] + data["joint_types"]
                )
                if selected_joint != "All":
                    filters["joint_type"] = selected_joint
            
            # Body Design filter
            if data.get("body_designs"):
                selected_design = st.selectbox(
                    "Body Design",
                    ["All"] + data["body_designs"]
                )
                if selected_design != "All":
                    filters["body_design"] = selected_design
            
            # Pressure filters
            st.subheader("Pressure Range (PSI)")
            col1, col2 = st.columns(2)
            with col1:
                min_pressure = st.number_input("Min PSI", min_value=0, value=0)
                if min_pressure > 0:
                    filters["min_pressure"] = min_pressure
            
            with col2:
                max_pressure = st.number_input("Max PSI", min_value=0, value=500)
                if max_pressure < 500:
                    filters["max_pressure"] = max_pressure
            
            # Results limit
            results_limit = st.slider("Max Results", min_value=5, max_value=50, value=10)
    
    # Perform search
    if search_query:
        with show_loading():
            search_result = api_client.search_products(
                query=search_query,
                enhanced=enhanced_search,
                limit=results_limit,
                **filters
            )
        
        if search_result["success"]:
            data = search_result["data"]
            
            # Display search info
            st.markdown(f"""
            <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: #ffffff; margin-top: 0;">Search Results</h3>
                <p style="color: #cccccc;">
                    Found <span class="highlight">{data['total_results']}</span> products 
                    for "<span class="highlight">{data['query']}</span>"
                    in {data['search_time_ms']}ms
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display results
            if data["results"]:
                for result in data["results"]:
                    search_result_display(result)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns([1, 1, 4])
                    with col1:
                        if st.button(f"View Details", key=f"view_{result['product']['id']}"):
                            st.session_state.selected_product = result['product']['id']
                            st.rerun()
                    
                    with col2:
                        if st.button(f"HTS Codes", key=f"hts_{result['product']['id']}"):
                            st.session_state.show_hts = result['product']['id']
                            st.rerun()
                    
                    st.divider()
            else:
                st.info("No products found matching your search criteria.")
        else:
            display_api_error(search_result["error"])
    
    else:
        # Show suggestions or popular searches
        st.info("💡 Try searching for: mechanical joint, C153, push-on, flanged, or high pressure")


def search_suggestions_widget():
    """Search suggestions widget"""
    if "search_input" in st.session_state and len(st.session_state.search_input) >= 2:
        api_client = get_api_client()
        suggestions = api_client.get_search_suggestions(st.session_state.search_input)
        
        if suggestions["success"] and suggestions["data"]["suggestions"]:
            st.write("💡 Suggestions:")
            for suggestion in suggestions["data"]["suggestions"][:5]:
                if st.button(suggestion, key=f"suggestion_{suggestion}"):
                    st.session_state.search_input = suggestion
                    st.rerun()