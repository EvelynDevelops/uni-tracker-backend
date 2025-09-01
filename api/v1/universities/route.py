from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from models.university_models import (
    UniversityResponse, 
    UniversityListResponse, 
    SearchSuggestionResponse,
    CountriesResponse, 
    StatisticsResponse
)
from services.university_service import UniversityService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/universities", tags=["universities"])

@router.get("/", response_model=UniversityListResponse)
async def get_universities(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for university name"),
    country_code: Optional[str] = Query(None, description="Filter by country code"),
    sort_by: str = Query("name", description="Sort by field (name, country_code, created_at)"),
    sort_order: str = Query("asc", description="Sort order (asc, desc)")
):
    """
    Get universities with pagination, search, and filtering.
    
    - **page**: Page number (1-based)
    - **per_page**: Number of items per page (1-100)
    - **search**: Search term for university name
    - **country_code**: Filter by country code (e.g., "US", "CA")
    - **sort_by**: Sort by field (name, country_code, created_at)
    - **sort_order**: Sort order (asc, desc)
    """
    try:
        result = UniversityService.get_universities_with_pagination(
            page=page,
            per_page=per_page,
            search=search,
            country_code=country_code,
            sort_by=sort_by,
            sort_order=sort_order
        )
        return UniversityListResponse(**result)
    except Exception as e:
        logger.error(f"Error getting universities: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{university_id}", response_model=UniversityResponse)
async def get_university(university_id: str):
    """
    Get a specific university by ID.
    
    - **university_id**: University UUID
    """
    try:
        university = UniversityService.get_university_by_id(university_id)
        if not university:
            raise HTTPException(status_code=404, detail="University not found")
        return university
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting university {university_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/search/suggestions", response_model=List[SearchSuggestionResponse])
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    country_code: Optional[str] = Query(None, description="Filter by country code")
):
    """
    Get search suggestions for university names.
    Useful for autocomplete functionality.
    
    - **q**: Search query (minimum 1 character)
    - **limit**: Maximum number of suggestions (1-50)
    - **country_code**: Optional country filter
    """
    try:
        suggestions = UniversityService.get_search_suggestions(
            query=q,
            limit=limit,
            country_code=country_code
        )
        return [SearchSuggestionResponse(**suggestion) for suggestion in suggestions]
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/countries", response_model=CountriesResponse)
async def get_countries():
    """
    Get list of countries that have universities.
    Useful for country filter dropdown.
    """
    try:
        countries = UniversityService.get_countries()
        return CountriesResponse(countries=countries)
    except Exception as e:
        logger.error(f"Error getting countries: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    Get university statistics.
    Useful for dashboard or overview pages.
    """
    try:
        stats = UniversityService.get_statistics()
        return StatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/country/{country_code}", response_model=List[UniversityResponse])
async def get_universities_by_country(
    country_code: str,
    search: Optional[str] = Query(None, description="Search term for university name")
):
    """
    Get all universities in a specific country.
    
    - **country_code**: Country code (e.g., "US", "CA")
    - **search**: Optional search term
    """
    try:
        universities = UniversityService.get_universities_by_country(
            country_code=country_code,
            search=search
        )
        return universities
    except Exception as e:
        logger.error(f"Error getting universities for country {country_code}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 