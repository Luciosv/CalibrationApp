from models.simulation_config import (
    SimulationConfig,
)

from utils.json_manager import JsonManager


class ReferenceManager:

    def __init__(self):
        self.reference_config: SimulationConfig | None = None

    def load_reference(self, path: str):
        self.reference_config = JsonManager.load_config(
            path,
            disable_missing=True,
        )

    def sync_from_config(
        self,
        editing_config: SimulationConfig,
    ) -> None:

        if self.reference_config is None:
            return

        for ref_tissue in self.reference_config.tissues:

            edit_tissue = editing_config.get_tissue(
                ref_tissue.name
            )

            if edit_tissue is None:
                continue

            ref_tissue.enabled = edit_tissue.enabled
            ref_tissue.thickness = edit_tissue.thickness

        self.reference_config.update_depths()

    def get_reference_config(self):
        return self.reference_config   