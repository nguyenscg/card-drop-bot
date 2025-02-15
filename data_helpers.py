import json
import os

COLLECTION_FILE = "collection.json"

def load_collection():
    if not os.path.exists("collection.json"):
        return {}  # Return an empty dictionary if the file doesn't exist

    try:
        with open("collection.json", "r") as data_file:
            data = json.load(data_file)
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {}  # Return an empty dictionary if the file is empty or invalid

def save_collection(collection):
    """Saves the updated collection to collection.json"""
    with open(COLLECTION_FILE, "w") as file:
        json.dump(collection, file, indent=4)

def add_card_to_collection(user_id, card):
    """Adds a card to the user's collection and saves it"""
    collection = load_collection()
    user_id = str(user_id)  # Convert to string for JSON consistency

    if user_id not in collection:
        collection[user_id] = []  # Initialize user collection

    collection[user_id].append(card)  # Add the new card
    save_collection(collection)  # Save to file
