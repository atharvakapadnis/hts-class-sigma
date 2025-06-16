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
    
    # Debug info
    if st.session_state.get("debug_mode", False):
        st.write("Debug - Session State Keys:", list(st.session_state.keys()))
    
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
            key="basic_search_query"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True, key="basic_search_btn")
    
    with col3:
        clear_button = st.button("Clear", use_container_width=True, key="basic_clear")
    
    # Compact controls row
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        results_limit = st.selectbox("Results", [10, 15, 25, 50], index=1, key="basic_limit")
    
    with col2:
        show_filters = st.button("Advanced Filters", use_container_width=True, key="toggle_filters")
    
    with col3:
        if search_query and len(search_query) >= 2:
            show_suggestions = st.button("Show Suggestions", use_container_width=True, key="toggle_suggestions")
        else:
            show_suggestions = False
    
    # Handle clear button
    if clear_button:
        # Clear all search-related session state
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith(('basic_search', 'search_results', 'show_filters', 'show_suggestions'))]
        for key in keys_to_clear:
            del st.session_state[key]
        st.rerun()
    
    # Advanced filters
    filters = {}
    if show_filters or st.session_state.get("show_filters_state", False):
        st.session_state.show_filters_state = True
        with st.expander("Advanced Filters", expanded=True):
            filter_options = get_filter_options()
            filters = create_filter_interface(filter_options, key_prefix="basic")
    
    # Suggestions
    if show_suggestions or st.session_state.get("show_suggestions_state", False):
        if search_query and len(search_query) >= 2:
            st.session_state.show_suggestions_state = True
            show_compact_suggestions(search_query, "basic")
    
    # Search execution
    if search_button and search_query:
        # Store search parameters
        st.session_state.current_search_query = search_query
        st.session_state.current_search_filters = filters
        st.session_state.current_search_limit = results_limit
        
        # Perform search
        api_client = get_api_client()
        with show_loading():
            search_result = api_client.search_products(
                query=search_query,
                enhanced=False,
                limit=results_limit,
                **filters
            )
        
        # Store results
        st.session_state.search_results_data = search_result
        st.session_state.search_type = "basic"
        st.rerun()
    
    elif search_button and not search_query:
        st.warning("Please enter a search query")
    
    # Display stored search results
    if st.session_state.get("search_results_data") and st.session_state.get("search_type") == "basic":
        display_persistent_search_results(
            st.session_state.search_results_data,
            st.session_state.get("current_search_query", ""),
            "basic"
        )
    
    # Popular searches when no active search
    elif not st.session_state.get("search_results_data"):
        show_popular_searches()


def ai_search_tab():
    """AI-powered natural language search tab"""
    st.markdown("Ask questions about products in natural language")
    
    # Main search section
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        ai_query = st.text_area(
            "Ask your question",
            placeholder="What products have push-on fittings for 6 inch pipes?",
            height=80,
            key="ai_search_query"
        )
    
    with col2:
        search_button = st.button("Ask AI", type="primary", use_container_width=True, key="ai_search_btn")
        show_examples = st.button("Examples", use_container_width=True, key="toggle_examples")
    
    with col3:
        results_limit = st.selectbox("Results", [5, 10, 15, 20], index=1, key="ai_limit")
        clear_button = st.button("Clear", use_container_width=True, key="ai_clear")
    
    # Handle clear button
    if clear_button:
        # Clear AI search-related session state
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith(('ai_search', 'show_examples'))]
        for key in keys_to_clear:
            del st.session_state[key]
        if "search_results_data" in st.session_state and st.session_state.get("search_type") == "ai":
            del st.session_state.search_results_data
            del st.session_state.search_type
        st.rerun()
    
    # Examples
    if show_examples or st.session_state.get("show_examples_state", False):
        st.session_state.show_examples_state = True
        show_compact_examples()
    
    # Search execution
    if search_button and ai_query:
        # Store search parameters
        st.session_state.current_ai_query = ai_query
        st.session_state.current_ai_limit = results_limit
        
        # Perform AI search
        api_client = get_api_client()
        with show_loading():
            search_result = api_client.search_products(
                query=ai_query,
                enhanced=True,
                limit=results_limit
            )
        
        # Store results
        st.session_state.search_results_data = search_result
        st.session_state.search_type = "ai"
        st.rerun()
    
    elif search_button and not ai_query:
        st.warning("Please enter your question")
    
    # Display stored AI search results
    if st.session_state.get("search_results_data") and st.session_state.get("search_type") == "ai":
        display_persistent_search_results(
            st.session_state.search_results_data,
            st.session_state.get("current_ai_query", ""),
            "ai"
        )
    
    # AI tips when no active search
    elif not st.session_state.get("search_results_data"):
        st.info("Ask natural language questions like: 'What products work with 12 inch pipes?' or 'Show me high pressure fittings'")


def display_persistent_search_results(search_result: dict, query: str, search_type: str):
    """Display search results that persist across page interactions"""
    
    if not search_result["success"]:
        display_api_error(search_result["error"])
        return
    
    data = search_result["data"]
    
    # Results header
    st.success(f'{search_type.title()} search results for "{query}"')
    
    # Compact results info
    col1, col2 = st.columns([3, 1])
    with col1:
        if search_type == "basic":
            st.info(f"Found {data['total_results']} products in {data.get('search_time_ms', 0)}ms")
        else:
            st.info(f"Found {data['total_results']} products using AI analysis")
    
    with col2:
        if st.button("New Search", key=f"new_search_{search_type}_btn"):
            # Clear search results
            if "search_results_data" in st.session_state:
                del st.session_state.search_results_data
            if "search_type" in st.session_state:
                del st.session_state.search_type
            st.rerun()
    
    # Display results
    if not data["results"]:
        st.warning("No products found matching your search criteria.")
        if search_type == "basic":
            st.info("Try different keywords, remove filters, or check spelling")
        else:
            st.info("Try rephrasing your question or being more specific")
        return
    
    st.divider()
    
    # Create a unique identifier for this search session
    search_session_id = f"{search_type}_{hash(query)}_{len(data['results'])}"
    
    for i, result in enumerate(data["results"], 1):
        product = result['product']
        
        # Create unique container
        container_key = f"result_container_{search_session_id}_{i}"
        
        with st.container(border=True, key=container_key):
            # Product header
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{i}. {product['title']}**")
                st.caption(f"Code: {product['product_code']} | Joint: {product['joint_type']} | Design: {product['body_design']}")
                st.caption(f"Size Range: {product['specifications']['size_range']} | Standard: {product['primary_standard']}")
                
                # Match score info
                if result.get('score'):
                    st.caption(f"Match Score: {result['score']:.0f} | Reason: {result.get('match_reason', 'N/A')}")
            
            with col2:
                # Create unique button keys
                details_btn_key = f"details_{product['id']}_{search_session_id}_{i}"
                hts_btn_key = f"hts_{product['id']}_{search_session_id}_{i}"
                similar_btn_key = f"similar_{product['id']}_{search_session_id}_{i}"
                
                # Action buttons with callbacks
                if st.button("Details", key=details_btn_key, use_container_width=True):
                    handle_product_details(product['id'])
                
                if st.button("HTS", key=hts_btn_key, use_container_width=True):
                    handle_hts_codes(product['id'])
                
                if st.button("Similar", key=similar_btn_key, use_container_width=True):
                    handle_similar_products(product['id'])


def handle_product_details(product_id: str):
    """Handle product details navigation"""
    st.session_state.selected_product = product_id
    st.session_state.came_from_search = True
    st.rerun()


def handle_hts_codes(product_id: str):
    """Handle HTS codes navigation"""
    st.session_state.show_hts = product_id
    st.session_state.came_from_search = True
    st.rerun()


def handle_similar_products(product_id: str):
    """Handle similar products navigation"""
    st.session_state.show_similar = product_id
    st.session_state.came_from_search = True
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
                    key=f"{key_prefix}_product_code_filter"
                )
                if selected_code != "All":
                    filters["product_code"] = selected_code
            
            if data.get("joint_types"):
                selected_joint = st.selectbox(
                    "Joint Type",
                    ["All"] + data["joint_types"],
                    key=f"{key_prefix}_joint_type_filter"
                )
                if selected_joint != "All":
                    filters["joint_type"] = selected_joint
        
        with col2:
            if data.get("body_designs"):
                selected_design = st.selectbox(
                    "Body Design",
                    ["All"] + data["body_designs"],
                    key=f"{key_prefix}_body_design_filter"
                )
                if selected_design != "All":
                    filters["body_design"] = selected_design
        
        with col3:
            st.markdown("**Pressure (PSI)**")
            pressure_col1, pressure_col2 = st.columns(2)
            
            with pressure_col1:
                min_pressure = st.number_input(
                    "Min", 
                    min_value=0, 
                    value=0, 
                    key=f"{key_prefix}_min_pressure_filter"
                )
                if min_pressure > 0:
                    filters["min_pressure"] = min_pressure
            
            with pressure_col2:
                max_pressure = st.number_input(
                    "Max", 
                    min_value=0, 
                    value=500, 
                    key=f"{key_prefix}_max_pressure_filter"
                )
                if max_pressure < 500:
                    filters["max_pressure"] = max_pressure
    
    else:
        st.error("Could not load filter options")
    
    return filters


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
                suggestion_key = f"suggestion_{search_type}_{i}_{hash(suggestion)}"
                if st.button(f"`{suggestion}`", key=suggestion_key, use_container_width=True):
                    # Trigger search with suggestion
                    if search_type == "basic":
                        st.session_state.basic_search_query = suggestion
                    else:
                        st.session_state.ai_search_query = suggestion
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
            example_key = f"example_{i}_{hash(example)}"
            if st.button(example, key=example_key, use_container_width=True):
                st.session_state.ai_search_query = example
                st.rerun()


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
            popular_key = f"popular_{i}_{hash(term)}"
            if st.button(term, key=popular_key, use_container_width=True):
                st.session_state.basic_search_query = term
                st.rerun()


# Legacy function for backward compatibility
def search_interface():
    """Legacy search interface - redirect to tabbed search"""
    tabbed_search_page()