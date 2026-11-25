# BreakTraceFix AI - 11-Stage Data Flow & Execution Tracing

## Overview
BreakTraceFix AI monitors the full execution lifecycle of Generative AI applications through an 11-stage pipeline tracer.

## Pipeline Stages
1. **User Input**: Ingestion of raw natural language prompt.
2. **Input Validation**: Adversarial injection and jailbreak screening.
3. **Prompt Construction**: Merging system templates, boundaries, and variables.
4. **Retrieval**: Querying vector indexes with tenant partition filters.
5. **Context Assembly**: Ranking and formatting chunks for prompt context.
6. **Model Invocation**: LLM inference and token stream generation.
7. **Tool Selection**: Parsing model intent and tool arguments.
8. **Authorization**: Evaluating permissions across the 8-axis matrix.
9. **Tool Execution**: Sandboxed tool invocation and result collection.
10. **Output Validation**: Sanitizing HTML/XSS and verifying safety invariants.
11. **Final Response**: Returning verified output to client.

## Data Scrubbing & OpenTelemetry
- All trace data is automatically scrubbed by `RedactionPipeline` before storage.
- Traces can be exported in standard OpenTelemetry `ResourceSpans` JSON format.

