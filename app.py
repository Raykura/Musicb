import websocket
import json
import requests
import base64
import threading
import time

# Bot API credentials
api_key = "432f23df3fc5076fe6c95ade994a533c9d473ecdb56acc31346899a94d6aaa6d"
room_id = "66d2726b2e80dd1f614c4dbb"

# Spotify credentials
client_id = "81135a7c3bb54c5ebdedb7dc95a8f5aa"
client_secret = "a85f1ed1eb5a4fa8afeb680acb2ef9f0"

# WebSocket URL for Highrise bots
websocket_url = f"wss://highrise.game/web/botapi?api_key={api_key}&room_id={room_id}"

def on_message(ws, message):
    print("Received message:", message)
    msg_data = json.loads(message)
    
    if msg_data.get('type') == 'chat':
        user_message = msg_data.get('message')
        if user_message.startswith('!play '):
            song_name = user_message[6:]
            play_song(song_name)

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

def play_song(song_name):
    token = get_spotify_token()
    search_url = f"https://api.spotify.com/v1/search?q={song_name}&type=track"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(search_url, headers=headers)
    song_data = response.json()
    
    if song_data['tracks']['items']:
        track = song_data['tracks']['items'][0]
        track_name = track['name']
        track_url = track['external_urls']['spotify']
        response_message = {
            "type": "chat",
            "message": f"Now playing: {track_name} - {track_url}"
        }
        ws.send(json.dumps(response_message))
    else:
        response_message = {
            "type": "chat",
            "message": f"Sorry, I couldn't find the song '{song_name}'."
        }
        ws.send(json.dumps(response_message))

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("Connection closed")

def on_open(ws):
    print("Connection opened")
    initial_message = {
        "type": "chat",
        "message": "MGBot has entered the room! Use !play <song name> to play a song."
    }
    ws.send(json.dumps(initial_message))

def keep_alive(ws):
    while True:
        time.sleep(30)
        keep_alive_message = {
            "type": "chat",
            "message": "Keep alive"
        }
        ws.send(json.dumps(keep_alive_message))

ws = websocket.WebSocketApp(websocket_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.on_open = on_open

# Run the WebSocket
ws.run_forever()
