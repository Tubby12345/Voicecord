import asyncio
import json
import requests
import websockets
import os

# ดึงค่าจาก Environment Variables
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("SERVER_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")

STATUS = os.getenv("STATUS", "online")
SELF_MUTE = os.getenv("SELF_MUTE", "False").lower() in ("true", "1", "yes")
SELF_DEAF = os.getenv("SELF_DEAF", "False").lower() in ("true", "1", "yes")

API = "https://discord.com/api/v10"

if not TOKEN or not GUILD_ID or not CHANNEL_ID:
    print("Error: Missing required environment variables! (TOKEN, SERVER_ID, or CHANNEL_ID)")
    exit()

res = requests.get(f"{API}/users/@me", headers={"Authorization": TOKEN})
if res.status_code != 200:
    print("Invalid token!")
    exit()

user = res.json()
print(f"Logged in as {user['username']} ({user['id']})!")

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))

async def main():
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"

    # [FIXED] ตั้งค่า max_size=None เพื่อไม่จำกัดขนาดข้อความ ป้องกัน Error 1009 (message too big)
    async with websockets.connect(uri, max_size=None) as ws:
        hello = json.loads(await ws.recv())
        heartbeat_interval = hello["d"]["heartbeat_interval"]

        asyncio.create_task(heartbeat(ws, heartbeat_interval))

        await ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                },
                "presence": {
                    "status": STATUS,
                    "afk": False
                }
            }
        }))

        while True:
            event = json.loads(await ws.recv())
            if event.get("t") == "READY":
                break

        await ws.send(json.dumps({
            "op": 4,
            "d": {
                "guild_id": GUILD_ID,
                "channel_id": CHANNEL_ID,
                "self_mute": SELF_MUTE,
                "self_deaf": SELF_DEAF
            }
        }))

        print(f"Joined the voice channel! (Mute: {SELF_MUTE}, Deaf: {SELF_DEAF})")

        while True:
            try:
                msg = await ws.recv()
            except:
                print("Disconnected, reconnecting...")
                break

async def run():
    while True:
        try:
            await main()
        except Exception as e:
            print("Error: ", e)
            await asyncio.sleep(5)

asyncio.run(run())
