"""
Carga y guardado de configuraciones JSON.
"""

import csv
import json

from config.formulas import FORMULAS

from models.parameter import Parameter
from models.simulation_config import (
    SimulationConfig,
)


class JsonManager:

    @staticmethod
    def export_for_unity(
        config: SimulationConfig,
    ) -> dict:

        data = {}

        for tissue in config.tissues:

            data[tissue.name] = {
                "family": tissue.family,
                "params": tissue.parameter_values,
                "z_width_mm": tissue.thickness,
            }

        return data

    @staticmethod
    def save_json(
        config: SimulationConfig,
        path: str,
    ) -> None:

        data = JsonManager.export_for_unity(
            config
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
            )

    @staticmethod
    def save_csv(
        config: SimulationConfig,
        path: str,
    ) -> None:

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow(
                ["tissue", "family", "parameter", "value"]
            )

            for tissue in config.tissues:

                for p in tissue.parameters:

                    writer.writerow(
                        [
                            tissue.name,
                            tissue.family,
                            p.name,
                            p.value,
                        ]
                    )

    @staticmethod
    def load_json(
        path: str,
        config: SimulationConfig,
        disable_missing: bool = False,
    ) -> None:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        found_tissues: set[str] = set()

        for tissue_name, tissue_data in data.items():

            tissue = config.get_tissue(
                tissue_name
            )

            if tissue is None:
                continue

            found_tissues.add(tissue_name)

            family = tissue_data["family"]

            tissue.family = family

            if "z_width_mm" in tissue_data:
                tissue.thickness = tissue_data["z_width_mm"]

            param_names = (
                FORMULAS[family]
                .parameter_names
            )

            param_values = (
                tissue_data["params"]
            )

            tissue.parameters = [
                Parameter(
                    name=name,
                    value=value,
                )
                for name, value in zip(
                    param_names,
                    param_values,
                )
            ]

        if disable_missing:

            for tissue in config.tissues:

                if (
                    tissue.name
                    not in found_tissues
                ):

                    tissue.enabled = False

        config.update_depths()
    
    @staticmethod
    def load_config(
        path: str,
        disable_missing: bool = False,
    ) -> SimulationConfig:
        config = SimulationConfig()

        JsonManager.load_json(
            path,
            config,
            disable_missing=disable_missing,
        )

        return config