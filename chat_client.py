from textual.app import App, ComposeResult
from textual.widgets import Header, Input, Button, Static, Label
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
import httpx

API_URL = "http://localhost:8000"  # API URL for login and registration


# RegisterLoginModal is the modal screen for registration or login.
class RegisterLoginModal(ModalScreen):
    def compose(self) -> ComposeResult:
        # Compose the layout of the modal screen
        yield Label("🔐 Register or Login")  # Title label
        self.username_input = Input(placeholder="Username", name="username")  # Input for username
        self.password_input = Input(placeholder="Password", password=True, name="password")  # Input for password
        yield self.username_input
        yield self.password_input
        # Two buttons: Register and Login
        yield Horizontal(
            Button("Register", id="register_btn"),  # Register button
            Button("Login", id="login_btn")         # Login button
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # When a button is pressed, grab the username and password values
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        # Dismiss the modal with the button ID and entered credentials
        self.dismiss((event.button.id, username, password))


# Main ChatApp class
class ChatApp(App):
    CSS_PATH = "chatapp.tcss"  # Path to the CSS file for styling

    def __init__(self):
        super().__init__()
        self.token = None  # To store the JWT token after login
        self.username = None  # To store the username of the logged-in user

    def compose(self) -> ComposeResult:
        # Compose the main screen layout with a title and status message
        yield Static("📨 ChatApp", id="header")  # Static header text
        self.status = Static("🔒 Not logged in", id="chatbox")  # Status showing the login state
        yield self.status

        # Adding "Back to Login" button in chat screen
        yield Button("Back to Login", id="back_to_login_btn")

    async def on_mount(self):
        # Show the RegisterLoginModal screen when the app starts
        result = await self.push_screen(RegisterLoginModal())

        if result:
            action, username, password = result  # Get the action (register or login) and credentials

            if action == "register_btn":
                # If the user clicked "Register", attempt to register
                success = await self.register(username, password)
                if success:
                    self.status.update("✅ User registered! Please restart app to login.")  # Show success message
                else:
                    self.status.update("❌ Registration failed.")  # Show failure message

            elif action == "login_btn":
                # If the user clicked "Login", attempt to login
                success = await self.login(username, password)
                if success:
                    self.status.update(f"✅ Welcome back, {username}!")  # Show welcome message
                else:
                    self.status.update("❌ Login failed.")  # Show failure message

    async def register(self, username: str, password: str) -> bool:
        # Perform user registration via an HTTP POST request
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}  # Set request headers
                res = await client.post(f"{API_URL}/register/", headers=headers, json={
                    "username": username,
                    "password": password
                })
                if res.status_code == 400:
                    self.status.update("⚠️ Username already exists.")  # Handle existing username error
                    return False
                res.raise_for_status()  # Raise an exception for any HTTP error status
                return True
            except httpx.HTTPStatusError as e:
                self.status.update(f"❌ Registration error: {e.response.text}")  # Show error message
                return False

    async def login(self, username: str, password: str) -> bool:
        # Perform user login via an HTTP POST request
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}  # Set request headers
                res = await client.post(f"{API_URL}/login/", headers=headers, json={
                    "username": username,
                    "password": password
                })
                res.raise_for_status()  # Raise an exception for any HTTP error status
                self.token = res.json()["access_token"]  # Store the access token on successful login
                self.username = username  # Store the username on successful login
                return True
            except httpx.HTTPStatusError:
                return False

    # Event handler for "Back to Login" button
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_to_login_btn":
            # When "Back to Login" is clicked, show the login screen again
            await self.push_screen(RegisterLoginModal())


# Main entry point to run the app
if __name__ == "__main__":
    app = ChatApp()  # Create an instance of the ChatApp
    app.run()  # Run the app
