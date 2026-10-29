"""Interface de linha de comando do projeto."""

from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
from typing import Sequence

from .manager import StorageError, TaskManager, TaskNotFoundError
from .models import PRIORITIES, Task


def valid_date(value: str) -> str:
    """Valida uma data no formato aceito pela aplicação."""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "use uma data válida no formato AAAA-MM-DD"
        ) from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task-manager",
        description="Gerencie suas tarefas diretamente pelo terminal.",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path(os.getenv("TASK_MANAGER_DB", ".tasks.json")),
        help=argparse.SUPPRESS,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="adiciona uma tarefa")
    add_parser.add_argument("title", help="título da tarefa")
    add_parser.add_argument("-d", "--description", default="", help="descrição")
    add_parser.add_argument(
        "-p",
        "--priority",
        choices=PRIORITIES,
        default="media",
        help="prioridade (padrão: media)",
    )
    add_parser.add_argument(
        "--due", type=valid_date, metavar="DATA", help="prazo em AAAA-MM-DD"
    )

    list_parser = subparsers.add_parser("list", help="lista as tarefas")
    list_parser.add_argument(
        "--status",
        choices=("all", "pending", "done"),
        default="all",
        help="filtra pelo status",
    )
    list_parser.add_argument("--priority", choices=PRIORITIES, help="filtra prioridade")
    list_parser.add_argument("--search", help="busca no título e na descrição")

    done_parser = subparsers.add_parser("done", help="conclui uma tarefa")
    done_parser.add_argument("id", type=int, help="identificador da tarefa")

    remove_parser = subparsers.add_parser("remove", help="remove uma tarefa")
    remove_parser.add_argument("id", type=int, help="identificador da tarefa")

    subparsers.add_parser("stats", help="exibe um resumo das tarefas")
    return parser


def _print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("Nenhuma tarefa encontrada.")
        return

    print(f"{'ID':<4} {'STATUS':<8} {'PRIORIDADE':<10} {'PRAZO':<12} TÍTULO")
    print("-" * 64)
    for task in tasks:
        status = "feita" if task.completed else "pendente"
        due_date = task.due_date or "-"
        print(
            f"{task.id:<4} {status:<8} {task.priority:<10} "
            f"{due_date:<12} {task.title}"
        )
        if task.description:
            print(f"     {task.description}")


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a aplicação e retorna um código de saída."""
    args = build_parser().parse_args(argv)
    manager = TaskManager(args.data_file)

    try:
        if args.command == "add":
            task = manager.add(
                args.title, args.description, args.priority, args.due
            )
            print(f"Tarefa #{task.id} adicionada: {task.title}")
        elif args.command == "list":
            _print_tasks(
                manager.list_tasks(args.status, args.priority, args.search)
            )
        elif args.command == "done":
            task = manager.complete(args.id)
            print(f"Tarefa #{task.id} concluída: {task.title}")
        elif args.command == "remove":
            task = manager.remove(args.id)
            print(f"Tarefa #{task.id} removida: {task.title}")
        elif args.command == "stats":
            stats = manager.stats()
            print(f"Total: {stats['total']}")
            print(f"Pendentes: {stats['pending']}")
            print(f"Concluídas: {stats['completed']}")
    except (StorageError, TaskNotFoundError, ValueError) as exc:
        print(f"Erro: {exc}")
        return 1

    return 0

