import json
import re
from langchain_core.tools import tool

from rag.vectorstore import search_restaurants
from data.load_data import load_restaurants_raw, get_restaurant_by_name, get_benefits_for_cards, get_top_restaurants_for_cards


def _parse_time(time_str: str) -> str:
    """Normalize time input like '8pm', '8:30 PM', '20:00' to HH:MM format."""
    time_str = time_str.strip().lower().replace(" ", "")
    match = re.match(r"^(\d{1,2}):?(\d{2})?\s*(am|pm)?$", time_str)
    if not match:
        return ""
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    period = match.group(3)
    if period == "pm" and hour < 12:
        hour += 12
    elif period == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return ""
    return f"{hour:02d}:{minute:02d}"


def _extract_discount_pct(discount_str: str) -> int:
    """Safely extract numeric discount percentage from string like '15% off'."""
    match = re.search(r"(\d+)%", discount_str)
    return int(match.group(1)) if match else 0


@tool
def semantic_search(query: str, location: str = "", max_price: int = 0) -> str:
    """Search restaurants using natural language. Best for descriptive queries about
    cuisine type, ambiance, mood, or occasion like 'romantic Italian place' or 'best biryani spot'.

    Use this tool when the user describes what they WANT in natural language.
    Use filter_restaurants instead when the user gives specific numeric criteria.

    Args:
        query: Natural language description of what the user is looking for
        location: Optional city filter (Bangalore, Mumbai, or Delhi)
        max_price: Optional maximum price for two in INR (0 means no limit)
    """
    filters = {}
    if location:
        filters["location"] = location
    if max_price > 0:
        filters["max_price"] = max_price

    try:
        results = search_restaurants(query, k=5, filters=filters if filters else None)
    except Exception as e:
        return f"Search failed: {str(e)}. Please try a different query."

    if not results:
        return "No restaurants found matching your criteria. Try broadening your search."

    output = []
    for doc in results:
        meta = doc.metadata
        benefits = json.loads(meta.get("amex_benefits", "{}"))
        benefit_str = ""
        if benefits:
            parts = []
            if benefits.get("discount"):
                parts.append(f"Discount: {benefits['discount']}")
            if benefits.get("points"):
                parts.append(f"Points: {benefits['points']}")
            if benefits.get("complimentary"):
                parts.append(f"Complimentary: {benefits['complimentary']}")
            if parts:
                benefit_str = " | Amex Benefits: " + "; ".join(parts)

        desc = doc.page_content
        desc_marker = "Description: "
        if desc_marker in desc:
            desc = desc.split(desc_marker)[-1].split("\n")[0]
        else:
            desc = ""

        output.append(
            f"- {meta['name']} | {meta['cuisine']} | {meta['location']}, {meta['area']} | "
            f"₹{meta['price_for_two']} for two | Rating: {meta['rating']}/5 | "
            f"Ambiance: {meta['ambiance']}{benefit_str}\n"
            f"  {desc}"
        )

    return "\n\n".join(output)


@tool
def filter_restaurants(
    location: str = "",
    cuisine: str = "",
    max_price: int = 0,
    min_rating: float = 0,
    dietary_need: str = "",
    tag: str = "",
) -> str:
    """Filter restaurants by specific structured criteria. Use this when the user
    gives exact requirements like a budget number, specific city, dietary restriction, or occasion.

    Use semantic_search instead when the user describes preferences in natural language.

    Args:
        location: City name (Bangalore, Mumbai, or Delhi)
        cuisine: Cuisine type to filter by (e.g. Italian, Japanese, North Indian)
        max_price: Maximum price for two in INR (Indian Rupees)
        min_rating: Minimum rating out of 5 (e.g. 4.5)
        dietary_need: Dietary requirement (vegetarian, vegan, gluten-free, jain, seafood)
        tag: Occasion/vibe tag (romantic, business dinner, casual, family, brunch, etc.)
    """
    try:
        restaurants = load_restaurants_raw()
    except Exception as e:
        return f"Failed to load restaurant data: {str(e)}"

    filtered = restaurants

    if location:
        filtered = [r for r in filtered if location.lower() in r["location"].lower()]
    if cuisine:
        filtered = [r for r in filtered if cuisine.lower() in r["cuisine"].lower()]
    if max_price > 0:
        filtered = [r for r in filtered if r["price_for_two"] <= max_price]
    if min_rating > 0:
        filtered = [r for r in filtered if r["rating"] >= min_rating]
    if dietary_need:
        filtered = [
            r for r in filtered
            if any(dietary_need.lower() in opt.lower() for opt in r.get("dietary_options", []))
        ]
    if tag:
        filtered = [
            r for r in filtered
            if any(tag.lower() in t.lower() for t in r.get("tags", []))
        ]

    filtered = sorted(filtered, key=lambda x: x["rating"], reverse=True)[:5]

    if not filtered:
        return "No restaurants match these specific criteria. Try relaxing some filters."

    output = []
    for r in filtered:
        benefits = r.get("amex_benefits", {})
        benefit_str = ""
        if benefits.get("discount"):
            benefit_str = f" | Amex: {benefits['discount']}"

        output.append(
            f"- {r['name']} | {r['cuisine']} | {r['location']}, {r['area']} | "
            f"₹{r['price_for_two']} for two | Rating: {r['rating']}/5 | "
            f"Ambiance: {r['ambiance']}{benefit_str}"
        )

    return "\n".join(output)


@tool
def check_availability(restaurant_name: str, preferred_time: str = "") -> str:
    """Check table availability for a specific restaurant. Use this when the user
    asks about booking, reservations, or available time slots at a named restaurant.

    Args:
        restaurant_name: Name of the restaurant to check
        preferred_time: Preferred time (e.g., '7pm', '8:30 PM', '19:00', '20:30')
    """
    restaurant = get_restaurant_by_name(restaurant_name)

    if not restaurant:
        return f"Restaurant '{restaurant_name}' not found in our database. Please check the name and try again."

    slots = restaurant.get("availability_slots", [])

    if preferred_time:
        normalized = _parse_time(preferred_time)
        if not normalized:
            return (
                f"Couldn't understand the time '{preferred_time}'. "
                f"Please use formats like '7pm', '8:30 PM', or '19:00'. "
                f"Available slots at {restaurant['name']}: {', '.join(slots)}"
            )

        if normalized in slots:
            return (
                f"Great news! {restaurant['name']} has a table available at {normalized}. "
                f"Location: {restaurant['area']}, {restaurant['location']}. "
                f"Phone: {restaurant.get('phone', 'N/A')} to confirm your booking."
            )

        try:
            norm_hour = int(normalized.split(":")[0])
            nearby = [s for s in slots if abs(int(s.split(":")[0]) - norm_hour) <= 1]
        except ValueError:
            nearby = []

        if nearby:
            return (
                f"{restaurant['name']} doesn't have a table at {normalized}, "
                f"but nearby slots are available: {', '.join(nearby)}. "
                f"Phone: {restaurant.get('phone', 'N/A')}"
            )
        return (
            f"Unfortunately, {restaurant['name']} doesn't have availability around {normalized}. "
            f"Available slots: {', '.join(slots)}"
        )

    return (
        f"{restaurant['name']} - Available time slots: {', '.join(slots)}. "
        f"Location: {restaurant['area']}, {restaurant['location']}. "
        f"Phone: {restaurant.get('phone', 'N/A')}"
    )


@tool
def get_card_benefits(restaurant_name: str = "", location: str = "", cards: str = "") -> str:
    """Get credit card dining benefits and rewards for restaurants. Use this when the user
    asks about card benefits, discounts, loyalty points, or exclusive rewards.

    Supports multiple cards: Amex Platinum, Amex Gold, HDFC Diners Club,
    ICICI Sapphiro, Axis Atlas, SBI Elite, SBI SimplyCLICK.

    Args:
        restaurant_name: Specific restaurant name to check benefits for (optional)
        location: City to show best deals in (optional — Bangalore, Mumbai, or Delhi)
        cards: Comma-separated card names the user has (e.g. 'Amex Platinum, HDFC Diners Club')
    """
    card_list = [c.strip() for c in cards.split(",") if c.strip()] if cards else []

    if restaurant_name:
        restaurant = get_restaurant_by_name(restaurant_name)
        if not restaurant:
            return f"Restaurant '{restaurant_name}' not found in our database."

        if card_list:
            benefits = get_benefits_for_cards(restaurant["id"], card_list)
            if not benefits:
                return f"No special card benefits found at {restaurant['name']} for your cards ({', '.join(card_list)})."

            output = [f"**Card Benefits at {restaurant['name']}:**"]
            for card_name, perks in benefits.items():
                output.append(f"\n  **{card_name}:**")
                if perks.get("discount"):
                    output.append(f"    - Discount: {perks['discount']}")
                if perks.get("points"):
                    output.append(f"    - Points: {perks['points']}")
                if perks.get("complimentary"):
                    output.append(f"    - Complimentary: {perks['complimentary']}")
            return "\n".join(output)
        else:
            benefits = restaurant.get("amex_benefits", {})
            if not benefits:
                return f"No card benefits found for {restaurant['name']}."
            parts = [f"**Benefits at {restaurant['name']}:**"]
            if benefits.get("discount"):
                parts.append(f"  - Discount: {benefits['discount']}")
            if benefits.get("points"):
                parts.append(f"  - Points: {benefits['points']}")
            if benefits.get("complimentary"):
                parts.append(f"  - Complimentary: {benefits['complimentary']}")
            return "\n".join(parts)

    if card_list:
        top = get_top_restaurants_for_cards(card_list, location)
        if not top:
            return f"No restaurants with special benefits found for your cards in {location or 'any city'}."

        output = [f"**Top Restaurants for Your Cards ({', '.join(card_list)}):**"]
        for item in top:
            r = item["restaurant"]
            line = f"\n- **{r['name']}** | {r['cuisine']} | {r['location']}, {r['area']} | ₹{r['price_for_two']} for two"
            for card_name, perks in item["card_benefits"].items():
                line += f"\n    {card_name}: {perks.get('discount', '')} | {perks.get('points', '')}"
                if perks.get("complimentary"):
                    line += f" | Free: {perks['complimentary']}"
            output.append(line)
        return "\n".join(output)

    try:
        restaurants = load_restaurants_raw()
    except Exception as e:
        return f"Failed to load data: {str(e)}"

    if location:
        filtered = [r for r in restaurants if location.lower() in r["location"].lower()]
    else:
        filtered = restaurants

    top_benefits = [r for r in filtered if r.get("amex_benefits", {}).get("discount")]
    top_benefits = sorted(
        top_benefits,
        key=lambda x: _extract_discount_pct(x.get("amex_benefits", {}).get("discount", "")),
        reverse=True,
    )[:5]

    if not top_benefits:
        return "No restaurants with special card benefits found."

    output = ["**Top Card Benefits:**"]
    for r in top_benefits:
        b = r["amex_benefits"]
        line = f"- {r['name']} ({r['location']}): {b.get('discount', '')}"
        if b.get("complimentary"):
            line += f" + {b['complimentary']}"
        if b.get("points"):
            line += f" | {b['points']}"
        output.append(line)

    return "\n".join(output)


ALL_TOOLS = [semantic_search, filter_restaurants, check_availability, get_card_benefits]
