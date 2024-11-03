from py_ecc.bn128 import G1, multiply, add, FQ, eq, Z1
from py_ecc.bn128 import curve_order as p
import numpy as np
from functools import reduce
import random

def random_element():
    return random.randint(0, p)

def add_points(*points):
    # Add multiple elliptic curve points together
    return reduce(add, points, Z1)

# If points = G1, G2, G3, G4 and scalars = a,b,c,d vector_commit returns
# aG1 + bG2 + cG3 + dG4
def vector_commit(points, scalars):
    return reduce(add, [multiply(P, i) for P, i in zip(points, scalars)], Z1)

# Custom inner product function using arbitrary-precision integers
def inner_product(a, b):
    return sum((ai * bi) % p for ai, bi in zip(a, b)) % p

# These EC points have unknown discrete logs:
G = [(FQ(6286155310766333871795042970372566906087502116590250812133967451320632869759), FQ(2167390362195738854837661032213065766665495464946848931705307210578191331138)),
     (FQ(6981010364086016896956769942642952706715308592529989685498391604818592148727), FQ(8391728260743032188974275148610213338920590040698592463908691408719331517047)),
     (FQ(15884001095869889564203381122824453959747209506336645297496580404216889561240), FQ(14397810633193722880623034635043699457129665948506123809325193598213289127838)),
     (FQ(6756792584920245352684519836070422133746350830019496743562729072905353421352), FQ(3439606165356845334365677247963536173939840949797525638557303009070611741415))]

H = [(FQ(13728162449721098615672844430261112538072166300311022796820929618959450231493), FQ(12153831869428634344429877091952509453770659237731690203490954547715195222919)),
    (FQ(17471368056527239558513938898018115153923978020864896155502359766132274520000), FQ(4119036649831316606545646423655922855925839689145200049841234351186746829602)),
    (FQ(8730867317615040501447514540731627986093652356953339319572790273814347116534), FQ(14893717982647482203420298569283769907955720318948910457352917488298566832491)),
    (FQ(419294495583131907906527833396935901898733653748716080944177732964425683442), FQ(14467906227467164575975695599962977164932514254303603096093942297417329342836))]

B = (FQ(12848606535045587128788889317230751518392478691112375569775390095112330602489), FQ(18818936887558347291494629972517132071247847502517774285883500818572856935411))

# scalar multiplication example: multiply(G, 42)
# EC addition example: add(multiply(G, 42), multiply(G, 100))

# Remember to do all arithmetic modulo p
def commit(a, sL, b, sR, alpha, beta, gamma, tau_1, tau_2):
    # A = <a, G> + <b, H> + alpha * B
    A = add_points(vector_commit(G, a), vector_commit(H, b), multiply(B, alpha % p))

    # S = <sL, G> + <sR, H> + beta * B
    S = add_points(vector_commit(G, sL), vector_commit(H, sR), multiply(B, beta % p))

    # V = v * G + gamma * B, where v = <a, b>
    v = inner_product(a, b) % p
    # Use G[0] as "G"
    V = add(multiply(G[0], v % p), multiply(B, gamma % p))

    # T1 = (<a, sR> + <b, sL>) * G + tau_1 * B
    T1_coeff = (inner_product(a, sR) + inner_product(b, sL)) % p
    T1 = add(multiply(G[0], T1_coeff), multiply(B, tau_1 % p))

    # T2 = <sL, sR> * G + tau_2 * B
    T2_coeff = inner_product(sL, sR) % p
    T2 = add(multiply(G[0], T2_coeff), multiply(B, tau_2 %p))

    return (A, S, V, T1, T2)


def evaluate(f_0, f_1, f_2, u):
    return (f_0 + f_1 * u + f_2 * pow(u, 2, p)) % p

def prove(blinding_0, blinding_1, blinding_2, u):
    # Compute proof: pi = blinding_0 + blinding_1 * u + blinding_2 * u^2 modulo p
    return (blinding_0 + blinding_1 * u + blinding_2 * pow(u, 2, p)) % p

## step 0: Prover and verifier agree on G, H, and B

## step 1: Prover creates the commitments
# Secret vector a
a = np.array([89,15,90,22], dtype=object) % p
# Secret vector b
b = np.array([16,18,54,12], dtype=object) % p

# Random vectors sL and sR
sL = np.array([random_element() for _ in range(4)], dtype=object)
sR = np.array([random_element() for _ in range(4)], dtype=object)

# Compute t1 and t2 coefficients
t1 = (inner_product(a, sR) + inner_product(b, sL)) % p
t2 = inner_product(sL, sR) % p

### Blinding terms
alpha = random_element()
beta = random_element()
gamma = random_element()
tau_1 = random_element()
tau_2 = random_element()

A, S, V, T1, T2 = commit(a, sL, b, sR, alpha, beta, gamma, tau_1, tau_2)

## step 2: Verifier picks u
u = random_element()

## step 3: Prover evaluates l(u), r(u), t(u) and creates evaluation proofs
# l(u) = a + sL * u
l_u = evaluate(a, sL, 0, u)
# r(u) = b + sR * u
r_u = evaluate(b, sR, 0, u)
# t(u) = v + t1 * u + t2 * u^2
t_u = evaluate(inner_product(a,b), t1, t2, u)

pi_lr = prove(alpha, beta, 0, u)
pi_t = prove(gamma, tau_1, tau_2, u)

## step 4: Verifier accepts or rejects

# First, check that t_u == <l_u, r_u> mod p
assert t_u == inner_product(np.array(l_u), np.array(r_u)), "tu !=〈lu, ru〉"

# Second, check A + S * u == <l_u, G> + <r_u, H> + pi_lr * B
left_side = add(A, multiply(S, u % p))
right_side = add_points(
    vector_commit(G, l_u),
    vector_commit(H, r_u),
    multiply(B, pi_lr % p)
)
assert eq(left_side, right_side), "l_u or r_u not evaluated correctly"

# Third, check t_u * G + pi_t * B == V + T1 * u + T2 * u^2
left_side_t = add(
    # Use G[0] as "G"
    multiply(G[0], t_u % p),
    multiply(B, pi_t % p)
)
right_side_t = add_points(
    V,
    multiply(T1, u % p),
    multiply(T2, pow(u, 2, p))
)
assert eq(left_side_t, right_side_t), "t_u not evaluated correctly"

print("Proof accepted. Inner product verified.")
