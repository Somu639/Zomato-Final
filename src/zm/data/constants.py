"""Column names and normalization constants for the Zomato CSV dataset."""

HF_DATASET_FILE = "zomato.csv"
CACHE_VERSION = "v1"
CACHE_RESTAURANTS_FILE = f"restaurants_{CACHE_VERSION}.jsonl"
CACHE_META_FILE = f"restaurants_{CACHE_VERSION}.meta.json"

# Raw CSV headers (ManikaSaini/zomato-restaurant-recommendation)
COL_URL = "url"
COL_ADDRESS = "address"
COL_NAME = "name"
COL_ONLINE_ORDER = "online_order"
COL_BOOK_TABLE = "book_table"
COL_RATE = "rate"
COL_VOTES = "votes"
COL_PHONE = "phone"
COL_LOCATION = "location"
COL_REST_TYPE = "rest_type"
COL_DISH_LIKED = "dish_liked"
COL_CUISINES = "cuisines"
COL_COST = "approx_cost(for two people)"
COL_REVIEWS_LIST = "reviews_list"
COL_MENU_ITEM = "menu_item"
COL_LISTED_IN_TYPE = "listed_in(type)"
COL_LISTED_IN_CITY = "listed_in(city)"

# Canonical city names extracted from address / URL
CITY_ALIASES: dict[str, str] = {
    "bangalore": "Bangalore",
    "bengaluru": "Bangalore",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "hyderabad": "Hyderabad",
    "chennai": "Chennai",
    "kolkata": "Kolkata",
    "calcutta": "Kolkata",
    "pune": "Pune",
    "gurgaon": "Gurgaon",
    "gurugram": "Gurgaon",
    "noida": "Noida",
}

# Rupee cost-for-two bands (approximate for Indian market)
COST_BAND_LOW_MAX = 300
COST_BAND_MEDIUM_MAX = 700
