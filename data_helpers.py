import json
import os

# Initialize user collection if the file doesn't exist or is empty
def load_collection():
    # Check if the collection file exists
    if os.path.exists("collection.json"):
        try:
            # Attempt to load the collection from the file
            with open("collection.json", "r", encoding="utf-8") as data_file:
                user_collection = json.load(data_file)
            return user_collection
        except json.JSONDecodeError:
            # Handle case where the JSON is malformed
            print("Error loading the JSON data. Returning empty collection.")
            return {}
    else:
        # If the file doesn't exist, initialize an empty collection
        print("collection.json not found. Creating a new one.")
        return {}

def add_card(user_id, selected_card):
    # Load the current user collection
    user_collection = load_collection()

    # Check if the user already has a collection or create one
    if user_id not in user_collection:
        user_collection[user_id] = {'cards': []}

    # Add the selected card to the user's collection
    user_collection[user_id]['cards'].append(selected_card)

    # Save the updated collection back to the file
    with open("collection.json", "w", encoding="utf-8") as f:
        json.dump(user_collection, f, indent=4)

    print(f"Added {selected_card} to {user_id}'s collection.")




