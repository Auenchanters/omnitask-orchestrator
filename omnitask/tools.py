"""Pure business logic for task, schedule, and notes management.
These functions are used by the MCP server -- no ADK dependencies here."""

from datetime import datetime, timedelta
from .db import get_connection


def _resolve_date(date_str: str) -> str:
    """Convert relative dates like 'today', 'tomorrow' to YYYY-MM-DD format."""
    lower = date_str.strip().lower()
    today = datetime.now()
    if lower in ("today", "now", ""):
        return today.strftime("%Y-%m-%d")
    if lower in ("tomorrow", "tmrw"):
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if lower == "yesterday":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    return date_str


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ─── Task Tools ───────────────────────────────────────────────


def create_task(title: str, description: str = "", due_date: str = "") -> dict:
    """Create a new task. due_date can be 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    try:
        resolved_date = _resolve_date(due_date) if due_date else ""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, due_date) VALUES (?, ?, ?)",
            (title, description, resolved_date),
        )
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return {"status": "success", "task_id": task_id, "title": title, "due_date": resolved_date}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_tasks(status_filter: str = "all") -> dict:
    """List tasks. Use status_filter='pending', 'done', or 'all'."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if status_filter == "all":
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        else:
            cursor.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC",
                (status_filter,),
            )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "tasks": rows, "count": len(rows)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_task(task_id: int, title: str = "", status: str = "", due_date: str = "") -> dict:
    """Update a task's title, status, or due_date. Set status to 'done' to mark complete."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
        if not cursor.fetchone():
            conn.close()
            return {"status": "error", "message": f"Task {task_id} not found"}
        if title:
            cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
        if status:
            cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        if due_date:
            resolved = _resolve_date(due_date)
            cursor.execute("UPDATE tasks SET due_date = ? WHERE id = ?", (resolved, task_id))
        conn.commit()
        conn.close()
        return {"status": "success", "task_id": task_id, "message": "Task updated"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_task(task_id: int) -> dict:
    """Delete a task by its ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        if deleted == 0:
            return {"status": "error", "message": f"Task {task_id} not found"}
        return {"status": "success", "message": f"Task {task_id} deleted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─── Schedule Tools ───────────────────────────────────────────


def create_event(title: str, start_time: str, end_time: str, description: str = "") -> dict:
    """Create a calendar event. Times must be in 'YYYY-MM-DD HH:MM' format."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (title, description, start_time, end_time) VALUES (?, ?, ?, ?)",
            (title, description, start_time, end_time),
        )
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return {"status": "success", "event_id": event_id, "title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_events(date: str = "") -> dict:
    """List calendar events. Filter by 'today', 'tomorrow', or 'YYYY-MM-DD'. Leave empty for all."""
    try:
        resolved = _resolve_date(date) if date else ""
        conn = get_connection()
        cursor = conn.cursor()
        if resolved:
            cursor.execute(
                "SELECT * FROM events WHERE start_time LIKE ? ORDER BY start_time",
                (f"{resolved}%",),
            )
        else:
            cursor.execute("SELECT * FROM events ORDER BY start_time")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "events": rows, "count": len(rows)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_availability(start_time: str, end_time: str) -> dict:
    """Check if a time slot is free. Times in 'YYYY-MM-DD HH:MM' format."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE start_time < ? AND end_time > ?",
            (end_time, start_time),
        )
        conflicts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        if conflicts:
            return {
                "status": "success",
                "available": False,
                "conflicts": conflicts,
                "message": f"Found {len(conflicts)} conflicting event(s)",
            }
        return {"status": "success", "available": True, "message": "The time slot is free"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─── Notes Tools ──────────────────────────────────────────────


def create_note(title: str, content: str, tags: str = "") -> dict:
    """Create a note. Tags are comma-separated (e.g. 'work,ideas')."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags),
        )
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()
        return {"status": "success", "note_id": note_id, "title": title}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def search_notes(query: str) -> dict:
    """Search notes by title, content, or tags."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        like = f"%{query}%"
        cursor.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY created_at DESC",
            (like, like, like),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "notes": rows, "count": len(rows)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_notes() -> dict:
    """List all notes."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"status": "success", "notes": rows, "count": len(rows)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ─── Overview Tool ────────────────────────────────────────────


def get_daily_overview(date: str = "") -> dict:
    """Get tasks due AND calendar events for a date. Use 'today', 'tomorrow', or 'YYYY-MM-DD'."""
    try:
        resolved = _resolve_date(date) if date else _today()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE due_date = ? ORDER BY created_at",
            (resolved,),
        )
        tasks = [dict(row) for row in cursor.fetchall()]
        cursor.execute(
            "SELECT * FROM events WHERE start_time LIKE ? ORDER BY start_time",
            (f"{resolved}%",),
        )
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {
            "status": "success",
            "date": resolved,
            "today": _today(),
            "tasks_due": tasks,
            "tasks_count": len(tasks),
            "events": events,
            "events_count": len(events),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
