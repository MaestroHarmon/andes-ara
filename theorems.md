# Theoretical Results and Hardness

## 1. Knapsack Problem Formulation (Section 4.1)

The core scheduling problem in Andes is formulated as a variant of the classic knapsack problem. Specifically, for a given batch size $B$, the problem is to select a set of $B$ requests (items) from $N$ total requests to run in the upcoming time quantum. Each request $i$ has a "value" (QoE gain) defined as $Q_{\textrm{serve},i}(B)-Q_{\textrm{wait},i}$ and a "weight" (GPU memory consumption) $l_i$ (context length). The goal is to maximize the total QoE gain while ensuring the total memory consumption does not exceed the GPU memory capacity $M$.

The mathematical formulation is:
$$
\max_{x} \sum_{i=1}^{N}\left(Q_{\text{serve},i}(B)-Q_{\text{wait},i}\right)\cdot x_{i}
$$
$$
\text{s.t. } x_{i}\in\{0,1\},~{}i\in 1,\ldots,N
$$
$$
\sum_{i=1}^{N}x_{i}=B
$$
$$
\sum_{i=1}^{N}l_{i}x_{i}\leq M
$$
where $x_i$ is an indicator variable (1 if request $i$ is served, 0 otherwise).

## 2. Algorithmic Hardness: Exact K-item Knapsack (Section 4.2)

This specific variant, where exactly $B$ items must be chosen, is known as the **Exact K-item Knapsack problem**.
*   **NP-Hardness**: The Exact K-item Knapsack problem is **weakly NP-Hard**. This means that while it is NP-Hard in general, it can be solved in pseudo-polynomial time if the numerical values (like $M$) are not excessively large.
*   **Dynamic Programming Solution**: An optimal solution can be found using a 3D dynamic programming approach (Algorithm 2 in Appendix C). The time complexity of this DP solution is $O(M \cdot N^2)$, where $M$ is the maximum number of tokens that can fit in GPU memory and $N$ is the total number of requests.
*   **Intractability for Online Serving**: Despite being pseudo-polynomial, this $O(M \cdot N^2)$ complexity is too high for online LLM serving systems. In practice, $N$ can be in the hundreds and $M$ in the thousands, making the DP solution intractable for repetitive, real-time scheduling decisions. The problem also needs to be solved for each possible batch size $B \in [1, N]$, further increasing the computational burden.

## 3. Preemption Frequency Bound (Section 4.2)

The paper theoretically analyzes the average preemption frequency needed to optimize QoE.
*   **Theoretical Bound**: If the serving system can handle $r_0$ requests per second and the actual request rate is $k \cdot r_0$ (where $k \geq 1$), then there are $(k-1) \cdot r_0$ "excess" requests whose QoE might degrade due to queuing. Roughly one preemption is needed to accommodate each of these requests.
*   **Average Preemption Frequency**: The average preemption frequency needed is bounded by $k-1$. This implies that as long as the load is not excessively high, the number of preemptions remains small, mitigating concerns about thrashing.
*   **Efficiency of Long Request Preemption**: Preempting a single long request can free up enough GPU memory to serve multiple new requests, further reducing the total number of preemptions required to alleviate head-of-line blocking.