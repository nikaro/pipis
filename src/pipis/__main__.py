#!/usr/bin/env python3

import argparse

from pipis.utils import Pipis


def main():
    parser = argparse.ArgumentParser(prog="pipis", description=Pipis.__doc__)
    subparsers = parser.add_subparsers(title="available commands", dest="command")
    commands = Pipis()

    # globals arguments
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose ouput"
    )

    # version command and arguments
    parser_version = subparsers.add_parser(
        "version", help=commands.show_version.__doc__
    )
    parser_version.set_defaults(func=commands.show_version)

    # freeze command and arguments
    parser_freeze = subparsers.add_parser("freeze", help=commands.freeze.__doc__)
    parser_freeze.set_defaults(func=commands.freeze)

    # search command and arguments
    parser_search = subparsers.add_parser("search", help=commands.search.__doc__)
    parser_search.add_argument("query", help="query name", action="store", type=str)
    parser_search.set_defaults(func=commands.search)

    # install command and arguments
    parser_install = subparsers.add_parser("install", help=commands.install.__doc__)
    parser_install.add_argument(
        "package", help="package name", action="store", type=str
    )
    parser_install.add_argument(
        "-y", "--yes", action="store_true", help="do not prompt for confirmation"
    )
    parser_install.add_argument(
        "-d",
        "--dependency",
        help="add the specified package as dependency of the main package",
        metavar="package",
        action="store",
        type=str,
    )
    parser_install.add_argument(
        "-s",
        "--system",
        help="give the virtual environment access to the system site-packages dir",
        action="store_true",
    )
    parser_install.add_argument(
        "-U",
        "--upgrade",
        help="upgrade package to the newest available version",
        action="store_true",
    )
    parser_install.add_argument(
        "-I",
        "--ignore-installed",
        help="ignore the installed packages (reinstalling instead)",
        action="store_true",
    )
    parser_install.set_defaults(func=commands.install)

    # update command and arguments
    parser_update = subparsers.add_parser("update", help=commands.update.__doc__)
    parser_update.add_argument("package", help="package name", action="store", type=str)
    parser_update.add_argument(
        "-y", "--yes", action="store_true", help="do not prompt for confirmation"
    )
    parser_update.set_defaults(func=commands.update)

    # uninstall command and arguments
    parser_uninstall = subparsers.add_parser(
        "uninstall", help=commands.uninstall.__doc__
    )
    parser_uninstall.add_argument(
        "package", help="package name", action="store", type=str
    )
    parser_uninstall.add_argument(
        "-y", "--yes", action="store_true", help="do not prompt for confirmation"
    )
    parser_uninstall.set_defaults(func=commands.uninstall)

    # parse and run
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
