"""Gerenciador de tarefas para terminal."""

from .manager import TaskManager
from .models import Task

__all__ = ["Task", "TaskManager"]
__version__ = "1.0.0"

