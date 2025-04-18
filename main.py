from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
#
from pydantic import BaseModel
from typing import Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
import json
import re

# MegaSecret KEYs
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "app://."
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB for current session :)))
fake_users_db: Dict[str, dict] = {}

# Configurare parole + tokenuri
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# === MODELS ===
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    to: str
    msg: str


# === SECURITY FUNCTIONS ===
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(username: str) -> str:
    return jwt.encode({"sub": username}, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# === CONNECTIONS ===
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_private_message(self, receiver: str, message: str):
        if receiver in self.active_connections:
            await self.active_connections[receiver].send_text(message)


manager = ConnectionManager()


# === ENDPOINTS ===
@app.post("/register/")
async def register(user: UserRegister):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already registered")

    hashed_password = get_password_hash(user.password)
    fake_users_db[user.username] = {"username": user.username, "hashed_password": hashed_password}
    return {"message": "User created successfully"}


@app.post("/login/")
async def login(user: UserLogin):
    user_data = fake_users_db.get(user.username)
    if not user_data or not verify_password(user.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/users/")
async def list_users():
    return {"users": list(fake_users_db.keys())}


# WEBSOCKET CONNECTION - JSON VERSION
@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    print("WebSocket request received!")
    if not token:
        raise HTTPException(status_code=400, detail="Token is missing")
    username = decode_jwt(token)
    if not username:
        await websocket.close()
        return

    await manager.connect(websocket, username)
    print(f"User {username} connected.")
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            receiver = message_data["to"]
            message = message_data["msg"]
            await manager.send_private_message(receiver, f"{username}: {message}")
    except WebSocketDisconnect:
        manager.disconnect(username)
