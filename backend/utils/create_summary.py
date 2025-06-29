import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

modelName = "gemini-1.5-flash"

@retry(wait=wait_random_exponential(min=10, max=60), stop=stop_after_attempt(4), retry=retry_if_exception_type(Exception))
def generateWithGemini(context, question):
    model = genai.GenerativeModel(modelName)
    prompt = f"""Use the context to respond to the question.

Context:
{context}

Question:
{question}
"""
    response = model.generate_content(prompt)
    return response.text

def createSummary(db):
    print("\n🧾 Generating summaries of each file...\n")
    docs = db.docstore._dict.values()
    summaries = {}

    for i, doc in enumerate(docs):
        context = doc.page_content
        source = doc.metadata.get("source", f"File_{i+1}")
        filename = os.path.basename(source)
        question = "Give a concise and clear summary of this file."

        try:
            summary = generateWithGemini(context, question)
            summaries[filename] = summary
            print(f"📄 Summary for {filename}:\n{summary}\n{'-'*60}")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Skipped {filename} due to error: {e}")
    
    return summaries
