import sys, os, requests

from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from app.core.config import MODEL

url = "http://localhost:11434/api/chat"


def generate_response(
    history: list, temperature: float = 0.7, top_p: float = 0.9
) -> str:
    data = {
        "model": "mistral",
        "messages": history,
        "options": {"temperature": temperature, "top_p": top_p},
    }

    response = requests.post(url, json=data, stream=False)
    return response.text


load_dotenv()
print(os.environ.get("MODEL"))
HISTORY = [{"role": "user", "content": "Hello, what model are you?"}]
r = generate_response(HISTORY)
print(r)
