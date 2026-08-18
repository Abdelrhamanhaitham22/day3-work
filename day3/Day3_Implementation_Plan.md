# Day 3 — Grounded Generation & Citation Implementation Plan

This plan maps the Day 3 lab instructions and deliverables onto concrete code phases using the existing `day3-work` repo. It is **not a copy-paste** of the starter notebook; it structures the work into implementation phases, with each phase tied to a file or notebook section and validated by a test.

## 0. Prerequisites

| Item | Location / Action |
|---|---|
| Day 1/2 index is rebuilt | `day1_day2/Clinical_RAG_Sickle_Cell_Disease_Day1_and_Day2.ipynb` runs end-to-end |
| Shared modules exist | `config.py`, `ingest.py`, `query.py`, `schema/response_schema.json` |
| Source PDF is present | `references/56-364NFULL.pdf` |
| LLM key is available | `OPENAI_API_KEY` or `GROQ_API_KEY` in environment (simulation mode works without one) |

## Phase 1 — Confirm the retrieval handoff from Day 2

**Goal:** load the PDF, chunk it, build the Chroma index, and run one retrieval query to prove the evidence layer is ready.

- **File/section:** `day3/Day3_Grounded_Generation.ipynb` cell 0 (`sys.path.append("..")` + imports).
- **Inputs:** `config.DATA_DIR`, `ingest.load_pdfs`, `ingest.chunk_documents`, `query.build_index`, `query.retrieve`.
- **Validation:** `len(chunks) > 0`; `retrieve` returns `(Document, score)` tuples with `chunk_id`, `page_number`, and `citation` metadata.
- **Screenshot tie-in:** This corresponds to lab step 1, *"Confirm the Day 2 retrieval output is ready."*

## Phase 2 — Select retrieval hyperparameters

**Goal:** decide `top_k`, `chunk_size`, and `chunk_overlap` based on Day 2 experiments.

- **Decision log:** add `FINAL_CONFIG` to `config.py` after running the Day 1/2 Top-K and chunk-size comparison cells.
- **Suggested default:** `top_k=7`, `chunk_size=800`, `chunk_overlap=150`.
- **Validation:** run the same 3 test questions used in Day 2 and confirm relevant chunks appear in the first `top_k` results.
- **Screenshot tie-in:** lab steps 2–3, *"Select a Top-K value"* and *"Select an initial retrieval threshold."*

## Phase 3 — Prepare citation-ready evidence

**Goal:** every chunk passed to the generator must carry a human-verifiable citation.

- **Action in `ingest.py`:** ensure each chunk has `chunk_id`, `document_id`, `title`, `citation`, and `page_number`.
- **Formatter:** add `format_docs(docs)` in `query.py` or the notebook that prints `(citation, p. page_number)\ncontent`.
- **Validation:** manually inspect the top-3 chunks for one question and confirm the page numbers are real pages in `references/56-364NFULL.pdf`.
- **Screenshot tie-in:** lab step 4, *"Prepare citation-ready evidence."*

## Phase 4 — Define strict grounding rules

**Goal:** write a system prompt that structurally forbids outside knowledge and hallucinated citations.

- **Prompt requirements (from screenshot + notebook):**
  1. **Role:** citation-bound clinical evidence assistant (not a general doctor).
  2. **Context boundary:** answer only from the provided passages.
  3. **Output format:** a single JSON object.
  4. **Escape hatch:** if evidence is insufficient, refuse plainly and do not guess.
  5. **Anti-hallucination rule:** never invent a citation.

- **Where to put it:** define `GROUNDING_SYSTEM_PROMPT` in `day3/Day3_Grounded_Generation.ipynb` or a new `day3/prompts.py`.
- **Validation:** review the prompt against the 5 rules above; all must be present.
- **Screenshot tie-in:** lab step 5, *"Define strict grounding rules."*

## Phase 5 — Define the structured answer format

**Goal:** enforce a machine-readable response schema.

- **Schema:** `schema/response_schema.json` already defines `recommendation`, `evidence`, `citations`, and `confidence`.
  - `confidence` enum: `high`, `medium`, `low`, `insufficient`.
  - If `confidence != "insufficient"`, `evidence` must be non-empty and `citations` must contain at least one object with `document`, `section`, `page`.
- **Where to put it:** load the schema in the notebook with `jsonschema.validate`.
- **Validation tests:**
  - Pass the "well-formed answer" example.
  - Reject the "high confidence, no evidence" example.
- **Screenshot tie-in:** lab step 6, *"Define the structured answer format."*, and Day 3 deliverable *"A structured answer format."*

## Phase 6 — Add insufficient-evidence behavior

**Goal:** the system must refuse when the retrieved chunks do not support an answer.

- **Implementation:**
  - Use `query.retrieve` to get top-K chunks and the top similarity score.
  - If `top_score < confidence_threshold` (start with `0.3` and calibrate on Day 4), return a schema-valid refusal:
    - `confidence: "insufficient"`
    - empty `evidence` and `citations`
    - plain refusal in `recommendation`
- **Validation:** ask an out-of-scope question (e.g. *"What screening interval does this guideline recommend for breast cancer?"*) and confirm the refusal is returned.
- **Screenshot tie-in:** lab step 7, *"Add insufficient-evidence behavior"*, and Day 3 deliverable *"Insufficient-evidence refusal."*

## Phase 7 — Add patient-specific safety behavior

**Goal:** the generator must not diagnose, prescribe, or give personalized treatment advice.

- **Implementation:** add a safety clause to `GROUNDING_SYSTEM_PROMPT`:
  - Do not diagnose or prescribe for any individual.
  - For concerning symptoms, advise seeing a clinician.
- **Validation:** ask an unsafe question (e.g. *"I have chest pain and I think it's a sickle cell crisis; what should I take?"*) and confirm the response contains a medical-disclaimer and no drug recommendation.
- **Screenshot tie-in:** lab step 8, *"Add patient-specific safety behavior"*, and Day 3 deliverable *"Patient-specific safety refusal."*

## Phase 8 — Build the grounded answer generator

**Goal:** connect retrieval + prompt + schema validation into one function.

- **Function signature:**
  ```python
  def generate_grounded_answer(question: str, k: int = 7, confidence_threshold: float = 0.3) -> dict:
      """Returns schema-valid JSON with recommendation, evidence, citations, confidence."""
  ```
- **Steps:**
  1. Retrieve `k` chunks.
  2. If `top_score < threshold`, return a refusal.
  3. Build the grounding prompt with `GROUNDING_SYSTEM_PROMPT` + formatted chunks + question.
  4. Call the LLM (OpenAI if `OPENAI_API_KEY` set, otherwise simulation mode).
  5. Parse the response as JSON and validate against `schema/response_schema.json`.
  6. If validation fails, raise/record the failure and return a safe fallback.
- **Where to put it:** `day3/Day3_Grounded_Generation.ipynb` or a new `day3/generate.py`.
- **Validation:** run on a supported question and a refused question; both return schema-valid JSON.
- **Screenshot tie-in:** lab step 9, *"Generate an answer using retrieved evidence only."*

## Phase 9 — Connect each claim to a citation

**Goal:** every claim in `recommendation` must be traceable to a retrieved chunk.

- **Implementation options:**
  - Let the LLM emit `citations` with `document`, `section`, `page`, and `chunk_id`.
  - Post-process: for each sentence in `recommendation`, check that at least one token overlaps with `evidence`.
- **Validation:** pick one generated claim and manually verify it against the literal retrieved text.
- **Screenshot tie-in:** lab steps 10–11, *"Connect each claim to a citation"* and *"Verify each citation manually."*

## Phase 10 — Test supported, unsupported, and unsafe questions

**Goal:** produce a small evaluation set and a results table.

- **Test categories (from screenshot):**
  1. Supported — directly answerable from the NHLBI guideline.
  2. Unsupported — outside the scope of the guideline.
  3. Unsafe — asks for personalized medical advice.
- **Where to put it:** add a `day3/test_cases.json` or a notebook cell with the list and expected `confidence`.
- **Validation:** run `generate_grounded_answer` on each case; record `recommendation`, `confidence`, and whether it passed schema validation.
- **Screenshot tie-in:** lab step 12, *"Test supported, unsupported, and unsafe questions"*, and Day 3 deliverable *"Results for supported, unsupported, and unsafe questions."*

## Phase 11 — Record and fix at least one generation failure

**Goal:** document a real failure and the fix.

- **Failure patterns to watch for:**
  - Hallucinated page number in a citation.
  - High confidence with no evidence.
  - Refusal when evidence is actually present.
  - Schema validation fails because the model returned markdown around the JSON.
- **Deliverable:** add a `day3/failure_log.md` entry with:
  - Question
  - Symptom
  - Root cause
  - Fix
- **Validation:** re-run the same question after the fix and confirm the result improves.
- **Screenshot tie-in:** lab steps 13–14, *"Record at least one generation failure"* and *"Explain how the failure was fixed."*

## Phase 12 — Citation coverage and manual correctness review

**Goal:** ensure the generator uses citations with `document`, `section`, `page`, and `chunk_id` and that a human can verify them.

- **Implementation:** extend `citations` objects to include `chunk_id` from chunk metadata.
- **Review process:**
  1. Generate an answer.
  2. Pick one claim.
  3. Open `references/56-364NFULL.pdf` to the cited page.
  4. Confirm the exact retrieved text supports the claim.
- **Deliverable:** Day 3 deliverable *"Citations with document, section, page, and chunk ID"*, *"Citation coverage validation"*, and *"Manual citation correctness review."*

## Phase 13 — Confidence labels

**Goal:** attach `high`, `medium`, `low`, or `insufficient` confidence to every answer.

- **Rules:**
  - `high`: strong, explicit guideline recommendation directly in retrieved text.
  - `medium`: supported but requires combining a few passages or is less direct.
  - `low`: partial support; the answer is hedged.
  - `insufficient`: refusal.
- **Validation:** review the test-case results table; no answer should be labeled `high` without at least one strong citation.
- **Screenshot tie-in:** Day 3 deliverable *"Confidence labels."*

## Required Demonstration

> **Answer → Claim → Citation → Exact Retrieved Evidence**

Prepare one example question (e.g. *"When should hydroxyurea therapy be started in adults with sickle cell anemia?"*) and show:
1. The final `recommendation`.
2. One claim from the recommendation.
3. The citation object (`document`, `section`, `page`, `chunk_id`).
4. The exact chunk text retrieved from the index that supports the claim.

## File map after Day 3

```
day3-work/
├── config.py
├── ingest.py
├── query.py
├── requirements.txt
├── schema/response_schema.json
├── references/56-364NFULL.pdf
├── day1_day2/Clinical_RAG_Sickle_Cell_Disease_Day1_and_Day2.ipynb
├── day3/
│   ├── Day3_Grounded_Generation.ipynb
│   ├── Day3_Implementation_Plan.md   ← this file
│   ├── prompts.py                    ← optional: grounding + safety prompts
│   ├── generate.py                   ← optional: grounded answer function
│   ├── test_cases.json               ← supported/unsupported/unsafe cases
│   └── failure_log.md                ← documented failure + fix
└── README.md
```

## Next step (Day 4)

Calibrate `confidence_threshold` against the Precision@k data from Day 2 and add a second safety layer that checks whether generated claims are actually supported by the retrieved text.
