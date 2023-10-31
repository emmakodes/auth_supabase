"""App module to demo authentication with supabase."""
import reflex as rx

from .base_state import State

from .registration import registration_page as registration_page
from .login import require_login


import supabase
from dotenv import load_dotenv
import os

# load env
load_dotenv()

# setup supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client = supabase.Client(supabase_url, supabase_key)


def index() -> rx.Component:
    """Render the index page.

    Returns:
        A reflex component.
    """
    # is_authenticated = supabase_client.auth.get_session() is not None
    # print('this is_authenticated',is_authenticated)

    return rx.fragment(
        rx.color_mode_button(rx.color_mode_icon(), float="right"),
        rx.vstack(
            rx.heading("Welcome to my homepage!", font_size="2em"),
            rx.cond(
                State.is_hydrated & ~State.is_authenticated,
                rx.link("Register", href="/register"),),


            rx.cond(
                State.is_hydrated & ~State.is_authenticated,
                rx.link("Login", href="/login"),),

            rx.cond(
                State.is_hydrated & State.is_authenticated,
                rx.link("Protected Page", href="/protected"),),

            rx.cond(
                State.is_hydrated & State.is_authenticated,
                rx.link("Logout", href="/", on_click=State.do_logout),),
            spacing="1.5em",
            padding_top="10%",
        ),
    )


@require_login
def protected() -> rx.Component:
    """Render a protected page.

    The `require_login` decorator will redirect to the login page if the user is
    not authenticated.

    Returns:
        A reflex component.
    """
    return rx.vstack(
        rx.heading(
            "Protected Page", font_size="2em"
        ),
        rx.link("Home", href="/"),
        rx.link("Logout", href="/", on_click=State.do_logout),
    )







app = rx.App()
app.add_page(index)
app.add_page(protected)
app.compile()