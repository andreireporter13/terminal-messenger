from textual.app import App, ComposeResult
from textual.widgets import Header, Input, Button, Static, Label
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
import httpx

API_URL = "http://localhost:8000"


class RegisterLoginModal(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Label("🔐 Register or Login")
        self.username_input = Input(placeholder="Username", name="username")
        self.password_input = Input(placeholder="Password", password=True, name="password")
        yield self.username_input
        yield self.password_input
        yield Horizontal(
            Button("Register", id="register_btn"),
            Button("Login", id="login_btn")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        username = self.username_input.value.strip()
        password = self.password_input.value.strip()
        self.dismiss((event.button.id, username, password))


class ChatApp(App):
    CSS_PATH = "chatapp.tcss"

    def __init__(self):
        super().__init__()
        self.token = None
        self.username = None

    def compose(self) -> ComposeResult:
        yield Static("📨 ChatApp", id="header")
        self.status = Static("🔒 Not logged in", id="chatbox")  # doar o zonă de status acum
        yield self.status

    async def on_mount(self):
        result = await self.push_screen(RegisterLoginModal())

        if result:
            action, username, password = result

            if action == "register_btn":
                success = await self.register(username, password)
                if success:
                    self.status.update("✅ User registered! Please restart app to login.")
                else:
                    self.status.update("❌ Registration failed.")

            elif action == "login_btn":
                success = await self.login(username, password)
                if success:
                    self.status.update(f"✅ Welcome back, {username}!")
                else:
                    self.status.update("❌ Login failed.")

    async def register(self, username: str, password: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}
                res = await client.post(f"{API_URL}/register/", headers=headers, json={
                    "username": username,
                    "password": password
                })
                if res.status_code == 400:
                    self.status.update("⚠️ Username already exists.")
                    return False
                res.raise_for_status()
                return True
            except httpx.HTTPStatusError as e:
                self.status.update(f"❌ Registration error: {e.response.text}")
                return False

    async def login(self, username: str, password: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}
                res = await client.post(f"{API_URL}/login/", headers=headers, json={
                    "username": username,
                    "password": password
                })
                res.raise_for_status()
                self.token = res.json()["access_token"]
                self.username = username
                return True
            except httpx.HTTPStatusError:
                return False


if __name__ == "__main__":
    app = ChatApp()
    app.run()
