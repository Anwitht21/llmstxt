import asyncio
import websockets
import json

async def test_crawl():
    uri = "ws://localhost:8000/ws/crawl"

    async with websockets.connect(uri) as websocket:
        payload = {
            "url": "https://example.com",
            "maxPages": 3,
            "descLength": 200
        }

        await websocket.send(json.dumps(payload))
        print(f"Sent: {payload}\n")

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if data["type"] == "log":
                    print(f"[LOG] {data['content']}")
                elif data["type"] == "result":
                    print(f"\n[RESULT]\n{data['content'][:500]}...")
                elif data["type"] == "url":
                    print(f"\n[HOSTED URL] {data['content']}")
                elif data["type"] == "error":
                    print(f"\n[ERROR] {data['content']}")

            except websockets.exceptions.ConnectionClosed:
                print("\nConnection closed")
                break

if __name__ == "__main__":
    asyncio.run(test_crawl())
