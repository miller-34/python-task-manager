import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from task_manager.manager import StorageError, TaskManager, TaskNotFoundError


class TaskManagerTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "tasks.json"
        self.manager = TaskManager(self.data_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_list_tasks(self):
        first = self.manager.add("Estudar Python", priority="alta")
        second = self.manager.add("Atualizar README", priority="baixa")

        tasks = self.manager.list_tasks()

        self.assertEqual(first.id, 1)
        self.assertEqual(second.id, 2)
        self.assertEqual(
            [task.title for task in tasks],
            ["Estudar Python", "Atualizar README"],
        )

    def test_complete_task_and_stats(self):
        task = self.manager.add("Criar testes")

        completed = self.manager.complete(task.id)

        self.assertTrue(completed.completed)
        self.assertEqual(
            self.manager.stats(),
            {"total": 1, "pending": 0, "completed": 1},
        )

    def test_filter_and_search_tasks(self):
        self.manager.add("Comprar café", "Ir ao mercado", priority="alta")
        self.manager.add("Ler livro", priority="baixa")

        self.assertEqual(len(self.manager.list_tasks(priority="alta")), 1)
        self.assertEqual(
            self.manager.list_tasks(search="mercado")[0].title,
            "Comprar café",
        )

    def test_remove_task(self):
        task = self.manager.add("Tarefa temporária")

        removed = self.manager.remove(task.id)

        self.assertEqual(removed.title, "Tarefa temporária")
        self.assertEqual(self.manager.list_tasks(), [])

    def test_unknown_task_raises_error(self):
        with self.assertRaises(TaskNotFoundError):
            self.manager.complete(99)

    def test_invalid_json_raises_friendly_error(self):
        self.data_file.write_text("not json", encoding="utf-8")

        with self.assertRaises(StorageError):
            self.manager.list_tasks()

    def test_empty_file_is_accepted(self):
        self.data_file.touch()

        self.assertEqual(self.manager.list_tasks(), [])

    def test_data_is_saved_as_readable_json(self):
        self.manager.add("Documentar projeto", due_date="2026-12-10")

        saved = json.loads(self.data_file.read_text(encoding="utf-8"))

        self.assertEqual(saved[0]["title"], "Documentar projeto")
        self.assertEqual(saved[0]["due_date"], "2026-12-10")


if __name__ == "__main__":
    unittest.main()
