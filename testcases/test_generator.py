import random
import uuid

points = 100
output_file = f"testcases/{points}.txt"
coordinates = [(random.randint(0, 600), random.randint(0, 500)) for _ in range(points)]

with open(output_file, 'w') as file:
    for x, y in coordinates:
        file.write(f"{x} {y}\n")

print(f"Koordinat random telah disimpan di '{output_file}'")