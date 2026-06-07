# 🧠 csv-query-agent

> A private project — natural language to SQL agent built with LangGraph, Groq, and Streamlit.
<img width="1470" height="832" alt="image" src="https://github.com/user-attachments/assets/61a5862c-76e9-4625-a8ff-f07fd0cddadf" />
<img width="1470" height="832" alt="image" src="https://github.com/user-attachments/assets/2402e21e-623b-430a-84b6-1aa7a6ccb584" />
<img width="1470" height="832" alt="image" src="https://github.com/user-attachments/assets/bee58a96-7e17-4765-a7b3-078113ca8b67" />
<img width="1470" height="832" alt="image" src="https://github.com/user-attachments/assets/5b726969-b2ca-49fa-ab49-c64ff1b60c36" />




---

## 📌 What is this?

**csv-query-agent** lets you upload any CSV file and ask questions about it in plain English. The agent converts your question into a SQL query, shows it to you for review, and returns a human-readable answer — no SQL knowledge needed.

---

## ✨ Features

- 🗣️ **Natural language to SQL** — plain English in, SQL out
- 👁️ **Human-in-the-loop approval** — UPDATE / DELETE queries always shown for review before running
- 📊 **Any CSV file** — upload any CSV, schema is read automatically
- 🔒 **Safe by design** — original CSV is never modified, all changes on a SQLite copy
- 💬 **Plain English answers** — raw results explained in simple language
- ⬇️ **Download updated data** — export the modified data as a new CSV at the end

---

## 🏗️ Architecture

```
User Question
      │
      ▼
┌─────────────────┐
│  Schema Fetcher  │  reads columns, types, sample values from CSV
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Generator   │  LLaMA 3.3-70b generates SQL using schema context
└────────┬────────┘
         │
         ▼
┌─────────────────┐     reject + feedback
│   HITL Approval │ ──────────────────────► back to SQL Generator
└────────┬────────┘
         │ approve
         ▼
┌─────────────────┐
│  SQL Executor   │  runs query on SQLite copy of your CSV
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│ Result Formatter │  LLM explains rows in plain English
└──────────────────┘
         │
         ▼
    Final Answer
```

---

## 🚀 Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/csv-query-agent.git
cd csv-query-agent
```

### 2. Create virtual environment
```bash
python -m venv myenv
source myenv/bin/activate       # Mac / Linux
myenv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free key at [console.groq.com](https://console.groq.com)

### 5. Run
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
csv-query-agent/
├── app.py                 ← Streamlit frontend
├── SQL_project.py         ← LangGraph backend
├── requirements.txt       ← dependencies
├── .env                   ← API key (never commit)
├── .gitignore
└── README.md
```

---

## 🔁 HITL Flow

```
SELECT query          →  runs immediately, no approval needed
UPDATE / DELETE query →  paused, shown for review
                         ✓ Approve → executes
                         ✕ Cancel  → discarded, nothing changes
```

---

## 💡 Example Queries

| Question | Generated SQL |
|---|---|
| Who has the highest salary? | `SELECT name, salary FROM data ORDER BY salary DESC LIMIT 1;` |
| Average salary by department | `SELECT department, AVG(salary) FROM data GROUP BY department;` |
| How many people in Engineering? | `SELECT COUNT(*) FROM data WHERE department = 'Engineering';` |
| Update Arjun's salary to 150000 | `UPDATE data SET salary=150000 WHERE name='Arjun';` ⚠️ needs approval |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Agent graph + HITL interrupt |
| [Groq](https://groq.com) | LLaMA 3.3-70b inference |
| [LangChain](https://python.langchain.com) | Prompts + structured output |
| [Pandas](https://pandas.pydata.org) | CSV loading + result formatting |
| SQLite | In-process SQL engine (stdlib) |
| [Streamlit](https://streamlit.io) | Web UI |
| [Pydantic](https://docs.pydantic.dev) | LLM output schema |

---

## 🔐 Environment Variables

| Variable | Description | Where to get |
|---|---|---|
| `GROQ_API_KEY` | Groq API key | [console.groq.com](https://console.groq.com) |

---

## 👨‍💻 Author

**Om Prakash Gupta**  
https://www.linkedin.com/in/om-prakash-gupta-686156377?utm_source=share_via&utm_content=profile&utm_medium=member_android
