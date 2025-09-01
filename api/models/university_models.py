from pydantic import BaseModel
from typing import List, Optional

class UniversityResponse(BaseModel):
    id: str
    name: str
    country_code: str
    state_province: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    domain: Optional[str] = None
    aliases: List[str] = []
    external_ids: dict = {}
    apply_portals: List[dict] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True

class UniversityListResponse(BaseModel):
    items: List[UniversityResponse]
    total: int
    page: int
    per_page: int
    pages: int

class SearchSuggestionResponse(BaseModel):
    id: str
    name: str
    country_code: str
    domain: Optional[str] = None

class CountriesResponse(BaseModel):
    countries: List[str]

class StatisticsResponse(BaseModel):
    total_universities: int
    total_countries: int
    with_website: int
    with_domain: int 