# Demo Video Script (~3 minutes)

## Opening (15 seconds)

**Show**: The ADK web UI at localhost:8000 with "omnitask" selected.

**Say**: "This is OmniTask, a multi-agent AI system that manages tasks, schedules, and notes. It's built with Google's Agent Development Kit and uses Gemini 2.5 Flash. Let me show you how it works."

---

## Part 1: Task Management (30 seconds)

**Type**: `Create a task called Prepare presentation due tomorrow`

**Say**: "I can create tasks with natural language. The system routes this to the task agent, which stores it in our SQLite database."

**Type**: `Create a task called Review pull requests due today`

**Say**: "Let me add another task for today."

**Type**: `List all my tasks`

**Say**: "I can list all tasks — you can see both with their due dates and status."

---

## Part 2: Calendar Events (30 seconds)

**Type**: `Schedule a team standup today at 10am to 10:30am`

**Say**: "When I mention a specific time, the coordinator recognizes this as a calendar event and routes it to the schedule agent."

**Type**: `Am I free today from 10am to 11am?`

**Say**: "I can check availability — it correctly detects the conflict with our standup."

---

## Part 3: Notes (20 seconds)

**Type**: `Save a note titled Sprint Goals with content: launch v2 by Friday, fix auth bug`

**Say**: "The notes agent handles information storage with searchable tags."

**Type**: `Search my notes for auth`

**Say**: "And I can search across all notes by keyword."

---

## Part 4: Daily Overview — The Key Feature (25 seconds)

**Type**: `What's on my schedule today?`

**Say**: "This is where multi-agent coordination shines. The schedule agent calls our daily overview tool, which queries BOTH the tasks and events tables, giving the user a complete picture of their day — tasks due AND calendar events in one response."

---

## Part 5: Multi-Step Workflow (30 seconds)

**Type**: `Check if I'm free tomorrow at 2pm, and if so schedule a design review from 2 to 3pm`

**Say**: "This is a multi-step workflow. Watch the trace on the left — the root agent delegates to the schedule agent, which first checks availability, confirms the slot is free, then creates the event. Two tool calls coordinated automatically."

**Type**: `Create a meeting with the client tomorrow at 4pm to 5pm, and add a task called Prepare meeting agenda due today`

**Say**: "Here's another multi-step: it creates a calendar event AND a task in sequence, routing to the right agent for each action."

---

## Part 6: Architecture Explanation (30 seconds)

**Show**: Switch to the code editor or a slide showing the architecture diagram.

**Say**: "Under the hood, we have a root agent coordinating three specialist agents — task, schedule, and notes. Each agent has its own tools that perform CRUD operations on a SQLite database. All tools are also exposed via an MCP server using FastMCP. The system is built with Google ADK and deploys to Cloud Run with a single command."

**Show**: Briefly flash the file structure (6 files total).

**Say**: "The entire system is just 6 files — about 300 lines of code. ADK handles the orchestration, routing, and UI for us."

---

## Closing (10 seconds)

**Say**: "OmniTask demonstrates how multi-agent systems can coordinate across tools and data sources to handle real-world productivity workflows. Thanks for watching."

---

## Tips for Recording

- Use a clean browser window (no bookmarks bar, no other tabs)
- Start a **New Session** before recording so there's no old data
- Wait for each response before typing the next command
- Point out the **Trace panel** on the left when showing multi-step workflows — it shows the agent transfers and tool calls
- Keep the pace steady — don't rush through commands
- If a response looks messy, just move on. The content matters more than formatting
