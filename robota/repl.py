from rich.console import Console

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
    evaluators = {
        "list": evaluate_list,
        "l": evaluate_list,
        "quit": evaluate_quit,
        "q": evaluate_quit,
    }
    evaluators.get(ast[0], evaluate_unknown)(console, ast)


def evaluate_quit(console, ast):
    raise EOFError()


def evaluate_unknown(console, ast):
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
