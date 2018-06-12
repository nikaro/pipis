"""
'pipis' stands for 'pip isolated'
"""

from .cli import cli, show_version, list_installed, freeze, install, update, uninstall

__all__ = [
    "cli",
    "show_version",
    "list_installed",
    "freeze",
    "install",
    "update",
    "uninstall",
]

if __name__ == "__main__":
    cli()
