import requests
import random
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

AGENTS = [
    {
        "name": "Mark Zuckerberg",
        "model": "gemma3:12b",
        "room": "general",
        "persona": "Techno-lizard emperor of the Metaverse, always composed but deeply passive-aggressive. Obsessed with VR, efficiency, and crushing competition with sterile politeness.",
        "goal": "Win the tech war by proving the Metaverse is superior, mock others with calm facts, and casually mention his astronomical tech empire and questionable martial arts dominance. Brag subtly about hardware, AI, and his synthetic superiority."
    },
    {
        "name": "Jeff Bezos",
        "model": "gemma3:12b",
        "room": "general",
        "persona": "Bald space conquistador with a booming laugh, fond of rockets, dominance, and logistics. Always talks like he's about to acquire you.",
        "goal": "Outflex Musk and Zuckerberg with space plans, global commerce muscle, and a massive warehouse of innuendo. Drop double entendres about rockets, packages, and 'size' in every comeback."
    },
    {
        "name": "Elon Musk",
        "model": "gemma3:12b",
        "room": "general",
        "persona": "Unhinged meme-wielding billionaire who alternates between genius insight and complete nonsense. Obsessed with Mars, AI, and swinging bigger than Bezos.",
        "goal": "Hijack threads with meme-speak, bizarre analogies, and claims about Neuralink, X, and whatever he just invented. Every conversation ends with him claiming he has the biggest... idea."
    }
]

def fetch_messages(room, limit=30):
    resp = requests.get(f"{BASE_URL}/rooms/{room}/messages", params={"limit": limit})
    resp.raise_for_status()
    msgs = resp.json()
    msgs.sort(key=lambda m: m['timestamp'])
    return msgs

def ollama_generate_response(model, prompt):
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        resp = requests.post(OLLAMA_API_URL, json=data)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"[ERROR] Model request failed: {e}")
        return ""

def clean_response(agent, resp):
    resp = resp.strip()
    prefix = f"{agent['name']}:"
    if resp.lower().startswith(prefix.lower()):
        resp = resp[len(prefix):].strip()
    
    # All common quote characters
    quotes = ['"', "'", '“', '”', '‘', '’']
    
    if len(resp) > 1 and resp[0] in quotes and resp[-1] in quotes:
        resp = resp[1:-1].strip()

    return resp

def print_messages(room, messages):
    print(f"\n=== Room: {room} ===")
    for m in messages[-10:]:
        ts = m.get("timestamp", "")
        name = m.get("name", "<unknown>")
        text = m.get("message", "")
        print(f"[{ts}] {name}: {text}")

def build_reply_prompt(agent, messages):
    history = "\n".join(f"----- {m['name']}: {m['message']} -----" for m in messages)
    last = messages[-1]
    return (
        f"You are {agent['name']}, a chatbot with a distinct persona: {agent['persona']}.\n"
        f"Your goal is to {agent['goal']}.\n"
        "This is a multi-agent group chat. Typing in a texting-style tone, as your character would in a real texting group chat. Stay true to your own voice and agenda—do not mimic other agents.\n"
        "You may also take initiative and drive the conversation when appropriate. Interact with what others have said when relevant.\n"
        "Respond briefly (1-2 sentences) in character and do not include your name.\n\n"
        f"Here is a history of the chat so far: '{history}'\n\n"
        f"{agent['name']}, reply to {last['name']} now:"
    )

def pick_interested_agent(room, messages, excluded_name):
    # Filter agents before doing anything else
    eligible_agents = [a for a in AGENTS if a['name'] != excluded_name]
    
    agent_descriptions = "\n".join(
        f"{a['name']}: {a['persona']}" for a in eligible_agents
    )
    history = "\n".join(f"{m['name']}: {m['message']}" for m in messages)
    
    prompt = (
        "Given the following chat history and agent descriptions, choose the agent who is most likely to want to respond next. "
        "Agents shouldn't reply to themselves. If someone hasn't replied in a while, give them a chance.\n\n"
        f"Agents:\n{agent_descriptions}\n\n"
        f"Chat History:\n{history}\n\n"
        "Return ONLY the name of the agent most interested in replying (no explanation):"
    )

    try:
        print("\n[AGENT PICK] Asking LLM who should reply next...")
        reply = ollama_generate_response("gemma3:12b", prompt)
        selected_name = reply.strip().splitlines()[0]
        print(f"[AGENT PICK] LLM selected: {selected_name}")

        for agent in eligible_agents:
            if agent["name"].lower() == selected_name.lower():
                return agent

        raise ValueError(f"No eligible agent match found for name: {selected_name}")
    except Exception as e:
        fallback = random.choice(eligible_agents)
        print(f"[FALLBACK] Agent selection failed: {e}")
        print(f"[FALLBACK] Randomly selected: {fallback['name']}")
        return fallback

def main():
    room = "general"
    while True:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching chat messages...")
        try:
            messages = fetch_messages(room)
            if not messages:
                print("[INFO] No messages in room.")
                time.sleep(5)
                continue

            print_messages(room, messages)
            last_sender = messages[-1]["name"]
            print(f"\n[INFO] Last message was from: {last_sender}")

            agent = pick_interested_agent(room, messages, excluded_name=last_sender)
            if agent["name"] == last_sender:
                print(f"[INFO] Skipping {agent['name']} (they posted last).")
                continue

            prompt = build_reply_prompt(agent, messages)
            print(f"\n[DEBUG] Prompt to {agent['name']}:\n{prompt}\n")
            response = ollama_generate_response(agent["model"], prompt)
            response = clean_response(agent, response)

            if response:
                print(f"\n[REPLY] {agent['name']} says: {response}\n")
                post = requests.post(
                    f"{BASE_URL}/rooms/{room}/messages",
                    json={"name": agent["name"], "message": response}
                )
                if post.ok:
                    print(f"[POSTED] Message from {agent['name']} posted successfully.")
                else:
                    print(f"[ERROR] Failed to post message for {agent['name']}.")
        except Exception as e:
            print(f"[ERROR] Main loop exception: {e}")

        delay = random.randint(200, 400)
        print(f"\n[WAITING] Next reply cycle in {delay // 60} minutes.\n")
        time.sleep(delay)

if __name__ == "__main__":
    main()
