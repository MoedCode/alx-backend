#!/usr/bin/python3
# from base_caching import BaseCaching # => 0
# import base_caching # => 1
from base_caching import *  # => 2


class PlateStack:
    def __init__(self, capacity=4):
        self.stack = []
        self.capacity = capacity

    def add_plate(self, plate):
        if len(self.stack) >= self.capacity:
            # If the stack is full, remove the first plate (FIFO)
            removed_plate = self.stack.pop(0)
            print(f"Plate removed: {removed_plate}")
        self.stack.append(plate)
        print(f"Plate added: {plate} stack now {self.stack}")

    def print_stack(self):
        print("Current stack:")
        print(self.stack)


# Create a PlateStack instance
plate_stack = PlateStack()

# Add plates to the stack
plate_stack.add_plate("Plate 1")
plate_stack.add_plate("Plate 2")
plate_stack.add_plate("Plate 3")
plate_stack.add_plate("Plate 4")
plate_stack.print_stack()

# Try to add another plate
plate_stack.add_plate("Plate 5")
plate_stack.print_stack()
