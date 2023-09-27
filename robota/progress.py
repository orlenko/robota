
import functools

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn


def with_progress(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with Progress(
            SpinnerColumn(),
            TimeElapsedColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task('processing', total=100)
            try:
                fn(progress, task)
            finally:
                progress.update(task, advance=100)

    return wrapper
