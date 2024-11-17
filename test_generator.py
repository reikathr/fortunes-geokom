# Change for points needed
import random


points = 50

coordinates = [(random.randint(0, 500), random.randint(0, 500)) for i in range(points)]

# Format and print the coordinates
formatted_coordinates = "\n".join(f"{x} {y}" for x, y in coordinates)
print(formatted_coordinates)
