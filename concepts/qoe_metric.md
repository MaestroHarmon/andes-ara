---
type: "concept"
id: "qoe_metric"
math_reqs: true
---

The Quality-of-Experience (QoE) metric quantifies user satisfaction with a text streaming service based on the Token Delivery Timeline (TDT). It compares the actual token delivery against the expected delivery.

The QoE is calculated as:

$QoE = \frac{S_{actual}}{S_{expected}} = \frac{\int_{0}^{TTLT} A(t) dt}{\int_{0}^{TTLT} min(T(t), l) dt}$

Where:

*   $T(t) = TDS_{expected} * (t - TTFT_{expected})$ is the expected token delivery curve.
*   $A(t)$ is the actual token delivery curve (slope capped by expected TDS).
*   $l$ is the response length.
*   $TTLT$ is the Time-To-Last-Token.
*   $S_{actual}$ is the area under the actual token delivery curve.
*   $S_{expected}$ is the area under the expected token delivery curve.

QoE Principles:

*   **Perfect Satisfaction:** $QoE = 1$ when actual meets or exceeds expected delivery.
*   **Excess Token Delivery:** Delivering tokens faster than the user's digest speed adds no value.
*   **Early Token Delivery:** Users prefer receiving more tokens earlier in the stream.