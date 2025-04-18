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

        self.selected_friend_label = Label("No friend selected", id="selected_friend")
        yield self.selected_friend_label

        # Adăugăm câmpul pentru a arăta utilizatorul ales
        self.selected_friend_display = Label("Message to: None", id="selected_friend_display")
        yield self.selected_friend_display  # Afișăm utilizatorul ales

        with Vertical(id="messages_container"):
            yield Static("Messages will appear here.", id="messages_placeholder")

        self.msg_input = Input(placeholder="Type your message here...", id="msg_input")
        yield self.msg_input

        self.send_btn = Button("Send", id="send_btn")
        self.send_btn.add_class("send_button")
        yield self.send_btn

        # Container pentru utilizatori (dacă nu există deja)
        self.users_container = Vertical(id="users_container")
        yield self.users_container  # Asigură-te că există un container pentru utilizatori

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_btn":
            message = self.msg_input.value.strip()
            if message:
                print(f"Sending message: {message}")
                self.msg_input.value = ""  # Șterge câmpul de input
            else:
                print("Message is empty.")

        elif event.button.id == "show_users_btn":
            # Verificăm dacă utilizatorii sunt deja afișați
            if len(self.users_container.children) == 0:
                # Afișăm utilizatorii când apesi pe "Show Users"
                users = await self.get_users_from_api()
                if users:
                    self.show_users(users)
                else:
                    print("No users found.")
            else:
                print("Users are already displayed.")

        elif event.button.id == "hide_users_btn":
            # Ascundem utilizatorii când apesi pe "Hide Users"
            self.hide_users()

    async def get_users_from_api(self) -> list:
        async with httpx.AsyncClient() as client:
            try:
                print("Making API request...")
                res = await client.get(f"{API_URL}/users/")
                print(f"API response status: {res.status_code}")
                print(f"API response body: {res.text}")

                if res.status_code == 200:
                    users = res.json().get("users", [])
                    print(f"Users fetched: {users}")
                    return users
                else:
                    print(f"Error fetching users: {res.status_code}")
                    return []
            except httpx.RequestError as e:
                print(f"Request error: {e}")
                return []

    def show_users(self, users: list) -> None:
        # Înainte de a adăuga butoane, curățăm containerul de utilizatori
        for widget in list(self.users_container.children):  # Iterăm prin copii
            self.users_container.children.remove(widget)  # Îndepărtăm fiecare widget existent

        # Verificăm dacă utilizatorii au fost adăugați
        if not users:
            print("No users to display.")
            return

        # Creăm butoane pentru fiecare utilizator activ
        for user in users:
            user_button = Button(user, id=f"user_{user}")
            print(f"Creating button for user: {user}")  # Verificăm dacă butonul este creat corect
            user_button.on_click = self.select_friend
            self.users_container.mount(user_button)
            print(f"User button {user} added to container.")  # Confirmare că butonul este adăugat

    def hide_users(self) -> None:
        # Ascundem lista de utilizatori prin eliminarea butoanelor
        for widget in list(self.users_container.children):  # Iterăm prin copii
            widget.remove()  # Îndepărtăm fiecare widget din container
        print("Users have been hidden.")  # Confirmare că utilizatorii au fost ascunși

    def select_friend(self, event: Button.Pressed) -> None:
        selected_user = event.button.id.replace("user_", "")
        print(f"Selected user: {selected_user}")  # Verificăm că funcția este apelată

        # Actualizare eticheta "Message to"
        self.selected_friend_display.update(f"Message to: {selected_user}")
        print(f"Updated message display: Message to: {selected_user}")  # Verificăm că se face update-ul corect

        # Actualizare eticheta "You are now chatting with"
        self.selected_friend_label.update(f"You are now chatting with {selected_user}")
        print(f"Updated label: You are now chatting with {selected_user}")  # Verificăm că se face update-ul corect




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
