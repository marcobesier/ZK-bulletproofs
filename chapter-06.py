from py_ecc.bn128 import G1, multiply, add, FQ, eq, Z1
from py_ecc.bn128 import curve_order as p
import random
from functools import reduce

def random_element():
    return random.randint(0, p)

def modinv(a, p):
    # Compute the modular inverse using Fermat's Little Theorem
    return pow(a, p - 2, p)

def add_points(*points):
    # Add multiple elliptic curve points together
    return reduce(add, points, Z1)

# Vector commitment function
def vector_commit(points, scalars):
    return reduce(add, [multiply(P, int(s % p)) for P, s in zip(points, scalars)], Z1)

# EC points with unknown discrete logs
G_vec = [
    (FQ(6286155310766333871795042970372566906087502116590250812133967451320632869759),
     FQ(2167390362195738854837661032213065766665495464946848931705307210578191331138)),
    (FQ(6981010364086016896956769942642952706715308592529989685498391604818592148727),
     FQ(8391728260743032188974275148610213338920590040698592463908691408719331517047)),
    (FQ(15884001095869889564203381122824453959747209506336645297496580404216889561240),
     FQ(14397810633193722880623034635043699457129665948506123809325193598213289127838)),
    (FQ(6756792584920245352684519836070422133746350830019496743562729072905353421352),
     FQ(3439606165356845334365677247963536173939840949797525638557303009070611741415))
]

# Fold scalar vector
def fold(scalar_vec, u, u_inv):
    n = len(scalar_vec)
    assert n % 2 == 0, "Length of scalar_vec must be even"
    folded = []
    for i in range(n // 2):
        idx1 = 2 * i
        idx2 = 2 * i + 1
        term = (scalar_vec[idx1] * u + scalar_vec[idx2] * u_inv) % p
        folded.append(term)
    return folded

# Fold point vector
def fold_points(point_vec, u_inv, u):
    n = len(point_vec)
    assert n % 2 == 0, "Length of point_vec must be even"
    folded = []
    for i in range(n // 2):
        idx1 = 2 * i
        idx2 = 2 * i + 1
        # Multiply G_vec[idx1] by u_inv and G_vec[idx2] by u
        P1 = multiply(point_vec[idx1], u_inv % p)
        P2 = multiply(point_vec[idx2], u % p)
        folded_point = add(P1, P2)
        folded.append(folded_point)
    return folded

# Compute L and R
def compute_secondary_diagonal(G_vec, a):
    n = len(a)
    assert n == len(G_vec), "Vectors a and G_vec must be the same length"
    assert n % 2 == 0, "Length of vectors must be even"
    L = Z1  # Initialize to point at infinity (neutral element of addtion, i.e., "zero")
    R = Z1
    for i in range(n // 2):
        idx1 = 2 * i
        idx2 = 2 * i + 1
        # L components: a[idx1] * G_vec[idx2]
        L = add(L, multiply(G_vec[idx2], a[idx1] % p))
        # R components: a[idx2] * G_vec[idx1]
        R = add(R, multiply(G_vec[idx1], a[idx2] % p))
    return (L, R)

# Secret vector a
a = [9, 45, 23, 42]  # Ensure len(a) is even and len(a) == len(G_vec)

# Prover commits
A = vector_commit(G_vec, a)
L, R = compute_secondary_diagonal(G_vec, a)

# Verifier computes randomness
u = random_element()
u_inv = modinv(u, p)
u2 = pow(u, 2, p)
u_inv2 = pow(u_inv, 2, p)

# Prover computes folded scalar vector
aprime = fold(a, u, u_inv)

# Verifier computes folded point vector
Gprime = fold_points(G_vec, u_inv, u)  # Note the order of u_inv and u

# Verification check
left_side = add_points(multiply(L, u2 % p), A, multiply(R, u_inv2 % p))
right_side = vector_commit(Gprime, aprime)

assert eq(left_side, right_side), "Invalid proof"
assert len(Gprime) == len(a) // 2 and len(aprime) == len(a) // 2, "Proof must be size n/2"

print("Proof accepted: opening verified with proof size n/2.")
