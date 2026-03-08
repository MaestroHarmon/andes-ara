# Key Definitions

## 1. Tokens (Section 1)
*   **Tokens**: The fundamental units of text processing and generation by Large Language Models (LLMs). Words or sub-word units (e.g., "streaming" may be "stream" and "ing").

## 2. Text Streaming Services (Section 1)
*   **Text Streaming Services**: LLM-based applications that provide interactive conversations where the LLM generates tokens one by one and streams them back to the user to be digested incrementally. This is analogous to frame-by-frame video streaming.

## 3. Token Delivery Timeline (TDT) (Section 1, 2.2)
*   **Token Delivery Timeline (TDT)**: A series of timestamps when each token was delivered to a user for a single request. It captures the user's continuous interaction with the service.
*   **Expected TDT**: The ideal TDT a user expects, defined by the minimum Time-To-First-Token (TTFT) and minimum Token Delivery Speed (TDS).

## 4. Time-To-First-Token (TTFT) (Section 2.2)
*   **Time-To-First-Token (TTFT)**: The duration a user waits for the first token of a response to arrive. A critical metric for initial user experience.

## 5. Token Delivery Speed (TDS) (Section 2.2)
*   **Token Delivery Speed (TDS)**: The rate at which tokens are delivered to the user after the first token. This rate depends on factors like application type and user demographics (e.g., reading speed, speaking speed).
*   **Expected TDS**: The desired rate at which tokens should be delivered for optimal user digestion.

## 6. Quality-of-Experience (QoE) (Section 1, 3.1)
*   **Quality-of-Experience (QoE)**: A metric formally defined in this paper to quantify user satisfaction in text streaming services. It compares the actual TDT of a request with its expected TDT, reflecting the user's experience throughout their entire interaction with the service.
    *   **Principles of QoE**:
        1.  **Perfect Satisfaction**: QoE = 1 when actual delivery meets or exceeds expected.
        2.  **Excess Token Delivery**: Delivering tokens faster than digestion speed does not increase QoE.
        3.  **Early Token Delivery**: Users prefer earlier token delivery; QoE is higher for shorter TTFT or faster TDS.

## 7. KV Cache (Section 2.1)
*   **KV Cache**: Key-Value cache. A significant amount of memory required by Transformer-based LLMs to store intermediate data (keys and values) for each token in its input prompt and output response. Its size grows with the number of tokens, limiting concurrent requests.

## 8. Continuous Batching (Section 4.1)
*   **Continuous Batching**: An optimization technique used in LLM serving systems where new requests are continuously added to the batch as soon as they arrive, and completed requests are removed, maximizing GPU utilization. Andes invokes its scheduler at each iteration of continuous batching.

## 9. Preemption (Section 4.2)
*   **Preemption**: The mechanism by which a running request is temporarily paused and its resources (e.g., GPU computation, KV cache memory) are freed up to be allocated to another request.
    *   **Swapping**: Moving a request's KV cache entries between GPU and CPU memory.
    *   **Recomputation**: Dropping all KV cache entries on preemption and recomputing them when the request restarts.

## 10. QoE Gain (Section 4.1)
*   **QoE Gain**: The difference in QoE a request would achieve if it were served versus if it were not served ($Q_{\textrm{serve},i}-Q_{\textrm{wait},i}$). This is the "value" used in the knapsack formulation.

## 11. Prediction Timeframe ($\Delta t$) (Section 4.1)
*   **Prediction Timeframe ($\Delta t$)**: The duration into the future for which the scheduler estimates QoE gains to make optimal scheduling decisions.

## 12. Preemption Cap ($P$) (Section 4.2)
*   **Preemption Cap ($P$)**: A configurable limit on the average number of times a request can be preempted throughout its lifetime, designed to safeguard against excessive preemption overhead (thrashing).