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
    """Main product catalog interface"""
    st.title("Product Catalog")

    api_client = get_api_client()

    # Catalog controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("### Browse our complete product catalog")

    with col2:
        view_limit = st.selectbox("Items per page", [5, 10, 20, 50], index=1)

    with col3:
        if st.button("Refresh Catalog"):
            st.cache_data.clear()
            st.rerun()

    # Get products
    with show_loading():
        products_result = api_client.get_products(limit=view_limit)

    if products_result["success"]:
        products = products_result["data"]

        if products:
            st.success(f"Loaded {len(products)} products")

            for product in products:
                create_product_card(product)

                col1, col2, col3, col4 = st.columns([1, 1, 1, 3])

                with col1:
                    if st.button("Details", key=f"details_{product['id']}"):
                        st.session_state.selected_product = product['id']
                        st.rerun()

                with col2:
                    if st.button("HTS Codes", key=f"hts_{product['id']}"):
                        st.session_state.show_hts = product['id']
                        st.rerun()

                with col3:
                    if st.button("Similar", key=f"similar_{product['id']}"):
                        st.session_state.show_similar = product['id']
                        st.rerun()

                st.divider()
        else:
            st.info("No products found in the catalog.")
    else:
        display_api_error(products_result["error"])


def product_detail_view(product_id: str):
    """Detailed product view"""
    api_client = get_api_client()

    with show_loading():
        product_result = api_client.get_product(product_id)

    if product_result["success"]:
        product = product_result["data"]

        st.title(f"{product['title']}")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Back to Catalog"):
                st.session_state.pop("selected_product", None)
                st.rerun()

        st.markdown("## Product Overview")
        create_product_card(product)

        st.markdown("## Detailed Specifications")
        specs_df = create_specifications_table(product)
        st.dataframe(specs_df, use_container_width=True, hide_index=True)

        st.markdown("## Construction Details")
        construction = product['construction']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Materials & Coatings")
            st.write(f"Lining: {construction['lining']}")
            st.write(f"Interior Coating: {construction['coating']['interior']}")
            st.write(f"Exterior Coating: {construction['coating']['exterior']}")

        with col2:
            st.markdown("### Gaskets & Fasteners")
            st.write(f"Standard Gasket: {construction['gaskets']['standard']}")
            if construction['gaskets'].get('optional'):
                st.write(f"Optional Gaskets: {', '.join(construction['gaskets']['optional'])}")
            if construction.get('fasteners'):
                st.write(f"Fasteners: {construction['fasteners']}")

        if construction.get('joint_details'):
            st.markdown("### Joint Details")
            for key, value in construction['joint_details'].items():
                st.write(f"{key.replace('_', ' ').title()}: {value}")

        st.markdown("## Testing & Certifications")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Testing")
            testing = product['testing']
            st.write(f"Hydrostatic Testing: {'Yes' if testing['hydrostatic_testing'] else 'No'}")
            st.write(f"Heat Coded Traceability: {'Yes' if testing['heat_coded_traceability'] else 'No'}")
            st.write("Standards:")
            for standard in testing['standards']:
                st.write(f"- {standard}")

        with col2:
            st.markdown("### Certifications")
            cert = product['certifications']
            st.write(f"NSF 61: {'Certified' if cert['nsf61'] else 'Not Certified'}")
            st.write(f"NSF 61 Annex G: {'Certified' if cert['nsf61_annex_g'] else 'Not Certified'}")
            st.write(f"NSF 372: {'Certified' if cert['nsf372'] else 'Not Certified'}")
            st.write(f"UL Listed: {cert['ul_listed']}")
            st.write(f"FM Approved: {cert['fm_approved']}")

        st.markdown("## Installation Requirements")
        installation = product['installation']

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Standards")
            for standard in installation['standards']:
                st.write(f"- {standard}")

        with col2:
            st.markdown("### Compatible Pipes")
            for pipe in installation['compatible_pipes']:
                st.write(f"- {pipe}")

        if installation.get('special_notes'):
            st.warning(f"Important Note: {installation['special_notes']}")

        st.markdown("## Documentation")
        metadata = product['metadata']

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"Source: {metadata['source_document']}")
        with col2:
            st.info(f"Revision: {metadata['revision_date']}")
        with col3:
            st.info(f"Category: {metadata['category']}")

        st.markdown("### Keywords")
        keyword_cols = st.columns(min(len(metadata['keywords']), 4))
        for i, keyword in enumerate(metadata['keywords']):
            with keyword_cols[i % 4]:
                st.markdown(f"`{keyword}`")

        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            if st.button("Generate HTS Codes"):
                st.session_state.show_hts = product_id
                st.rerun()

        with col2:
            if st.button("Find Similar Products"):
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

    api_client = get_api_client()
    products_result = api_client.get_products()

    if products_result["success"]:
        products = products_result["data"]
        product_options = {f"{p['title']} ({p['product_code']})": p['id'] for p in products}

        st.markdown("### Select Products to Compare")
        selected_products = st.multiselect(
            "Choose 2-5 products for comparison:",
            options=list(product_options.keys()),
            help="Select multiple products to see side-by-side comparison"
        )

        if len(selected_products) < 2:
            st.info("Please select at least 2 products to compare.")
        elif len(selected_products) > 5:
            st.warning("Please select no more than 5 products for comparison.")
        else:
            product_ids = [product_options[name] for name in selected_products]

            if st.button("Compare Selected Products"):
                with show_loading():
                    comparison_result = api_client.compare_products(product_ids)

                if comparison_result["success"]:
                    comparison_data = comparison_result["data"]

                    st.success(f"Comparing {len(comparison_data['products'])} products")

                    comparison_df = create_comparison_table(comparison_data["products"])
                    st.dataframe(comparison_df, use_container_width=True)

                    st.markdown("### Quick Comparison Matrix")
                    matrix = comparison_data["comparison_matrix"]

                    matrix_data = {
                        "Product": [p['title'] for p in comparison_data['products']],
                        "Joint Type": matrix["joint_types"],
                        "Body Design": matrix["body_designs"],
                        "Size Range": matrix["size_ranges"],
                        "Standard": matrix["standards"]
                    }

                    matrix_df = pd.DataFrame(matrix_data)
                    st.dataframe(matrix_df, use_container_width=True, hide_index=True)
                else:
                    display_api_error(comparison_result["error"])
    else:
        display_api_error(products_result["error"])


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
