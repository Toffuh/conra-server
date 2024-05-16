import asyncio
from websockets.server import serve


async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)


class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def draw(self):
        print("draw")

    async def draw_continuously(self):
        while True:
            await self.draw()
            await asyncio.sleep(1 / 10)


runner = BackgroundRunner()


async def main():
    asyncio.create_task(runner.draw_continuously())
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
