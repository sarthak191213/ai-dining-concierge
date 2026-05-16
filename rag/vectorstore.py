import json
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain.schema import Document

from rag.embeddings import get_embeddings

COLLECTION_NAME = "restaurants"

_vectorstore_cache = None


def _build_document(restaurant: dict) -> Document:
    text_parts = [
        f"Restaurant: {restaurant['name']}",
        f"Cuisine: {restaurant['cuisine']}",
        f"Location: {restaurant['location']}, {restaurant['area']}",
        f"Price for two: {restaurant['price_for_two']} INR ({restaurant['price_range']})",
        f"Rating: {restaurant['rating']}/5",
        f"Ambiance: {restaurant['ambiance']}",
        f"Dietary options: {', '.join(restaurant.get('dietary_options', []))}",
        f"Description: {restaurant.get('description', '')}",
        f"Best for: {', '.join(restaurant.get('tags', []))}",
    ]
    benefits = restaurant.get("amex_benefits", {})
    if benefits:
        benefit_parts = []
        if benefits.get("discount"):
            benefit_parts.append(f"Discount: {benefits['discount']}")
        if benefits.get("points"):
            benefit_parts.append(f"Points: {benefits['points']}")
        if benefits.get("complimentary"):
            benefit_parts.append(f"Complimentary: {benefits['complimentary']}")
        if benefit_parts:
            text_parts.append(f"Amex Benefits: {'; '.join(benefit_parts)}")

    return Document(
        page_content="\n".join(text_parts),
        metadata={
            "id": restaurant.get("id", ""),
            "name": restaurant.get("name", ""),
            "cuisine": restaurant.get("cuisine", ""),
            "location": restaurant.get("location", ""),
            "area": restaurant.get("area", ""),
            "price_for_two": restaurant.get("price_for_two", 0),
            "rating": restaurant.get("rating", 0),
            "ambiance": restaurant.get("ambiance", ""),
            "tags": json.dumps(restaurant.get("tags", [])),
            "dietary_options": json.dumps(restaurant.get("dietary_options", [])),
            "availability_slots": json.dumps(restaurant.get("availability_slots", [])),
            "amex_benefits": json.dumps(restaurant.get("amex_benefits", {})),
            "phone": restaurant.get("phone", ""),
        },
    )


def _load_restaurants() -> list:
    data_path = os.path.join(Path(__file__).parent.parent, "data", "restaurants.json")
    with open(data_path) as f:
        return json.load(f)


def get_vectorstore() -> Chroma:
    global _vectorstore_cache
    if _vectorstore_cache is not None:
        return _vectorstore_cache

    embeddings = get_embeddings()
    restaurants = _load_restaurants()
    documents = [_build_document(r) for r in restaurants]

    _vectorstore_cache = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
    )
    return _vectorstore_cache


def search_restaurants(query: str, k: int = 5, filters: dict = None) -> list:
    vectorstore = get_vectorstore()
    where_filter = None
    if filters:
        conditions = []
        if filters.get("location"):
            conditions.append({"location": {"$eq": filters["location"]}})
        if filters.get("max_price"):
            conditions.append({"price_for_two": {"$lte": filters["max_price"]}})
        if filters.get("min_rating"):
            conditions.append({"rating": {"$gte": filters["min_rating"]}})
        if conditions:
            where_filter = {"$and": conditions} if len(conditions) > 1 else conditions[0]

    try:
        results = vectorstore.similarity_search(query, k=k, filter=where_filter)
    except Exception:
        results = vectorstore.similarity_search(query, k=k)
    return results
