from py_ecc.bn128 import G1, multiply, add, FQ
from py_ecc.bn128 import curve_order as p
import random

def random_field_element():
    return random.randint(0, p)

# These EC points have unknown discrete logs:
G = (FQ(6286155310766333871795042970372566906087502116590250812133967451320632869759), FQ(2167390362195738854837661032213065766665495464946848931705307210578191331138))

B = (FQ(12848606535045587128788889317230751518392478691112375569775390095112330602489), FQ(18818936887558347291494629972517132071247847502517774285883500818572856935411))

# Scalar multiplication example: multiply(G, 42)
# EC addition example: add(multiply(G, 42), multiply(G, 100))

# Remember to do all arithmetic modulo p

def commit(f_0, f_1, f_2, gamma_0, gamma_1, gamma_2, G, B):
    # Commit to each coefficient using Pedersen commitments
    C0 = add(multiply(G, f_0 % p), multiply(B, gamma_0 % p))
    C1 = add(multiply(G, f_1 % p), multiply(B, gamma_1 % p))
    C2 = add(multiply(G, f_2 % p), multiply(B, gamma_2 % p))
    return (C0, C1, C2)

def evaluate(f_0, f_1, f_2, u):
    # Since u can be large, compute u**2 modulo p directly to prevent overflow
    return (f_0 + f_1 * u + f_2 * pow(u, 2, p)) % p

def prove(gamma_0, gamma_1, gamma_2, u):
    # Compute the proof pi
    return (gamma_0 + gamma_1 * u + gamma_2 * pow(u, 2, p)) % p

def verify(C0, C1, C2, G, B, f_u, pi):
    # Compute left-hand side of the verification equation: C0 + C1 * u + C2 * u**2
    LHS = add(C0, add(multiply(C1, u % p), multiply(C2, pow(u, 2, p))))

    # Compute right-hand side of the verification equation: f_u * G + pi * B
    RHS = add(multiply(G, f_u % p), multiply(B, pi % p))

    # Check if LHS equals RHS
    return LHS == RHS

## step 0: Prover and verifier agree on G and B
# G and B are already defined above

## step 1: Prover creates the commitments
### f(x) = f_0 + f_1x + f_2x^2
# Randomly select coefficients f_0, f_1, f_2 from the field
f_0 = random_field_element()
f_1 = random_field_element()
f_2 = random_field_element()

### blinding terms
# Randomly select blinding terms gamma_0, gamma_1, gamma_2 from the field
gamma_0 = random_field_element()
gamma_1 = random_field_element()
gamma_2 = random_field_element()

# Prover commits to the coefficients
C0, C1, C2 = commit(f_0, f_1, f_2, gamma_0, gamma_1, gamma_2, G, B)

## step 2: Verifier picks random u
u = random_field_element()

## step 3: Prover evaluates f(u) and pi
f_u = evaluate(f_0, f_1, f_2, u)
pi = prove(gamma_0, gamma_1, gamma_2, u)

## step 4: Verifier accepts or rejects
if verify(C0, C1, C2, G, B, f_u, pi):
    print("accept")
else:
    print("reject")
