import random
import uuid

points = 50
output_file = f"testcases/{uuid.uuid4()}.txt"
coordinates = [(random.randint(0, 600), random.randint(0, 500)) for _ in range(points)]

with open(output_file, 'w') as file:
    for x, y in coordinates:
        file.write(f"{x} {y}\n")

print(f"Koordinat random telah disimpan di '{output_file}'")