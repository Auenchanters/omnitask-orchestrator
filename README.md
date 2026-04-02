# OmniTask Orchestrator

A multi-agent AI system built with Google's Agent Development Kit (ADK) that helps users manage tasks, schedules, and notes through natural language.

## Architecture

```
User <-> ADK Web UI <-> Root Agent (Coordinator)
                            |
              +-------------+-------------+
              |             |             |
         task_agent   schedule_agent  notes_agent
         (4 tools)     (4 tools)      (3 tools)
              |             |             |
              +------+------+------+------+
                     |             |
                SQLite DB     MCP Server
              (omnitask.db)  (11 tools via
                              stdio protocol)
```

### Multi-Agent Design

| Agent | Role | Tools |
|-------|------|-------|
| **Root Agent** (Coordinator) | Routes requests to specialist agents, handles multi-step workflows | Delegation only |
| **Task Agent** | CRUD operations on to-do items | `create_task`, `list_tasks`, `update_task`, `delete_task` |
| **Schedule Agent** | Calendar events, availability checking, daily overview | `create_event`, `list_events`, `check_availability`, `get_daily_overview` |
| **Notes Agent** | Note-taking and information retrieval | `create_note`, `search_notes`, `list_notes` |

### Key Features

- **Multi-agent coordination**: Root agent intelligently routes to specialist sub-agents
- **Structured database storage**: SQLite with 3 normalized tables (tasks, events, notes)
- **MCP integration**: Standalone MCP server exposes all 11 tools via Model Context Protocol
- **Multi-step workflows**: Handles complex requests like "check availability then schedule a meeting"
- **API-based deployment**: One-command deploy to Google Cloud Run

## Tech Stack

- **Agent Framework**: Google ADK (Agent Development Kit)
- **LLM**: Gemini 2.5 Flash
- **Database**: SQLite
- **MCP Server**: FastMCP (stdio transport)
- **Deployment**: Google Cloud Run
- **Language**: Python 3.10+

## Project Structure

```
V2/
├── omnitask/
│   ├── __init__.py        # Package init
│   ├── agent.py           # Root agent + 3 sub-agents
│   ├── tools.py           # 11 tool functions (business logic)
│   ├── db.py              # SQLite schema & connection
│   └── mcp_server.py      # MCP server (FastMCP)
├── .env                   # API key config
├── requirements.txt       # Dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.10+
- Google Gemini API key ([get one here](https://ai.google.dev))

### Install

```bash
cd V2
pip install -r requirements.txt
```

### Configure

Edit `.env` and add your Gemini API key:

```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your-api-key-here
```

### Run Locally

```bash
adk web
```

Open http://localhost:8000 and start chatting.

### Run MCP Server (standalone)

```bash
python -m omnitask.mcp_server
```

## Deploy to Cloud Run

```bash
adk deploy cloud_run \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --service_name=omnitask \
  --with_ui \
  .
```

## Example Interactions

**Task Management:**
```
> Create a task called Buy groceries due tomorrow
Created **Buy groceries** (due tomorrow).

> List all my tasks
**Tasks:**
• Buy groceries (due: Apr 2) - pending
```

**Scheduling:**
```
> Schedule a team meeting today at 2pm to 3pm
Scheduled **Team meeting** today, 2:00 PM to 3:00 PM.

> Am I free today from 2pm to 4pm?
Not available — conflicts with **Team meeting** (2:00 PM to 3:00 PM).
```

**Multi-step Workflow:**
```
> Check if I'm free tomorrow at 3pm, and if so schedule a design review
You're free tomorrow at 3:00 PM. Scheduled **Design review** for tomorrow, 3:00 PM to 4:00 PM.
```

**Notes:**
```
> Save a note titled Sprint Ideas with content: add dark mode feature
Saved note **Sprint Ideas**.

> Search my notes for dark mode
**Notes matching 'dark mode':**
• Sprint Ideas — add dark mode feature
```

## Database Schema

### tasks
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| title | TEXT | Task name |
| description | TEXT | Optional details |
| status | TEXT | 'pending' or 'done' |
| due_date | TEXT | YYYY-MM-DD format |
| created_at | TEXT | Timestamp |

### events
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| title | TEXT | Event name |
| description | TEXT | Optional details |
| start_time | TEXT | YYYY-MM-DD HH:MM format |
| end_time | TEXT | YYYY-MM-DD HH:MM format |
| created_at | TEXT | Timestamp |

### notes
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment primary key |
| title | TEXT | Note title |
| content | TEXT | Note body |
| tags | TEXT | Comma-separated tags |
| created_at | TEXT | Timestamp |

## How It Meets the Requirements

| Requirement | Implementation |
|---|---|
| Primary agent + sub-agents | Root agent delegates to task, schedule, and notes agents |
| Database storage | SQLite with 3 tables for structured CRUD |
| Tools via MCP | 11 tools exposed via FastMCP server + ADK tool wrappers |
| Multi-step workflows | Agent chains sub-agent calls sequentially |
| API deployment | `adk deploy cloud_run` produces HTTP API endpoint |

## Team

Built for the APAC Gen AI Academy Hackathon 2026.
