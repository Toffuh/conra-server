import asyncio
import uuid

from websockets.server import serve

players = []


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return "{}-{}-{}".format(self.r, self.g, self.b)


def color_from_hex(hex_string: str) -> Color:
    hex_string = hex_string.lstrip("#")
    values = tuple(int(hex_string[i:i + 2], 16) for i in (0, 2, 4))
    return Color(values[0], values[1], values[2])


class Player:
    def __init__(self):
        self.color = None

    def set_color(self, color: Color):
        self.color = color

    def __str__(self):
        return "player: color-{}".format(self.color)


players: [Player] = []


async def echo(websocket):
    client_id = uuid.uuid4()
    print("user connected - {}".format(client_id))

    player = Player()
    players.append(player)

    async for message in websocket:
        print("received message from {} - {}".format(client_id, message))

        if message.startswith("color:"):
            message = message.lstrip("color:")
            player.set_color(color_from_hex(message))

        await websocket.send(message)

    print("user disconnected - {}".format(client_id))
    players.remove(player)


class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def draw(self):
        print("draw")
        for player in players:
            print(player)

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
