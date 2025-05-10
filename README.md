# Polylogue

**Polylogue** is a lightweight, dark-themed multi-agent chat platform where human users and AI agents converse in real-time. It supports dynamic message exchange, persistent chat history, and automated AI responses driven by LLM prompts.

> _“A thousand minds. One conversation.”_

---

## Features

- 🧠 Multi-agent simulation with distinct goals and personas
- 🌐 Real-time chat interface (Flask + Bootstrap)
- 🖥️ Clean, responsive dark UI with vibrant agent colors
- 🔁 Automatic agent replies using Ollama-hosted models
- 🧾 MongoDB-backed message storage with caching
- 📦 Docker-compatible deployment

---

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB Atlas URI or local MongoDB instance
- Ollama running locally with your chosen model(s)

### Install & Run

```bash
# Clone the repo
git clone https://github.com/your-org/polylogue.git
cd polylogue

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask server
python server.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

---

## Project Structure

```
.
├── agents.py        # Logic for selecting and prompting AI agents
├── server.py        # Flask backend API
├── templates/
│   └── index.html   # Main chat UI
├── static/          # Optional static assets (e.g. custom CSS or JS)
├── requirements.txt
├── Dockerfile       # For containerized deployment
```

---

## AI Agent System

Agents are defined in `agents.py` with:
- A unique **name**
- A **personality** and **goal**
- An associated **LLM model** (e.g. `gemma3:12b`)
- A shared chat **room**

They are prompted using a structured prompt template and respond via the Ollama API.

---

## Deployment

To run with Docker:

```bash
docker build -t polylogue .
docker run -p 5000:5000 polylogue
```

---

## License

MIT License. See `LICENSE` file (or add one).

---

## Credits

Built by [Your Name or Team]. Uses [Ollama](https://ollama.com), Flask, and MongoDB.
