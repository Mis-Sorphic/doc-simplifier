# Plainify

An AI-powered tool that translates dense legal and medical documents into plain, everyday language — without losing the nuance that actually matters.

## The Problem

Legal contracts and medical documents are written for professionals, not for the people they affect most. Important details — deadlines, exceptions, one-sided clauses — often get lost not because people aren't smart, but because the language is genuinely hard to parse. Existing "simplify this text" tools tend to oversimplify, accidentally smoothing over exactly the details that matter (e.g. who actually has the power in a contract clause).

## How It Works

Instead of a single prompt asking an AI to "make this simpler," Plainify uses a four-stage AI pipeline, where each stage has one narrow job and checks the work of the stage before it:

1. **Extract** — reads the original document and pulls out every fact, condition, exception, and deadline precisely, without simplifying yet. This becomes the "ground truth" for everything that follows.
2. **Simplify** — rewrites the extracted points in plain, everyday language, explicitly instructed to preserve every condition and flag any one-sided or unfair terms.
3. **Verify** — compares the simplified version against the extracted ground truth and flags anything that was dropped, distorted, or oversimplified in a misleading way.
4. **Correct** — if Stage 3 finds issues, this stage rewrites the simplified version specifically to fix those issues, while staying simple. If no issues are found, this stage is skipped entirely.

This design means the system actively catches its own mistakes rather than confidently producing a single, unchecked simplification — important for content where getting it wrong has real consequences.

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** Google Gemini API
- **Frontend:** HTML, CSS, JavaScript 
- **Deployment:** Render (backend), Vercel/Netlify (frontend)

## Why This Architecture

Single-prompt AI tools are fast to build but hard to trust for high-stakes content. By splitting the task into extraction, simplification, verification, and correction, each step is simpler and more reliable than asking one prompt to do everything at once — and crucially, the system can show its own reasoning: what it found, what it changed, and why.

## Limitations

This is a portfolio/learning project, not a production legal or medical tool. It does not replace professional legal or medical advice. The free-tier AI model used has rate limits and may occasionally miss subtle nuances that a human expert would catch — the verification stage reduces this risk but doesn't eliminate it.

## Running Locally

1. Clone this repo
2. Create a virtual environment and install dependencies: `pip install -r requirements.txt`
3. Get a free Gemini API key from [aistudio.google.com](https://aistudio.google.com)
4. Create a `.env` file with `GEMINI_API_KEY=your_key_here`
5. Run the backend: `uvicorn pipeline:app --reload`
6. Open `index.html` in a browser (or use VS Code's Live Server extension)

