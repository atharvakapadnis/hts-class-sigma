"""
Pydantic models for product data structures
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MaterialSpec(BaseModel):
    """Material specification model"""
    type: str
    standard: str
    grades: List[str]


class PressureRating(BaseModel):
    """Pressure rating model"""
    sizes: str
    psi: int


class DeflectionLimit(BaseModel):
    """Deflection limit model"""
    sizes: str
    max_degrees: int
    note: Optional[str] = None


class Specifications(BaseModel):
    """Product specifications model"""
    size_range: str
    material: MaterialSpec
    pressure_ratings: List[PressureRating]
    deflection_limits: List[DeflectionLimit]


class Coating(BaseModel):
    """Coating specification model"""
    interior: str
    exterior: str


class Gaskets(BaseModel):
    """Gasket specification model"""
    standard: str
    optional: List[str]
    standard_ref: str


class Construction(BaseModel):
    """Construction details model"""
    lining: str
    coating: Coating
    gaskets: Gaskets
    fasteners: Optional[str] = None
    joint_details: Optional[Dict[str, str]] = None


class Testing(BaseModel):
    """Testing specifications model"""
    hydrostatic_testing: bool
    heat_coded_traceability: bool
    standards: List[str]


class Certifications(BaseModel):
    """Certification model"""
    nsf61: bool
    nsf61_annex_g: bool
    nsf372: bool
    ul_listed: str
    fm_approved: str


class Installation(BaseModel):
    """Installation requirements model"""
    standards: List[str]
    compatible_pipes: List[str]
    special_notes: Optional[str] = None


class ProductMetadata(BaseModel):
    """Product metadata model"""
    source_document: str
    revision_date: str
    category: str
    subcategory: str
    keywords: List[str]
    search_text: str


class Product(BaseModel):
    """Main product model"""
    id: str
    product_code: str
    title: str
    joint_type: str
    body_design: str
    primary_standard: str
    specifications: Specifications
    construction: Construction
    testing: Testing
    certifications: Certifications
    installation: Installation
    metadata: ProductMetadata


class ProductCatalog(BaseModel):
    """Product catalog container model"""
    metadata: Dict[str, Any]
    products: List[Product]


class SearchQuery(BaseModel):
    """Search query model"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: Optional[int] = Field(default=10, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Search result model"""
    product: Product
    score: Optional[float] = None
    match_reason: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    total_results: int
    results: List[SearchResult]
    search_time_ms: int


class HTSCodeSuggestion(BaseModel):
    """HTS code suggestion model"""
    code: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class HTSCodeResponse(BaseModel):
    """HTS code response model"""
    product_id: str
    suggestions: List[HTSCodeSuggestion]
    generated_at: str