"""Pretend payment provider. Example only: it records charges instead of sending them."""

charges = []


def charge(card, amount):
    charges.append((card, amount))
    print(f"Charged ${amount:.2f} to card ending {card[-4:]}")
