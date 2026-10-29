"""Modelos usados pelo gerenciador de tarefas."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


PRIORITIES = ("baixa", "media", "alta")


@dataclass(slots=True)
class Task:
    """Representa uma tarefa persistida no arquivo JSON."""

    id: int
    title: str
    description: str = ""
    priority: str = "media"
    due_date: str | None = None
    completed: bool = False
    created_at: str = ""

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.description = self.description.strip()

        if not self.title:
            raise ValueError("O título não pode estar vazio.")
        if self.priority not in PRIORITIES:
            raise ValueError(f"Prioridade inválida: {self.priority}")
        if not self.created_at:
            self.created_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        """Converte a tarefa para uma estrutura serializável."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        """Cria uma tarefa a partir dos dados armazenados."""
        return cls(**data)

