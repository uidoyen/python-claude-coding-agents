"""Run one checkout: python -m shop.demo"""
from shop.cart import Item
from shop.checkout import checkout

checkout([Item("Coffee beans", 18.00), Item("Mug", 12.00, 2)], "4242424242424242")
