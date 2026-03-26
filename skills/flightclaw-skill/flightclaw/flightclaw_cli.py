#!/usr/bin/env python3
"""Flightclaw CLI — Stateful Click harness with REPL.

One-shot:
  flightclaw --json today
  flightclaw search --from BJS --to SHA --date 2026-04-01

Interactive REPL (default when no subcommand):
  flightclaw
"""

from __future__ import annotations

import json
import shlex
import sys
from typing import Any

import click

from flightclaw import __version__
from flightclaw.core.models import SearchQuery
from flightclaw.core.search import parse_date, today_payload
from flightclaw.core.session import get_session
from flightclaw.providers import PROVIDERS, get_provider

_json_output = False
_repl_mode = False


def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                click.echo(f"[{i}] {item}")
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0) -> None:
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    click.echo(f"{prefix}  [{i}]")
                    _print_dict(item, indent + 2)
                else:
                    click.echo(f"{prefix}  - {item}")
        else:
            click.echo(f"{prefix}{k}: {v}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "ValueError"}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Machine-readable JSON output")
@click.version_option(__version__, prog_name="flightclaw")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Flightclaw — flight search via pluggable crawlers (no MCP).

    Run with no subcommand to enter interactive REPL.
    """
    global _json_output
    _json_output = use_json

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl_cmd)


@cli.command("today")
@handle_error
def today_cmd() -> None:
    """Print today's date (YYYY-MM-DD)."""
    output(today_payload())


@cli.command("search")
@click.option("--from", "origin", required=True, help="Origin IATA/city code")
@click.option("--to", "destination", required=True, help="Destination IATA/city code")
@click.option("--date", "flight_date", required=True, help="YYYY-MM-DD")
@click.option("--provider", default="example", show_default=True, help="Provider name")
@handle_error
def search_cmd(origin: str, destination: str, flight_date: str, provider: str) -> None:
    """Run search via provider; updates session last result."""
    d = parse_date(flight_date)
    p = get_provider(provider)
    result = p.search(origin, destination, d)
    sess = get_session()
    q = SearchQuery(origin=origin.upper(), destination=destination.upper(), date=d)
    sess.set_last_search(q, result)
    output(result.to_json_dict())


@cli.command("providers")
@handle_error
def providers_cmd() -> None:
    """List registered provider names."""
    output({"providers": sorted(PROVIDERS.keys())})


@cli.command("session")
@handle_error
def session_cmd() -> None:
    """Show last search query/result if any."""
    sess = get_session()
    output(
        {
            "last_query": sess.last_query.model_dump() if sess.last_query else None,
            "last_result": sess.last_result,
        }
    )


@cli.command("repl")
@handle_error
def repl_cmd() -> None:
    """Interactive REPL (same as running with no arguments)."""
    global _repl_mode
    _repl_mode = True

    click.echo(
        f"Flightclaw REPL — type 'help', 'exit', or shell-style commands "
        f"(e.g. search --from BJS --to SHA --date 2026-04-01). v{__version__}"
    )
    _repl_commands = {
        "today": "today",
        "search": "--from --to --date [--provider]",
        "providers": "list registered providers",
        "session": "last query/result",
        "help": "this help",
        "exit / quit / q": "leave REPL",
    }

    while True:
        try:
            line = input("flightclaw> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("")
            break
        if not line:
            continue
        low = line.lower()
        if low in ("exit", "quit", "q"):
            break
        if low == "help":
            click.echo(json.dumps(_repl_commands, indent=2, ensure_ascii=False))
            continue
        try:
            args = shlex.split(line)
        except ValueError as e:
            click.echo(f"parse error: {e}", err=True)
            continue
        try:
            cli.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            click.echo(f"Usage: {e}", err=True)
        except Exception as e:
            click.echo(f"{e}", err=True)

    _repl_mode = False


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
