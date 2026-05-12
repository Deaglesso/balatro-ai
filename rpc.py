import traceback

import requests
import time


class RPCClient:

    def __init__(self, url: str):
        self.url = url

    def call(self, method: str, params: dict = {}):
            try:
                print(self.url, method, params)
                response = requests.post(
                    self.url,
                    json={
                        "jsonrpc": "2.0",
                        "method": method,
                        "params": params,
                        "id": 1,
                    }
                )

                data = response.json()

                if "error" in data:
                    raise RuntimeError(data["error"]["message"])

                return data["result"]
            except requests.exceptions.ConnectionError:
                print(traceback.format_exc())
                return self.call("gamestate")