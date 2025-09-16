<!-- # Smart Todo (Gemini)

An AI-powered todo manager with **FastAPI backend**, **CLI interface**, and **SQLite persistence**. Tasks are automatically categorized, prioritized, and scheduled using Google Gemini.

---




## Features
- **Natural task input**: Add todos like `"Finish API doc by 5pm"`.
- **AI enrichment**: Gemini assigns category, priority, and due date.
- **FastAPI REST API** with Swagger docs at `/docs`.
- **Interactive CLI** (terminal REPL) for quick use.
- **SQLite persistence** via SQLAlchemy — tasks survive restarts.
- **Features supported**:
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
initialize api keys and api layer
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
MIT -->

# Momentum — Keep Your Work in Motion

An AI-assisted task manager with a **FastAPI backend**, **React frontend**, and **Postgres persistence**. Tasks are added in natural language, enriched with AI (categories, priorities, due dates), and summarized into daily or weekly insights.

---

<img width="2126" height="1690" alt="screenshot" src="https://github.com/user-attachments/assets/393a01bd-a3a8-4400-bcf2-82a6ffd6dd7d6" />

## Features

* **Natural task input**: Add todos like `"Meeting Steph at 4"` or `"Pay hydro tomorrow"`.
* **AI-powered enrichment**: Gemini categorizes tasks, sets due dates, and priorities.
* **NLP commands**:

  * `show <category>` or `show today`
  * `summarize today|this_week|all`
  * `complete all`
  * `delete <category>`
* **Smart categories + isolated tasks**.
* **Mark done / delete** with instant updates.
* **AI summaries**: human-style briefs for today, this week, or all.
* **Quick Stats card** with live progress bar.
* **Neo-Brutalism inspired UI**: bold borders, pastel cards, playful hover states.
* **Upcoming features**: sidebar with deadlines, AI-powered insight cards.

---

## Tech Stack

* **Frontend**: React + TypeScript, TailwindCSS, Flowbite, Framer Motion
* **Backend**: FastAPI (Python)
* **Database**: Postgres + SQLAlchemy ORM
* **Models**: Pydantic v2
* **AI**: Google Gemini (NLP parser, task enrichment, summarizer)
* **Infrastructure**: Uvicorn, dotenv (config)

---

## Architecture

* **Frontend**: input parsing, task grouping, QuickStats, UI cards
* **API**: `/tasks`, `/nlp/command`, `/summary`
* **AI layers**:

  * L1: command parsing
  * L2: task enrichment (category, due, priority)
  * L3: summarization (narratives + KPIs)
* **Storage**: Postgres with task schema (`id`, `text`, `category`, `status`, `priority`, `due_dt`, `created_at`, `updated_at`)

---

## Setup

1. **Clone & enter repo**

```bash
git clone <your-repo-url>
cd momentum
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
DATABASE_URL=postgresql://user:pass@localhost:5432/momentum
GEMINI_API_KEY=your_api_key_here
```

5. **Initialize database**

```bash
python -c "from db import init_db; init_db()"
```

---

## Running

### Backend API

```bash
uvicorn api:app --reload
```

Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Example:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"text":"finish API doc by 5pm"}'
```

### Frontend

```bash
cd frontend
npm install
yarn dev   # or npm run dev
```

Open: [http://localhost:5173](http://localhost:5173)

---

## Roadmap

* [ ] Slide-out sidebar for navigation & upcoming deadlines
* [ ] AI-powered insight cards (risky/overdue tasks)
* [ ] User profiles / multi-user support
* [ ] Deploy full stack on AWS

---

## License

MIT
