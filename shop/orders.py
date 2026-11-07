from shop.payments import charge

orders = []


def save_order(cart, total, card):
    order = {"items": [item.name for item in cart], "total": total}
    orders.append(order)
    charge(card, total)
    return order
