import os
from dotenv import load_dotenv
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("watchfiles").setLevel(logging.WARNING)
import supabase

# load env
load_dotenv()

def supabase_client():
    # setup supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    client = supabase.Client(supabase_url, supabase_key)
    return client