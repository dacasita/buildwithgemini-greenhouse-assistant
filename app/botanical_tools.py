"""Botanical taxonomy lookup using GBIF (Global Biodiversity Information Facility) API."""

import os
import json
import urllib.parse
import urllib.request
from typing import Dict, Any


def lookup_botanical_taxonomy(plant_name: str) -> Dict[str, Any]:
    """Looks up official global botanical taxonomy, family, genus, and scientific name
    for any plant species using the GBIF (Global Biodiversity Information Facility) API.

    Args:
        plant_name: Common or scientific name of the plant (e.g. 'Monstera deliciosa', 'Ficus lyrata', 'Peace Lily').

    Returns:
        A dictionary containing scientific name, family, genus, taxonomic rank, and status.
    """
    try:
        encoded_name = urllib.parse.quote(plant_name.strip())
        url = f"https://api.gbif.org/v1/species/match?name={encoded_name}"

        headers = {"User-Agent": "GreenhouseAssistant/1.0"}
        # Optional API key support if configured in environment
        api_key = os.environ.get("GBIF_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())

        if data.get("matchType") == "NONE":
            return {"error": f"No botanical taxonomy record found for '{plant_name}'."}

        return {
            "query": plant_name,
            "scientific_name": data.get("scientificName"),
            "canonical_name": data.get("canonicalName"),
            "family": data.get("family"),
            "genus": data.get("genus"),
            "class": data.get("class"),
            "rank": data.get("rank"),
            "status": data.get("status"),
            "confidence": data.get("confidence"),
        }
    except Exception as e:
        return {"error": f"Failed to lookup botanical data: {str(e)}"}
