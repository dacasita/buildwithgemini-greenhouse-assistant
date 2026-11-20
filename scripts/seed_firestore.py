"""Seed script for greenhouse inventory in Firestore."""

from google.cloud import firestore

GCP_PROJECT_ID = "qwiklabs-gcp-03-144fb6d3227f"

PLANTS = [
    {
        "id": "monstera-deliciosa",
        "name": "Monstera Deliciosa",
        "species": "Monstera deliciosa",
        "price": 38.0,
        "stock": 12,
        "care_level": "Easy",
        "sunlight": "Bright indirect light",
        "watering": "Every 1-2 weeks, let soil dry between waterings",
        "description": "Iconic Swiss cheese plant with split leaves. Great statement plant.",
    },
    {
        "id": "snake-plant",
        "name": "Snake Plant (Sansevieria)",
        "species": "Dracaena trifasciata",
        "price": 24.0,
        "stock": 20,
        "care_level": "Easy",
        "sunlight": "Low to bright indirect light",
        "watering": "Every 2-3 weeks, very drought tolerant",
        "description": "Indestructible architectural plant that purifies indoor air.",
    },
    {
        "id": "fiddle-leaf-fig",
        "name": "Fiddle Leaf Fig",
        "species": "Ficus lyrata",
        "price": 55.0,
        "stock": 6,
        "care_level": "Moderate",
        "sunlight": "Consistent bright filtered light",
        "watering": "Weekly when top 2 inches of soil feel dry",
        "description": "Dramatic violin-shaped leaves that love steady light and humidity.",
    },
    {
        "id": "peace-lily",
        "name": "Peace Lily",
        "species": "Spathiphyllum",
        "price": 28.0,
        "stock": 15,
        "care_level": "Easy",
        "sunlight": "Medium to low indirect light",
        "watering": "Weekly, droops gently when thirsty",
        "description": "Glossy green leaves and elegant white blooms. Great air filter.",
    },
    {
        "id": "golden-pothos",
        "name": "Golden Pothos",
        "species": "Epipremnum aureum",
        "price": 18.0,
        "stock": 25,
        "care_level": "Easy",
        "sunlight": "Any light condition from low to bright",
        "watering": "Every 1-2 weeks",
        "description": "Fast-growing cascading vine with heart-shaped variegated leaves.",
    },
]


def seed():
    print(f"Connecting to Firestore for project {GCP_PROJECT_ID}...")
    db = firestore.Client(project=GCP_PROJECT_ID)
    collection = db.collection("inventory")
    for plant in PLANTS:
        doc_id = plant["id"]
        data = {k: v for k, v in plant.items() if k != "id"}
        collection.document(doc_id).set(data)
        print(f"Seeded: {plant['name']} ({doc_id})")
    print("Seeding completed successfully!")


if __name__ == "__main__":
    seed()
