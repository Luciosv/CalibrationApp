"""
Configuración completa de la simulación.
"""

from dataclasses import dataclass, field

from config.formulas import (
    FORMULAS,
    get_default_params,
)

from config.tissues import DEFAULT_TISSUES

from models.parameter import Parameter
from models.tissue import Tissue


DEFAULT_DELTA = 0.01


@dataclass(slots=True)
class SimulationConfig:
    """
    Estado completo de la aplicación.
    """

    tissues: list[Tissue] = field(default_factory=list)

    step_mm: float = 0.05

    def __post_init__(self) -> None:

        if not self.tissues:
            self.tissues = self._build_default_tissues()

        self.update_depths()

    # --------------------------------------------------
    # Construcción
    # --------------------------------------------------

    def _build_default_tissues(self) -> list[Tissue]:

        tissues = []

        for definition in DEFAULT_TISSUES:

            param_names = FORMULAS[
                definition.default_family
            ].parameter_names

            param_values = get_default_params(
                definition.default_family
            )

            parameters = [
                Parameter(
                    name=name,
                    value=value,
                    delta=DEFAULT_DELTA,
                )
                for name, value in zip(
                    param_names,
                    param_values,
                )
            ]

            tissues.append(
                Tissue(
                    name=definition.name,
                    thickness=definition.default_thickness,
                    family=definition.default_family,
                    color=definition.color,
                    enabled=definition.enabled,
                    parameters=parameters,
                )
            )

        return tissues

    # --------------------------------------------------
    # Profundidades
    # --------------------------------------------------

    def update_depths(self) -> None:
        """
        Recalcula profundidades acumuladas.
        """

        current_depth = 0.0

        for tissue in self.tissues:

            if not tissue.enabled:
                continue

            tissue.set_start_depth(current_depth)

            current_depth += tissue.thickness

    @property
    def total_depth(self) -> float:
        """
        Profundidad total activa.
        """

        return sum(
            tissue.thickness
            for tissue in self.tissues
            if tissue.enabled
        )

    @property
    def active_tissues(self) -> list[Tissue]:
        """
        Devuelve únicamente los tejidos activos.
        """

        return [
            tissue
            for tissue in self.tissues
            if tissue.enabled
        ]

    # --------------------------------------------------
    # Utilidades
    # --------------------------------------------------

    def get_tissue(self, name: str) -> Tissue | None:

        for tissue in self.tissues:
            if tissue.name == name:
                return tissue

        return None