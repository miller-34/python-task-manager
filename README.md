# Python Task Manager

Um gerenciador de tarefas simples para terminal, feito em Python e sem
dependências externas. O projeto salva os dados localmente em JSON e foi
organizado para servir como exemplo de portfólio no GitHub.

## Funcionalidades

- Adicionar tarefas com descrição, prioridade e prazo
- Listar e filtrar por status ou prioridade
- Buscar palavras no título e na descrição
- Marcar tarefas como concluídas
- Remover tarefas
- Exibir estatísticas
- Persistir os dados em um arquivo JSON

## Requisitos

- Python 3.10 ou superior

## Instalação

Clone o repositório e instale o projeto em modo editável:

```bash
git clone https://github.com/SEU-USUARIO/python-task-manager.git
cd python-task-manager
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
python3 -m pip install -e .
```

## Como usar

Adicione uma tarefa:

```bash
task-manager add "Estudar Python" --priority alta --due 2026-12-10
```

Liste as tarefas:

```bash
task-manager list
task-manager list --status pending
task-manager list --priority alta
task-manager list --search python
```

Conclua ou remova uma tarefa usando o ID:

```bash
task-manager done 1
task-manager remove 1
```

Veja um resumo:

```bash
task-manager stats
```

Também é possível executar sem instalar o comando:

```bash
PYTHONPATH=src python3 -m task_manager list
```

## Testes

Execute a suíte (não é necessário instalar dependências):

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

O GitHub Actions executa os testes automaticamente a cada `push` e pull
request.

## Estrutura

```text
src/task_manager/
├── cli.py       # comandos do terminal
├── manager.py   # regras de negócio e persistência
└── models.py    # modelo de tarefa
tests/           # testes automatizados
```

## Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE).
