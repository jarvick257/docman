import argparse

from docman import Document
import docman.cli
import docman.utils


def main():
    commands = [key for key in docman.cli.__dict__.keys() if not key.startswith("__")]
    default_config_path = docman.utils.get_config_path()

    parser = argparse.ArgumentParser("docman")
    parser.add_argument(
        "--config",
        metavar="PATH",
        default=default_config_path,
        help="Overwrite default config path. DEFAULT: %(default)s",
    )
    parser.set_defaults(function=docman.cli.default_action)
    # Build sub parser
    command_parser = parser.add_subparsers(title="command", help="available commands")
    for cmd in commands:
        if cmd == "default_action":
            continue
        getattr(docman.cli, cmd)(command_parser)
    args = parser.parse_args()
    docman.utils.set_config_path(args.config)
    doc = Document.load()
    doc, retval = args.function(doc, args)

    if doc is not None:
        doc.save()
        doc.cleanup()

    exit(retval)


if __name__ == "__main__":
    main()
