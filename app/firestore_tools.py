"""Firestore tools for Greenhouse Assistant inventory."""

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcode project ID as string per lab instructions:
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-144fb6d3227f"


def get_firestore_client() -> firestore.Client:
    return firestore.Client(project=FIRESTORE_PROJECT_ID)


def list_inventory() -> List[Dict[str, Any]]:
    """Fetches all plant items in the greenhouse inventory from Firestore.

    Returns:
        A list of dictionaries, where each dictionary contains plant details such as
        id, name, species, price, stock, care_level, sunlight, and watering.
    """
    db = get_firestore_client()
    docs = db.collection("inventory").stream()
    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)
    return items


def get_plant_details(query: str) -> Optional[Dict[str, Any]]:
    """Looks up detailed information about a specific plant in the greenhouse inventory.

    Args:
        query: The name or document ID of the plant (e.g. 'monstera-deliciosa' or 'Monstera').

    Returns:
        A dictionary with the plant's information if found, or None if not found.
    """
    db = get_firestore_client()
    query_lower = query.lower().strip()

    # First check direct doc ID
    doc = db.collection("inventory").document(query_lower).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data

    # Otherwise scan for matching name or species
    for d in db.collection("inventory").stream():
        data = d.to_dict()
        name = data.get("name", "").lower()
        species = data.get("species", "").lower()
        if query_lower in name or query_lower in species or query_lower in d.id:
            data["id"] = d.id
            return data

    return None


def update_plant_stock(plant_id: str, new_stock: int) -> str:
    """Updates the inventory stock count for a given plant in Firestore.

    Args:
        plant_id: The document ID of the plant in the inventory (e.g. 'monstera-deliciosa').
        new_stock: The new stock quantity (non-negative integer).

    Returns:
        A status message confirming the update.
    """
    db = get_firestore_client()
    doc_ref = db.collection("inventory").document(plant_id)
    doc = doc_ref.get()
    if not doc.exists:
        return f"Plant with ID '{plant_id}' was not found in the inventory."

    doc_ref.update({"stock": new_stock})
    plant_name = doc.to_dict().get("name", plant_id)
    return f"Successfully updated stock for {plant_name} ({plant_id}) to {new_stock} units."


def add_plant_to_inventory(
    name: str,
    species: str,
    price: float,
    stock: int,
    care_level: str,
    sunlight: str,
    watering: str,
    description: str = "",
) -> str:
    """Adds a new plant to the greenhouse inventory collection in Firestore.

    Args:
        name: Common name of the plant (e.g. 'Bird of Paradise').
        species: Botanical species name (e.g. 'Strelitzia reginae').
        price: Price in USD.
        stock: Available quantity in stock.
        care_level: Difficulty level ('Easy', 'Moderate', 'Expert').
        sunlight: Sunlight requirements (e.g. 'Direct to bright indirect light').
        watering: Watering guidance (e.g. 'Keep soil moist in spring and summer').
        description: Brief description of the plant.

    Returns:
        A confirmation message with the generated plant ID.
    """
    db = get_firestore_client()
    doc_id = name.lower().replace(" ", "-").replace("(", "").replace(")", "").strip("-")
    data = {
        "name": name,
        "species": species,
        "price": float(price),
        "stock": int(stock),
        "care_level": care_level,
        "sunlight": sunlight,
        "watering": watering,
        "description": description,
    }
    db.collection("inventory").document(doc_id).set(data)
    return f"Successfully added {name} to inventory with ID '{doc_id}'."
