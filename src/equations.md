# Key Mathematical Formulations

## 1. Quality-of-Experience (QoE) Definition (Equation 1, Section 3.1)

The QoE of a request with response length $l$ is defined as the ratio of the actual area under the user's token digestion curve $A(t)$ to the expected area under the ideal token delivery curve $T(t)$, up to the actual time to the last token (TTLT):

$$
QoE=\frac{S_{\textrm{actual}}}{S_{\textrm{expected}}}=\frac{\int_{0}^{TTLT}A(t)dt}{\int_{0}^{TTLT}\min(T(t),l)dt}
$$

Where:
*   $T(t) = TDS_{\textrm{expected}}\cdot (t - TTFT_{\textrm{expected}})$ represents the ideal timeline for token delivery.
*   $A(t)$ reflects the actual timeline of how tokens are digested by the user, with its slope capped by $TDS_{\textrm{expected}}$.
*   $S_{\textrm{actual}}$ is the area under $A(t)$.
*   $S_{\textrm{expected}}$ is the area under $\min(T(t),l)$.

## 2. QoE Penalizing Term for TTFT (Section 3.1)

To prioritize a shorter TTFT, a penalizing term can be added to the default QoE definition:

$$
\alpha^{TTFT_{\textrm{actual}}-TTFT_{\textrm{expected}}} \cdot \frac{S_{\textrm{actual}}}{S_{\textrm{expected}}}
$$

Where $\alpha \in [0,1]$. A smaller $\alpha$ applies a stronger penalty for longer actual TTFTs.

## 3. Scheduling Objective: QoE Gain (Equation 2, Section 4.1)

The objective function for scheduling request $i$ is defined as the QoE gain, which is the difference between the QoE if the request is served and if it is not served in the upcoming timeframe $\Delta t$:

$$
Q_{\textrm{serve},i}-Q_{\textrm{wait},i}
$$

Where:
*   $Q_{\textrm{serve},i}$ is the estimated QoE of request $i$ after $\Delta t$ if it is selected to be served.
*   $Q_{\textrm{wait},i}$ is the estimated QoE of request $i$ after $\Delta t$ if it remains in the queue and is not served.

## 4. Knapsack Problem Formulation (Equation 4, Section 4.1)

For a specific batch size $B$, the scheduling problem is formulated as an Exact K-item Knapsack problem:

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

Where:
*   $x_i$ is an indicator variable (1 if request $i$ is served, 0 otherwise).
*   $N$ is the total number of requests.
*   $l_i$ is the context length of request $i$ (representing memory consumption).
*   $M$ is the total KV cache capacity in GPU memory.
*   $Q_{\textrm{serve},i}(B)$ explicitly shows the dependence of $Q_{\textrm{serve},i}$ on the batch size $B$.

## 5. Greedy Priority Function (Equation 5, Section 4.2)

For the greedy packing algorithm, the priority of request $i$ is defined as the ratio of its QoE gain to its context length:

$$
\frac{Q_{\textrm{serve},i}(B)-Q_{\textrm{wait},i}}{l_{i}}
$$

This function prioritizes requests that yield high QoE gain while consuming less GPU memory.

## 6. Alternative Scheduling Objectives (Appendix A)

### Maximizing the Minimum QoE (Equation 6, Appendix A)
To maximize the minimum QoE across all requests, the gain (item value in knapsack) of request $i$ can be formulated as:

$$
\max(Q_{\min}-Q_{\textrm{wait},i},0)
$$

Where $Q_{\min}$ is the current minimum QoE across all requests. This prioritizes requests that, if not served, would further degrade the minimum QoE.

### Maximizing the Number of Requests with Perfect QoE (Equation 7, Appendix A)
To optimize the number of requests that achieve perfect QoE, the gain (item value in knapsack) of request $i$ can be formulated as:

$$
[\mathbb{1}(Q_{\textrm{serve, i}}=1)-\mathbb{1}(Q_{\textrm{wait, i}}=1)]\cdot\mathbb{1}(Q_{\textrm{current},i}=1)
$$

Where $\mathbb{1}(\cdot)$ is the indicator function (1 if true, 0 otherwise), and $Q_{\textrm{current},i}$ is the request's current QoE. This prioritizes requests that are currently at perfect QoE and would degrade if not served.