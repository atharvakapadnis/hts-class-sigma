"""
SIGMA Product Catalog - Streamlit Frontend
Main application entry point
"""

import streamlit as st
from streamlit_option_menu import option_menu
import time

# Import components
from components.search import tabbed_search_page
from components.products import product_catalog, product_detail_view, product_comparison
from components.filters import quick_filters, advanced_filters_sidebar
from components.hts_codes import hts_codes_interface, hts_product_view, bulk_hts_interface
from services.api_client import get_api_client
from utils.helpers import display_api_error
from config.settings import settings

# Page configuration
st.set_page_config(**settings.PAGE_CONFIG)

def main():
    """Main application function"""
    
    # Header
    st.title("SIGMA Product Catalog")
    st.caption("Ductile Iron Fittings with AI-Powered Search & HTS Code Generation")
    
    # Debug toggle (remove in production)
    if st.sidebar.checkbox("Debug Mode"):
        st.session_state.debug_mode = True
        st.sidebar.json(dict(st.session_state))
    
    # Check API connectivity
    check_api_connection()
    
    # Initialize navigation state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Handle special states first (these override normal navigation)
    if "selected_product" in st.session_state:
        if st.session_state.get("came_from_search"):
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("← Back to Search"):
                    del st.session_state.selected_product
                    del st.session_state.came_from_search
                    st.session_state.current_page = "Search"
                    st.rerun()
        
        product_detail_view(st.session_state.selected_product)
        return
    
    if "show_hts" in st.session_state:
        if st.session_state.get("came_from_search"):
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("← Back to Search"):
                    del st.session_state.show_hts
                    del st.session_state.came_from_search
                    st.session_state.current_page = "Search"
                    st.rerun()
        
        hts_product_view(st.session_state.show_hts)
        
        if not st.session_state.get("came_from_search"):
            if st.button("← Back"):
                del st.session_state.show_hts
                st.rerun()
        return
    
    if "show_similar" in st.session_state:
        if st.session_state.get("came_from_search"):
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("← Back to Search"):
                    del st.session_state.show_similar
                    del st.session_state.came_from_search
                    st.session_state.current_page = "Search"
                    st.rerun()
        
        show_similar_products(st.session_state.show_similar)
        return
    
    # Navigation menu
    menu_options = ["Home", "Search", "Catalog", "Compare", "HTS Codes", "Bulk HTS"]
    icons = ["house", "search", "grid", "arrow-repeat", "tags", "collection"]
    
    # Get current index
    try:
        current_index = menu_options.index(st.session_state.current_page)
    except ValueError:
        current_index = 0
        st.session_state.current_page = "Home"
    
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=icons,
        menu_icon="cast",
        default_index=current_index,
        orientation="horizontal",
        key="main_menu",
    )
    
    # Update session state when menu selection changes
    if selected != st.session_state.current_page:
        st.session_state.current_page = selected
        st.rerun()
    
    # Main navigation based on session state
    current_page = st.session_state.current_page
    
    if current_page == "Home":
        home_page()
    elif current_page == "Search":
        tabbed_search_page()
    elif current_page == "Catalog":
        product_catalog()
    elif current_page == "Compare":
        product_comparison()
    elif current_page == "HTS Codes":
        hts_codes_interface()
    elif current_page == "Bulk HTS":
        bulk_hts_interface()


def home_page():
    """Home page with overview and quick actions"""
    
    # Welcome section
    st.header("Welcome to SIGMA Product Catalog")
    st.write("Your comprehensive resource for ductile iron fittings with intelligent search capabilities")
    
    # Quick stats
    api_client = get_api_client()
    products_result = api_client.get_products()
    
    if products_result["success"]:
        products = products_result["data"]
        total_products = len(products)
        
        # Calculate some basic stats
        joint_types = set(p['joint_type'] for p in products)
        product_codes = set(p['product_code'] for p in products)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Products", total_products, help="Complete product catalog size")
        
        with col2:
            st.metric("Joint Types", len(joint_types), help="Available joint connection types")
        
        with col3:
            st.metric("Product Series", len(product_codes), help="Distinct product code series")
        
        with col4:
            st.metric("AI Features", "3", help="Search, HTS Codes, Recommendations")
    
    # Quick actions
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Start Smart Search", use_container_width=True, type="primary"):
            st.session_state.current_page = "Search"
            st.rerun()
    
    with col2:
        if st.button("Browse Catalog", use_container_width=True):
            st.session_state.current_page = "Catalog"
            st.rerun()
    
    with col3:
        if st.button("Generate HTS Codes", use_container_width=True):
            st.session_state.current_page = "HTS Codes"
            st.rerun()
    
    # Quick filters
    st.divider()
    quick_filter_result = quick_filters()
    
    if quick_filter_result:
        st.session_state.quick_filters = quick_filter_result
        st.session_state.current_page = "Search"
        st.rerun()
    
    # Featured products
    if products_result["success"]:
        st.divider()
        st.subheader("Featured Products")
        
        # Show first 3 products as featured in cards
        featured_products = products[:3]
        
        # Create columns for card layout
        cols = st.columns(len(featured_products))
        
        for idx, product in enumerate(featured_products):
            with cols[idx]:
                # Create a card using st.container with border
                with st.container(border=True):
                    st.markdown(f"##### {product['title']}")
                    
                    # Product details in organized format
                    st.markdown(f"""
                    **Product Code:** `{product['product_code']}`  
                    **Joint Type:** {product['joint_type']}  
                    **Body Design:** {product['body_design']}  
                    **Size Range:** {product['specifications']['size_range']}  
                    **Standard:** {product['primary_standard']}
                    """)
                    
                    # Pressure ratings summary
                    pressure_ratings = product['specifications']['pressure_ratings']
                    if pressure_ratings:
                        max_pressure = max([pr['psi'] for pr in pressure_ratings])
                        st.metric("Max Pressure", f"{max_pressure} PSI")
                    
                    # Action buttons
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("Details", key=f"featured_details_{product['id']}", use_container_width=True):
                            st.session_state.selected_product = product['id']
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("HTS", key=f"featured_hts_{product['id']}", use_container_width=True):
                            st.session_state.show_hts = product['id']
                            st.rerun()


def show_similar_products(product_id: str):
    """Show similar products interface"""
    st.title("Similar Products")
    
    api_client = get_api_client()
    
    # Get the reference product
    product_result = api_client.get_product(product_id)
    
    if product_result["success"]:
        product = product_result["data"]
        
        st.subheader(f"Similar to: {product['title']}")
        
        # Get similar products
        similar_result = api_client.get_similar_products(product_id, limit=5)
        
        if similar_result["success"]:
            data = similar_result["data"]
            
            if data["similar_products"]:
                st.success(f"Found {len(data['similar_products'])} similar products")
                
                # Show similarity criteria
                st.info(f"Similarity based on: {', '.join(data['similarity_criteria'])}")
                
                # Display similar products
                for result in data["similar_products"]:
                    similar_product = result["product"]
                    
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.write(f"**{similar_product['title']}**")
                        st.caption(f"Code: {similar_product['product_code']} | Joint: {similar_product['joint_type']} | Design: {similar_product['body_design']}")
                        st.caption(f"Size Range: {similar_product['specifications']['size_range']}")
                    
                    with col2:
                        if st.button("View Details", key=f"similar_details_{similar_product['id']}"):
                            st.session_state.selected_product = similar_product['id']
                            del st.session_state.show_similar
                            st.rerun()
                    
                    st.divider()
            else:
                st.info("No similar products found.")
        else:
            display_api_error(similar_result["error"])
    
    else:
        display_api_error(product_result["error"])
    
    # Back button
    if not st.session_state.get("came_from_search"):
        if st.button("← Back to Original Product"):
            st.session_state.selected_product = product_id
            del st.session_state.show_similar
            st.rerun()


def check_api_connection():
    """Check backend API connectivity"""
    api_client = get_api_client()
    health_result = api_client.health_check()
    
    if not health_result["success"]:
        st.error("""
        **Backend API Connection Failed**
        
        The frontend cannot connect to the backend API. Please ensure:
        1. Backend server is running on http://localhost:8000
        2. Run: `cd backend && uvicorn main:app --reload`
        3. Check that all dependencies are installed
        """)
        st.stop()
    else:
        # Show connection status in sidebar
        with st.sidebar:
            st.success("API Connected")


def sidebar_info():
    """Display sidebar information"""
    with st.sidebar:
        st.divider()
        st.subheader("System Info")
        st.info(f"**Version:** {settings.APP_TITLE}")
        st.info(f"**API:** {settings.API_BASE_URL}")
        
        if settings.DEBUG:
            st.warning("Debug Mode Active")


if __name__ == "__main__":
    # Add sidebar info
    sidebar_info()
    
    # Run main application
    main()