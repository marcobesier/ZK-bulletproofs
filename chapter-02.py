from py_ecc.bn128 import is_on_curve, FQ
from py_ecc.fields import field_properties
from hashlib import sha256
from libnum import has_sqrtmod_prime_power, sqrtmod_prime_power


# Field modulus for the bn128 curve, i.e., the prime order of the field
field_mod = field_properties["bn128"]["field_modulus"]

# Curve parameter 'b' in the equation y^2 = x^3 + b
b = 3 # For bn128, the curve equation is y^2 = x^3 + 3

# Seed for initial x value. (Can be any arbitrary string.)
seed = "RareSkills"

# Convert the seed into an integer x within the field using SHA-256 hash
x = int(sha256(seed.encode('ascii')).hexdigest(), 16) % field_mod 

# List to store the generated elliptic curve points ("vector basis")
vector_basis = []

# Number of points to generate
n = 10

# Loop to generate n points with unknown discrete logarithms
for _ in range(n):
    # Initialize entropy for randomness in y-coordinate selection
    entropy = 0
    # Flag to indicate when a valid point is found
    found_point = False

    # Inner loop to find a valid point on the elliptic curve
    while not found_point:
        # Candidate x-coordinate (adjusted with entropy to avoid duplicates)
        x_candidate = (x + entropy) % field_mod

        # Compute the right-hand side of the curve equation y^2 = x^3 + b
        rhs = (x_candidate ** 3 + b) % field_mod

        # Check if there exists a square root of rhs modulo field_mod
        if has_sqrtmod_prime_power(rhs, field_mod, 1):
            # Get the two possible y-values (since sqrt has two solutions)
            y_values = list(sqrtmod_prime_power(rhs, field_mod, 1))

            # Choose one y-value based on the current entropy (for randomness)
            y_candidate = y_values[entropy % 2]

            # Form the point with the candidate x and y coordinates
            point = (FQ(x_candidate), FQ(y_candidate))

            # Verify that the point actually lies on the curve
            if is_on_curve(point, b):
                # Add the valid point to the vector basis
                vector_basis.append(point)
                # Exit the inner loop since point is found
                found_point = True

        # Increment entropy to change y-coordinate selection in case of failure
        entropy += 1

    # Update x for the next iteration to ensure new points are generated
    # Hash the current x to get a new starting point for the next loop
    x = int(sha256(str(x).encode('ascii')).hexdigest(), 16) % field_mod

# vector_basis now contains n elliptic curve points with unknown discrete logs.
# These point can be used in Pedersen commitments.
print("Generated elliptic curve points (vector basis):")
for idx, point in enumerate(vector_basis):
    # point[0] is FQ(x_candidate), point[1] is FQ(y_candidate)
    # Use .n to get the integer values of x and y
    print(f"Point {idx + 1}: x = {point[0].n}, y = {point[1].n}")
