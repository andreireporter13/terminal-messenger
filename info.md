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

websocat "ws://localhost:8000/ws/?token=token"
