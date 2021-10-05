import argparse

from docman import Document
import docman.cli
import docman.utils


def main():
    default_config_path = docman.utils.get_config_path()

    parser = argparse.ArgumentParser("docman")
    parser.add_argument(
        "--config",
        metavar="PATH",
        default=default_config_path,
        help="Overwrite default config path. DEFAULT: %(default)s",
    )
    parser.set_defaults(function=docman.cli.DEFAULT.run)
    # Build sub parser
    command_parser = parser.add_subparsers(title="command", help="available commands")
    for cmd in docman.cli.COMMANDS:
        cmd.add_parser(command_parser)
    args = parser.parse_args()
    docman.utils.set_config_path(args.config)
    doc = Document.load()
    retval = args.function(doc, **vars(args))
    exit(retval)


if __name__ == "__main__":
    main()
