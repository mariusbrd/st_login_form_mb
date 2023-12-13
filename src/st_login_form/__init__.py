import os
import streamlit as st
from supabase import Client, create_client 


__version__ = "0.2.1"


@st.cache_resource
def init_connection() -> Client:
    try:
        SUPABASE_URL = st.secrets["SUPABASE_URL"]
        SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    except:
        SUPABASE_URL = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def login_success(message: str, username: str) -> None:
    st.success(message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username


# Create the python function that will be called
def login_form(
    title: str = "Benutzer-Verwaltung",
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    create_title: str = "Registrieren :baby: ",
    login_title: str = "Login :prince: ",
    allow_guest: bool = False,
    guest_title: str = "Gäste :ninja: ",
    create_username_label: str = "Email-Adresse",
    create_username_placeholder: str = None,
    create_username_help: str = None,
    create_password_label: str = "Passwort erstellen",
    create_password_placeholder: str = None,
    create_password_help: str = "Das Passwort wird im Klartext gespeichert. Nicht von anderen Websites wiederverwenden. Das Passwort kann nicht wiederhergestellt werden.",
    create_submit_label: str = "Konto erstellen",
    create_success_message: str = "Konto erstellt :tada:",
    login_username_label: str = "Email-Adresse",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Passwort",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    login_submit_label: str = "Login",
    login_success_message: str = "Anmeldung erfolgreich :tada:",
    login_error_message: str = "Falscher Benutzername/Passwort :x: ",
    guest_submit_label: str = "Anmeldung als Gast",
) -> Client:
    """Creates a user login form in Streamlit apps.

    Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets.
    Sets `session_state["authenticated"]` to True if the login is successful.
    Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

    Returns:
    Supabase client instance
    """

    # Initialize supabase connection
    client = init_connection()

    # User Authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = None

    with st.expander(title, expanded=not st.session_state["authenticated"]):
        if allow_guest:
            create_tab, login_tab, guest_tab = st.tabs(
                [
                    create_title,
                    login_title,
                    guest_title,
                ]
            )
        else:
            create_tab, login_tab = st.tabs(
                [
                    create_title,
                    login_title,
                ]
            )

        # Create new account
        with create_tab:
            with st.form(key="create"):
                username = st.text_input(
                    label=create_username_label,
                    placeholder=create_username_placeholder,
                    help=create_username_help,
                    disabled=st.session_state["authenticated"],
                )

                password = st.text_input(
                    label=create_password_label,
                    placeholder=create_password_placeholder,
                    help=create_password_help,
                    type="password",
                    disabled=st.session_state["authenticated"],
                )

                if st.form_submit_button(
                    label=create_submit_label,
                    type="primary",
                    disabled=st.session_state["authenticated"],
                ):
                    try:
                        data, _ = (
                            client.table(user_tablename)
                            .insert({username_col: username, password_col: password})
                            .execute()
                        )
                    except Exception as e:
                        st.error(e.message)
                    else:
                        login_success(create_success_message, username)

        # Login to existing account
        with login_tab:
            with st.form(key="login"):
                username = st.text_input(
                    label=login_username_label,
                    placeholder=login_username_placeholder,
                    help=login_username_help,
                    disabled=st.session_state["authenticated"],
                )

                password = st.text_input(
                    label=login_password_label,
                    placeholder=login_password_placeholder,
                    help=login_password_help,
                    type="password",
                    disabled=st.session_state["authenticated"],
                )

                if st.form_submit_button(
                    label=login_submit_label,
                    disabled=st.session_state["authenticated"],
                    type="primary",
                ):
                    data, _ = (
                        client.table(user_tablename)
                        .select(f"{username_col}, {password_col}")
                        .eq(username_col, username)
                        .eq(password_col, password)
                        .execute()
                    )

                    if len(data[-1]) > 0:
                        login_success(login_success_message, username)
                    else:
                        st.error(login_error_message)

        # Guest login
        if allow_guest:
            with guest_tab:
                if st.button(
                    label=guest_submit_label,
                    type="primary",
                    disabled=st.session_state["authenticated"],
                ):
                    st.session_state["authenticated"] = True

        return client


def main() -> None:
    login_form(
        create_username_placeholder="Username will be visible in the global leaderboard.",
        create_password_placeholder="⚠️ Password will be stored as plain text. You won't be able to recover it if you forget.",
        guest_submit_label="Play as a guest ⚠️ Scores won't be saved",
    )


if __name__ == "__main__":
    main()
