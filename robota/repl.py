from collections import defaultdict

from rich.console import Console

from .repl_github import evaluate_org, evaluate_prs, evaluate_workon
from .repl_jira import evaluate_list

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
    "l": evaluate_list,
    "w": evaluate_workon,
    "o": evaluate_org,
    "p": evaluate_prs,
    "q": evaluate_quit,
    "h": evaluate_help,
}


def loop():
    while True:
        try:
            s = console.input(f"[green]robota ({'/'.join(evaluators.keys())}) > ")
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
