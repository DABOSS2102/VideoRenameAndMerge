import os

class UserPreferences:
    APP_SUBFOLDER = "VideoRenameAndMerge"
    FILENAME = "preferences.txt"

    @staticmethod
    def get_store_path():
        appdata = os.environ.get("LOCALAPPDATA")
        if not appdata:
            raise EnvironmentError("LOCALAPPDATA not found.")
        folder = os.path.join(appdata, UserPreferences.APP_SUBFOLDER)
        os.makedirs(folder, exist_ok=True)
        return os.path.join(folder, UserPreferences.FILENAME)

    @staticmethod
    def save_last_folder(path: str):
        store_path = UserPreferences.get_store_path()
        lines = []
        if os.path.exists(store_path):
            with open(store_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        # ensure list has at least 3 lines (folder, base_name, concatenated_name)
        while len(lines) < 3:
            lines.append("\n")
        lines[0] = path + "\n"
        with open(store_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    @staticmethod
    def load_last_folder() -> str | None:
        store_path = UserPreferences.get_store_path()
        if os.path.exists(store_path):
            with open(store_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) >= 1:
                    return lines[0].strip()
        return None

    @staticmethod
    def save_last_base_name(base_name: str):
        store_path = UserPreferences.get_store_path()
        lines = []
        if os.path.exists(store_path):
            with open(store_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        # ensure list has at least 3 lines
        while len(lines) < 3:
            lines.append("\n")
        lines[1] = base_name + "\n"
        with open(store_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    @staticmethod
    def load_last_base_name() -> str | None:
        store_path = UserPreferences.get_store_path()
        if os.path.exists(store_path):
            with open(store_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) >= 2:
                    return lines[1].strip()
        return None

    @staticmethod
    def save_last_concatenated_name(concatenated_name: str):
        store_path = UserPreferences.get_store_path()
        lines = []
        if os.path.exists(store_path):
            with open(store_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        # ensure list has at least 3 lines
        while len(lines) < 3:
            lines.append("\n")
        lines[2] = concatenated_name + "\n"
        with open(store_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    @staticmethod
    def load_last_concatenated_name() -> str | None:
        store_path = UserPreferences.get_store_path()
        if os.path.exists(store_path):
            with open(store_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) >= 3:
                    return lines[2].strip()
        return None