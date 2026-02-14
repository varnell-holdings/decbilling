"""Backup CSV files listed in backup_config.ini.

Creates dated copies in a backups/ subfolder next to each CSV.
Keeps at most 5 backups per file, deleting the oldest extras.
Safe to run multiple times per day — skips if today's backup exists.
"""

import configparser
import shutil
from datetime import date
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "backup_config.ini"
MAX_BACKUPS = 5


def get_csv_paths():
    """Read backup_config.ini and return a list of Path objects."""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    paths = []
    for key in config["files"]:
        raw_path = config["files"][key]
        # Resolve relative paths based on the config file's directory
        csv_path = (CONFIG_FILE.parent / raw_path).resolve()
        paths.append(csv_path)

    return paths


def backup_one_file(csv_path):
    """Back up a single CSV file. Returns a status message."""
    if not csv_path.exists():
        return f"WARNING: {csv_path} does not exist, skipping"

    backup_dir = csv_path.parent / "backups"
    backup_dir.mkdir(exist_ok=True)

    today = date.today().isoformat()  # YYYY-MM-DD
    stem = csv_path.stem  # e.g. "follow_up"
    backup_name = f"{stem}_{today}.csv"
    backup_path = backup_dir / backup_name

    if backup_path.exists():
        return f"Already backed up today: {backup_path.name}"

    shutil.copy2(csv_path, backup_path)
    message = f"Backed up: {backup_path.name}"

    # Clean up old backups — keep only the newest MAX_BACKUPS
    # Pattern matches e.g. follow_up_2026-02-14.csv
    existing = sorted(backup_dir.glob(f"{stem}_*.csv"))
    if len(existing) > MAX_BACKUPS:
        to_delete = existing[: len(existing) - MAX_BACKUPS]
        for old_backup in to_delete:
            old_backup.unlink()
            message += f"\n  Deleted old backup: {old_backup.name}"

    return message


def main():
    csv_paths = get_csv_paths()

    if not csv_paths:
        print("No files listed in backup_config.ini")
        return

    print(f"Backing up {len(csv_paths)} file(s)...\n")

    for csv_path in csv_paths:
        result = backup_one_file(csv_path)
        print(f"  {csv_path.name}")
        for line in result.split("\n"):
            print(f"    {line}")
        print()

    print("Done!")


if __name__ == "__main__":
    main()
