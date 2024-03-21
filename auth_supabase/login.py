"""Login page and authentication logic."""
import reflex as rx

from .base_state import State
from .supabase__client import supabase_client



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
            user_sign_in = supabase_client().auth.sign_in_with_password({"email": email, "password": password})
            self.auth_token = user_sign_in.session.access_token
            self.error_message = ""
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

        if not self.token_is_valid and page != LOGIN_ROUTE:
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
    login_form = rx.chakra.form(
        rx.chakra.input(placeholder="email", id="email", type_="email"),
        rx.chakra.password(placeholder="password", id="password"),
        rx.chakra.button("Login", type_="submit", is_loading=LoginState.is_loading),
        width="80vw",
        on_submit=LoginState.on_submit,
    )

    return rx.fragment(
        rx.cond(
            LoginState.is_hydrated,  # type: ignore
            rx.chakra.vstack(
                rx.cond(  # conditionally show error messages
                    LoginState.error_message != "",
                    rx.chakra.text(LoginState.error_message),
                ),
                login_form,
                rx.chakra.link("Register", href=REGISTER_ROUTE),
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
        return rx.fragment(
            rx.cond(
                State.is_hydrated,                
                rx.cond(
                    State.token_is_valid, page(), login_page()
                ), 
                rx.chakra.center(
                    # When this spinner mounts, it will redirect to the login page
                    rx.chakra.spinner(),
                ),
            )
        )

    protected_page.__name__ = page.__name__
    return protected_page
