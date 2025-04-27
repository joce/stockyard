"""Main entry point for the application."""

import argparse
from pathlib import Path

from appui import StockyardApp
from expui import ExpUI

parser = argparse.ArgumentParser(description="Stockyard Application")
parser.add_argument("-e", "--exp", action="store_true", help="Use experimental UI")
args = parser.parse_args()

home_dir: Path = Path("~").expanduser()
config_file_name: str = (home_dir / ".stockyard").as_posix()

if args.exp:
    exp_app: ExpUI = ExpUI()
    exp_app.run()
else:
    app: StockyardApp = StockyardApp()
    app.load_config(config_file_name)
    app.run()
    app.save_config(config_file_name)
