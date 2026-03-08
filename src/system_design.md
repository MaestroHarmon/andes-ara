# System Design: Andes

Andes is an LLM serving system designed to optimize Quality-of-Experience (QoE) for text streaming services. It consists of a server-side QoE-aware scheduler and a client-side token buffer.

## 1. Andes Overview Workflow (Figure 6, Section 3.2)

The overall workflow of Andes is as follows:

1.  **User Request Submission**: A user submits a request to the server. This request includes pre-specified QoE requirements (e.g., expected TTFT and TDS) defined by the application developer.
2.  **QoE Tracker and Waiting Queue**: Upon receiving the request, the **QoE tracker** component assigns an initial scheduling priority to the request based on its QoE requirements and places it into a **waiting queue**.
3.  **Dynamic Rescheduling**: At the beginning of each scheduling iteration (which aligns with each inference iteration in continuous batching):
    *   The QoE tracker refreshes the priorities of all requests, both those in the waiting queue and those currently running in the **running queue**.
    *   Andes then executes its QoE-aware scheduling algorithm. This algorithm decides which requests to admit from the waiting queue to the GPU workers and which low-priority running requests to **preempt** (evict) back to the server.
    *   For preempted requests, their states (primarily the KV cache) are stored in a **request metadata store** located in CPU RAM for future retrieval when they are rescheduled.
4.  **Token Generation**: During each inference iteration, the selected running requests generate one token each using the **GPU workers**.
5.  **Client-Side Token Delivery**: The newly generated tokens are immediately sent to the client.
6.  **Client-Side Token Buffer**: On the client side, a **token buffer** is responsible for receiving these tokens. It temporarily stores any excess tokens (generated faster than the user's digestion speed) and displays them to the user at their expected pace, ensuring a smooth and consistent token delivery experience.

## 2. Server-Side QoE-Aware Scheduler (Section 5)

The server-side scheduler is the core intelligence of Andes.

*   **Integration**: It is designed to work with any LLM serving system that supports continuous batching and at least one preemption mechanism. The paper implements it on top of `vLLM`.
*   **Scope**: The scheduler manages requests coming into the specific LLM instance it's integrated with, assuming cluster-level load balancing and fault tolerance are handled externally.
*   **Scheduling Algorithm**:
    *   **Problem Formulation**: The scheduling decision is framed as an Exact K-item Knapsack problem (Equation 4), aiming to maximize the total QoE gain ($Q_{\textrm{serve},i}-Q_{\textrm{wait},i}$) for a batch of requests, subject to GPU memory capacity ($M$) and a target batch size ($B$).
    *   **Efficiency Optimizations**:
        *   **Selective Triggering**: The complex knapsack solver is only invoked when GPU memory is constrained (e.g., >90% KV cache occupancy) or token generation latency exceeds stringent TDS requirements. Otherwise, all requests are served.
        *   **Batch Size Search Space Pruning**: The range of possible batch sizes $B$ to evaluate is narrowed to $[B_{\min}, B_{\max}]$ to reduce computation.
        *   **Greedy Packing Algorithm (Algorithm 1)**: An $O(N \log N)$ greedy algorithm is used to select requests. It prioritizes requests based on the ratio of QoE gain to context length ($\frac{Q_{\textrm{serve},i}(B)-Q_{\textrm{wait},i}}{l_{i}}$). This priority function inherently balances QoE merit, prevents starvation, and favors preempting long requests to free up significant memory.
        *   **Preemption Cap**: A configurable cap $P$ (e.g., $P=1$) is applied to the average number of preemptions per request to prevent thrashing and manage overhead.
*   **Preemption Mechanisms**:
    *   **Swapping**: Moving a request's KV cache entries from GPU memory to CPU memory when preempted, and back when resumed. This is generally preferred due to lower overhead (Appendix D).
    *   **Recomputation**: Discarding KV cache entries upon preemption and recomputing them from scratch when the request is restarted. Used if host memory for swapping is exhausted.

## 3. Client-Side Token Buffer (Section 5, Figure 8)

The client-side token buffer is a crucial component for ensuring a smooth user experience.

*   **Functionality**: It receives tokens from the server as soon as they are generated, even if the server's generation pace exceeds the user's expected Token Delivery Speed (TDS).
*   **Smoothing**: The buffer then smooths out the token delivery timeline, pacing the display of tokens to the user at their expected TDS.
*   **Network Resilience**: It naturally absorbs fluctuations in network latency, providing a consistent flow of text to the user.
*   **Server Awareness**: The server is aware of the buffer's state. If a request has accumulated enough tokens in its client buffer, the server can preempt it to serve other requests, knowing the user's experience will remain smooth as the buffer drains.
*   **Implementation**: The buffer should be implemented in the client-side application environment (e.g., TypeScript for web frontends, Python for API consumers).