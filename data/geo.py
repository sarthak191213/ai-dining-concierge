import math
from typing import Optional

BANGALORE_AREAS = {
    "Indiranagar": (12.9784, 77.6408),
    "Koramangala": (12.9352, 77.6245),
    "MG Road": (12.9756, 77.6068),
    "UB City": (12.9716, 77.5946),
    "Residency Road": (12.9700, 77.6000),
    "Ashok Nagar": (12.9591, 77.5806),
    "Malleshwaram": (13.0035, 77.5647),
    "Basavanagudi": (12.9422, 77.5738),
    "JP Nagar": (12.9063, 77.5857),
    "Whitefield": (12.9698, 77.7500),
    "Hennur": (13.0450, 77.6370),
    "Yelahanka": (13.1007, 77.5963),
}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def get_nearby_areas(lat: float, lon: float, radius_km: float = 7.0) -> list:
    """Return Bangalore areas within radius_km, sorted by distance."""
    results = []
    for area, (alat, alon) in BANGALORE_AREAS.items():
        dist = haversine_km(lat, lon, alat, alon)
        if dist <= radius_km:
            results.append({"area": area, "distance_km": round(dist, 1)})
    results.sort(key=lambda x: x["distance_km"])
    return results
