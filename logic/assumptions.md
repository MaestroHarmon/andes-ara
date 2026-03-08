# Assumptions

## Explicit Assumptions
1.  **Text Streaming Service Characteristics**: The paper assumes that LLM-based applications are increasingly interactive and stream text token-by-token, akin to video streaming, justifying the need for a QoE metric that captures continuous interaction.
2.  **User Digestion Speed**: Users have an "expected" token delivery speed (TDS) and time-to-first-token (TTFT) that can be estimated based on factors like reading speed (WPM by age group) or speaking speed (WPM by language). These speeds are used to define the expected Token Delivery Timeline (TDT).
3.  **QoE Requirements Specification**: Application developers can pre-specify QoE requirements (expected TTFT and TDS) for each request.
4.  **Continuous Batching Support**: The underlying LLM serving system supports continuous batching, allowing the scheduler to make decisions at each inference iteration.
5.  **Preemption Mechanism Availability**: The underlying LLM serving system supports at least one preemption mechanism (swapping KV cache or recomputation) to enable dynamic resource allocation.
6.  **Correlation of Batch Size and Total Context Length**: Token generation latency can be modeled primarily as a function of batch size, as batch size and total context length are highly correlated in a live serving system (Pearson correlation coefficient 0.997).

## Implicit Assumptions
1.  **User Perception of QoE**: The proposed mathematical QoE definition accurately reflects human perception of quality in text streaming services.
2.  **Predictability of Future QoE**: The system can reasonably estimate $Q_{\textrm{serve},i}$ and $Q_{\textrm{wait},i}$ for a future timeframe $\Delta t$.
3.  **Resource Bottleneck**: The primary bottleneck for QoE in LLM serving is GPU memory and computation, rather than network bandwidth or other factors (though the client-side buffer helps with network fluctuations).
4.  **KV Cache Management**: The overhead of storing and retrieving KV cache (swapping) is manageable and does not negate the benefits of preemption.
5.  **Workload Characteristics**: Request arrival patterns can be modeled by distributions like Poisson or Gamma, and request lengths follow distributions observed in datasets like ShareGPT.
6.  **Scheduler Overhead**: The computational overhead of the scheduling algorithm (greedy packing) is low enough to be practical for online serving.
7.  **Client-Side Buffer Adoption**: Clients will adopt and correctly implement the token buffer to smooth delivery.