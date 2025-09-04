# Smart Todo (Gemini)

An AI-powered todo manager with **FastAPI backend**, **CLI interface**, and **SQLite persistence**. Tasks are automatically categorized, prioritized, and scheduled using Google Gemini.

---

## Features
- **Natural task input**: Add todos like `"Finish API doc by 5pm"`.
- **AI enrichment**: Gemini assigns category, priority, and due date.
- **FastAPI REST API** with Swagger docs at `/docs`.
- **Interactive CLI** (terminal REPL) for quick use.
- **SQLite persistence** via SQLAlchemy — tasks survive restarts.
- **Commands supported**:
  - `add <text>`
  - `show all`
  - `show <category>`
  - `show immediate`
  - `done <id>`
  - `delete <id>`
  - `help`
  - `exit`

---

## Tech Stack
- **Python 3.10+**
- **FastAPI** + **Uvicorn** (HTTP API)
- **SQLAlchemy** + **SQLite** (persistence)
- **Pydantic v2** (models)
- **Rich** (CLI tables)
- **Google Generative AI** (`google-generativeai`)
- **Dateparser** (natural datetime parsing)
- **Dotenv** (for config)

---

## Setup

1. **Clone & enter repo**
```bash
git clone <your-repo-url>
cd smart_todo_gemini
```

2. **Create & activate venv**
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# .\venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up .env**
```env
GEMINI_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-1.5-flash
LOCAL_TZ=America/Toronto
```

5. **Initialize database**
```bash
python -c "from db import init_db; init_db()"
```

---

## Running

### CLI
```bash
python main.py
```
Example:
```
todo> add Meeting with Ralph tomorrow at 2pm
Added Meeting with Ralph tomorrow at 2pm → work (p4)

todo> show immediate
┏━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃id ┃ category ┃ priority┃ due                  ┃ status ┃ text                     ┃
┡━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
┃1  ┃ work     ┃ 4       ┃ 2025-09-04T14:00-04:00┃ open   ┃ Meeting with someone...    ┃
└───┴──────────┴─────────┴──────────────────────┴────────┴──────────────────────────┘
```

### API
Start server:
```bash
uvicorn api:app --reload
```
Open Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example request:
```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"text":"finish API doc by 17:30"}'
```

Response:
```json
{
  "id": 1,
  "text": "finish API doc by 17:30",
  "category": "work",
  "priority": 4,
  "due_dt": "2025-09-04T17:30:00-04:00",
  "status": "open",
  "created_at": "2025-09-03T21:29:01.002352"
}
```

---

## Roadmap
- [ ] Add AI-powered intent recognition (natural language interface).
- [ ] Add user profiles / multi-user DB.
- [ ] Deploy FastAPI backend on AWS.
- [ ] Add React frontend.

---

## License
MIT
