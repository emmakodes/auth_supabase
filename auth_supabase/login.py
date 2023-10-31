"""Login page and authentication logic."""
import reflex as rx

from .base_state import State


import supabase
from dotenv import load_dotenv
import os

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase_client = supabase.Client(supabase_url, supabase_key)



LOGIN_ROUTE = "/login"
REGISTER_ROUTE = "/register"


class LoginState(State):
    """Handle login form submission and redirect to proper routes after authentication."""

    error_message: str = ""
    redirect_to: str = ""

    is_loading: bool = False

    def on_submit(self, form_data) -> rx.event.EventSpec:
        """Handle login form on_submit.

        Args:
            form_data: A dict of form fields and values.
        """

        # set the following values to spin the button
        self.is_loading = True
        yield

        self.error_message = ""
        email = form_data["email"]
        password = form_data["password"]

        try:
            supabase_client.auth.sign_in_with_password({"email": email, "password": password})
            self.error_message = ""
            self.is_authenticated = supabase_client.auth.get_session() is not None
            return LoginState.redir()  # type: ignore
        except:
            self.error_message = "There was a problem logging in, please try again."

            # reset state variable again
            self.is_loading = False
            yield


    def redir(self) -> rx.event.EventSpec | None:
        """Redirect to the redirect_to route if logged in, or to the login page if not."""
        if not self.is_hydrated:
            # wait until after hydration
            return LoginState.redir()  # type: ignore
        page = self.get_current_page()

        # is_authenticated = supabase_client.auth.get_session() is not None
        # print('is_authenticated',is_authenticated)

        if not self.is_authenticated and page != LOGIN_ROUTE:
            self.redirect_to = page

            # reset state variable again
            self.is_loading = False
            yield

            return rx.redirect(LOGIN_ROUTE)
        elif page == LOGIN_ROUTE:

            # reset state variable again
            self.is_loading = False
            yield

            return rx.redirect(self.redirect_to or "/")



@rx.page(route=LOGIN_ROUTE)
def login_page() -> rx.Component:
    """Render the login page.

    Returns:
        A reflex component.
    """
    login_form = rx.form(
        rx.input(placeholder="email", id="email", type_="email"),
        rx.password(placeholder="password", id="password"),
        rx.button("Login", type_="submit", is_loading=LoginState.is_loading),
        width="80vw",
        on_submit=LoginState.on_submit,
    )

    return rx.fragment(
        rx.cond(
            LoginState.is_hydrated,  # type: ignore
            rx.vstack(
                rx.cond(  # conditionally show error messages
                    LoginState.error_message != "",
                    rx.text(LoginState.error_message),
                ),
                login_form,
                rx.link("Register", href=REGISTER_ROUTE),
                padding_top="10vh",
            ),
        )
    )



def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Decorator to require authentication before rendering a page.

    If the user is not authenticated, then redirect to the login page.

    Args:
        page: The page to wrap.

    Returns:
        The wrapped page component.
    """

    def protected_page():
        # is_authenticated = supabase_client.auth.get_session() is not None
        return rx.fragment(
            rx.cond(
                State.is_hydrated & State.is_authenticated, # type: ignore
                page(),
                rx.center(
                    # When this spinner mounts, it will redirect to the login page
                    rx.spinner(on_mount=LoginState.redir),
                ),
            )
        )

    protected_page.__name__ = page.__name__
    return protected_page
