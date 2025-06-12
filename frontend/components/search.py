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
    st.write("Choose between basic keyword search or AI-powered natural language search.")
    
    # Create tabs
    tab1, tab2 = st.tabs(["**Basic Search**", "**AI Search**"])
    
    with tab1:
        basic_search_tab()
    
    with tab2:
        ai_search_tab()


def basic_search_tab():
    """Basic keyword search tab"""
    st.markdown("### Keyword & Filter Search")
    st.write("Search using specific keywords, product codes, and filters.")
    
    # Search input
    search_query = st.text_input(
        "Search products...",
        placeholder="e.g., C153, mechanical joint, ductile iron, 350 PSI",
        help="Search by product code, joint type, material, pressure rating, or other specifications",
        key="basic_search_input"
    )
    
    # Filters
    with st.expander("Search Filters", expanded=False):
        filter_options = get_filter_options()
        filters = create_filter_interface(filter_options, key_prefix="basic")
    
    # Search controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        results_limit = st.slider("Max Results", min_value=5, max_value=50, value=15, key="basic_limit")
    
    with col2:
        if st.button("Search", type="primary", use_container_width=True, key="basic_search_btn"):
            if search_query:
                perform_basic_search(search_query, filters, results_limit)
            else:
                st.warning("Please enter a search query")
    
    with col3:
        if st.button("Clear", use_container_width=True, key="basic_clear"):
            st.rerun()
    
    # Search suggestions for basic search
    if search_query and len(search_query) >= 2:
        show_search_suggestions(search_query, "basic")
    
    # Popular searches when no query
    if not search_query:
        show_popular_searches()


def ai_search_tab():
    """AI-powered natural language search tab"""
    st.markdown("### Natural Language Search")
    st.write("Ask questions about products in natural language. The AI will understand your intent and find relevant products.")
    
    # Example queries in a more compact format
    with st.expander("Example Questions", expanded=True):
        st.markdown("**Try asking questions like:**")
        
        example_questions = [
            "What products have push-on fittings?",
            "Show me compact fittings for high pressure applications",
            "Which fittings are suitable for 6 inch pipes?",
            "Find mechanical joint fittings with NSF certification",
            "What C153 products support deflection?",
            "Show me full body designs for water applications"
        ]
        
        # Display example questions as clickable buttons
        example_cols = st.columns(2)
        
        for i, question in enumerate(example_questions):
            with example_cols[i % 2]:
                if st.button(f"{question}", key=f"example_{i}", use_container_width=True):
                    st.session_state.ai_query_tab = question
                    st.rerun()
    
    # AI search input
    ai_query = st.text_area(
        "Ask your question:",
        value=st.session_state.get("ai_query_tab", ""),
        placeholder="Type your question in natural language...\n\nFor example:\n- What products have push-on fittings?\n- Show me high pressure fittings for 6 inch pipes\n- Find compact mechanical joint fittings",
        help="Describe what you're looking for in your own words. The AI will interpret your question and find relevant products.",
        height=120,
        key="ai_search_input"
    )
    
    # AI search controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        results_limit = st.slider("Max Results", min_value=5, max_value=20, value=10, key="ai_limit")
    
    with col2:
        if st.button("Ask AI", type="primary", use_container_width=True, key="ai_search_btn"):
            if ai_query:
                perform_ai_search(ai_query, results_limit)
            else:
                st.warning("Please enter your question")
    
    with col3:
        if st.button("Clear", use_container_width=True, key="ai_clear"):
            if "ai_query_tab" in st.session_state:
                del st.session_state.ai_query_tab
            st.rerun()
    
    # AI search tips when no query
    if not ai_query:
        st.info("""
        **AI Search Tips:**
        - Ask questions naturally, as you would to a person
        - Be specific about what you need (size, pressure, application, etc.)
        - Use product terminology when you know it
        - The AI understands synonyms and related terms
        
        **Example queries:**
        - "What products work with 12 inch pipes?"
        - "Show me fittings rated for 350 PSI"
        - "Find push-on joints for water applications"
        """)


def get_filter_options():
    """Get filter options from API"""
    api_client = get_api_client()
    return api_client.get_filter_options()


def create_filter_interface(filter_options, key_prefix=""):
    """Create filter interface"""
    filters = {}
    
    if filter_options["success"]:
        data = filter_options["data"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Product Code filter
            if data.get("product_codes"):
                selected_code = st.selectbox(
                    "Product Code",
                    ["All"] + data["product_codes"],
                    key=f"{key_prefix}_product_code"
                )
                if selected_code != "All":
                    filters["product_code"] = selected_code
            
            # Joint Type filter
            if data.get("joint_types"):
                selected_joint = st.selectbox(
                    "Joint Type",
                    ["All"] + data["joint_types"],
                    key=f"{key_prefix}_joint_type"
                )
                if selected_joint != "All":
                    filters["joint_type"] = selected_joint
        
        with col2:
            # Body Design filter
            if data.get("body_designs"):
                selected_design = st.selectbox(
                    "Body Design",
                    ["All"] + data["body_designs"],
                    key=f"{key_prefix}_body_design"
                )
                if selected_design != "All":
                    filters["body_design"] = selected_design
        
        with col3:
            # Pressure filters
            st.write("**Pressure Range (PSI)**")
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
            enhanced=False,  # Basic search only
            limit=limit,
            **filters
        )
    
    display_search_results(search_result, f'Basic search for "{query}"', "basic")


def perform_ai_search(query: str, limit: int):
    """Perform AI-enhanced search"""
    api_client = get_api_client()
    
    with show_loading():
        search_result = api_client.search_products(
            query=query,
            enhanced=True,  # AI search
            limit=limit
        )
    
    display_search_results(search_result, f'AI search for "{query}"', "ai")


def display_search_results(search_result: dict, title: str, search_type: str):
    """Display search results"""
    if search_result["success"]:
        data = search_result["data"]
        
        # Results header
        st.success(f"{title}")
        
        # Show search time for basic search, not for AI (since it's processed differently)
        if search_type == "basic":
            st.info(f"Found **{data['total_results']}** products in {data.get('search_time_ms', 0)}ms")
        else:
            st.info(f"Found **{data['total_results']}** products using AI analysis")
        
        # Display results
        if data["results"]:
            st.divider()
            
            for i, result in enumerate(data["results"], 1):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"#### {i}. {result['product']['title']}")
                        search_result_display(result)
                    
                    with col2:
                        # Show match score if available
                        if result.get('score'):
                            st.metric("Match Score", f"{result['score']:.0f}", help=f"Match reason: {result.get('match_reason', 'N/A')}")
                        
                        # Action buttons
                        if st.button("View Details", key=f"view_{result['product']['id']}_{i}_{search_type}", use_container_width=True):
                            st.session_state.selected_product = result['product']['id']
                            st.rerun()
                        
                        if st.button("HTS Codes", key=f"hts_{result['product']['id']}_{i}_{search_type}", use_container_width=True):
                            st.session_state.show_hts = result['product']['id']
                            st.rerun()
                        
                        if st.button("Similar", key=f"similar_{result['product']['id']}_{i}_{search_type}", use_container_width=True):
                            st.session_state.show_similar = result['product']['id']
                            st.rerun()
        else:
            st.warning("No products found matching your search criteria.")
            
            # Suggestions for no results
            if search_type == "basic":
                st.info("""
                **Try these tips:**
                - Use different keywords
                - Remove some filters
                - Check spelling
                - Try broader terms
                """)
            else:
                st.info("""
                **Try these tips:**
                - Rephrase your question
                - Be more specific about what you need
                - Use different terminology
                - Try the examples above
                """)
    else:
        display_api_error(search_result["error"])


def show_search_suggestions(query: str, search_type: str):
    """Show search suggestions"""
    api_client = get_api_client()
    suggestions = api_client.get_search_suggestions(query, limit=5)
    
    if suggestions["success"] and suggestions["data"]["suggestions"]:
        st.markdown("**Suggestions:**")
        suggestion_cols = st.columns(min(len(suggestions["data"]["suggestions"]), 5))
        
        for i, suggestion in enumerate(suggestions["data"]["suggestions"]):
            with suggestion_cols[i]:
                if st.button(suggestion, key=f"suggestion_{suggestion}_{i}_{search_type}", use_container_width=True):
                    # Trigger search with suggestion
                    if search_type == "basic":
                        perform_basic_search(suggestion, {}, 15)
                    else:
                        st.session_state.ai_query_tab = suggestion
                        st.rerun()


def show_popular_searches():
    """Show popular searches for basic search"""
    st.markdown("### Popular Searches")
    
    popular_terms = [
        "mechanical joint", "C153", "push-on", "flanged", 
        "high pressure", "ductile iron", "compact design"
    ]
    
    cols = st.columns(min(len(popular_terms), 4))
    
    for i, term in enumerate(popular_terms):
        with cols[i % 4]:
            if st.button(f"{term}", key=f"popular_{term}", use_container_width=True):
                # Perform search with popular term
                perform_basic_search(term, {}, 10)


# Legacy function for backward compatibility
def search_interface():
    """Legacy search interface - redirect to tabbed search"""
    tabbed_search_page()