"""
Search API endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from app.models.product import SearchQuery, SearchResponse, SearchResult
from app.services.search_service import search_service
from app.services.openai_service import openai_service
from app.utils.helpers import clean_query, validate_filters, calculate_search_metrics

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., description="Search query"),
    limit: Optional[int] = Query(default=10, ge=1, le=50),
    enhanced: Optional[bool] = Query(default=False, description="Use AI-enhanced search"),
    product_code: Optional[str] = Query(default=None),
    joint_type: Optional[str] = Query(default=None),
    body_design: Optional[str] = Query(default=None),
    min_pressure: Optional[int] = Query(default=None),
    max_pressure: Optional[int] = Query(default=None)
):
    """Search products with optional AI enhancement"""
    try:
        # Clean and validate query
        cleaned_query = clean_query(q)
        if not cleaned_query:
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        # Build filters
        filters = {}
        if product_code:
            filters["product_code"] = product_code
        if joint_type:
            filters["joint_type"] = joint_type
        if body_design:
            filters["body_design"] = body_design
        if min_pressure:
            filters["min_pressure"] = min_pressure
        if max_pressure:
            filters["max_pressure"] = max_pressure
        
        validated_filters = validate_filters(filters)
        
        # Perform search
        if enhanced:
            # Use AI-enhanced search
            results = await openai_service.enhanced_search(cleaned_query, limit)
            search_time_ms = 0  # AI search doesn't track time the same way
        else:
            # Use basic search
            results, search_time_ms = search_service.search_products(
                cleaned_query, limit, validated_filters
            )
        
        return SearchResponse(
            query=cleaned_query,
            total_results=len(results),
            results=results,
            search_time_ms=search_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/", response_model=SearchResponse)
async def search_products_post(search_query: SearchQuery):
    """Search products using POST with request body"""
    try:
        cleaned_query = clean_query(search_query.query)
        if not cleaned_query:
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        validated_filters = validate_filters(search_query.filters) if search_query.filters else {}
        
        results, search_time_ms = search_service.search_products(
            cleaned_query, 
            search_query.limit, 
            validated_filters
        )
        
        return SearchResponse(
            query=cleaned_query,
            total_results=len(results),
            results=results,
            search_time_ms=search_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: Optional[int] = Query(default=8, ge=1, le=20)
):
    """Get search suggestions for autocomplete"""
    try:
        if len(q.strip()) < 2:
            return {"suggestions": []}
        
        suggestions = search_service.get_search_suggestions(q.strip())
        
        return {
            "query": q,
            "suggestions": suggestions[:limit]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.get("/analytics")
async def get_search_analytics():
    """Get search analytics and popular terms"""
    try:
        # This would typically connect to analytics storage
        # For now, return sample data
        return {
            "popular_searches": [
                {"query": "mechanical joint", "count": 45},
                {"query": "C153", "count": 38},
                {"query": "push-on", "count": 32},
                {"query": "ductile iron", "count": 28},
                {"query": "flanged", "count": 24}
            ],
            "recent_searches": [
                "6 inch mechanical joint",
                "C110 flanged fittings",
                "high pressure fittings",
                "compact body design",
                "AWWA C153"
            ],
            "search_trends": {
                "mechanical_joint": 35.2,
                "push_on": 28.7,
                "flanged": 18.9,
                "compact": 17.2
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/similar/{product_id}")
async def get_similar_products(
    product_id: str,
    limit: Optional[int] = Query(default=5, ge=1, le=10)
):
    """Find products similar to the given product"""
    try:
        from app.services.product_service import product_service
        
        # Get the reference product
        reference_product = product_service.get_product_by_id(product_id)
        if not reference_product:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
        
        # Create a search query based on the product characteristics
        search_terms = [
            reference_product.product_code,
            reference_product.joint_type,
            reference_product.body_design
        ]
        
        # Search for similar products
        results, _ = search_service.search_products(
            " ".join(search_terms), 
            limit + 1  # +1 to account for the original product
        )
        
        # Filter out the original product
        similar_products = [
            result for result in results 
            if result.product.id != product_id
        ][:limit]
        
        return {
            "reference_product_id": product_id,
            "similar_products": similar_products,
            "similarity_criteria": search_terms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find similar products: {str(e)}")