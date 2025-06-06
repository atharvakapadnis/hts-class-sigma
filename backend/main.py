"""
SIGMA Product Catalog FastAPI Application
Main entry point for the API server
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import products, search, hts_codes


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="Product catalog API with AI-powered search and HTS code suggestions",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(
        products.router,
        prefix="/api/v1/products",
        tags=["products"]
    )
    
    app.include_router(
        search.router,
        prefix="/api/v1/search",
        tags=["search"]
    )
    
    app.include_router(
        hts_codes.router,
        prefix="/api/v1/hts-codes",
        tags=["hts-codes"]
    )

    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "SIGMA Product Catalog API",
            "version": settings.PROJECT_VERSION,
            "docs": "/docs"
        }

    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy", "service": "sigma-product-catalog"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )