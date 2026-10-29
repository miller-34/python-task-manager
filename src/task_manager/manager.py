"""Regras de negócio e persistência das tarefas."""

from __future__ import annotations

import json
from pathlib import Path

from .models import PRIORITIES, Task


class StorageError(RuntimeError):
    """Indica que o arquivo de dados não pôde ser lido ou salvo."""


class TaskNotFoundError(LookupError):
    """Indica que uma tarefa não existe."""


class TaskManager:
    """Gerencia tarefas armazenadas em um arquivo JSON local."""

    def __init__(self, data_file: str | Path = ".tasks.json") -> None:
        self.data_file = Path(data_file)

    def _load(self) -> list[Task]:
        if not self.data_file.exists():
            return []

        try:
            content = self.data_file.read_text(encoding="utf-8")
            if not content.strip():
                return []
            raw_tasks = json.loads(content)
            if not isinstance(raw_tasks, list):
                raise ValueError("o conteúdo principal deve ser uma lista")
            return [Task.from_dict(item) for item in raw_tasks]
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Não foi possível ler '{self.data_file}': {exc}"
            ) from exc

    def _save(self, tasks: list[Task]) -> None:
        temporary_file = self.data_file.with_suffix(self.data_file.suffix + ".tmp")
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            payload = [task.to_dict() for task in tasks]
            temporary_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_file.replace(self.data_file)
        except OSError as exc:
            raise StorageError(
                f"Não foi possível salvar '{self.data_file}': {exc}"
            ) from exc

    def add(
        self,
        title: str,
        description: str = "",
        priority: str = "media",
        due_date: str | None = None,
    ) -> Task:
        """Cria e salva uma nova tarefa."""
        tasks = self._load()
        next_id = max((task.id for task in tasks), default=0) + 1
        task = Task(
            id=next_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
        )
        tasks.append(task)
        self._save(tasks)
        return task

    def list_tasks(
        self,
        status: str = "all",
        priority: str | None = None,
        search: str | None = None,
    ) -> list[Task]:
        """Lista tarefas e aplica filtros opcionais."""
        if status not in {"all", "pending", "done"}:
            raise ValueError(f"Status inválido: {status}")
        if priority is not None and priority not in PRIORITIES:
            raise ValueError(f"Prioridade inválida: {priority}")

        tasks = self._load()
        if status != "all":
            expected_completed = status == "done"
            tasks = [task for task in tasks if task.completed == expected_completed]
        if priority:
            tasks = [task for task in tasks if task.priority == priority]
        if search:
            term = search.casefold()
            tasks = [
                task
                for task in tasks
                if term in task.title.casefold()
                or term in task.description.casefold()
            ]

        priority_order = {"alta": 0, "media": 1, "baixa": 2}
        return sorted(
            tasks,
            key=lambda task: (
                task.completed,
                priority_order[task.priority],
                task.due_date or "9999-12-31",
                task.id,
            ),
        )

    def complete(self, task_id: int) -> Task:
        """Marca uma tarefa como concluída."""
        tasks = self._load()
        task = self._find(tasks, task_id)
        task.completed = True
        self._save(tasks)
        return task

    def remove(self, task_id: int) -> Task:
        """Exclui uma tarefa."""
        tasks = self._load()
        task = self._find(tasks, task_id)
        tasks.remove(task)
        self._save(tasks)
        return task

    def stats(self) -> dict[str, int]:
        """Retorna contadores gerais das tarefas."""
        tasks = self._load()
        completed = sum(task.completed for task in tasks)
        return {
            "total": len(tasks),
            "pending": len(tasks) - completed,
            "completed": completed,
        }

    @staticmethod
    def _find(tasks: list[Task], task_id: int) -> Task:
        for task in tasks:
            if task.id == task_id:
                return task
        raise TaskNotFoundError(f"Tarefa #{task_id} não encontrada.")
