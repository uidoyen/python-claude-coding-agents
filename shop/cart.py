from dataclasses import dataclass


@dataclass
class Item:
    name: str
    price: float
    qty: int = 1


def cart_total(cart):
    return sum(item.price * item.qty for item in cart)
