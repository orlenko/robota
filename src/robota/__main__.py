"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Robota."""


if __name__ == "__main__":
    main(prog_name="robota")  # pragma: no cover
