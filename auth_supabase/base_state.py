"""
Top-level State for the App.

Authentication data is stored in the base State class so that all substates can
access it for verifying access to event handlers and computed vars.
"""
import reflex as rx


import supabase
from dotenv import load_dotenv
import os

# load env
load_dotenv()

# setup supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client = supabase.Client(supabase_url, supabase_key)



class State(rx.State):

    is_authenticated: bool = supabase_client.auth.get_session() is not None


    def do_logout(self) -> None:
        """signout."""

        res = supabase_client.auth.get_session()
        if res is not None:
            res = supabase_client.auth.sign_out()
            self.is_authenticated = False