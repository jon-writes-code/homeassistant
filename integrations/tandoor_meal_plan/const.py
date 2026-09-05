"""Constants for the Tandoor Meal Plan integration."""

DOMAIN = "tandoor_meal_plan"

CONF_URL = "url"
CONF_API_TOKEN = "api_token"

MEAL_PLAN_SCAN_INTERVAL_SECONDS = 900
SHOPPING_LIST_SCAN_INTERVAL_SECONDS = 60
RECIPE_SCAN_INTERVAL_SECONDS = 3600

DAYS_AHEAD = 6
RECIPE_PAGE_SIZE = 50

MEAL_PLAN_ENDPOINT = "/api/meal-plan/"
SHOPPING_LIST_ENTRY_ENDPOINT = "/api/shopping-list-entry/"
RECIPE_ENDPOINT = "/api/recipe/"

SERVICE_SEARCH_RECIPES = "search_recipes"
ATTR_QUERY = "query"
