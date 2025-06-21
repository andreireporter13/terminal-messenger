# terminal-messenger on VPS Server and Kubernetes (K3S on RPI 5)

A terminal-based messaging app that can be deployed on a **VPS** using Docker + NGINX or inside a **Kubernetes cluster** (e.g., on Raspberry Pi 5).

---

## 🔧 Install on VPS (Docker + NGINX)

### 1. Clone the repository
```bash
git clone https://github.com/andreireporter13/terminal-messenger.git
cd terminal-messenger
```

### 2. Use the included Dockerfile
The project already includes a Dockerfile in the root directory, so you can build and run the app directly without modifying anything.
```bash
docker build -t terminal-messenger .
docker run -d -p 8000:8000 terminal-messenger
```

### 3. 🎬 Demo & Walkthrough

Watch terminal-messenger live in action:

[![terminal-messenger Demo](https://img.youtube.com/vi/wqdllVNsiyw/0.jpg)](https://www.youtube.com/watch?v=wqdllVNsiyw)
*Demo by Andrei Reporter*
