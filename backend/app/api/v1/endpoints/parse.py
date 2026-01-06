from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import re

router = APIRouter()

class ParseRequest(BaseModel):
    url: str

class ParseResponse(BaseModel):
    ingredients: list[str]
    steps: list[str]
    author: str

def soup_from_url(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()

    return BeautifulSoup(res.text, "html.parser")

def extract_instructions(soup):
    instructions = []

    # Look for headings with "step" or "instruction" (case-insensitive)
    heading_tags = soup.find_all(re.compile("^h[1-6]$"))
    for heading in heading_tags:
        if re.search(r"(steps?|instructions?|directions?|method)", heading.get_text(), re.I):
            # The next sibling could be <ol>, <ul>, or <p>
            next_tag = heading.find_next_sibling()
            if next_tag:
                if next_tag.name in ["ol", "ul", "div"]:
                    items = [li.get_text(strip=True) for li in next_tag.find_all("li")]
                    instructions.extend(items)
                elif next_tag.name == "p":
                    instructions.append(next_tag.get_text(strip=True))

    return instructions

def extract_ingredients(soup):
    ingredients = []

    heading_tags = soup.find_all(re.compile("^h[1-6]$"))
    for heading in heading_tags:
        if re.search(r"ingredients", heading.get_text(), re.I):
            # The next sibling could be <ol>, <ul>, or <p>
            next_tag = heading.find_next_sibling()
            if next_tag:
                if next_tag.name in ["ol", "ul", "div"]:
                    items = [li.get_text(strip=True) for li in next_tag.find_all("li")]
                    ingredients.extend(items)
                elif next_tag.name == "p":
                    ingredients.append(next_tag.get_text(strip=True))

    return ingredients

@router.post("/parse", response_model=ParseResponse)
async def parse_website(payload: ParseRequest):
    url = payload.url
    print(url)
    if not url.startswith("http"):
        raise HTTPException(status_code=400, details="Invalid URL")

    soup = soup_from_url(payload.url)
    steps = extract_instructions(soup)
    ingredients = extract_ingredients(soup)
    print("INGREDIENTS: ", ingredients)
    
    # items = [li.get_text(strip=True) for li in soup.find_all("li")]

    return {
        "ingredients": ingredients,
        "steps": steps,
        "author": ""
    }