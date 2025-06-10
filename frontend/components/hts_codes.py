"""
HTS Codes components for Streamlit frontend
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from services.api_client import get_api_client
from utils.helpers import display_api_error, create_hts_display, show_loading


def hts_codes_interface():
    """Main HTS codes interface"""
    st.title("HTS Code Generator")

    st.markdown("""
    Generate Harmonized Tariff Schedule (HTS) codes for SIGMA products using AI analysis.
    HTS codes are essential for international trade classification and customs purposes.
    """)

    api_client = get_api_client()

    products_result = api_client.get_products()

    if products_result["success"]:
        products = products_result["data"]

        product_options = {}
        for product in products:
            display_name = f"{product['title']} ({product['product_code']})"
            product_options[display_name] = product['id']

        selected_product_name = st.selectbox(
            "Select Product for HTS Code Generation:",
            options=list(product_options.keys()),
            help="Choose a product to generate HTS codes"
        )

        if selected_product_name:
            product_id = product_options[selected_product_name]

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Generate HTS Codes", type="primary"):
                    generate_hts_codes(product_id)

            with col2:
                if st.button("View Product Details"):
                    st.session_state.selected_product = product_id
                    st.rerun()

    else:
        display_api_error(products_result["error"])

    # HTS Code validation tool
    st.markdown("---")
    st.markdown("## HTS Code Validation Tool")

    hts_input = st.text_input(
        "Enter HTS Code to Validate:",
        placeholder="e.g., 7307.99.1000",
        help="Enter an HTS code in format NNNN.NN.NNNN"
    )

    if hts_input:
        if st.button("Validate HTS Code"):
            validate_hts_code(hts_input)


def generate_hts_codes(product_id: str):
    """Generate HTS codes for a specific product"""
    api_client = get_api_client()

    with show_loading():
        hts_result = api_client.get_hts_codes(product_id)

    if hts_result["success"]:
        data = hts_result["data"]

        st.success(f"Generated HTS codes for product: {data['product_id']}")
        st.info(f"Generated at: {data['generated_at']}")

        if data["suggestions"]:
            st.markdown("### HTS Code Suggestions")
            create_hts_display(data["suggestions"])

            # Export options
            st.markdown("### Export Options")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Copy to Clipboard"):
                    hts_text = "\n".join([
                        f"{s['code']}: {s['description']} (Confidence: {s['confidence']:.1%})"
                        for s in data["suggestions"]
                    ])
                    st.text_area("HTS Codes:", value=hts_text, height=100)

            with col2:
                df = pd.DataFrame(data["suggestions"])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"hts_codes_{product_id}.csv",
                    mime="text/csv"
                )

            with col3:
                if st.button("Regenerate"):
                    st.cache_data.clear()
                    generate_hts_codes(product_id)

        else:
            st.warning("No HTS code suggestions were generated for this product.")

    else:
        display_api_error(hts_result["error"])


def validate_hts_code(hts_code: str):
    """Validate HTS code format"""
    api_client = get_api_client()

    with show_loading():
        validation_result = api_client.validate_hts_code(hts_code)

    if validation_result["success"]:
        data = validation_result["data"]

        if data["is_valid"]:
            st.success(f"Valid HTS Code: {data['hts_code']}")
            st.info(f"Format: {data['format']}")
        else:
            st.error(f"Invalid HTS Code: {data['hts_code']}")
            st.warning(data.get("error", "Invalid format"))
            st.info(f"Expected format: {data['format']}")

    else:
        display_api_error(validation_result["error"])


def hts_product_view(product_id: str):
    """Show HTS codes for a specific product"""
    st.markdown("## HTS Codes")

    api_client = get_api_client()

    product_result = api_client.get_product(product_id)

    if product_result["success"]:
        product = product_result["data"]
        st.markdown(f"### For: {product['title']}")

        if st.button("Generate HTS Codes for This Product"):
            generate_hts_codes(product_id)

        if f"hts_{product_id}" in st.session_state:
            st.markdown("### Cached HTS Codes")
            create_hts_display(st.session_state[f"hts_{product_id}"])

    else:
        display_api_error(product_result["error"])


def bulk_hts_interface():
    """Bulk HTS code generation interface"""
    st.title("Bulk HTS Code Generation")

    st.markdown("""
    Generate HTS codes for multiple products simultaneously. 
    This is useful for large product catalogs or batch exports.
    """)

    api_client = get_api_client()
    products_result = api_client.get_products()

    if products_result["success"]:
        products = products_result["data"]

        product_options = {}
        for product in products:
            display_name = f"{product['title']} ({product['product_code']})"
            product_options[display_name] = product['id']

        selected_products = st.multiselect(
            "Select Products for Bulk HTS Generation:",
            options=list(product_options.keys()),
            help="Choose multiple products (max 20)"
        )

        if selected_products:
            if len(selected_products) > 20:
                st.error("Maximum 20 products allowed for bulk processing")
            else:
                st.success(f"Selected {len(selected_products)} products")

                if st.button("Start Bulk Generation"):
                    product_ids = [product_options[name] for name in selected_products]

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    results = []

                    for i, product_id in enumerate(product_ids):
                        status_text.text(f"Processing {i+1}/{len(product_ids)}: {selected_products[i]}")

                        hts_result = api_client.get_hts_codes(product_id)

                        if hts_result["success"]:
                            results.append({
                                "product": selected_products[i],
                                "product_id": product_id,
                                "suggestions": hts_result["data"]["suggestions"]
                            })

                        progress_bar.progress((i + 1) / len(product_ids))

                    status_text.text("Bulk processing complete!")

                    if results:
                        st.markdown("### Bulk Generation Results")

                        for result in results:
                            with st.expander(f"{result['product']}"):
                                if result["suggestions"]:
                                    create_hts_display(result["suggestions"])
                                else:
                                    st.warning("No suggestions generated")

                        if st.button("Export All Results"):
                            export_bulk_results(results)

        else:
            st.info("Please select products for bulk HTS generation")

    else:
        display_api_error(products_result["error"])


def export_bulk_results(results: List[Dict[str, Any]]):
    """Export bulk HTS results"""
    export_data = []

    for result in results:
        for suggestion in result["suggestions"]:
            export_data.append({
                "Product": result["product"],
                "Product ID": result["product_id"],
                "HTS Code": suggestion["code"],
                "Description": suggestion["description"],
                "Confidence": suggestion["confidence"],
                "Reasoning": suggestion.get("reasoning", "")
            })

    if export_data:
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)

        st.download_button(
            label="Download Bulk Results (CSV)",
            data=csv,
            file_name="bulk_hts_codes.csv",
            mime="text/csv"
        )

        st.success("Bulk results ready for download!")
    else:
        st.warning("No data to export")
