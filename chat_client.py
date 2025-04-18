import httpx
from textual.app import App
from textual.widgets import Button, Input, Label, Static
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

API_URL = "http://localhost:8000"

class ChatScreen(Screen):

    def compose(self) -> None:
        yield Static("💬 Chat - Choose a Friend", id="header")

        # Butoanele Show și Hide Users puse pe orizontală
        with Horizontal():
            self.show_users_btn = Button("Show Users", id="show_users_btn")
            yield self.show_users_btn

            self.hide_users_btn = Button("Hide Users", id="hide_users_btn")
            yield self.hide_users_btn

        # Eticheta pentru utilizatorul selectat
        self.selected_friend_label = Label("No friend selected", id="selected_friend")
        yield self.selected_friend_label

        # Eticheta pentru "Message to: None" care va fi actualizată
        self.selected_friend_display = Label("Message to: None", id="selected_friend_display")
        yield self.selected_friend_display

        with Vertical(id="messages_container"):
            yield Static("Messages will appear here.", id="messages_placeholder")

        self.msg_input = Input(placeholder="Type your message here...", id="msg_input")
        yield self.msg_input

        self.send_btn = Button("Send", id="send_btn")
        self.send_btn.add_class("send_button")
        yield self.send_btn

        # Container pentru utilizatori pe orizontală
        self.users_container = Horizontal(id="users_container")
        yield self.users_container

        # Variabilă pentru a stoca utilizatorul selectat
        self.selected_user = None

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "send_btn":
            message = self.msg_input.value.strip()
            if message and self.selected_user:
                print(f"Sending message to {self.selected_user}: {message}")
                self.msg_input.value = ""
            elif not self.selected_user:
                print("No user selected. Please select a user first.")
            else:
                print("Message is empty.")

        elif button_id == "show_users_btn":
            if len(self.users_container.children) == 0:
                users = await self.get_users_from_api()
                if users:
                    self.show_users(users)
                else:
                    print("No users found.")
            else:
                print("Users are already displayed.")

            # Actualizează eticheta "Message to" dacă un user este selectat
            self.update_message_to_label()

        elif button_id == "hide_users_btn":
            self.hide_users()

        elif button_id and button_id.startswith("user_"):
            self.select_friend(event)

    async def get_users_from_api(self) -> list:
        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(f"{API_URL}/users/")
                if res.status_code == 200:
                    return res.json().get("users", [])
                else:
                    return []
            except httpx.RequestError:
                return []

    def show_users(self, users: list) -> None:
        for widget in list(self.users_container.children):
            self.users_container.children.remove(widget)

        if not users:
            return

        for user in users:
            user_button = Button(user, id=f"user_{user}")
            self.users_container.mount(user_button)

    def hide_users(self) -> None:
        for widget in list(self.users_container.children):
            widget.remove()

    def select_friend(self, event: Button.Pressed) -> None:
        selected_user = event.button.id.replace("user_", "")
        print(f"Selected user: {selected_user}")

        self.selected_user = selected_user

        try:
            self.selected_friend_display.update(f"Message to: {selected_user}")
            print(f"Updated 'Message to' label: {selected_user}")
        except Exception as e:
            print(f"Error while updating 'Message to' label: {e}")

        try:
            self.selected_friend_label.update(f"You are now chatting with {selected_user}")
            print(f"Updated 'You are now chatting with' label to: {selected_user}")
        except Exception as e:
            print(f"Error while updating 'selected_friend' label: {e}")


    def update_message_to_label(self):
        if self.selected_user:
            self.selected_friend_display.update(f"Message to: {self.selected_user}")
        else:
            self.selected_friend_display.update("Message to: None")


class AuthApp(App):
    CSS_PATH = 'chatapp.tcss'

    def __init__(self):
        super().__init__()
        self.is_register = True

    def compose(self):
        yield Static("🔐 Register or Login", id="header")

        with Vertical():
            self.username_input = Input(placeholder="Username", id="username_input")
            self.password_input = Input(placeholder="Password", password=True, id="password_input")
            self.status_label = Label("Enter your details", id="status_label")

            yield self.username_input
            yield self.password_input

            yield Horizontal(
                Button("Register", id="register_btn"),
                Button("Login", id="login_btn"),
                id="action_buttons"
            )

            yield self.status_label

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register_btn":
            username = self.username_input.value.strip()
            password = self.password_input.value.strip()

            if not username or not password:
                self.status_label.update("❌ Please enter both username and password.")
                return

            self.status_label.update("⏳ Sending request...")
            success, message = await self.register(username, password)
            self.status_label.update(message)

        elif event.button.id == "login_btn":
            username = self.username_input.value.strip()
            password = self.password_input.value.strip()

            if not username or not password:
                self.status_label.update("❌ Please enter both username and password.")
                return

            self.status_label.update("⏳ Sending request...")
            success, message = await self.login(username, password)
            self.status_label.update(message)

            if success:
                self.push_screen(ChatScreen())

    async def register(self, username: str, password: str) -> tuple:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}
                data = {"username": username, "password": password}
                res = await client.post(f"{API_URL}/register/", headers=headers, json=data)

                if res.status_code == 200:
                    return True, "✅ User registered successfully!"
                elif res.status_code == 400:
                    return False, "❌ Username already exists."
                else:
                    return False, f"❌ Unexpected response: {res.status_code}. Message: {res.text}"

            except httpx.RequestError as e:
                return False, f"❌ Request failed: {str(e)}"

            except Exception as e:
                return False, f"❌ An error occurred: {str(e)}"

    async def login(self, username: str, password: str) -> tuple:
        async with httpx.AsyncClient() as client:
            try:
                headers = {"Content-Type": "application/json"}
                data = {"username": username, "password": password}
                res = await client.post(f"{API_URL}/login/", headers=headers, json=data)

                if res.status_code == 200:
                    return True, "✅ Login successful!"
                elif res.status_code == 401:
                    return False, "❌ Invalid credentials."
                else:
                    return False, f"❌ Unexpected response: {res.status_code}. Message: {res.text}"

            except httpx.RequestError as e:
                return False, f"❌ Request failed: {str(e)}"

            except Exception as e:
                return False, f"❌ An error occurred: {str(e)}"

if __name__ == "__main__":
    app = AuthApp()
    app.run()
