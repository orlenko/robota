from collections import defaultdict
from rich.console import Console
from robota.repl_git import evaluate_workon

from robota.repl_jira import evaluate_list

console = Console()


class RobotaError(Exception):
    pass


def tokenize(s):
    return s.split()


def parse(tokens):
    ast = []
    current_token_parts = []

    def add_token():
        if current_token_parts:
            ast.extend(current_token_parts)
        current_token_parts.clear()

    for token in tokens:
        if token.startswith('"') and not token.endswith('"'):
            current_token_parts.append(token.lstrip('"'))
        elif token.endswith('"'):
            current_token_parts.append(token.rstrip('"'))
            add_token()
        else:
            current_token_parts.append(token)
            add_token()
    add_token()
    return ast


def evaluate(ast):
    evaluators.get(ast[0], evaluate_unknown)(console, ast)


def evaluate_quit(console, ast):
    """Quit the program"""
    raise EOFError()


def evaluate_unknown(console, ast):
    raise RobotaError(f"Unknown command {ast[0]}")


def evaluate_help(console, ast):
    """Display this help message"""
    console.print("Available commands:")
    grouped_evaluators = defaultdict(list)
    for name, fn in evaluators.items():
        grouped_evaluators[fn].append(name)
    for fn, names in grouped_evaluators.items():
        console.print(f"  {', '.join(names)}: {evaluators[names[0]].__doc__}")


evaluators = {
    "list": evaluate_list,
    "l": evaluate_list,

    "workon": evaluate_workon,
    "w": evaluate_workon,

    "quit": evaluate_quit,
    "q": evaluate_quit,

    "help": evaluate_help,
    "h": evaluate_help,
    "?": evaluate_help,
}


def loop():
    while True:
        try:
            s = console.input("[green]robota> ")
        except EOFError:
            break
        if not s:
            continue
        try:
            tokens = tokenize(s)
            ast = parse(tokens)
            result = evaluate(ast)
            if result is not None:
                console.print(result)
        except RobotaError as e:
            console.print(e)
        except EOFError:
            console.print("Bye!")
            break
        except Exception as e:
            console.print_exception(show_locals=True)
            break


if __name__ == "__main__":
    loop()
