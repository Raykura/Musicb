import requests
import json
import websockets
import asyncio

class HighriseMusicBot:
    def __init__(self):
        self.queue = []
        self.current_song = None
        self.spotify_access_token = None
        self.bot_api_key = "432f23df3fc5076fe6c95ade994a533c9d473ecdb56acc31346899a94d6aaa6d"
        self.room_id = "66d2726b2e80dd1f614c4dbb"
        self.spotify_client_id = "81135a7c3bb54c5ebdedb7dc95a8f5aa"
        self.spotify_client_secret = "a85f1ed1eb5a4fa8afeb680acb2ef9f0"
        self.token_url = "https://accounts.spotify.com/api/token"
        self.websocket_url = "wss://highrise.game/web/botapi"

    async def get_spotify_token(self):
        headers = {
            "Authorization": f"Basic {self.spotify_client_id}:{self.spotify_client_secret}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials"
        }
        response = requests.post(self.token_url, headers=headers, data=data)
        if response.status_code == 200:
            self.spotify_access_token = response.json()["access_token"]

    async def search_song(self, song_name):
        url = f"https://api.spotify.com/v1/search?q={song_name}&type=track"
        headers = {"Authorization": f"Bearer {self.spotify_access_token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tracks = response.json()['tracks']['items']
            if tracks:
                return tracks[0]['uri']  # Return the first track's URI
        return None

    async def play_song(self, song_uri):
        self.current_song = song_uri
        self.queue.append(song_uri)
        payload = {
            "api_key": self.bot_api_key,
            "room_id": self.room_id,
            "action": "play",
            "song_uri": song_uri
        }
        async with websockets.connect(self.websocket_url) as websocket:
            await websocket.send(json.dumps(payload))

    async def show_queue(self):
        return self.queue

    async def skip_song(self):
        if self.queue:
            self.queue.pop(0)  # Remove the first song
            if self.queue:  # Play the next song if available
                next_song = self.queue[0]
                await self.play_song(next_song)

    async def handle_command(self, command):
        if command.startswith("-p "):
            song_name = command[3:]

            # Check if it's a URL (basic check)
            if song_name.startswith("http://") or song_name.startswith("https://"):
                await self.play_radio(song_name)
                return f"Now playing radio: {song_name}"

            # Otherwise, treat it as a song name for Spotify
            song_uri = await self.search_song(song_name)
            if song_uri:
                await self.play_song(song_uri)
                return f"Now playing: {song_name}"
            return "Song not found."
        elif command == "-q":
            return await self.show_queue()
        elif command == "-skip":
            await self.skip_song()
            return "Skipped to next song."
        return "Unknown command."

    async def listen_for_commands(self):
        async with websockets.connect(self.websocket_url) as websocket:
            while True:
                command = await websocket.recv()
                response = await self.handle_command(command)
                print(response)  # You can adjust this to send responses back to the chat

    async def run(self):
        await self.get_spotify_token()
        await self.listen_for_commands()

if __name__ == "__main__":
    bot = HighriseMusicBot()
    asyncio.run(bot.run())
