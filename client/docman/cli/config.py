from docman.utils import get_config_path


def config(subparser):
    parser = subparser.add_parser(
        "config",
        description="Opens docman config in editor (uses $EDITOR environment variable).",
    )
    parser.set_defaults(function=_run)


def _run(doc, args):
    import os

    if "EDITOR" in os.environ:
        editor = os.environ["EDITOR"]
    else:
        print("EDITOR environment variable not set. Falling back to vi.")
        editor = "vi"
    os.system(f"{editor} {get_config_path()}")
    return None, 0
