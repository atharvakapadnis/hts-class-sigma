"""
Product API endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models.product import Product
from app.services.product_service import product_service
from app.utils.helpers import validate_filters, format_product_summary

router = APIRouter()


@router.get("/", response_model=List[Product])
async def get_all_products(
    limit: Optional[int] = Query(default=None, ge=1, le=100),
    product_code: Optional[str] = Query(default=None),
    joint_type: Optional[str] = Query(default=None),
    body_design: Optional[str] = Query(default=None)
):
    """Get all products with optional filtering"""
    try:
        # Build filters
        filters = {}
        if product_code:
            filters["product_code"] = product_code
        if joint_type:
            filters["joint_type"] = joint_type
        if body_design:
            filters["body_design"] = body_design
        
        # Get products
        if filters:
            products = product_service.filter_products(validate_filters(filters))
        else:
            products = product_service.get_all_products()
        
        # Apply limit
        if limit:
            products = products[:limit]
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve products: {str(e)}")


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    try:
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product: {str(e)}")


@router.get("/{product_id}/summary")
async def get_product_summary(product_id: str):
    """Get a brief summary of a product"""
    try:
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
        
        return {
            "id": product.id,
            "title": product.title,
            "product_code": product.product_code,
            "joint_type": product.joint_type,
            "size_range": product.specifications.size_range,
            "pressure_ratings": product.specifications.pressure_ratings,
            "summary": format_product_summary(product)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve product summary: {str(e)}")


@router.get("/filters/options")
async def get_filter_options():
    """Get available filter options for products"""
    try:
        return {
            "product_codes": product_service.get_product_codes(),
            "joint_types": product_service.get_joint_types(),
            "body_designs": product_service.get_body_designs()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve filter options: {str(e)}")


@router.post("/compare")
async def compare_products(product_ids: List[str]):
    """Compare multiple products"""
    try:
        if len(product_ids) < 2:
            raise HTTPException(status_code=400, detail="At least 2 products required for comparison")
        
        if len(product_ids) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 products allowed for comparison")
        
        products = []
        missing_ids = []
        
        for product_id in product_ids:
            product = product_service.get_product_by_id(product_id)
            if product:
                products.append(product)
            else:
                missing_ids.append(product_id)
        
        if missing_ids:
            raise HTTPException(
                status_code=404, 
                detail=f"Products not found: {', '.join(missing_ids)}"
            )
        
        # Build comparison data
        comparison = {
            "products": products,
            "comparison_matrix": {
                "joint_types": [p.joint_type for p in products],
                "body_designs": [p.body_design for p in products],
                "size_ranges": [p.specifications.size_range for p in products],
                "standards": [p.primary_standard for p in products]
            }
        }
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compare products: {str(e)}")