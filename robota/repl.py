from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from .jira import get_my_issues

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
    evaluators = {
        "list": evaluate_list,
        "l": evaluate_list,
        "quit": evaluate_quit,
        "q": evaluate_quit,
    }
    evaluators.get(ast[0], evaluate_unknown)(ast)


def evaluate_list(ast):
    with Progress(
        SpinnerColumn(),
        TimeElapsedColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Loading issues", total=100)
        my_issues = get_my_issues()
        progress.update(task, advance=100)
    for issue in sorted(
        my_issues, key=lambda i: int(i.key.split("-")[1]), reverse=True
    ):
        console.print(
            f"[link={issue.permalink()}]{issue.key}[/link]: {issue.fields.summary}"
        )


def evaluate_quit(ast):
    raise EOFError()


def evaluate_unknown(ast):
    raise RobotaError(f"Unknown command {ast[0]}")


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
                print(result)
        except RobotaError as e:
            print(e)
        except Exception as e:
            print(e)
            break


if __name__ == "__main__":
    loop()
