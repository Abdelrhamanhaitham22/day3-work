# day3-work

Clinical RAG work for sickle cell disease, based on the NHLBI 2014 *Evidence-Based Management of Sickle Cell Disease* guideline.

## Structure

- `day1_day2/` — Day 1 & 2 notebook (`Clinical_RAG_Sickle_Cell_Disease_Day1_and_Day2.ipynb`): PDF ingestion, chunking, embedding, retrieval, and evaluation.
- `day3/` — Day 3 notebook (`Day3_Grounded_Generation.ipynb`) and implementation plan (`Day3_Implementation_Plan.md`): grounded generation, citation, schema validation, and refusal behavior.
  - `day3/screenshots/` — reference screenshots from the hackathon instructions.
- `references/` — source guideline (`56-364NFULL.pdf`).
- `schema/response_schema.json` — JSON schema for the grounded answer format.
- `config.py`, `ingest.py`, `query.py` — shared modules used by the Day 3 notebook.
- `requirements.txt` — Python dependencies.

## Setup

```bash
pip install -r requirements.txt
```

To use a real LLM in the Day 1/2 or Day 3 notebooks, set one of:

```bash
export GROQ_API_KEY=...
export OPENAI_API_KEY=...
```

Without an API key, the notebooks run in **simulation mode** so the retrieval, schema, and refusal logic are still fully testable.

## Running the notebooks

```bash
jupyter nbconvert --to notebook --execute day1_day2/Clinical_RAG_Sickle_Cell_Disease_Day1_and_Day2.ipynb
jupyter nbconvert --to notebook --execute day3/Day3_Grounded_Generation.ipynb
```

## Safety note

This is an educational RAG demo. It does not diagnose, prescribe, or replace a clinician.
