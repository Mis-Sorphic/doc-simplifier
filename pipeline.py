import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from fastapi import FastAPI
from pydantic import BaseModel
 
# Load the .env file so we can read GEMINI_API_KEY
load_dotenv()
 
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
 
app = FastAPI()
 
 
class DocumentRequest(BaseModel):
    text: str
 
 
model = genai.GenerativeModel("gemini-2.5-flash-lite")
 
 
def generate_with_retry(prompt, max_retries=3):
    """
    Calls the model and automatically retries with increasing wait times
    if we hit a rate limit (429 error). This is called 'exponential backoff' -
    each retry waits longer than the last, giving the quota time to free up.
    """
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            wait_time = 30 * (attempt + 1)
            print(f"Rate limited. Waiting {wait_time}s before retry "
                  f"({attempt + 1}/{max_retries})...")
            time.sleep(wait_time)
    raise Exception("Max retries exceeded - quota likely exhausted for today.")
 
 
def run_pipeline(document_text: str):
    extraction_prompt = f"""You are a precise legal/medical document analyst.
Read the document below and extract its key facts as a clear list.
 
For each key point, capture:
- What the rule/fact actually says
- Who it applies to
- Any conditions, exceptions, or deadlines attached to it
 
Be exhaustive - do not skip exceptions or edge cases, even small ones.
Do not simplify language yet, just extract the precise meaning accurately.
 
DOCUMENT:
{document_text}
 
EXTRACTED KEY POINTS:"""
    extracted_points = generate_with_retry(extraction_prompt)
 
    simplify_prompt = f"""You are an expert at explaining legal and medical
documents to everyday people with no specialist background.
 
Below is a list of precise key points extracted from a document.
Rewrite them in plain, simple, everyday language a teenager could understand.
 
Rules:
- Keep every condition, exception, and deadline - do not drop any of them
- Use short sentences and common words
- Where a term is asymmetric or unfair to one party, make that clear and obvious
- Do not add information that wasn't in the key points
 
KEY POINTS:
{extracted_points}
 
PLAIN LANGUAGE VERSION:"""
    simplified_text = generate_with_retry(simplify_prompt)
 
    verify_prompt = f"""You are a meticulous fact-checker comparing two versions
of the same information.
 
ORIGINAL KEY POINTS (ground truth):
{extracted_points}
 
SIMPLIFIED VERSION (to be checked):
{simplified_text}
 
Compare them carefully and list any issues found, such as:
- Any condition, exception, or deadline that was dropped or changed
- Any meaning that was distorted or oversimplified in a misleading way
- Any important nuance (like one-sided terms) that got lost or softened
 
If everything checks out with no issues, simply say:
"No issues found - the simplified version preserves all key meaning."
 
ISSUES FOUND:"""
    verification_result = generate_with_retry(verify_prompt)
 
    no_issues_phrase = "no issues found"
    if no_issues_phrase in verification_result.lower():
        final_text = simplified_text
        was_corrected = False
    else:
        correction_prompt = f"""You are revising a plain-language explanation
to fix specific accuracy issues, while keeping it simple and easy to read.
 
ORIGINAL KEY POINTS (ground truth):
{extracted_points}
 
CURRENT SIMPLIFIED VERSION (has issues):
{simplified_text}
 
ISSUES TO FIX:
{verification_result}
 
Rewrite the simplified version to fix every issue listed above.
Keep the language simple and easy to read - do not make it complicated
again just to be precise. Add brief clarifying phrases where needed
instead of legal jargon.
 
CORRECTED PLAIN LANGUAGE VERSION:"""
        final_text = generate_with_retry(correction_prompt)
        was_corrected = True
 
    return {
        "extracted_points": extracted_points,
        "simplified_text": simplified_text,
        "verification_result": verification_result,
        "final_text": final_text,
        "was_corrected": was_corrected,
    }
 
 
@app.post("/simplify")
def simplify_document(request: DocumentRequest):
    result = run_pipeline(request.text)
    return result
 
 
@app.get("/")
def root():
    return {"message": "Document simplifier API is running"}
 

if __name__ == "__main__":
    # This block ONLY runs when you do `python pipeline.py` directly.
    # It does NOT run when uvicorn imports this file to start the server.
    # Useful for quick local testing without spinning up the whole API.
    with open("sample_legal.txt", "r", encoding="utf-8") as f:
        test_text = f.read()

    result = run_pipeline(test_text)

    print("===== EXTRACTED POINTS =====")
    print(result["extracted_points"])
    print()
    print("===== SIMPLIFIED TEXT =====")
    print(result["simplified_text"])
    print()
    print("===== VERIFICATION RESULT =====")
    print(result["verification_result"])
    print()
    print("===== FINAL TEXT (was_corrected:", result["was_corrected"], ") =====")
    print(result["final_text"])