"""App module to demo authentication with supabase."""
import reflex as rx

from .base_state import State
from .registration import registration_page as registration_page
from .login import require_login



def show_logout_or_login_comp() -> rx.Component:
    return rx.cond(
        State.is_hydrated & State.token_is_valid,
        rx.chakra.box(
            rx.chakra.link("Protected Page", href="/protected",padding_right="10px"),
            rx.chakra.link("Logout", href="/", on_click=State.do_logout),
            spacing="1.5em",
            padding_top="10%",
        ),
        rx.chakra.box(
            rx.chakra.link("Register", href="/register",padding_right="10px"),
            rx.chakra.link("Login", href="/login"),
            spacing="1.5em",
            padding_top="10%",
        )
    ) 


def index() -> rx.Component:
    """Render the index page.

    Returns:
        A reflex component.
    """
    return  rx.fragment(
        rx.chakra.color_mode_button(rx.chakra.color_mode_icon(), float="right"),
        rx.chakra.vstack(
            rx.chakra.heading("Welcome to my homepage!", font_size="2em"),
            show_logout_or_login_comp(),
        )
    )


@require_login
def protected() -> rx.Component:
    """Render a protected page.

    The `require_login` decorator will redirect to the login page if the user is
    not authenticated.

    Returns:
        A reflex component.
    """
    return rx.chakra.vstack(
        rx.chakra.heading(
            "Protected Page", font_size="2em"
        ),
        rx.chakra.link("Home", href="/"),
        rx.chakra.link("Logout", href="/", on_click=State.do_logout),
    )



app = rx.App()
app.add_page(index)
app.add_page(protected)