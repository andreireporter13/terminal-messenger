curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ion", "password": "parola123"}'


curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ion", "password": "parola123"}'


curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "maria", "password": "parola321"}'


curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "maria", "password": "parola321"}'

curl http://localhost:8000/users/

# ion
websocat "ws://localhost:8000/ws/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJpb24ifQ.KoNnadSAMPoTCEpRgIL7QnoX56rVoouB69TpLlZCxQQ"
"maria" "Hello, can you help me?"

# maria
websocat "ws://localhost:8000/ws/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJpYSJ9.7zpVfCE85elhQzORCPU3tWlUHO6jN3NVT_jBekC303M"
"ion" "Hello, how are you?"

# JSON VERSION
{"to": "maria", "msg": "Hello, Ion, ce faci?"}

uvicorn main:app --reload --host 0.0.0.0 --port 8000

# LocalTunnel
curl https://loca.lt/mytunnelpassword

lt --port 8000 --subdomain zsecretchat2025
