"""
Search components for Streamlit frontend
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from services.api_client import get_api_client
from utils.helpers import display_api_error, search_result_display, show_loading


def tabbed_search_page():
    """Tabbed search interface with Basic and AI options"""
    st.title("Product Search")
    
    # Create tabs with cleaner styling
    tab1, tab2 = st.tabs(["Basic Search", "AI Search"])
    
    with tab1:
        basic_search_tab()
    
    with tab2:
        ai_search_tab()


def basic_search_tab():
    """Basic keyword search tab"""
    st.markdown("Search using keywords, product codes, and filters")
    
    # Main search section
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search products",
            placeholder="Enter product code, joint type, material, etc.",
            key="basic_search_input",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True, key="basic_search_btn")
    
    with col3:
        clear_button = st.button("Clear", use_container_width=True, key="basic_clear")
        if clear_button:
            st.rerun()
    
    # Compact controls row
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        results_limit = st.selectbox("Results", [10, 15, 25, 50], index=1, key="basic_limit")
    
    with col2:
        if st.button("Advanced Filters", use_container_width=True):
            st.session_state.show_filters = not st.session_state.get("show_filters", False)
    
    with col3:
        if search_query and len(search_query) >= 2:
            if st.button("Show Suggestions", use_container_width=True):
                st.session_state.show_suggestions = not st.session_state.get("show_suggestions", False)
    
    # Advanced filters in collapsible section
    if st.session_state.get("show_filters", False):
        with st.expander("Advanced Filters", expanded=True):
            filter_options = get_filter_options()
            filters = create_filter_interface(filter_options, key_prefix="basic")
    else:
        filters = {}
    
    # Compact suggestions display
    if st.session_state.get("show_suggestions", False) and search_query and len(search_query) >= 2:
        show_compact_suggestions(search_query, "basic")
    
    # Search execution
    if search_button and search_query:
        perform_basic_search(search_query, filters, results_limit)
    elif search_button and not search_query:
        st.warning("Please enter a search query")
    
    # Popular searches when no query
    if not search_query:
        show_popular_searches()


def ai_search_tab():
    """AI-powered natural language search tab"""
    st.markdown("Ask questions about products in natural language")
    
    # Main search section
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        ai_query = st.text_area(
            "Ask your question",
            value=st.session_state.get("ai_query_tab", ""),
            placeholder="What products have push-on fittings for 6 inch pipes?",
            height=80,
            key="ai_search_input",
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("Ask AI", type="primary", use_container_width=True, key="ai_search_btn")
        if st.button("Examples", use_container_width=True):
            st.session_state.show_examples = not st.session_state.get("show_examples", False)
    
    with col3:
        results_limit = st.selectbox("Results", [5, 10, 15, 20], index=1, key="ai_limit")
        clear_button = st.button("Clear", use_container_width=True, key="ai_clear")
        if clear_button:
            if "ai_query_tab" in st.session_state:
                del st.session_state.ai_query_tab
            st.rerun()
    
    # Compact examples display
    if st.session_state.get("show_examples", False):
        show_compact_examples()
    
    # Search execution
    if search_button and ai_query:
        perform_ai_search(ai_query, results_limit)
    elif search_button and not ai_query:
        st.warning("Please enter your question")
    
    # AI tips when no query
    if not ai_query:
        st.info("Ask natural language questions like: 'What products work with 12 inch pipes?' or 'Show me high pressure fittings'")


def show_compact_suggestions(query: str, search_type: str):
    """Show search suggestions in compact format"""
    api_client = get_api_client()
    suggestions = api_client.get_search_suggestions(query, limit=5)
    
    if suggestions["success"] and suggestions["data"]["suggestions"]:
        st.markdown("**Suggestions:**")
        
        # Display suggestions in a horizontal layout
        cols = st.columns(len(suggestions["data"]["suggestions"]))
        
        for i, suggestion in enumerate(suggestions["data"]["suggestions"]):
            with cols[i]:
                if st.button(f"`{suggestion}`", key=f"suggestion_{suggestion}_{i}_{search_type}", use_container_width=True):
                    if search_type == "basic":
                        perform_basic_search(suggestion, {}, 15)
                    else:
                        st.session_state.ai_query_tab = suggestion
                        st.rerun()


def show_compact_examples():
    """Show AI examples in compact format"""
    examples = [
        "Push-on fittings for 6 inch pipes",
        "High pressure mechanical joints",
        "Compact design C153 products",
        "Flanged fittings with NSF certification"
    ]
    
    st.markdown("**Example Questions:**")
    cols = st.columns(2)
    
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, key=f"example_{i}", use_container_width=True):
                st.session_state.ai_query_tab = example
                st.rerun()


def get_filter_options():
    """Get filter options from API"""
    api_client = get_api_client()
    return api_client.get_filter_options()


def create_filter_interface(filter_options, key_prefix=""):
    """Create compact filter interface"""
    filters = {}
    
    if filter_options["success"]:
        data = filter_options["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if data.get("product_codes"):
                selected_code = st.selectbox(
                    "Product Code",
                    ["All"] + data["product_codes"],
                    key=f"{key_prefix}_product_code"
                )
                if selected_code != "All":
                    filters["product_code"] = selected_code
            
            if data.get("joint_types"):
                selected_joint = st.selectbox(
                    "Joint Type",
                    ["All"] + data["joint_types"],
                    key=f"{key_prefix}_joint_type"
                )
                if selected_joint != "All":
                    filters["joint_type"] = selected_joint
        
        with col2:
            if data.get("body_designs"):
                selected_design = st.selectbox(
                    "Body Design",
                    ["All"] + data["body_designs"],
                    key=f"{key_prefix}_body_design"
                )
                if selected_design != "All":
                    filters["body_design"] = selected_design
        
        with col3:
            st.markdown("**Pressure (PSI)**")
            pressure_col1, pressure_col2 = st.columns(2)
            
            with pressure_col1:
                min_pressure = st.number_input("Min", min_value=0, value=0, key=f"{key_prefix}_min_pressure")
                if min_pressure > 0:
                    filters["min_pressure"] = min_pressure
            
            with pressure_col2:
                max_pressure = st.number_input("Max", min_value=0, value=500, key=f"{key_prefix}_max_pressure")
                if max_pressure < 500:
                    filters["max_pressure"] = max_pressure
    
    else:
        st.error("Could not load filter options")
    
    return filters


def perform_basic_search(query: str, filters: dict, limit: int):
    """Perform basic keyword search"""
    api_client = get_api_client()
    
    with show_loading():
        search_result = api_client.search_products(
            query=query,
            enhanced=False,
            limit=limit,
            **filters
        )
    
    display_search_results(search_result, f'Search results for "{query}"', "basic")


def perform_ai_search(query: str, limit: int):
    """Perform AI-enhanced search"""
    api_client = get_api_client()
    
    with show_loading():
        search_result = api_client.search_products(
            query=query,
            enhanced=True,
            limit=limit
        )
    
    display_search_results(search_result, f'AI search results for "{query}"', "ai")


def display_search_results(search_result: dict, title: str, search_type: str):
    """Display search results"""
    if search_result["success"]:
        data = search_result["data"]
        
        # Results header
        st.success(title)
        
        # Compact results info
        col1, col2 = st.columns([3, 1])
        with col1:
            if search_type == "basic":
                st.info(f"Found {data['total_results']} products in {data.get('search_time_ms', 0)}ms")
            else:
                st.info(f"Found {data['total_results']} products using AI analysis")
        
        with col2:
            if st.button("New Search"):
                st.rerun()
        
        # Display results
        if data["results"]:
            st.divider()
            
            for i, result in enumerate(data["results"], 1):
                with st.container(border=True):
                    # Product header
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**{i}. {result['product']['title']}**")
                        
                        # Compact product info
                        product = result['product']
                        st.caption(f"Code: {product['product_code']} | Joint: {product['joint_type']} | Design: {product['body_design']}")
                        st.caption(f"Size Range: {product['specifications']['size_range']} | Standard: {product['primary_standard']}")
                        
                        # Match score info
                        if result.get('score'):
                            st.caption(f"Match Score: {result['score']:.0f} | Reason: {result.get('match_reason', 'N/A')}")
                    
                    with col2:
                        # Action buttons in vertical layout
                        if st.button("Details", key=f"view_{result['product']['id']}_{i}_{search_type}", use_container_width=True):
                            st.session_state.selected_product = result['product']['id']
                            st.rerun()
                        
                        if st.button("HTS", key=f"hts_{result['product']['id']}_{i}_{search_type}", use_container_width=True):
                            st.session_state.show_hts = result['product']['id']
                            st.rerun()
                        
                        if st.button("Similar", key=f"similar_{result['product']['id']}_{i}_{search_type}", use_container_width=True):
                            st.session_state.show_similar = result['product']['id']
                            st.rerun()
        else:
            st.warning("No products found matching your search criteria.")
            
            if search_type == "basic":
                st.info("Try different keywords, remove filters, or check spelling")
            else:
                st.info("Try rephrasing your question or being more specific")
    else:
        display_api_error(search_result["error"])


def show_popular_searches():
    """Show popular searches in compact format"""
    st.markdown("### Popular Searches")
    
    popular_terms = [
        "mechanical joint", "C153", "push-on", "flanged", 
        "high pressure", "ductile iron", "compact design"
    ]
    
    cols = st.columns(4)
    
    for i, term in enumerate(popular_terms):
        with cols[i % 4]:
            if st.button(term, key=f"popular_{term}", use_container_width=True):
                perform_basic_search(term, {}, 10)


# Legacy function for backward compatibility
def search_interface():
    """Legacy search interface - redirect to tabbed search"""
    tabbed_search_page()