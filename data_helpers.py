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
    # Load the current collection
    user_collection = load_collection()

    # Check if the user already has a collection
    if user_id in user_collection:
        # Check if the card already exists in the user's collection
        card_exists = any(card['name'] == selected_card['name'] and card['group'] == selected_card['group'] for card in user_collection[user_id]['cards'])
        
        if card_exists:
            print(f"Card {selected_card['name']} already exists in the collection for user {user_id}.")
            return  # Don't add the card again
        else:
            # Append the new card to the existing collection
            user_collection[user_id]['cards'].append(selected_card)
            print(f"Card {selected_card['name']} added to user {user_id}'s collection.")
    else:
        # Create a new collection for the user if it doesn't exist
        user_collection[user_id] = {'cards': [selected_card]}
        print(f"New collection created for user {user_id}.")

    # Save the updated collection to the file
    with open("collection.json", "w", encoding="utf-8") as data_file:
        json.dump(user_collection, data_file, indent=4, ensure_ascii=False)
    print(f"User collection saved successfully.")
