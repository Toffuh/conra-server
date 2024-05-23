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
        # -1 == left | 0 == stop | 1 == right
        self.direction = 0
        self.jump = False

        self.pos = (0, 0)

    def set_color(self, color: Color):
        self.color = color

    def set_direction(self, direction: str):
        if direction == "left":
            self.direction = -1
        if direction == "right":
            self.direction = 1
        if direction == "stop":
            self.direction = 0

    def jump_now(self):
        self.jump = True

    def __str__(self):
        return "player: color-{} direction-{}".format(self.color, self.direction)


players: [Player] = []


async def echo(websocket):
    client_id = uuid.uuid4()
    print("user connected - {}".format(client_id))

    player = Player()
    players.append(player)

    async for message in websocket:
        if message.startswith("color:"):
            message = message.lstrip("color:")
            player.set_color(color_from_hex(message))

        if message.startswith("direction:"):
            message = message.replace("direction:", "")
            player.set_direction(message)

        if message.startswith("jump:"):
            player.jump_now()

        await websocket.send(message)

    print("user disconnected - {}".format(client_id))
    players.remove(player)


class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def draw(self):
        # clear screen
        print(40 * "\n")

        for y in range(0, 9):
            for x in range(0, 9):

                has_player = False

                for player in players:
                    if player.pos[0] == x and player.pos[1] == y:
                        has_player = True

                if has_player:
                    print("■", end="")
                else:
                    print(" ", end="")
            print("")

    def update(self):
        for player in players:
            player.pos = (player.pos[0] + player.direction, player.pos[1])

    async def draw_continuously(self):
        while True:
            self.update()
            await self.draw()
            await asyncio.sleep(1 / 10)


runner = BackgroundRunner()


async def main():
    asyncio.create_task(runner.draw_continuously())
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
