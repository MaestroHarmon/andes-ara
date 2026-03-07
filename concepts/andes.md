---
type: "concept"
id: "andes"
math_reqs: false
---

Andes is a QoE-aware LLM serving system designed to enhance user experience in text streaming services. It achieves this by dynamically prioritizing requests based on their expected QoE gain and resource usage.

Key components:

1.  **QoE Tracker:** Assigns scheduling priority, manages waiting/running queues.
2.  **Request Metadata Store:** Stores KV cache on CPU RAM for preempted requests.
3.  **GPU Workers:** Execute inference iterations.
4.  **Client-Side Token Buffer:** Smooths token delivery at expected TDS.

The system uses a [preemptive request scheduler](./src/scheduler.py) to optimize resource allocation and improve [QoE](./claims/qoe_improvement.md).