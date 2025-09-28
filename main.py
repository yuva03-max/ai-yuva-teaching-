from flask import Flask, render_template, request
from groq import Groq
import asyncio
import markdown

app = Flask(__name__)

API_KEY = "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"

def get_groq_client(api_key):
    return Groq(api_key=api_key)

async def ask_groq(prompt: str, api_key: str, model="llama-3.3-70b-versatile") -> str:
    try:
        client = get_groq_client(api_key)
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI teaching assistant. Reply in Markdown format with well-structured sections and simulated Google Doc links."
                },
                {"role": "user", "content": prompt}
            ],
            model=model
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

async def run_agents(topic, api_key):
    prompts = {
        "professor": f"Create a detailed knowledge base on '{topic}' including key concepts, applications, and fundamentals. Include a simulated Google Doc link.",
        "advisor": f"Design a structured learning roadmap for '{topic}', broken into beginner to expert levels. Include time estimates and a simulated Google Doc link.",
        "librarian": f"Curate a list of high-quality resources (videos, docs, blogs) for learning '{topic}' with descriptions. Simulate Google Doc link.",
        "assistant": f"Create practice exercises and real-world projects for mastering '{topic}', including solutions. Include a simulated Google Doc link."
    }
    tasks = [ask_groq(prompts[role], api_key) for role in prompts]
    raw_responses = await asyncio.gather(*tasks)
    responses = {}
    for role, markdown_text in zip(prompts.keys(), raw_responses):
        html = markdown.markdown(
            markdown_text,
            extensions=["fenced_code", "nl2br", "tables", "sane_lists"]
        )
        responses[role] = html
    return responses

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        topic = request.form.get("topic")

        if not topic:
            return render_template("index.html", error="Please enter a Topic.")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        responses = loop.run_until_complete(run_agents(topic, API_KEY))

        return render_template("index.html", topic=topic, responses=responses)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
