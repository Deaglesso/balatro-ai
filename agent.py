from balatro_server import BalatroServer
from rpc import RPCClient


class Agent:

    def __init__(self, agent_id: int, port: int):

        self.agent_id = agent_id
        self.port = port

        self.server = BalatroServer(port)

    def run(self):

        self.server.start()

        try:

            rpc = RPCClient(self.server.url)

            rpc.call("menu")

            state = rpc.call("start", {
                "deck": "CHECKERED",
                "stake": "WHITE",
            })

            while state["state"] != "GAME_OVER":
                match state["state"]:

                    case "BLIND_SELECT":
                        state = rpc.call("select")

                    case "SELECTING_HAND":
                        cards = list(range(min(5, len(state["hand"]["cards"]))))
                        state = rpc.call("play", {"cards": cards})

                    case "ROUND_EVAL":
                        state = rpc.call("cash_out")

                    case "SHOP":
                        state = rpc.call("next_round")

                    case _:
                        state = rpc.call("gamestate")

            return state["won"]

        finally:
            self.server.stop()