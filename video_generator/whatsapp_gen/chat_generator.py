import os
from dotenv import load_dotenv
import openai

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_chat(participants):
    sender, receiver = participants
    prompt = (
        f"Gere uma conversa engraçada de WhatsApp entre duas pessoas chamadas {sender} e {receiver}. "
        "A conversa deve ser completa, com início, meio e fim, e deve construir até o ponto principal da piada, entregando a punchline no final. "
        "Formate como uma lista de objetos de mensagem, cada um com 'from', 'to' e 'text'. "
        f"'from' deve ser '{sender}' ou '{receiver}', 'to' deve ser o outro participante. "
        "Mantenha o tom leve e humorístico, em português brasileiro. "
        "Exemplo: [ {\"from\": \"Ana\", \"to\": \"Bruno\", \"text\": \"Oi!\"}, ... ]"
    )
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.9,
    )
    content = response.choices[0].message.content
    import json
    try:
        chat = json.loads(content)
    except Exception:
        chat = [{"from": sender, "to": receiver, "text": content}]
    return chat 