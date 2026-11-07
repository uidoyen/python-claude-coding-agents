from shop.cart import cart_total
from shop.orders import save_order
from shop.payments import charge


def checkout(cart, card):
    total = cart_total(cart)
    charge(card, total)
    return save_order(cart, total, card)
