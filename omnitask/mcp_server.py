"""MCP Server exposing task, schedule, and notes tools via Model Context Protocol.
Run standalone: python -m omnitask.mcp_server"""

import json
import logging
import sys
import os

# Suppress FastMCP banner and logs that interfere with stdio JSON-RPC
logging.disable(logging.CRITICAL)

# Ensure parent directory is on path so imports work when run as subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from omnitask import tools

mcp = FastMCP(
    "OmniTask MCP Server",
    instructions="Tools for managing tasks, calendar events, and notes. All data is stored in a SQLite database.",
    log_level="CRITICAL",
)


# ─── Task Tools ───────────────────────────────────────────────


@mcp.tool()
def create_task(title: str, description: str = "", due_date: str = "") -> str:
    """Create a new task. due_date can be 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    return json.dumps(tools.create_task(title, description, due_date))


@mcp.tool()
def list_tasks(status_filter: str = "all") -> str:
    """List tasks. Use status_filter='pending', 'done', or 'all'."""
    return json.dumps(tools.list_tasks(status_filter))


@mcp.tool()
def update_task(task_id: int, title: str = "", status: str = "", due_date: str = "") -> str:
    """Update a task's title, status, or due_date. Set status to 'done' to mark complete."""
    return json.dumps(tools.update_task(task_id, title, status, due_date))


@mcp.tool()
def delete_task(task_id: int) -> str:
    """Delete a task by its ID."""
    return json.dumps(tools.delete_task(task_id))


# ─── Schedule Tools ───────────────────────────────────────────


@mcp.tool()
def create_event(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """Create a calendar event. Times must be in 'YYYY-MM-DD HH:MM' format."""
    return json.dumps(tools.create_event(title, start_time, end_time, description))


@mcp.tool()
def list_events(date: str = "") -> str:
    """List calendar events. Filter by 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    return json.dumps(tools.list_events(date))


@mcp.tool()
def check_availability(start_time: str, end_time: str) -> str:
    """Check if a time slot is free. Times in 'YYYY-MM-DD HH:MM' format."""
    return json.dumps(tools.check_availability(start_time, end_time))


# ─── Notes Tools ──────────────────────────────────────────────


@mcp.tool()
def create_note(title: str, content: str, tags: str = "") -> str:
    """Create a note. Tags are comma-separated (e.g. 'work,ideas')."""
    return json.dumps(tools.create_note(title, content, tags))


@mcp.tool()
def search_notes(query: str) -> str:
    """Search notes by title, content, or tags."""
    return json.dumps(tools.search_notes(query))


@mcp.tool()
def list_notes() -> str:
    """List all notes."""
    return json.dumps(tools.list_notes())


# ─── Overview Tool ────────────────────────────────────────────


@mcp.tool()
def get_daily_overview(date: str = "") -> str:
    """Get tasks due AND calendar events for a date. Use 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    return json.dumps(tools.get_daily_overview(date))


if __name__ == "__main__":
    mcp.run(transport="stdio")
