import os
import json
import requests
from openai import OpenAI

# --- OpenAI client (uses your proxy & key pattern) ---
ENDPOINT = os.getenv("OPENAI_BASE_URL", "https://cdong1--azure-proxy-web-app.modal.run")
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_DEPLOYMENT", "gpt-4o")

client = OpenAI(base_url=ENDPOINT, api_key=API_KEY)

SOURCE_URL = "https://www.kentuckyderby.com/past-winners/"
OUT_TXT = "kentucky_derby.txt"

# ---- Define a tool the model can call to "grab" the URL ----
tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the content of a URL over HTTP GET and return the HTML as text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The absolute URL to fetch"}
                },
                "required": ["url"]
            }
        }
    }
]

def run():
    # System prompt tells the model how to use the tool and what to return.
    messages = [
        {
            "role": "system",
            "content": (
                "You can call fetch_url to retrieve web pages. "
                "Task: Visit the provided Kentucky Derby page, parse the FIRST HTML table, "
                "take the FIRST 3 DATA ROWS (skip header rows), and output a clean, "
                "readable PLAIN TEXT block containing just:\n"
                "- An optional header line with column names\n"
                "- Three lines for the first 3 rows, preserving key fields\n"
                "Rules: No markdown, no code fences, no extra commentary."
            )
        },
        {
            "role": "user",
            "content": f"The page is here: {SOURCE_URL}"
        }
    ]

    # First request — model will likely call our tool.
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0
    )

    message = resp.choices[0].message

    print(f"Saved: {OUT_TXT}")

if __name__ == "__main__":
    run()