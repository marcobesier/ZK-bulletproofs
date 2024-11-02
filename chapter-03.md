# Exercise 1

Write out the steps for how a prover would convince a verifier they correctly evaluated a degree 1 polynomial, without revealing the polynomial to the verifier.

### Answer

The prover wants to prove they have a degree 1 polynomial $p(x) = c_0 + c_1 x$ and that they correctly evaluated it at a point $u$, resulting in $y=p(u)$, without revealing the coefficients $c_0$ and $c_1$.

#### Step 1: Setup Phase

Both the prover and verifier agree on the elliptic curve group and two points $G$ and $B$ with unknown discrete logarithm relationships.

#### Step 2: Commitment Phase

The prover selects random blinding factors $\gamma_0$ and $\gamma_1$.
Subsequently, the prover computes the Pedersen commitments for the two coefficients $c_0$ and $c_1$:

$$
\begin{align*}
C_0 &= c_0G + \gamma_0B \\
C_1 &= c_1G + \gamma_1B
\end{align*}
$$

Lastly, the prover sends $(C_0, C_1)$ to the verifier.
By committing to $c_0$ and $c_1$ using Pedersen commitments, the prover "locks in" the coefficients without revealing them.

#### Step 3: Challenge Phase

The verifier selects a random finite field element $u$ and sends it to the prover.
Randomly selecting $u$ prevents the prover from precomputing responses and, therefore, ensures the integrity of the proof.

#### Step 4: Proving Phase

First, the prover computes $y=p(u)=c_0+c_1u$ modulo the field order $p$.
Subsequently, the prover computes the blinding sum $\pi=\gamma_0+\gamma_1 u$ modulo $p$.
Lastly, the prover sends $(y,\pi)$ to the verifier, where $y$ is the claimed evaluation of the polynomial at $u$ and $\pi$ serves as a proof that links the commitments to the evaluation without revealing the coefficients.

#### Step 5: Verification Phase

The verifier now computes the left-hand side (LHS) of the verification equation

$$
LHS = C_0 + C_1u
$$

and the right-hand side (RHS) of the verification equation:

$$
RHS = yG + \pi B
$$

The verifier then checks whether $LHS = RHS$ holds.
If it does, it implies that the commitments $C_0$ and $C_1$ correspond to coefficients $c_0$ and $c_1$ such that $y=c_0+c_1 u$.
The blinding factors $\gamma_0$ and $\gamma_1$ are appropriately accounted for in $\pi$, ensuring the commitments align with the evaluation.