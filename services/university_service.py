from typing import List, Optional
from db.orms import UniversityCRUD
import logging

logger = logging.getLogger(__name__)

class UniversityService:
    """Service layer for university business logic"""
    
    @staticmethod
    def get_universities_with_pagination(
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        country_code: Optional[str] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ):
        """Get universities with pagination and filtering"""
        try:
            # Get universities based on filters
            if search or country_code:
                universities = UniversityCRUD.search_universities(
                    search_term=search or "", 
                    country_code=country_code, 
                    limit=per_page * 10  # Temporary limit
                )
            else:
                universities = UniversityCRUD.get_all_universities()
            
            # Apply sorting
            if sort_by == "name":
                universities.sort(key=lambda x: x.name.lower() if x.name else "")
            elif sort_by == "country_code":
                universities.sort(key=lambda x: x.country_code)
            elif sort_by == "created_at":
                universities.sort(key=lambda x: x.created_at or "")
            
            if sort_order == "desc":
                universities.reverse()
            
            # Apply pagination
            total = len(universities)
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_universities = universities[start_idx:end_idx]
            
            return {
                "items": paginated_universities,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page
            }
            
        except Exception as e:
            logger.error(f"Error in get_universities_with_pagination: {e}")
            raise

    @staticmethod
    def get_university_by_id(university_id: str):
        """Get a specific university by ID"""
        try:
            return UniversityCRUD.get_university_by_id(university_id)
        except Exception as e:
            logger.error(f"Error in get_university_by_id: {e}")
            raise

    @staticmethod
    def get_search_suggestions(
        query: str,
        limit: int = 10,
        country_code: Optional[str] = None
    ):
        """Get search suggestions for autocomplete"""
        try:
            suggestions = UniversityCRUD.search_universities(
                search_term=query,
                country_code=country_code,
                limit=limit
            )
            
            return [
                {
                    "id": str(uni.id),
                    "name": uni.name,
                    "country_code": uni.country_code,
                    "domain": uni.domain
                } for uni in suggestions
            ]
        except Exception as e:
            logger.error(f"Error in get_search_suggestions: {e}")
            raise

    @staticmethod
    def get_countries():
        """Get list of countries with universities"""
        try:
            return UniversityCRUD.get_countries_with_universities()
        except Exception as e:
            logger.error(f"Error in get_countries: {e}")
            raise

    @staticmethod
    def get_statistics():
        """Get university statistics"""
        try:
            all_universities = UniversityCRUD.get_all_universities()
            countries = UniversityCRUD.get_countries_with_universities()
            
            total = len(all_universities)
            total_countries = len(countries)
            with_website = len([u for u in all_universities if u.website])
            with_domain = len([u for u in all_universities if u.domain])
            
            return {
                "total_universities": total,
                "total_countries": total_countries,
                "with_website": with_website,
                "with_domain": with_domain
            }
        except Exception as e:
            logger.error(f"Error in get_statistics: {e}")
            raise

    @staticmethod
    def get_universities_by_country(
        country_code: str,
        search: Optional[str] = None
    ):
        """Get universities in a specific country"""
        try:
            if search:
                universities = UniversityCRUD.search_universities(
                    search_term=search,
                    country_code=country_code,
                    limit=1000
                )
            else:
                universities = UniversityCRUD.get_universities_by_country(country_code)
            
            return universities
        except Exception as e:
            logger.error(f"Error in get_universities_by_country: {e}")
            raise 