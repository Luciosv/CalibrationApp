from utils.json_manager import JsonManager


class ReferenceManager:

    def __init__(self):
        self.reference_config = None

    def load_reference(self, path: str):
        self.reference_config = JsonManager.load_config(
            path
        )

    def get_reference_config(self):
        return self.reference_config   