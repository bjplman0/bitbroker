import json
import os
from settings import SAVE_FILE_PATH
from model import EconomyModel

class SaveRepository:

    def __init__(self, filepath=SAVE_FILE_PATH):
        self.filepath = filepath

    def exists(self):
        if not os.path.isfile(self.filepath):
            return False
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return isinstance(data, dict) and "balance" in data
        except (OSError, json.JSONDecodeError, ValueError):
            return False

    def save(self, economy):
        try:
            data = economy.to_dict()
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except OSError as e:
            print(f"Failed to save game: {e}")
            return False

    def load(self):
        if not os.path.isfile(self.filepath):
            return None
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return EconomyModel.from_dict(data)
        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as e:
            print(f"Save file is missing or corrupted: {e}")
            return None

    def delete(self):
        if os.path.isfile(self.filepath):
            try:
                os.remove(self.filepath)
            except OSError as e:
                print(f"Failed to delete save file: {e}")