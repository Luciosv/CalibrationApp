"""
Generación de curvas fuerza-profundidad.
"""

from typing import Tuple

import numpy as np

from config.formulas import get_formula

from models.simulation_config import SimulationConfig


class CurveGenerator:

    @staticmethod
    def generate(
        config: SimulationConfig
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Genera la curva completa.

        Returns
        -------
        x : profundidad global
        y : fuerza
        """

        all_x = []
        all_y = []

        previous_force = None

        for tissue in config.active_tissues:

            # ----------------------------------
            # Coordenadas locales
            # ----------------------------------

            dz = np.arange(
                0.0,
                tissue.thickness + config.step_mm,
                config.step_mm
            )

            # garantizar último punto exacto

            if dz[-1] > tissue.thickness:
                dz[-1] = tissue.thickness

            # ----------------------------------
            # Puntos críticos de ruptura
            # ----------------------------------

            if tissue.family == "simone_pop":
                f0, k, fr = tissue.parameter_values
                rdz = (fr - f0) / k
                if 0 < rdz < tissue.thickness:
                    dz = np.sort(
                        np.append(dz, [rdz - 1e-6, rdz])
                    )

            elif tissue.family == "kv_rupture":
                k, fr, _ = tissue.parameter_values
                rdz = fr / k
                if 0 < rdz < tissue.thickness:
                    dz = np.sort(
                        np.append(dz, [rdz])
                    )

            # ----------------------------------
            # Evaluación fórmula
            # ----------------------------------

            formula = get_formula(
                tissue.family
            )

            local_force = formula.evaluator(
                dz,
                tissue.parameter_values
            )

            # ----------------------------------
            # Profundidad global
            # ----------------------------------

            global_depth = (
                dz +
                tissue.start_depth
            )

            # ----------------------------------
            # Salto vertical
            # ----------------------------------

            if previous_force is not None:

                jump_x = global_depth[0]

                all_x.append(jump_x)
                all_y.append(previous_force)

                all_x.append(jump_x)
                all_y.append(local_force[0])

            # ----------------------------------
            # Curva tejido
            # ----------------------------------

            all_x.extend(global_depth.tolist())
            all_y.extend(local_force.tolist())

            previous_force = float(
                local_force[-1]
            )

        return (
            np.array(all_x),
            np.array(all_y)
        )
        
    @staticmethod
    def get_regions(
        config: SimulationConfig
    ) -> list[dict]:
        """
        Devuelve información de las regiones anatómicas
        para dibujar fondos, divisiones y etiquetas.

        Returns
        -------
        [
            {
                "name": "Skin",
                "start": 4.0,
                "end": 6.8
            },
            ...
        ]
        """

        regions = []

        for tissue in config.active_tissues:

            regions.append(
                {
                    "name": tissue.name,
                    "start": tissue.start_depth,
                    "end": tissue.end_depth,
                }
            )

        return regions
    
    @staticmethod
    def get_force_range(config: SimulationConfig) -> tuple[float, float]:
        _, y = CurveGenerator.generate(config)

        return (
            float(y.min()),
            float(y.max())
        )