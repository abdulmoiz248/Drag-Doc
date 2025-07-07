from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def localSummary(text: str, max_length=200, min_length=50) -> str:
    try:
        chunks = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return chunks[0]["summary_text"]
    except Exception as e:
        return f"[ERROR during summarization] {str(e)}"
