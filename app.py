# app.py
import gradio as gr
import docx
import os
from openai import OpenAI

# Initialize OpenAI client (reads secret from Hugging Face or local env)
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def extract_text_docx(file):
    """Extract plain text from a DOCX file object."""
    try:
        doc = docx.Document(file)
        text = "\n".join([p.text for p in doc.paragraphs])
        return text.strip()
    except Exception:
        return None

def call_gpt(prompt):
    """Call OpenAI using new openai-python v1 interface. If no key, return demo text."""
    if client is None:
        # Demo fallback (no real API calls)
        return (
            "(Demo mode) OpenAI key not configured or quota exceeded. "
            "This is a simulated summary. Set OPENAI_API_KEY in your Space to enable real summaries."
        )
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500,
    )
    # new client response object
    return resp.choices[0].message.content.strip()

def summarize_docx(file):
    text = extract_text_docx(file)
    if not text:
        return "⚠️ Could not extract text from the DOCX file. Please upload a valid .docx document."

    max_chunk = 4000
    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summaries = []
    for chunk in chunks:
        prompt = (
            "Summarize the following document section into a concise professional summary. "
            "Focus on main objectives, test cases, results, and conclusions:\n\n" + chunk
        )
        try:
            s = call_gpt(prompt)
            summaries.append(s)
        except Exception as e:
            return f" Error contacting OpenAI API: {e}"

    final_summary = "\n\n".join(summaries)
    return f"###  Document Summary\n{final_summary}"

iface = gr.Interface(
    fn=summarize_docx,
    inputs=gr.File(label=" Upload DOCX file"),
    outputs="markdown",
    title="AI DOCX Summarizer (OpenAI GPT)",
    description="Upload a Word document (.docx) to generate a professional AI summary.",
    allow_flagging="never",
)

if __name__ == "__main__":
    iface.launch()
