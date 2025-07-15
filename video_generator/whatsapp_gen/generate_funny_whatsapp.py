import openai
import os
import json
import dotenv
dotenv.load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_funny_whatsapp_chat(participants):
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
    try:
        chat = json.loads(content)
    except Exception:
        chat = [{"from": sender, "to": receiver, "text": content}]
    return chat

def paginate_messages(messages, per_page=6):
    pages = []
    total = len(messages)
    num_pages = (total + per_page - 1) // per_page
    for page in range(num_pages):
        start = page * per_page
        end = start + per_page
        paginated = messages[start:end]
        has_next = (page < num_pages - 1)
        pages.append({
            "page": page + 1,
            "has_next": has_next,
            "messages": paginated
        })
    return pages

def main():
    participants = ["Ana", "Bruno"]
    messages = generate_funny_whatsapp_chat(participants)
    pages = paginate_messages(messages, per_page=6)
    output = {
        "participants": participants,
        "pages": pages
    }
    with open("output_paginated.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("Output written to output_paginated.json")

if __name__ == "__main__":
    main()