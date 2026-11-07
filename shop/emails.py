def receipt(order):
    lines = [f"- {name}" for name in order["items"]]
    return "Thanks for your order!\n" + "\n".join(lines) + f"\nTotal: ${order['total']:.2f}"
