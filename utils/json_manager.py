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
    ) -> None:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        for tissue_name, tissue_data in data.items():

            tissue = config.get_tissue(
                tissue_name
            )

            if tissue is None:
                continue

            family = tissue_data["family"]

            tissue.family = family

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

        config.update_depths()
    
    @staticmethod
    def load_config(path: str) -> SimulationConfig:
        config = SimulationConfig()

        JsonManager.load_json(
            path,
            config
        )

        return config