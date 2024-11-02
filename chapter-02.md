# Exercise 1

If we used the same $G₁…Gₙ$ for both vectors before adding them, how could a committer open two different vectors for $C_3$? Give an example. How does using a different set of points $H₁…Hₙ$ prevent this?

### Answer

Suppose we have two commitments of the following form:

$$
\begin{align*}
C_1 &= v_1 G_1 + v_2 G_2 + \ldots + v_n G_n + r B \\
C_2 &= w_1 G_1 + w_2 G_2 + \ldots + w_n G_n + s B 
\end{align*}
$$

Then, the sum of those two commitments would be:

$$
C_3 = C_1 + C_2 = \sum_{i=1}^n(v_i+w_i)G_i+(r+s)B
$$

Because the same $G_i$ are used, the committer can redistribute the sums $v_i+w_i$ between $v_i$ and $w_i$ in any way that maintains the total.
This allows the committer to produce alternative openings for $C_1$ and $C_2$ that still sum to the same $C_3$.

#### Example

Let $n=2$, $v=[1,2]$, and $w=[3,4]$.
Then, we have:

$$
\begin{align*}
C_1 &= 1 G_1 + 2 G_2 + r B \\
C_2 &= 3 G_1 + 4 G_2 + s B 
\end{align*}
$$

The combined commitment is, therefore:

$$
\begin{align*}
C_3 &= C_1 + C_2 \\
    &= (1+3) G_1 + (2+4) G_2 + (r+s) B \\ 
    &= 4 G_1 + 6 G_2 + (r+s) B
\end{align*}
$$

Now, the committer could choose different vectors that still sum to the same combined vector.

For example, let $v^\prime=[2,5]$ and $w^\prime=[2,1]$.
Note that $v_i^\prime + w_i^\prime = v_i+w_i$ for each $i$:

$$
\begin{align*}
v_1^\prime + w_1^\prime &= 2 + 2 = 4 = v_1 + w_1 \\
v_2^\prime + w_2^\prime &= 5 + 1 = 6 = v_2 + w_2 
\end{align*}
$$

The new commitments are:

$$
\begin{align*}
C_1^\prime &= 2G_1 + 5G_2 + r^\prime B \\
C_2^\prime &= 2G_1 + 1G_2 + s^\prime B
\end{align*}
$$

Note, however, that the combined commitment remains the same if we assume that $r^\prime+s^\prime=r+s$ (the commiter can simply adjust the blinding factors so that this assumption holds):

$$
\begin{align*}
C_3^\prime &= C_1^\prime + C_2^\prime \\
    &= (2+2) G_1 + (5+1) G_2 + (r^\prime+s^\prime) B \\ 
    &= 4 G_1 + 6 G_2 + (r^\prime+s^\prime) B \\
    &= C_3 \space\space (\text{if }r^\prime+s^\prime = r+s)
\end{align*}
$$

This manipulation allows the committer to open $C_3$ to $v^\prime$, $w^\prime$, which are different from the original vectors $v$ and $w$.

### Conclusion
If we used the same $G₁…Gₙ$ for both vectors before adding them, the commitment would no longer be binding.
By using different sets of points for each vector, i.e., $G₁…Gₙ$ for the first and $H₁…Hₙ$ for the second, any redistribution of values between $v_i$ and $w_i$ affects different points $G_i$ and $H_i$, changing the combined commitment $C_3$.
Therefore, the committer cannot manipulate the openings without detection because the points are distinct, and their discrete logs are unknown.

# Exercise 2

What happens if the committer tries to switch the same elements inside the vector?

For example, they commit

$$
C_1 = v_1G_1+v_2G_2+\dots+v_nG_n+rB
$$

but open with the first two elements swapped:

$$
[v_2,v_1,v_3,\dots,v_n]
$$

Assume that the vector $G_1,\dots,G_n$ is unpermuted.

### Answer

If the committer tries to open the commitment using the swapped vector, the claimed commitment would be:

$$
C_1^\prime=v_2G_1+v_1G_2+v_3G_3+\dots+v_nG_n+rB
$$

In the verification process, the verifier computes this commitment using the provided values and compares it with the original commitment $C_1$.
However, since $G_1\neq G_2$ and $v_1\neq v_2$, the verifier concludes $C_1^\prime\neq C_1$.
Therefore, the committer cannot successfully open the commitment using the swapped vector.

# Exercise 3

Suppose we commit a vector of values to the points $G_1$ and $G_2$.
The discrete logarithm for $G_1$ is known, but the discrete logarithm for $G_2$ is not known. 
We will ignore the blinding term for now.
Can the committer open to two different vectors?
Why or why not?

### Answer

Let $C = v_1G_1 + v_2G_2$ be a commitment.
Furthermore, let $G_1 = g_1G$ and $G_2 = g_2G$, where $G$, $G_1$, and $G_2$ are elliptic curve points and $g_1$ and $g_2$ are the discrete logarithms of $G_1$ and $G_2$, respectively.
We assume that the committer knows $g_1$ but does not know $g_2$.

Suppose the committer wants to find different values $v_1^\prime$ and $v_2^\prime$ such that $C = v_1^\prime G_1 + v_2^\prime G_2$.
As a first step, the committer might express $G_1$ in terms of $G$ such that:

$$
C = v_1g_1G + v_2G_2
$$

Then, the committer could set up the equality for the alternative opening

$$
C = v_1^\prime g_1G + v_2^\prime G_2
$$

subtract the original commitment from the forged commitment

$$
0 = (v_1^\prime - v_1) g_1 G + (v_2^\prime - v_2) G_2
$$

and rearrange this equation as:

$$
(v_1^\prime - v_1) g_1 G = - (v_2^\prime - v_2) G_2
$$

Recall that the committer knows $g_1$ and can, therefore, compute the left-hand side of the above equation.
However, since they do not know the discrete logarithm of $G_2$, they cannot compute $-(v_2^\prime - v_2)G_2$ in terms of $G$.
In other words, they cannot find $v_2^\prime$ that satisfies the equation without knowing $g_2$.

As a conclusion, the committer cannot find alternative $v_1^\prime$, $v_2^\prime$ to open $C$ differently because the unknown discrete logarithm of $G_2$ prevents them from adjusting $v_2$ accordingly.
Any attempt to change $v_1$ would require a corresponding change in $v_2$, which is not feasible without knowledge of $g_2$.
Therefore, the committer is bound to the original vector $(v_1, v_2)$.