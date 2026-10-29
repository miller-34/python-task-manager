import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from task_manager.cli import main


class CliTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.data_file = str(Path(self.temp_dir.name) / "tasks.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, *arguments):
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["--data-file", self.data_file, *arguments])
        return exit_code, output.getvalue()

    def test_cli_workflow(self):
        exit_code, output = self.run_cli(
            "add", "Publicar no GitHub", "--priority", "alta"
        )
        self.assertEqual(exit_code, 0)
        self.assertIn("Tarefa #1 adicionada", output)

        exit_code, output = self.run_cli("list")
        self.assertEqual(exit_code, 0)
        self.assertIn("Publicar no GitHub", output)
        self.assertIn("alta", output)

        exit_code, output = self.run_cli("done", "1")
        self.assertEqual(exit_code, 0)
        self.assertIn("concluída", output)

    def test_cli_returns_error_for_unknown_task(self):
        exit_code, output = self.run_cli("remove", "404")

        self.assertEqual(exit_code, 1)
        self.assertIn("não encontrada", output)


if __name__ == "__main__":
    unittest.main()
