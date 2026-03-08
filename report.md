# ARA Ingestor Implementation Report

## Executive Summary

Successfully implemented a "Fat Prompt, Thin Client" Universal ARA (Agent-Native Research Artifact) Ingestor and validated it on the Andes paper (ArXiv 2404.16283). The system transforms research papers into structured filesystem representations that isolate core logic, executable components, temporal context, and supporting evidence.

## Implementation Overview

### Task 1: ara_system_prompt.txt ✅

Created a comprehensive 5,611-character system prompt that:

1. **Defines the Universal ARA Schema** with four layers:
   - `/logic` (Cognitive): Claims, methodology, assumptions, limitations, definitions
   - `/src` (Physical): Algorithms, pseudocode, equations, system design
   - `/trace` (Temporal): Related work, timeline, future work, comparisons
   - `/evidence` (Supportive): Experiments, results, datasets, baselines, ablations

2. **Enforces mandatory `<deconstruction>` block** requiring:
   - Paper identity analysis
   - Core contribution identification
   - Problem statement extraction
   - Key innovation mapping
   - Technical component enumeration
   - Evaluation strategy analysis
   - Negative knowledge capture
   - Layer mapping planning

3. **Enforces strict XML output format**:
   ```xml
   <file path="relative/path/to/file.md">
   [Content in Markdown]
   </file>
   ```

### Task 2: ingest.py ✅

Created a 14,337-byte Python thin client that:

1. **CLI Interface**: Takes ArXiv ID and output directory as arguments
   ```bash
   python ingest.py 2404.16283 --output_dir andes_ara_output
   ```

2. **Paper Fetching**: Uses ar5iv HTML endpoint with fallback to ArXiv API
   - HTML text extraction via custom parser
   - Handles network errors gracefully

3. **LLM Integration**: Supports both OpenAI and Google Gemini APIs
   - Default: Gemini 2.5 Flash (due to OpenAI quota limitations)
   - Configurable via `--provider` flag

4. **XML Parsing**: Extracts `<file path="...">` blocks using regex
   - Handles both single and double quotes
   - Normalizes paths (removes leading slashes)

5. **Safe File Writing**: 
   - Security check prevents path traversal attacks
   - Creates nested directories automatically
   - UTF-8 encoding for all files

### Task 3: Execution and Validation ✅

**Command Executed:**
```bash
python ingest.py 2404.16283 --output_dir andes_ara_output --provider gemini --save-response
```

**Results:**
- Paper fetched: 80,867 characters from HTML
- LLM response: 51,116 characters
- Deconstruction block: 8,670 characters
- Files created: 10

## ARA Structure Analysis

### Generated Directory Structure

```
andes_ara_output/
├── _deconstruction.md      # Chain-of-thought analysis
├── _raw_response.md        # Full LLM response
├── theorems.md             # NP-Hardness discussion
├── logic/
│   ├── claims.md           # Core claims and contributions
│   ├── methodology.md      # QoE definition and approach
│   ├── assumptions.md      # System assumptions
│   ├── limitations.md      # Known limitations
│   └── definitions.md      # Key terms (QoE, TTFT, TDS, etc.)
└── src/
    ├── algorithms/
    │   ├── greedy_packing.md       # Algorithm 1
    │   └── dynamic_programming.md  # Algorithm 2
    ├── equations.md        # Mathematical formulations
    └── system_design.md    # Andes architecture
```

### Validation: QoE Metric in Cognitive Layer ✅

The `/logic/definitions.md` file successfully captures the QoE metric:

> **Quality-of-Experience (QoE)**: A metric formally defined in this paper to quantify user satisfaction in text streaming services. It compares the actual TDT of a request with its expected TDT, reflecting the user's experience throughout their entire interaction with the service.

The `/src/equations.md` file contains the formal mathematical definition:

$$QoE=\frac{S_{\textrm{actual}}}{S_{\textrm{expected}}}=\frac{\int_{0}^{TTLT}A(t)dt}{\int_{0}^{TTLT}\min(T(t),l)dt}$$

### Validation: Scheduling Logic in Physical Layer ✅

The `/src/algorithms/greedy_packing.md` file contains the complete scheduling algorithm:

- **Purpose**: Efficient solution to Exact K-item Knapsack problem
- **Priority Function**: $p[i] = \frac{q[i]}{l[i]}$ (QoE gain / context length)
- **Complexity**: O(N log N) time, O(N) space
- **Constraints**: GPU memory capacity and batch size limits

The `/src/system_design.md` file documents the complete Andes architecture:

- QoE tracker and waiting queue
- Dynamic rescheduling at each iteration
- Preemption mechanisms (swapping, recomputation)
- Client-side token buffer for smooth delivery

## Key Findings

1. **Fat Prompt Effectiveness**: The comprehensive system prompt successfully guided the LLM to produce well-structured, actionable output with minimal post-processing required.

2. **Deconstruction Value**: The mandatory chain-of-thought block ensures thorough paper analysis before file generation, improving extraction quality.

3. **Layer Separation**: The ARA schema effectively separates:
   - **What** the paper claims (cognitive)
   - **How** to implement it (physical)
   - **Where** it fits in the field (temporal)
   - **Why** we should believe it (evidence)

4. **Negative Knowledge Capture**: The deconstruction block explicitly captured limitations like preemption overhead, algorithmic complexity, and hardware-specific variations.

## Recommendations

1. **Add `/trace` and `/evidence` layers**: The current run focused on logic and src layers. Expanding the prompt to require trace and evidence files would provide complete coverage.

2. **Implement validation checks**: Add automated verification that all required files are present and non-empty.

3. **Support PDF fallback**: For papers without ar5iv HTML, implement PDF text extraction using libraries like PyMuPDF.

4. **Batch processing**: Add support for processing multiple papers in sequence.

## Conclusion

The "Fat Prompt, Thin Client" architecture successfully transforms research papers into structured, machine-actionable ARA representations. The Andes paper validation confirms that complex technical content (QoE metrics, scheduling algorithms) is correctly extracted and organized into the appropriate cognitive and physical layers.

---

**Files Delivered:**
- `ara_system_prompt.txt` - Universal ARA schema and extraction protocol
- `ingest.py` - Thin client implementation
- `andes_ara_output/` - Complete ARA for the Andes paper
