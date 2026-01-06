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
    notes: list[str]

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

    for heading in soup.find_all(re.compile("^h[1-6]$")):
        if re.search(r"ingredients?", heading.get_text(), re.I):
            sibling = heading.next_sibling
            while sibling:
                # Stop at next heading
                if sibling.name and re.match("^h[1-6]$", sibling.name):
                    break

                # Grab <ul>/<ol>
                if sibling.name in ["ul", "ol"]:
                    for li in sibling.find_all("li"):
                        text = li.get_text(separator=" ", strip=True)
                        text = re.sub(r"^[^\w\d]+", "", text)
                        if is_valid_ingredient(text):
                            ingredients.append(text)

                # Grab <p>
                elif sibling.name == "p":
                    text = sibling.get_text(separator=" ", strip=True)
                    text = re.sub(r"^[^\w\d]+", "", text)
                    if is_valid_ingredient(text):
                        ingredients.append(text)

                # Grab checkboxes
                elif sibling.name == "div":
                    for cb in sibling.find_all("input", type="checkbox"):
                        label = cb.find_parent("label")
                        if label:
                            cb.extract()
                            text = label.get_text(separator=" ", strip=True)
                            text = re.sub(r"^[^\w\d]+", "", text)
                            if is_valid_ingredient(text):
                                ingredients.append(text)

                sibling = sibling.next_sibling
            break  # only first ingredients section

    return ingredients

def is_valid_ingredient(text):
    """
    Simple heuristic to filter out lines like '1x', 'Original recipe ...'
    Only accept lines that contain at least one number and a word
    """
    # Remove empty lines
    if not text.strip():
        return False
    # Ignore lines that are just multipliers like "1x", "2x"
    if re.match(r"^\d+\s*x$", text.strip(), re.I):
        return False
    # Ignore notes like "Original recipe ..."
    if re.match(r"^Original recipe", text.strip(), re.I):
        return False
    # Accept lines that contain a number + unit/ingredient
    if re.search(r"\d", text):
        return True
    # Or lines with a measurement word
    if re.search(r"(cup|teaspoon|tablespoon|stick|lb|g|ml)", text, re.I):
        return True
    return False


def extract_notes(soup):
    notes = []

    heading_tags = soup.find_all(re.compile("^h[1-6]$"))
    for heading in heading_tags:
        if re.search(r"notes", heading.get_text(), re.I):
            # The next sibling could be <ol>, <ul>, or <p>
            next_tag = heading.find_next_sibling()
            if next_tag:
                if next_tag.name in ["ol", "ul", "div"]:
                    items = [li.get_text(separator=" ",strip=True).replace("▢","") for li in next_tag.find_all("li")]
                    notes.extend(items)
                elif next_tag.name == "p":
                    notes.append(next_tag.get_text(strip=True))

    return notes

@router.post("/parse", response_model=ParseResponse)
async def parse_website(payload: ParseRequest):
    url = payload.url
    print(url)
    if not url.startswith("http"):
        raise HTTPException(status_code=400, details="Invalid URL")

    soup = soup_from_url(payload.url)
    steps = extract_instructions(soup)
    ingredients = extract_ingredients(soup)
    notes = extract_notes(soup)

    return {
        "ingredients": ingredients,
        "steps": steps,
        "author": "",
        "notes": notes
    }