---
type: "temporal"
id: "decisions"
---

This file documents key architectural decisions made during the development of Andes.

*   **QoE-aware Priority Scheduling:** The decision to prioritize requests based on their expected QoE gain and resource usage was driven by the goal of maximizing overall user satisfaction.

*   **Greedy Packing Algorithm:**  The choice of the greedy packing algorithm over the DP solution was based on the need for a faster scheduling algorithm that could handle a large number of requests in real-time.

*   **Client-Side Token Buffer:**  The client-side token buffer was implemented to smooth out network latency fluctuations and ensure a consistent token delivery rate for the user.

*   **Preemption Cap:** A preemption cap was introduced to limit the number of times a request can be preempted, mitigating the overhead associated with preemption.