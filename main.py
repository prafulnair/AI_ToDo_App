from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

from services import TaskService
from utils import parse_command

svc = TaskService()
# svc.load()  # load tasks.json if present

console = Console()
console.print("[bold green]Smart Todo (Gemini) — CLI[/]  type 'help'")

def print_tasks(tasks):
    if not tasks:
        console.print("[dim]No tasks[/]")
        return
    table = Table(show_lines=False)
    for col in ("id","category","priority","due","status","text"):
        table.add_column(col)
    for t in tasks:
        due = t.due_dt.isoformat() if t.due_dt else "-"
        table.add_row(str(t.id), t.category, str(t.priority), due, t.status, t.text)
    console.print(table)

while True:
    try:
        cmd, arg = parse_command(console.input("[bold cyan]todo>[/] ").strip())
        if cmd == "exit":
            # svc.save()
            console.print("[dim]Saved. Bye![/]")
            break
        elif cmd == "help":
            console.print("Commands: add <text> | show all | show <category> | show immediate | done <id> | delete <id> | exit")
        elif cmd == "show_all":
            print_tasks(svc.list_tasks())
        elif cmd == "show_category":
            print_tasks(svc.list_tasks(category=arg))
        elif cmd == "show_immediate":
            from datetime import datetime, timedelta
            cutoff = datetime.now() + timedelta(hours=24)
            print_tasks(svc.list_immediate(cutoff))
        elif cmd == "done":
            ok = svc.mark_done(arg)
            console.print("Marked done." if ok else "[red]Not found or already done[/]")
            # svc.save()
        elif cmd == "delete":
            ok = svc.delete(arg)
            console.print("Deleted." if ok else "[red]Not found[/]")
            # svc.save()
        elif cmd == "add":
            task = svc.add_task(arg)
            console.print(f"Added [bold]{task.text}[/] → {task.category} (p{task.priority})")
            # svc.save()
        else:
            pass
    except KeyboardInterrupt:
        # svc.save()
        console.print("\n[dim]Saved. Bye![/]")
        break
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")