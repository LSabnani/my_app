"""Explainer Application Launcher
Starts FastAPI backend server and serves the Interactive Web GUI.
"""
import sys
import argparse
import webbrowser
import threading
import time
import uvicorn
from rich.console import Console
from rich.panel import Panel

console = Console()


def open_browser(port: int = 8000, host: str = "127.0.0.1"):
    """Wait for server to boot, then open default web browser."""
    time.sleep(1.2)
    url = f"http://{host}:{port}"
    console.print(f"[bold cyan]Opening Explainer GUI at:[/] [underline green]{url}[/]")
    webbrowser.open(url)


def main():
    parser = argparse.ArgumentParser(description="Explainer Application Launcher")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind server (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind server (default: 127.0.0.1)")
    args = parser.parse_args()

    banner_text = (
        "[bold white]EXPLAINER: PPT & Video Knowledge System[/]\n"
        "[dim]Multi-Agent Search (Greeter • Researcher • Evaluator)[/]\n"
        "[yellow]CLEATS Evaluation Rubric (C • L • E • A • T • S)[/]\n"
        "[bold gold1]★ Best Known Method (BKM) Triangulation Engine[/]"
    )
    console.print(Panel(banner_text, border_style="bright_blue", expand=False))

    # Launch browser thread
    threading.Thread(target=open_browser, args=(args.port, args.host), daemon=True).start()

    # Start FastAPI / Uvicorn server
    uvicorn.run(
        "backend.app:app",
        host=args.host,
        port=args.port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
