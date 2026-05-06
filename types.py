from typing import List
from typing import Any
from dataclasses import dataclass
import json


@dataclass
class State:
    limit: int
    highlighted_limit: int
    cards: List[Card]
    count: int

    @staticmethod
    def from_dict(obj: Any) -> 'State':
        _limit = int(obj.get("limit"))
        _highlighted_limit = int(obj.get("highlighted_limit"))
        _cards = [Card.from_dict(y) for y in obj.get("cards")]
        _count = int(obj.get("count"))
        return State(_limit, _highlighted_limit, _cards, _count)

@dataclass
class Card:
    label: str
    state: List[object]
    id: int
    set: str
    modifier: List[object]
    cost: Cost
    value: Value
    key: str

    @staticmethod
    def from_dict(obj: Any) -> 'Card':
        _label = str(obj.get("label"))
        #_state = [.from_dict(y) for y in obj.get("state")]
        _id = int(obj.get("id"))
        _set = str(obj.get("set"))
        #_modifier = [.from_dict(y) for y in obj.get("modifier")]
        _cost = Cost.from_dict(obj.get("cost"))
        _value = Value.from_dict(obj.get("value"))
        _key = str(obj.get("key"))
        #return Card(_label, _state, _id, _set, _modifier, _cost, _value, _key)
        return Card(_label, _id, _set, _cost, _value, _key)

@dataclass
class Cost:
    sell: int
    buy: int

    @staticmethod
    def from_dict(obj: Any) -> 'Cost':
        _sell = int(obj.get("sell"))
        _buy = int(obj.get("buy"))
        return Cost(_sell, _buy)


@dataclass
class Value:
    suit: str
    effect: str
    rank: str

    @staticmethod
    def from_dict(obj: Any) -> 'Value':
        _suit = str(obj.get("suit"))
        _effect = str(obj.get("effect"))
        _rank = str(obj.get("rank"))
        return Value(_suit, _effect, _rank)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
