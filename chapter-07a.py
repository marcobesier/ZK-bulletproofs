# Import necessary modules and functions from the py_ecc library
from py_ecc.bn128 import G1, multiply, add, FQ, eq, Z1
from py_ecc.bn128 import curve_order as p
import numpy as np
from functools import reduce
import random

def random_element():
    return random.randint(0, p)

def add_points(*points):
    # Sum multiple elliptic curve points together
    return reduce(add, points, Z1)

def vector_commit(points, scalars):
    """
    Compute a vector commitment.

    Given lists of points and scalars, compute the commitment:
    commitment = sum_i (scalars_i * points_i)

    Parameters:
    - points: list of elliptic curve points (G1 elements)
    - scalars: list of scalars (integers modulo p)

    Returns:
    - commitment: an elliptic curve point representing the commitment
    """
    return reduce(add, [multiply(P, i) for P, i in zip(points, scalars)], Z1)

# These elliptic curve points have unknown discrete logarithms:
G_vec = [
    (
        FQ(6286155310766333871795042970372566906087502116590250812133967451320632869759),
        FQ(2167390362195738854837661032213065766665495464946848931705307210578191331138)
    ),
    (
        FQ(6981010364086016896956769942642952706715308592529989685498391604818592148727),
        FQ(8391728260743032188974275148610213338920590040698592463908691408719331517047)
    ),
    (
        FQ(15884001095869889564203381122824453959747209506336645297496580404216889561240),
        FQ(14397810633193722880623034635043699457129665948506123809325193598213289127838)
    ),
    (
        FQ(6756792584920245352684519836070422133746350830019496743562729072905353421352),
        FQ(3439606165356845334365677247963536173939840949797525638557303009070611741415)
    )
]

def fold(scalar_vec, u):
    """
    Fold a scalar vector using a challenge scalar u.

    Parameters:
    - scalar_vec: list of scalars (integers modulo p)
    - u: challenge scalar

    Returns:
    - folded_vec: folded list of scalars
    """
    n = len(scalar_vec)
    assert n % 2 == 0, "Length of scalar_vec must be even to fold"  # If not, pad with zeros
    folded_vec = []
    u_inv = pow(u, -1, p)  # Compute modular inverse of u modulo p
    for i in range(0, n, 2):
        # Fold the scalars using the formula:
        # folded_element = scalar_vec[i] * u + scalar_vec[i+1] * u_inv (mod p)
        folded_ele = scalar_vec[i] * u + scalar_vec[i + 1] * u_inv
        folded_vec.append(folded_ele % p)
    return folded_vec

def fold_points(point_vec, u):
    """
    Fold a point vector using a challenge scalar u.

    Parameters:
    - point_vec: list of elliptic curve points
    - u: challenge scalar

    Returns:
    - folded_vec: folded list of points
    """
    n = len(point_vec)
    assert n % 2 == 0, "Length of point_vec must be even to fold"  # If not, pad with identity points
    folded_vec = []
    u_inv = pow(u, -1, p)  # Compute modular inverse of u modulo p
    for i in range(0, n, 2):
        # Fold the points using the formula:
        # folded_point = point_vec[i] * u + point_vec[i+1] * u_inv
        P1 = multiply(point_vec[i], u)
        P2 = multiply(point_vec[i + 1], u_inv)
        folded_ele = add(P1, P2)
        folded_vec.append(folded_ele)
    return folded_vec

def compute_secondary_diagonal(G_vec, a):
    """
    Compute the L and R commitments for the recursive proof.

    Parameters:
    - G_vec: list of elliptic curve points
    - a: list of scalars

    Returns:
    - (L, R): tuple of elliptic curve points representing the commitments
    """
    assert len(G_vec) == len(a), "Unequal length of G_vec and a"
    n = len(a)
    if n == 4:
        # For n = 4, compute L and R as per the specified indices
        # L = a1 * G2 + a3 * G4
        # R = a2 * G1 + a4 * G3
        L = add(
            multiply(G_vec[1], a[0]),
            multiply(G_vec[3], a[2])
        )
        R = add(
            multiply(G_vec[0], a[1]),
            multiply(G_vec[2], a[3])
        )
    else:
        # For n = 2, compute L and R accordingly
        # L = a1 * G2
        # R = a2 * G1
        L = multiply(G_vec[1], a[0])
        R = multiply(G_vec[0], a[1])
    return (L, R)

# Secret scalar vector a
a = [4, 2, 42, 420]  # Example scalars

# Compute the initial commitment P = sum_i (a_i * G_i)
P = vector_commit(G_vec, a)

# First folding step
L1, R1 = compute_secondary_diagonal(G_vec, a)
u1 = random_element()  # Prover receives a challenge u1 from the verifier
aprime = fold(a, u1)
Gprime = fold_points(G_vec, pow(u1, -1, p))

# Second folding step
L2, R2 = compute_secondary_diagonal(Gprime, aprime)
u2 = random_element()  # Prover receives a challenge u2 from the verifier
aprimeprime = fold(aprime, u2)
Gprimeprime = fold_points(Gprime, pow(u2, -1, p))

# Ensure that the vectors have been folded down to length 1
assert len(Gprimeprime) == 1 and len(aprimeprime) == 1, "Final vector must be of length 1"

# Verify the proof
# Reconstruct the commitment using the folded scalars and points, and the L and R commitments
# The verification equation is:
# vector_commit(G'', a'') == L2 * u2^2 + L1 * u1^2 + P + R1 * u1^-2 + R2 * u2^-2
left_side = vector_commit(Gprimeprime, aprimeprime)
right_side = add_points(
    multiply(L2, pow(u2, 2, p)),
    multiply(L1, pow(u1, 2, p)),
    P,
    multiply(R1, pow(u1, -2, p)),
    multiply(R2, pow(u2, -2, p))
)
assert eq(left_side, right_side), "Invalid proof"

print("Proof accepted. Opening verified with proof size log n.")
