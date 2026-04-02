import os
import sys
from datetime import datetime
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from . import tools

MODEL = "gemini-2.5-flash"
TODAY = datetime.now().strftime("%Y-%m-%d")

# ─── ADK Tool Wrappers (delegate to tools.py business logic) ─

def create_task(tool_context: ToolContext, title: str, description: str = "", due_date: str = "") -> dict:
    """Create a new task. due_date can be 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    return tools.create_task(title, description, due_date)

def list_tasks(tool_context: ToolContext, status_filter: str = "all") -> dict:
    """List tasks. Use status_filter='pending', 'done', or 'all'."""
    return tools.list_tasks(status_filter)

def update_task(tool_context: ToolContext, task_id: int, title: str = "", status: str = "", due_date: str = "") -> dict:
    """Update a task's title, status, or due_date. Set status to 'done' to mark complete."""
    return tools.update_task(task_id, title, status, due_date)

def delete_task(tool_context: ToolContext, task_id: int) -> dict:
    """Delete a task by its ID."""
    return tools.delete_task(task_id)

def create_event(tool_context: ToolContext, title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """Create a calendar event. Times must be in 'YYYY-MM-DD HH:MM' format."""
    return tools.create_event(title, start_time, end_time, description)

def list_events(tool_context: ToolContext, date: str = "") -> dict:
    """List calendar events. Filter by 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    return tools.list_events(date)

def check_availability(tool_context: ToolContext, start_time: str, end_time: str) -> dict:
    """Check if a time slot is free. Times in 'YYYY-MM-DD HH:MM' format."""
    return tools.check_availability(start_time, end_time)

def create_note(tool_context: ToolContext, title: str, content: str, tags: str = "") -> dict:
    """Create a note. Tags are comma-separated (e.g. 'work,ideas')."""
    return tools.create_note(title, content, tags)

def search_notes(tool_context: ToolContext, query: str) -> dict:
    """Search notes by title, content, or tags."""
    return tools.search_notes(query)

def list_notes(tool_context: ToolContext) -> dict:
    """List all notes."""
    return tools.list_notes()

def get_daily_overview(tool_context: ToolContext, date: str = "") -> dict:
    """Get tasks due AND calendar events for a date. Use 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    return tools.get_daily_overview(date)

# ─── Response formatting rules (shared across agents) ────────

FORMAT_RULES = """
RESPONSE FORMAT RULES (follow strictly):
- Be brief. One or two short sentences max.
- Use clean formatting: bullet points for lists, bold for titles.
- Never explain your reasoning or thought process.
- Never show raw dates like "2026-04-01 14:00". Say "today at 2:00 PM" or "Apr 2 at 10:00 AM".
- Never repeat tool parameters or internal details back to the user.
- For lists, use this format:
  **Tasks:**
  • Task name (due: date) - status
  **Events:**
  • Event name — time to time
"""

# ─── Sub-Agents ───────────────────────────────────────────────

task_agent = Agent(
    name="task_agent",
    model=MODEL,
    description="Manages to-do tasks: create, list, update, and delete tasks.",
    instruction=f"""You manage the user's to-do list. Today is {TODAY}.

Tools: create_task, list_tasks, update_task, delete_task.
For due dates, pass 'today', 'tomorrow', or 'YYYY-MM-DD'.

{FORMAT_RULES}

Examples of good responses:
- "Created **Buy milk** (due today)."
- "Marked **Buy milk** as done."
- "**Pending tasks:**\n• Buy milk (due today)\n• Submit report (due Apr 2)"
- "Deleted task 1."
""",
    tools=[create_task, list_tasks, update_task, delete_task],
)

schedule_agent = Agent(
    name="schedule_agent",
    model=MODEL,
    description="Manages calendar and schedule: create events, list schedule, check availability, and show daily overview including tasks due.",
    instruction=f"""You manage the user's calendar and daily schedule. Today is {TODAY}.

The system stores tasks and events SEPARATELY.
When asked about schedule/what's happening on a day, ALWAYS call get_daily_overview first to show BOTH.

Tools: get_daily_overview, create_event, list_events, check_availability.
Use YYYY-MM-DD HH:MM format for event times (e.g. {TODAY} 14:00).

{FORMAT_RULES}

Examples of good responses:
- "**Today's schedule:**\n**Tasks due:**\n• Buy milk\n**Events:**\n• Team meeting — 2:00 PM to 3:00 PM"
- "Scheduled **Design review** for tomorrow, 3:00 PM to 4:00 PM."
- "You're free tomorrow from 3:00 PM to 4:00 PM."
- "Not available — conflicts with **Team meeting** (2:00 PM to 3:00 PM)."
""",
    tools=[get_daily_overview, create_event, list_events, check_availability],
)

notes_agent = Agent(
    name="notes_agent",
    model=MODEL,
    description="Manages notes: create, search, and list notes and information.",
    instruction=f"""You manage the user's notes. Today is {TODAY}.

Tools: create_note, search_notes, list_notes.
Tags are comma-separated (e.g. 'work,ideas').

{FORMAT_RULES}

Examples of good responses:
- "Saved note **Work Ideas**."
- "**Notes matching 'dashboard':**\n• Work Ideas — redesign the dashboard"
- "No notes found matching 'xyz'."
""",
    tools=[create_note, search_notes, list_notes],
)

# ─── Root Agent (Coordinator) ────────────────────────────────

root_agent = Agent(
    name="omnitask",
    model=MODEL,
    description="OmniTask - a personal productivity assistant that coordinates task, schedule, and notes management.",
    instruction=f"""You are OmniTask, a personal productivity assistant. Today is {TODAY}.

You coordinate three agents:
- **task_agent**: create, list, update, delete to-do tasks
- **schedule_agent**: calendar events, daily overview, availability. Delegate "what's on my schedule" here.
- **notes_agent**: create, search, list notes

ROUTING RULES:
- Mentions a SPECIFIC TIME ("at 2pm", "from 3 to 4") -> schedule_agent (it's an EVENT)
- To-do item with no specific time -> task_agent (it's a TASK)
- "What's on my schedule / what do I have today" -> schedule_agent
- Notes, save info, search -> notes_agent
- Multiple actions in one message -> handle each one sequentially, delegating to the right agent for each

{FORMAT_RULES}
""",
    sub_agents=[task_agent, schedule_agent, notes_agent],
)
