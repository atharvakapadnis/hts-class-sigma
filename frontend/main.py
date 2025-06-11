"""
SIGMA Product Catalog - Streamlit Frontend
Main application entry point
"""

import streamlit as st
from streamlit_option_menu import option_menu
import time

# Import components
from components.search import search_interface
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
    st.markdown("""
    <div style="text-align: center; padding: 20px 0; margin-bottom: 30px;">
        <h1 style="color: #ffffff; font-size: 3em; margin: 0;">
            SIGMA Product Catalog
        </h1>
        <p style="color: #cccccc; font-size: 1.2em; margin: 10px 0;">
            Ductile Iron Fittings with AI-Powered Search & HTS Code Generation
        </p>
    </div>
    """, unsafe_allow_html=True)

    check_api_connection()

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    menu_options = ["Home", "Search", "Catalog", "Compare", "HTS Codes", "Bulk HTS"]
    icons = ["house", "search", "grid", "arrow-repeat", "tags", "collection"]

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
        styles={
            "container": {"padding": "0!important", "background-color": "#1e1e1e"},
            "icon": {"color": "#ffffff", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "padding": "10px",
                "color": "#ffffff",
                "--hover-color": "#2d2d2d"
            },
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )

    if selected != st.session_state.current_page:
        clear_navigation_states()
        st.session_state.current_page = selected
        st.rerun()

    if "selected_product" in st.session_state:
        product_detail_view(st.session_state.selected_product)
        return

    if "show_hts" in st.session_state:
        hts_product_view(st.session_state.show_hts)
        if st.button("Back"):
            del st.session_state.show_hts
            st.rerun()
        return

    if "show_similar" in st.session_state:
        show_similar_products(st.session_state.show_similar)
        return

    current_page = st.session_state.current_page

    if current_page == "Home":
        home_page()
    elif current_page == "Search":
        search_interface()
    elif current_page == "Catalog":
        product_catalog()
    elif current_page == "Compare":
        product_comparison()
    elif current_page == "HTS Codes":
        hts_codes_interface()
    elif current_page == "Bulk HTS":
        bulk_hts_interface()


def clear_navigation_states():
    """Clear navigation-related session states"""
    states_to_clear = ["selected_product", "show_hts", "show_similar", "quick_filters"]
    for state in states_to_clear:
        if state in st.session_state:
            del st.session_state[state]


def home_page():
    """Home page with overview and quick actions"""

    st.markdown("""
    <div style="background-color: #1e1e1e; padding: 30px; border-radius: 15px; margin-bottom: 30px;">
        <h2 style="color: #ffffff; text-align: center;">Welcome to SIGMA Product Catalog</h2>
        <p style="color: #cccccc; text-align: center; font-size: 1.1em;">
            Your comprehensive resource for ductile iron fittings with intelligent search capabilities
        </p>
    </div>
    """, unsafe_allow_html=True)

    api_client = get_api_client()
    products_result = api_client.get_products()

    if products_result["success"]:
        products = products_result["data"]
        total_products = len(products)

        joint_types = set(p['joint_type'] for p in products)
        product_codes = set(p['product_code'] for p in products)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Products", total_products)
        with col2:
            st.metric("Joint Types", len(joint_types))
        with col3:
            st.metric("Product Series", len(product_codes))
        with col4:
            st.metric("AI Features", "3")

    st.markdown("### Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Start Smart Search", use_container_width=True):
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

    st.markdown("---")
    st.markdown("### News & Updates")
    news_placeholder()

    st.markdown("---")
    quick_filter_result = quick_filters()
    if quick_filter_result:
        st.session_state.quick_filters = quick_filter_result
        st.session_state.current_page = "Search"
        st.rerun()

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


def news_placeholder():
    """News feed placeholder section"""
    st.markdown("""
    <div style="background-color: #2d2d2d; padding: 20px; border-radius: 10px; border: 2px dashed #404040;">
        <h4 style="color: #ffffff; text-align: center; margin-top: 0;">News Feed Coming Soon</h4>
        <p style="color: #cccccc; text-align: center;">
            This section will feature:
        </p>
        <ul style="color: #cccccc; text-align: left; max-width: 500px; margin: 0 auto;">
            <li>Product updates and releases</li>
            <li>Industry news and standards updates</li>
            <li>Technical bulletins and advisories</li>
            <li>Training and certification announcements</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)


def show_similar_products(product_id: str):
    """Show similar products interface"""
    st.title("Similar Products")
    api_client = get_api_client()
    product_result = api_client.get_product(product_id)

    if product_result["success"]:
        product = product_result["data"]
        st.markdown(f"### Similar to: {product['title']}")
        similar_result = api_client.get_similar_products(product_id, limit=5)

        if similar_result["success"]:
            data = similar_result["data"]
            if data["similar_products"]:
                st.success(f"Found {len(data['similar_products'])} similar products")
                st.info(f"Similarity based on: {', '.join(data['similarity_criteria'])}")
                for result in data["similar_products"]:
                    similar_product = result["product"]
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 4px solid #4bb543;">
                            <h4 style="color: #ffffff; margin-top: 0;">{similar_product['title']}</h4>
                            <p style="color: #cccccc;">
                                <strong>Code:</strong> {similar_product['product_code']} |
                                <strong>Joint:</strong> {similar_product['joint_type']} |
                                <strong>Design:</strong> {similar_product['body_design']}
                            </p>
                            <p style="color: #cccccc;">
                                <strong>Size Range:</strong> {similar_product['specifications']['size_range']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("View Details", key=f"similar_{similar_product['id']}"):
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

    if st.button("Back to Original Product"):
        st.session_state.selected_product = product_id
        del st.session_state.show_similar
        st.rerun()


def check_api_connection():
    """Check backend API connectivity"""
    api_client = get_api_client()
    health_result = api_client.health_check()

    if not health_result["success"]:
        st.error("""
        Backend API Connection Failed

        The frontend cannot connect to the backend API. Please ensure:
        1. Backend server is running on http://localhost:8000
        2. Run: `cd backend && uvicorn main:app --reload`
        3. Check that all dependencies are installed
        """)
        st.stop()
    else:
        with st.sidebar:
            st.success("API Connected")


def sidebar_info():
    """Display sidebar information"""
    with st.sidebar:
        st.markdown("---")
        st.markdown("### System Info")
        st.info(f"Version: {settings.APP_TITLE}")
        st.info(f"API: {settings.API_BASE_URL}")
        if settings.DEBUG:
            st.warning("Debug Mode Active")

        st.markdown("---")
        st.markdown("### Quick Tools")
        if st.button("Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
            time.sleep(1)
            st.rerun()

        if st.button("API Documentation", use_container_width=True):
            st.markdown(f"[Open API Docs]({settings.API_BASE_URL}/docs)")

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        SIGMA Product Catalog is a modern web application for browsing 
        ductile iron fittings with intelligent search and AI-powered features.

        Features:
        - Smart product search
        - AI-enhanced queries
        - HTS code generation
        - Product comparisons
        - Responsive design
        """)


if __name__ == "__main__":
    sidebar_info()
    main()
