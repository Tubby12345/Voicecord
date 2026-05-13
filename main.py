import asyncio
import json
import requests
import websockets

TOKEN = "MTQ5NzMxNTAxOTcxMTQ0NzE5Mg.GG7Q_Q.kC1-C77TAjX-nG78IQMiOr78oT0Vw03JdNEF9w"
GUILD_ID = "1406578842499551322"
CHANNEL_ID = "1480834475972759563"

STATUS = "online" # online / dnd / idle
SELF_MUTE = False
SELF_DEAF = False

API = "https://discord.com/api/v10"

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

    async with websockets.connect(uri, max_size=10 * 1024 * 1024) as ws:
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

        print("Joined the voice channel!")

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
