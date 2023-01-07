import os
import asyncio
from fastapi import FastAPI, WebSocket, Cookie, Depends, WebSocketDisconnect
from jose import jwt
import redis
import datetime
import uuid
import json
import logging

r = redis.Redis(host='redis', port=6379)

JWT_SECRET = os.environ.get('JWT_SECRET')
assert JWT_SECRET is not None, "Please set JWT_SECRET"

#
# WEBSOCKET MANAGER
#
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        # we make a copy to avoid iterating over a list that might be modified
        # during iteration.
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except RunTimeError as error:
                # this can happen if a websocket is closed during iteration.
                print(error)

manager = ConnectionManager()

# 
# BROADCAST TO WEBSOCKETS
#
def broadcast_chat_messages_from_redis(message_from_redis):
    async def async_wrapper ():
        await manager.broadcast(message_from_redis["data"].decode())
    asyncio.run(async_wrapper())

broadcaster = r.pubsub(ignore_subscribe_messages=True)
broadcaster.subscribe(**{'chat': broadcast_chat_messages_from_redis})

thread = broadcaster.run_in_thread(sleep_time=0.005, daemon=True)

#
# RECEIVE FROM WEBSOCKETS
# 
app = FastAPI()

async def auth_token(
    websocket: WebSocket,
    session: str | None = Cookie(default=None),
):
    if session is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    session = jwt.decode(session, JWT_SECRET)
    return session

@app.websocket("/")
async def websocket_endpoint(
    websocket: WebSocket,
    session: str = Depends(auth_token)
):
    r = redis.Redis(host='redis', port=6379)
    # Obtention de l'identifiant du client
    client_id = session["id"]
    username = session["username"]
    await manager.connect(websocket)
     # Récupération des 20 derniers messages
    messages = r.lrange('messages', -20, -1)
    for message in messages:
        # Convert the message into a dict
        message = json.loads(message.decode())
        
        # Gets the reactions for the specified message and merge it to the current message
        reaction = r.get(f"message:{message['id']}")
        reaction = json.loads(reaction)["reaction"]
        message['reaction'] = reaction

        # Convert to json and send the response
        message = json.dumps(message)
        await websocket.send_text(message)

    try:
        while True:

            # Réception de messages du client
            message = await websocket.receive_text()
            if message:
                # Décodage du message en JSON
                data = json.loads(message)

            if 'reaction' in data:
                # Récupération du message
                key = f"message:{data['id']}"
                jsonString = r.get(key)
                message = json.loads(jsonString)

                # Vérification si l'utilisateur peut retirer ou ajouter une réaction
                found = False
                for reaction in message['reaction']:
                    if reaction['reaction'] == data['reaction']:
                        if data['id'] in reaction['client']:
                            reaction['client'].remove(data['id'])
                        else:
                            reaction['client'].append(data['id'])
                        found = True
                        break
                if not found:
                    message['reaction'].append({ "reaction": data['reaction'], "client": [data['id']] })

                message['type'] = "reaction"
                # Enregistrement du message mis à jour
                r.set(key, json.dumps(message))
                manager.broadcast
                await manager.broadcast(json.dumps(message))

            else:
                # Préparation du message
                message = {
                    "id": uuid.uuid4().hex,  # Génération d'un ID unique pour le message
                    "client_id": client_id,
                    "username": username,
                    "message": data['message'],
                    "date": datetime.datetime.utcnow().isoformat(),
                    "reaction": []
                }

                # Enregistrement du message dans la liste "messages"
                key = f"message:{message['id']}"
                r.set(key, json.dumps(message))
                r.rpush('messages', json.dumps(message))

                # Publication du message sur le canal "chat"
                r.publish('chat', json.dumps(message))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
