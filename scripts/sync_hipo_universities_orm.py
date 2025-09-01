import argparse
import asyncio
import os
import sys
from typing import List, Optional

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from dotenv import load_dotenv

# Import our ORM models
from db.orms import University, Base, UniversityCRUD

HIPOLABS_URL = "http://universities.hipolabs.com/search"

DEFAULT_COUNTRIES = [
    "Australia", "United States", "United Kingdom", "Canada",
    "China", "Germany", "France", "Japan", "Singapore", "New Zealand",
]

# ---------- Helpers ----------
def first_or_none(arr: Optional[list]) -> Optional[str]:
    if isinstance(arr, list) and arr:
        return arr[0]
    return None

def normalize(item: dict) -> dict:
    """
    Map Hipo fields to our universities table:
    - country_code: alpha_two_code
    - state_province: state-province
    - website: web_pages[0]
    - domain: domains[0]
    """
    name = (item.get("name") or "").strip()
    cc = (item.get("alpha_two_code") or "").strip().upper() or None
    state = item.get("state-province")
    website = first_or_none(item.get("web_pages")) or None
    domain = first_or_none(item.get("domains")) or None

    return {
        "name": name,
        "country_code": cc,
        "state_province": state,
        "city": None,                 # Hipo doesn't provide city, leave empty
        "website": website,
        "domain": domain,             # CITEXT UNIQUE, can be NULL
        "aliases": [],                # Leave empty for now
        "external_ids": {},           # Leave empty, can be filled later with OpenAlex/ROR
        "apply_portals": [],          # Leave empty for now
    }

async def fetch_country(country: str) -> list:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(HIPOLABS_URL, params={"country": country})
        r.raise_for_status()
        return r.json()

async def sync_countries_orm(countries: List[str]) -> dict:
    fetched = upserted = 0
    
    for country in countries:
        items = await fetch_country(country)
        fetched += len(items)
        
        for item in items:
            data = normalize(item)
            if not data["name"] or not data["country_code"]:
                # Skip if missing key fields
                continue
            
            try:
                UniversityCRUD.create_or_update_university(data)
                upserted += 1
            except Exception as e:
                print(f"Error processing {data['name']}: {e}")
                continue
    
    return {"countries": len(countries), "fetched": fetched, "upserted": upserted}

# ---------- CLI ----------
def parse_args():
    p = argparse.ArgumentParser("Sync universities (Hipo) into your DB schema using ORM")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--countries", help="Comma separated, e.g. 'Australia,United States'")
    g.add_argument("--countries-file", help="Text file: one country per line")
    g.add_argument("--all", action="store_true", help="Use built-in sample list")
    return p.parse_args()

def read_countries(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

def main():
    args = parse_args()
    if args.countries:
        countries = [x.strip() for x in args.countries.split(",") if x.strip()]
    elif args.countries_file:
        countries = read_countries(args.countries_file)
    else:
        countries = DEFAULT_COUNTRIES

    print("Using ORM for database operations")
    print(f"Will sync {len(countries)} country/countries: {countries}")
    
    result = asyncio.run(sync_countries_orm(countries))
    print("Sync result:", result)

if __name__ == "__main__":
    main() 