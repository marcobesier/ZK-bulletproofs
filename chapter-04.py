from py_ecc.bn128 import G1, multiply, add, FQ, eq
from py_ecc.bn128 import curve_order as p
import random

def random_element():
    return random.randint(0, p)

# These EC points have unknown discrete logs:
G = (FQ(6286155310766333871795042970372566906087502116590250812133967451320632869759), FQ(2167390362195738854837661032213065766665495464946848931705307210578191331138))

H = (FQ(13728162449721098615672844430261112538072166300311022796820929618959450231493), FQ(12153831869428634344429877091952509453770659237731690203490954547715195222919))

B = (FQ(12848606535045587128788889317230751518392478691112375569775390095112330602489), FQ(18818936887558347291494629972517132071247847502517774285883500818572856935411))

# Utility function to add three elliptic curve points
def addd(A, B, C):
    return add(A, add(B, C))

# Scalar multiplication example: multiply(G, 42)
# EC addition example: add(multiply(G, 42), multiply(G, 100))

# Remember to do all arithmetic modulo p
def commit(a, sL, b, sR, alpha, beta, gamma, tau_1, tau_2):
    # Commitment to a and b: A = aG + bH + alpha B
    A = add(add(multiply(G, a % p), multiply(H, b % p)), multiply(B, alpha % p))

    # Commitment to the linear terms: S = sL G + sR H + beta B
    S = add(add(multiply(G, sL % p), multiply(H, sR % p)), multiply(B, beta % p))

    # Commitment to the product v: V = a * b * G + gamma B
    V = add(multiply(G, (a * b) % p), multiply(B, gamma % p))

    # Linear coefficient of t(x): T1 = (a sR + b sL) G + tau_1 B
    T1 = add(multiply(G, (a * sR + b * sL) % p), multiply(B, tau_1 % p))

    # Quadratic coefficient of t(x): T2 = sL * sR * G + tau_2 B
    T2 = add(multiply(G, (sL * sR) % p), multiply(B, tau_2 % p))

    return (A, S, V, T1, T2)


def evaluate(f_0, f_1, f_2, u):
    return (f_0 + f_1 * u + f_2 * pow(u, 2 ,p)) % p

def prove(blinding_0, blinding_1, blinding_2, u):
    # Compute the proof: pi = blinding_0 + blinding_1 * u + blinding_2 * u^2
    return (blinding_0 + blinding_1 * u + blinding_2 * pow(u, 2, p)) % p

## step 0: Prover and verifier agree on G and B
# G, H, and B are defined above

## step 1: Prover creates the commitments
# Randomly select scalars a and b
a = random_element()
b = random_element()

# Randomly select linear coefficients sL and sR
sL = random_element()
sR = random_element()

# Compute coefficients for t(x)
# Linear coefficient
t1 = (a * sR + b * sL) % p
# Quadratic coefficient
t2 = (sL * sR) % p

### Blinding terms
alpha = random_element()
beta = random_element()
gamma = random_element()
tau_1 = random_element()
tau_2 = random_element()

# Prover commits to the values
A, S, V, T1, T2 = commit(a, sL, b, sR, alpha, beta, gamma, tau_1, tau_2)

## step 2: Verifier picks u
u = random_element()

## step 3: Prover evaluates l(u), r(u), t(u) and creates evaluation proofs
# l(u) = a + sL * u
l_u = evaluate(a, sL, 0, u)
# r(u) = b + sR * u
r_u = evaluate(b, sR, 0, u)
# t(u) = ab + t1 * u + t2 * u^2
t_u = evaluate(a*b, t1, t2, u)

# Prover computes the proofs
pi_lr = prove(alpha, beta, 0, u)
pi_t = prove(gamma, tau_1, tau_2, u)

## step 4: Verifier accepts or rejects
# Check that t_u = l_u * r_u modulo p
assert t_u == (l_u * r_u) % p, "tu != lu*ru"
assert eq(add(A, multiply(S, u)), addd(multiply(G, l_u), multiply(H, r_u), multiply(B, pi_lr))), "l_u or r_u not evaluated correctly"
assert eq(add(multiply(G, t_u), multiply(B, pi_t)), addd(V, multiply(T1, u), multiply(T2, u**2 % p))), "t_u not evaluated correctly"
