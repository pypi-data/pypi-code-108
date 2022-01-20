import builtins
import functools

from segno import QRCode


def check_is_notebook() -> bool:
    """Checks if the current environment is a Python notebook."""
    return hasattr(builtins, "__IPYTHON__")


def only_notebook(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if IS_NOTEBOOK:
            return func(*args, **kwargs)
        else:
            raise RuntimeError(
                "Attempting to run notebook utility in a non-notebook environment. "
                "If you are not in a notebook environment, this is a bug - let us know how you ran into it!"
            )

    return wrapper


@only_notebook
def show_qr(qr: QRCode):
    """Generates and displays a QR code."""
    from IPython.display import display, SVG
    return display(SVG(
        qr.svg_inline(scale=10, light="#fff")
    ))


@only_notebook
def register_write_and_run():
    from IPython.core.magic import register_cell_magic

    @register_cell_magic
    def write_and_run(line, cell):
        """Saves the contents of the cell to a file and reloads the class.

        Call with
            %%write_and_run directory file_name class_name
        E.g.
          %%write_and_run bot bot.py Bot
              will save the cell to bot/bot.py, and import the class Bot
        """
        from importlib import reload
        from pathlib import Path

        directory, file_name, class_name = line.split()
        file_path = Path(directory) / file_name
        file_path.parent.mkdir(exist_ok=True)

        print(f"Saving cell to {file_path} and reloading class {class_name}.")

        # Save cell to file
        with file_path.open('w') as f:
            f.write(cell)

        # Import and reload the bot class.
        exec(f"import {directory}.{file_path.stem}")
        eval(f"reload({directory}.{file_path.stem})")
        ipython = get_ipython()
        ipython.push({class_name: eval(f"{directory}.{file_path.stem}.{class_name}")})


IS_NOTEBOOK = check_is_notebook()


@only_notebook
def setup_notebook():
    try:
        import nest_asyncio
        nest_asyncio.apply()
        print("Set up nest_asyncio for TRoom.")
    except Exception:
        raise RuntimeError(
            "Error setting up nest_asyncio. If you are in a notebook, use `pip install chaipy[notebook]`. "
            "If not, this is a bug - let us know how you ran into it!"
        )

    try:
        register_write_and_run()
        print("Set up write_and_run magic.")
    except Exception:
        raise RuntimeError(
            "Error setting up write_and_run magic."
        )
