"""
Product display components for Streamlit frontend
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from services.api_client import get_api_client
from utils.helpers import (
    display_api_error, create_product_card, create_specifications_table,
    show_loading, pagination_controls
)
from config.settings import settings


def product_catalog():
    """Main product catalog interface with grid card layout"""
    st.title("Product Catalog")
    st.caption("Browse our complete collection of ductile iron fittings")

    api_client = get_api_client()

    # Catalog controls
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        # Search within catalog
        catalog_search = st.text_input(
            "Filter catalog",
            placeholder="Search by product code, joint type, etc.",
            key="catalog_search"
        )

    with col2:
        view_limit = st.selectbox("Items per page", [6, 12, 18, 24], index=1, key="catalog_limit")

    with col3:
        sort_by = st.selectbox("Sort by", ["Product Code", "Joint Type", "Size Range"], key="catalog_sort")

    with col4:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filter controls
    with st.expander("Filter Options", expanded=False):
        filter_options = get_filter_options()
        filters = create_catalog_filters(filter_options)

    # Get products
    with show_loading():
        products_result = api_client.get_products(limit=None)

    if products_result["success"]:
        products = products_result["data"]

        # Apply catalog search filter
        if catalog_search:
            products = filter_products_by_search(products, catalog_search)

        # Apply other filters
        if filters:
            products = apply_catalog_filters(products, filters)

        # Apply sorting
        products = sort_products(products, sort_by)

        # Pagination
        total_products = len(products)
        start_idx = 0
        end_idx = min(view_limit, total_products)
        display_products = products[start_idx:end_idx]

        if display_products:
            # Results info
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"Showing {len(display_products)} of {total_products} products")
            with col2:
                if total_products > view_limit:
                    if st.button("Load More", use_container_width=True):
                        st.session_state.catalog_page = st.session_state.get("catalog_page", 1) + 1
                        st.rerun()

            st.divider()

            # Grid layout - 3 cards per row
            for i in range(0, len(display_products), 3):
                cols = st.columns(3)
                row_products = display_products[i:i+3]
                
                for j, product in enumerate(row_products):
                    with cols[j]:
                        create_enhanced_product_card(product, f"catalog_{product['id']}")

        else:
            st.warning("No products found matching your criteria.")
            st.info("Try adjusting your filters or search terms.")

    else:
        display_api_error(products_result["error"])


def get_filter_options():
    """Get filter options from API"""
    api_client = get_api_client()
    return api_client.get_filter_options()


def create_catalog_filters(filter_options):
    """Create catalog-specific filters"""
    filters = {}
    
    if filter_options["success"]:
        data = filter_options["data"]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if data.get("product_codes"):
                selected_code = st.multiselect(
                    "Product Codes",
                    options=data["product_codes"],
                    key="catalog_product_codes"
                )
                if selected_code:
                    filters["product_codes"] = selected_code
            
        with col2:
            if data.get("joint_types"):
                selected_joints = st.multiselect(
                    "Joint Types",
                    options=data["joint_types"],
                    key="catalog_joint_types"
                )
                if selected_joints:
                    filters["joint_types"] = selected_joints
        
        with col3:
            if data.get("body_designs"):
                selected_designs = st.multiselect(
                    "Body Designs",
                    options=data["body_designs"],
                    key="catalog_body_designs"
                )
                if selected_designs:
                    filters["body_designs"] = selected_designs
                    
        with col4:
            # Certification filters
            st.markdown("**Certifications:**")
            nsf61_only = st.checkbox("NSF 61 Only", key="catalog_nsf61")
            ul_listed_only = st.checkbox("UL Listed Only", key="catalog_ul")
            
            if nsf61_only or ul_listed_only:
                filters["certifications"] = {
                    "nsf61": nsf61_only,
                    "ul_listed": ul_listed_only
                }
    
    return filters


def filter_products_by_search(products: List[Dict], search_term: str) -> List[Dict]:
    """Filter products by search term"""
    if not search_term:
        return products
    
    search_lower = search_term.lower()
    filtered = []
    
    for product in products:
        # Search in various fields
        searchable_text = f"""
        {product['product_code']} {product['title']} {product['joint_type']} 
        {product['body_design']} {product['primary_standard']} 
        {product['specifications']['size_range']}
        """.lower()
        
        if search_lower in searchable_text:
            filtered.append(product)
    
    return filtered


def apply_catalog_filters(products: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to product list"""
    filtered = products.copy()
    
    for key, value in filters.items():
        if key == "product_codes" and value:
            filtered = [p for p in filtered if p['product_code'] in value]
        elif key == "joint_types" and value:
            filtered = [p for p in filtered if p['joint_type'] in value]
        elif key == "body_designs" and value:
            filtered = [p for p in filtered if p['body_design'] in value]
        elif key == "certifications" and value:
            if value.get("nsf61"):
                filtered = [p for p in filtered if p['certifications']['nsf61']]
            if value.get("ul_listed"):
                filtered = [p for p in filtered if "3\"" in p['certifications']['ul_listed']]
    
    return filtered


def sort_products(products: List[Dict], sort_by: str) -> List[Dict]:
    """Sort products based on criteria"""
    if sort_by == "Product Code":
        return sorted(products, key=lambda x: x['product_code'])
    elif sort_by == "Joint Type":
        return sorted(products, key=lambda x: x['joint_type'])
    elif sort_by == "Size Range":
        return sorted(products, key=lambda x: x['specifications']['size_range'])
    
    return products


def create_enhanced_product_card(product: Dict[str, Any], key_prefix: str):
    """Create enhanced product card with better visual design"""
    with st.container(border=True):
        # Product header with status badge
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {product['product_code']}")
            
        with col2:
            # Status badge based on certifications
            if product['certifications']['nsf61']:
                st.success("NSF 61")
            else:
                st.info("Standard")

        # Product title
        st.markdown(f"**{product['title']}**")
        
        # Key specifications in organized layout
        spec_col1, spec_col2 = st.columns(2)
        
        with spec_col1:
            st.markdown(f"**Joint:** {product['joint_type']}")
            st.markdown(f"**Design:** {product['body_design']}")
            
        with spec_col2:
            st.markdown(f"**Size:** {product['specifications']['size_range']}")
            
            # Get max pressure
            pressure_ratings = product['specifications']['pressure_ratings']
            if pressure_ratings:
                max_pressure = max([pr['psi'] for pr in pressure_ratings])
                st.markdown(f"**Max PSI:** {max_pressure}")

        # Standard info
        st.caption(f"Standard: {product['primary_standard']}")
        
        # Certifications row with text indicators
        cert_cols = st.columns(4)
        certifications = product['certifications']
        
        with cert_cols[0]:
            if certifications['nsf61']:
                st.markdown("PASS NSF 61")
            else:
                st.markdown("FAIL NSF 61")
                
        with cert_cols[1]:
            if certifications['nsf372']:
                st.markdown("PASS NSF 372")
            else:
                st.markdown("FAIL NSF 372")
                
        with cert_cols[2]:
            if "3\"" in certifications['ul_listed']:
                st.markdown("PASS UL Listed")
            else:
                st.markdown("FAIL UL Listed")
                
        with cert_cols[3]:
            if "3\"" in certifications['fm_approved']:
                st.markdown("PASS FM Approved")
            else:
                st.markdown("FAIL FM Approved")

        st.divider()

        # Action buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)

        with btn_col1:
            if st.button("Details", key=f"{key_prefix}_details", use_container_width=True):
                st.session_state.selected_product = product['id']
                st.rerun()

        with btn_col2:
            if st.button("HTS Codes", key=f"{key_prefix}_hts", use_container_width=True):
                st.session_state.show_hts = product['id']
                st.rerun()

        with btn_col3:
            if st.button("Similar", key=f"{key_prefix}_similar", use_container_width=True):
                st.session_state.show_similar = product['id']
                st.rerun()


def product_detail_view(product_id: str):
    """Detailed product view"""
    api_client = get_api_client()

    with show_loading():
        product_result = api_client.get_product(product_id)

    if product_result["success"]:
        product = product_result["data"]

        # Header with back button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Back", use_container_width=True):
                st.session_state.pop("selected_product", None)
                st.rerun()
        with col2:
            st.title(f"{product['title']}")

        # Product overview card
        with st.container(border=True):
            st.markdown("## Product Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Product Code", product['product_code'])
                st.metric("Joint Type", product['joint_type'])
                
            with col2:
                st.metric("Body Design", product['body_design'])
                st.metric("Size Range", product['specifications']['size_range'])
                
            with col3:
                max_pressure = max([pr['psi'] for pr in product['specifications']['pressure_ratings']], default=0)
                st.metric("Max Pressure", f"{max_pressure} PSI")
                st.metric("Standard", product['primary_standard'])

        # Detailed specifications
        st.markdown("## Detailed Specifications")
        specs_df = create_specifications_table(product)
        st.dataframe(specs_df, use_container_width=True, hide_index=True)

        # Construction details
        st.markdown("## Construction Details")
        construction = product['construction']

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("### Materials & Coatings")
                st.write(f"**Lining:** {construction['lining']}")
                st.write(f"**Interior Coating:** {construction['coating']['interior']}")
                st.write(f"**Exterior Coating:** {construction['coating']['exterior']}")

        with col2:
            with st.container(border=True):
                st.markdown("### Gaskets & Fasteners")
                st.write(f"**Standard Gasket:** {construction['gaskets']['standard']}")
                if construction['gaskets'].get('optional'):
                    st.write(f"**Optional Gaskets:** {', '.join(construction['gaskets']['optional'])}")
                if construction.get('fasteners'):
                    st.write(f"**Fasteners:** {construction['fasteners']}")

        # Testing & Certifications
        st.markdown("## Testing & Certifications")

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown("### Testing")
                testing = product['testing']
                st.write(f"**Hydrostatic Testing:** {'Yes' if testing['hydrostatic_testing'] else 'No'}")
                st.write(f"**Heat Coded Traceability:** {'Yes' if testing['heat_coded_traceability'] else 'No'}")
                st.write("**Standards:**")
                for standard in testing['standards']:
                    st.write(f"- {standard}")

        with col2:
            with st.container(border=True):
                st.markdown("### Certifications")
                cert = product['certifications']
                st.write(f"**NSF 61:** {'Certified' if cert['nsf61'] else 'Not Certified'}")
                st.write(f"**NSF 61 Annex G:** {'Certified' if cert['nsf61_annex_g'] else 'Not Certified'}")
                st.write(f"**NSF 372:** {'Certified' if cert['nsf372'] else 'Not Certified'}")
                st.write(f"**UL Listed:** {cert['ul_listed']}")
                st.write(f"**FM Approved:** {cert['fm_approved']}")

        # Action buttons
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("Generate HTS Codes", use_container_width=True, type="primary"):
                st.session_state.show_hts = product_id
                st.rerun()

        with col2:
            if st.button("Find Similar Products", use_container_width=True):
                st.session_state.show_similar = product_id
                st.rerun()

    else:
        display_api_error(product_result["error"])
        if st.button("Back to Catalog"):
            st.session_state.pop("selected_product", None)
            st.rerun()


def product_comparison():
    """Product comparison interface"""
    st.title("Product Comparison")
    st.caption("Compare up to 5 products side by side")

    api_client = get_api_client()
    products_result = api_client.get_products()

    if products_result["success"]:
        products = products_result["data"]
        product_options = {f"{p['title']} ({p['product_code']})": p['id'] for p in products}

        st.markdown("### Select Products to Compare")
        selected_products = st.multiselect(
            "Choose 2-5 products for comparison",
            options=list(product_options.keys()),
            help="Select multiple products to see side-by-side comparison"
        )

        if len(selected_products) < 2:
            st.info("Please select at least 2 products to compare.")
        elif len(selected_products) > 5:
            st.warning("Please select no more than 5 products for comparison.")
        else:
            product_ids = [product_options[name] for name in selected_products]

            if st.button("Compare Selected Products", type="primary"):
                with show_loading():
                    comparison_result = api_client.compare_products(product_ids)

                if comparison_result["success"]:
                    comparison_data = comparison_result["data"]

                    st.success(f"Comparing {len(comparison_data['products'])} products")

                    # Enhanced comparison display
                    display_product_comparison(comparison_data["products"])

                else:
                    display_api_error(comparison_result["error"])
    else:
        display_api_error(products_result["error"])


def display_product_comparison(products: List[Dict[str, Any]]):
    """Display enhanced product comparison"""
    # Quick comparison cards
    st.markdown("### Quick Comparison")
    cols = st.columns(len(products))
    
    for i, product in enumerate(products):
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"**{product['product_code']}**")
                st.caption(product['title'])
                st.write(f"Joint: {product['joint_type']}")
                st.write(f"Design: {product['body_design']}")
                st.write(f"Size: {product['specifications']['size_range']}")
                
                max_pressure = max([pr['psi'] for pr in product['specifications']['pressure_ratings']], default=0)
                st.metric("Max PSI", max_pressure)

    # Detailed comparison table
    st.markdown("### Detailed Comparison")
    comparison_df = create_comparison_table(products)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)


def create_comparison_table(products: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create detailed comparison table"""
    comparison_data = {
        "Specification": [
            "Title",
            "Product Code",
            "Joint Type",
            "Body Design",
            "Size Range",
            "Material Type",
            "Material Standard",
            "Primary Standard",
            "Max Pressure (PSI)",
            "NSF 61 Certified",
            "UL Listed",
            "FM Approved"
        ]
    }

    for product in products:
        max_pressure = max([pr['psi'] for pr in product['specifications']['pressure_ratings']], default=0)

        comparison_data[product['product_code']] = [
            product['title'],
            product['product_code'],
            product['joint_type'],
            product['body_design'],
            product['specifications']['size_range'],
            product['specifications']['material']['type'],
            product['specifications']['material']['standard'],
            product['primary_standard'],
            f"{max_pressure} PSI",
            "Yes" if product['certifications']['nsf61'] else "No",
            product['certifications']['ul_listed'],
            product['certifications']['fm_approved']
        ]

    return pd.DataFrame(comparison_data)