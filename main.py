import asyncio
import uuid

from sense_hat import SenseHat

sense = SenseHat()

from websockets.server import serve

players = []

screenWidth = 8


class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return "{}-{}-{}".format(self.r, self.g, self.b)


def color_from_hex(hex_string: str) -> Color:
    hex_string = hex_string.lstrip("#")
    print(hex_string)
    values = tuple(int(hex_string[i:i + 2], 16) for i in (2, 4, 6))
    return Color(values[0], values[1], values[2])


class Player:
    def __init__(self, websocket):
        self.color = None
        self.direction = 0
        self.jump = False
        self.websocket = websocket

        self.pos = (0, 0)

    def set_color(self, color: Color):
        self.color = color

    def set_direction(self, direction: str):
        if direction == "left":
            self.direction = 1
        if direction == "right":
            self.direction = -1
        if direction == "stop":
            self.direction = 0

    def jump_now(self):
        if self.pos[1] == 0:
            self.jump = 3

    def __str__(self):
        return "player: color-{} direction-{}".format(self.color, self.direction)


players: [Player] = []


async def echo(websocket):
    try:
        client_id = uuid.uuid4()
        print("user connected - {}".format(client_id))

        player = Player(websocket)
        players.append(player)

        print(len(players))

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
    except Exception as ignore:
        print("")
    finally:
        players.remove(player)


class BackgroundRunner:
    def __init__(self):
        self.value = 0

    async def draw(self):
        sense.clear((0, 0, 0))
        for player in players:
            if player.color is not None and player.pos[1] <= 7:
                sense.set_pixel(player.pos[0], player.pos[1], (player.color.r, player.color.g, player.color.b))

    async def update(self):
        for player in players:

            if player.pos[1] != 0:
                player.pos = (player.pos[0] + player.direction, max(player.pos[1] - 1, 0))
            else:
                is_free = True

                for playerB in players:
                    if playerB.pos[1] == 0 and playerB.pos[0] == player.pos[0] + player.direction:
                        is_free = False

                if is_free:
                    player.pos = (player.pos[0] + player.direction, max(player.pos[1] - 1, 0))

            player.pos = (max(min(player.pos[0], screenWidth - 1), 0), player.pos[1] % screenWidth)

            if player.jump == 1:
                player.pos = (player.pos[0], player.pos[1] + 2)
                player.jump = 0
            if player.jump == 2:
                player.pos = (player.pos[0], player.pos[1] + 2)
                player.jump = 1
            if player.jump == 3:
                player.pos = (player.pos[0], player.pos[1] + 2)
                player.jump = 2

        for playerB in players:
            for playerA in players:
                if playerA.pos[0] == playerB.pos[0] and playerA.pos[1] + 1 == playerB.pos[1]:
                    await playerB.websocket.send("kill:")
                    await playerA.websocket.send("dead:")

                    playerA.pos = (int(screenWidth / 2), screenWidth - 1)

    async def draw_continuously(self):
        while True:
            await self.update()
            await self.draw()
            await asyncio.sleep(1 / 5)


runner = BackgroundRunner()


async def main():
    asyncio.create_task(runner.draw_continuously())
    async with serve(echo, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
