"""
HTS Code API endpoints
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.models.product import HTSCodeResponse, HTSCodeSuggestion
from app.services.openai_service import openai_service
from app.services.product_service import product_service

router = APIRouter()


@router.get("/{product_id}", response_model=HTSCodeResponse)
async def get_hts_codes(product_id: str):
    """Get HTS code suggestions for a specific product"""
    try:
        # Get the product
        product = product_service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found")
        
        # Generate HTS code suggestions
        suggestions = await openai_service.generate_hts_codes(product)
        
        return HTSCodeResponse(
            product_id=product_id,
            suggestions=suggestions,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate HTS codes: {str(e)}")


@router.post("/bulk")
async def generate_bulk_hts_codes(
    product_ids: List[str],
    background_tasks: BackgroundTasks
):
    """Generate HTS codes for multiple products (async background task)"""
    try:
        if len(product_ids) > 20:
            raise HTTPException(
                status_code=400, 
                detail="Maximum 20 products allowed for bulk processing"
            )
        
        # Validate all product IDs exist
        missing_products = []
        valid_products = []
        
        for product_id in product_ids:
            product = product_service.get_product_by_id(product_id)
            if product:
                valid_products.append(product)
            else:
                missing_products.append(product_id)
        
        if missing_products:
            raise HTTPException(
                status_code=404,
                detail=f"Products not found: {', '.join(missing_products)}"
            )
        
        # Start background task for HTS generation
        task_id = f"hts_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        background_tasks.add_task(
            process_bulk_hts_generation,
            task_id,
            valid_products
        )
        
        return {
            "task_id": task_id,
            "status": "started",
            "products_count": len(valid_products),
            "estimated_completion": "2-5 minutes",
            "check_status_url": f"/api/v1/hts-codes/bulk-status/{task_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bulk HTS generation: {str(e)}")


@router.get("/bulk-status/{task_id}")
async def get_bulk_status(task_id: str):
    """Get status of bulk HTS code generation"""
    try:
        # In a real implementation, this would check task status from a queue/database
        # For now, return a mock response
        return {
            "task_id": task_id,
            "status": "in_progress",
            "progress": "3/5 products completed",
            "estimated_remaining": "1-2 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.get("/search/{hts_code}")
async def search_by_hts_code(hts_code: str):
    """Find products that might match a given HTS code"""
    try:
        # This would typically involve reverse lookup functionality
        # For now, return a placeholder response
        return {
            "hts_code": hts_code,
            "description": "Pipe fittings of iron or steel",
            "matching_products": [],
            "similar_codes": [
                {"code": "7307.99.1000", "description": "Other tube or pipe fittings"},
                {"code": "8481.80.9090", "description": "Other valves and similar articles"}
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search by HTS code: {str(e)}")


@router.get("/validate/{hts_code}")
async def validate_hts_code(hts_code: str):
    """Validate if an HTS code format is correct"""
    try:
        import re
        
        # Basic HTS code validation (US format)
        # Pattern: NNNN.NN.NNNN
        hts_pattern = r'^\d{4}\.\d{2}\.\d{4}$'
        
        is_valid = bool(re.match(hts_pattern, hts_code))
        
        result = {
            "hts_code": hts_code,
            "is_valid": is_valid,
            "format": "NNNN.NN.NNNN"
        }
        
        if not is_valid:
            result["error"] = "HTS code must be in format NNNN.NN.NNNN (e.g., 7307.99.1000)"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate HTS code: {str(e)}")


async def process_bulk_hts_generation(task_id: str, products: List):
    """Background task to process bulk HTS code generation"""
    try:
        # In a real implementation, this would:
        # 1. Update task status in database
        # 2. Process each product
        # 3. Store results
        # 4. Send notification when complete
        
        print(f"Starting bulk HTS generation for task {task_id}")
        print(f"Processing {len(products)} products...")
        
        # Simulate processing
        for i, product in enumerate(products):
            print(f"Processing product {i+1}/{len(products)}: {product.title}")
            # Generate HTS codes for each product
            suggestions = await openai_service.generate_hts_codes(product)
            # Store results (would save to database in real implementation)
            
        print(f"Completed bulk HTS generation for task {task_id}")
        
    except Exception as e:
        print(f"Error in bulk HTS generation: {e}")