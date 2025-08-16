import os

# Fetch values from environment variables
# (Add them in Koyeb dashboard under Environment Variables)

api_id = int(os.getenv("API_ID", "12345"))  # default 12345 if not set
api_hash = os.getenv("API_HASH", "your api hash here")
bot_token = os.getenv("BOT_TOKEN", "your bot token here")
mu_token = os.getenv("MU_TOKEN", "your manga-update token here")
mal_client_id = os.getenv("MAL_CLIENT_ID", "your mal client id here")
SAUCE_KEY = os.getenv("SAUCE_KEY", "saucenao api key here")
