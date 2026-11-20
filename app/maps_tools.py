"""Google Maps Geocoding and Places API (New) tools."""

import os
import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional


def _get_api_key() -> str:
    key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    return key


def geocode_address(address: str) -> Dict[str, Any]:
    """Uses the Google Maps Geocoding API to turn an address or city name into coordinates.

    Args:
        address: The address or place to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Taipei 101').

    Returns:
        A dictionary containing the formatted address and latitude/longitude coordinates.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "error": "GOOGLE_MAPS_API_KEY is not configured. Please set a valid key in .env."
        }

    try:
        encoded_address = urllib.parse.quote(address.strip())
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
        req = urllib.request.Request(url, headers={"User-Agent": "GreenhouseAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "OK" or not data.get("results"):
            return {
                "error": f"Geocoding failed for '{address}': {data.get('status', 'NO_RESULTS')}"
            }

        first_result = data["results"][0]
        location = first_result["geometry"]["location"]
        return {
            "address": first_result.get("formatted_address"),
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
        }
    except Exception as e:
        return {"error": f"Geocoding request failed: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "florist",
    radius_meters: float = 5000.0,
) -> List[Dict[str, Any]]:
    """Uses the Google Places API (New) to search for nearby places (e.g. florists, plant nurseries, greenhouses).

    Args:
        latitude: Latitude of the center location.
        longitude: Longitude of the center location.
        place_type: Type of place to search (e.g. 'florist', 'park', 'store').
        radius_meters: Search radius in meters (max 50000, default 5000).

    Returns:
        A list of key fields (name, address, location) for nearby places found.
    """
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return [
            {
                "error": "GOOGLE_MAPS_API_KEY is not configured. Please set a valid key in .env."
            }
        ]

    try:
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }
        body = {
            "includedTypes": [place_type],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                    },
                    "radius": float(radius_meters),
                }
            },
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())

        places = []
        for p in data.get("places", []):
            places.append(
                {
                    "name": p.get("displayName", {}).get("text", ""),
                    "address": p.get("formattedAddress", ""),
                    "location": p.get("location", {}),
                }
            )
        return places
    except Exception as e:
        return [{"error": f"Places search failed: {str(e)}"}]
