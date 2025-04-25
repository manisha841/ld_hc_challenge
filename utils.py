import json
from pathlib import Path
from typing import Dict

# Configuration
DATA_DIR = Path("data")
ITEMS_FILE = DATA_DIR / "items.json"
USERS_FILE = DATA_DIR / "users.json"


def ensure_data_dir():
    """Ensure the data directory exists"""
    DATA_DIR.mkdir(exist_ok=True)


def load_json_file(file_path: Path) -> Dict:
    """Load data from a JSON file"""
    if not file_path.exists():
        return {}
    with file_path.open() as f:
        return json.load(f)


def save_json_file(file_path: Path, data: Dict):
    """Save data to a JSON file"""
    with file_path.open("w") as f:
        json.dump(data, f, indent=4)


def load_items() -> Dict:
    """Load items from JSON file"""
    ensure_data_dir()
    return load_json_file(ITEMS_FILE)


def save_items(items: Dict):
    """Save items to JSON file"""
    ensure_data_dir()
    save_json_file(ITEMS_FILE, items)


def load_users() -> Dict:
    """Load users from JSON file"""
    ensure_data_dir()
    return load_json_file(USERS_FILE)


def save_users(users: Dict):
    """Save users to JSON file"""
    ensure_data_dir()
    save_json_file(USERS_FILE, users)


def initialize_data():
    ensure_data_dir()

    if not ITEMS_FILE.exists():
        default_items = {
            "1": {
                "id": 1,
                "name": "Item 1",
                "description": "Description 1",
                "owner_id": "user1",
                "price": 10.99,
            },
            "2": {
                "id": 2,
                "name": "Item 2",
                "description": "Description 2",
                "owner_id": "user2",
                "price": 20.99,
            },
            "3": {
                "id": 3,
                "name": "Item 3",
                "description": "Description 3",
                "owner_id": "user1",
                "price": 30.99,
            },
        }
        save_items(default_items)

    # Initialize users if file doesn't exist
    if not USERS_FILE.exists():
        default_users = {
            "user1": {
                "id": "user1",
                "email": "user1@example.com",
                "hashed_password": "$2b$12$ouni1QINbB7LVooJUrXQQ.5NgpVf1cN.V79F/A.PW9N2OgHz8kteq",  # "password123"
            },
            "user2": {
                "id": "user2",
                "email": "user2@example.com",
                "hashed_password": "$2b$12$ouni1QINbB7LVooJUrXQQ.5NgpVf1cN.V79F/A.PW9N2OgHz8kteq",  # "password123"
            },
        }
        save_users(default_users)


# Initialize data on module import
initialize_data()
