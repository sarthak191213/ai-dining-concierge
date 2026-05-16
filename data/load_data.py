import json
from pathlib import Path
from typing import Optional


def load_restaurants_raw() -> list:
    data_path = Path(__file__).parent / "restaurants.json"
    with open(data_path) as f:
        return json.load(f)


def load_card_benefits() -> dict:
    data_path = Path(__file__).parent / "card_benefits.json"
    with open(data_path) as f:
        return json.load(f)


def get_restaurant_by_id(restaurant_id: str) -> Optional[dict]:
    restaurants = load_restaurants_raw()
    for r in restaurants:
        if r["id"] == restaurant_id:
            return r
    return None


def get_restaurant_by_name(name: str) -> Optional[dict]:
    restaurants = load_restaurants_raw()
    name_lower = name.lower()
    for r in restaurants:
        if name_lower in r["name"].lower():
            return r
    return None


def get_benefits_for_cards(restaurant_id: str, card_names: list) -> dict:
    """Get benefits for specific cards at a restaurant."""
    all_benefits = load_card_benefits()
    result = {}
    for card in card_names:
        if card in all_benefits and restaurant_id in all_benefits[card]:
            result[card] = all_benefits[card][restaurant_id]
    return result


def get_top_restaurants_for_cards(card_names: list, location: str = "") -> list:
    """Get restaurants with the best benefits for given cards."""
    all_benefits = load_card_benefits()
    restaurants = load_restaurants_raw()

    if location:
        restaurants = [r for r in restaurants if location.lower() in r["location"].lower()]

    scored = []
    for r in restaurants:
        card_perks = {}
        for card in card_names:
            if card in all_benefits and r["id"] in all_benefits[card]:
                card_perks[card] = all_benefits[card][r["id"]]
        if card_perks:
            scored.append({"restaurant": r, "card_benefits": card_perks})

    scored.sort(key=lambda x: len(x["card_benefits"]), reverse=True)
    return scored[:8]
