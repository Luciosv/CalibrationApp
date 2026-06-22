"""
Definición centralizada de todas las familias de ecuaciones.

La interfaz gráfica se genera automáticamente a partir de estas
definiciones.

Agregar una nueva ecuación debería requerir únicamente:

1. Crear la función matemática.
2. Registrar una nueva FormulaDefinition.

Sin tocar la UI.
"""

from dataclasses import dataclass
from typing import Callable

import numpy as np


# ============================================================
# MODELO
# ============================================================

@dataclass(slots=True)
class FormulaDefinition:
    """
    Describe completamente una familia matemática.
    """

    name: str
    parameter_names: list[str]
    bounds: list[tuple[float, float]]
    default_values: list[float]
    evaluator: Callable


# ============================================================
# FORMULAS ESPECIALES
# ============================================================

def _kv_rupture(dz: np.ndarray, params: list[float]) -> np.ndarray:
    """
    Kelvin-Voigt con ruptura.

    Parámetros:
        k            : rigidez
        Fr           : fuerza de ruptura
        decay_slope  : pendiente posterior a ruptura

    Comportamiento:
        F = k * dz

    hasta alcanzar Fr.

    Luego:
        F = Fr + decay_slope * delta

    saturando en 0.5 N.
    """

    k, fr, decay_slope = params

    rupture_depth = fr / k

    force = np.empty_like(dz, dtype=float)

    before = dz <= rupture_depth
    after = ~before

    force[before] = k * dz[before]

    force[after] = (
        fr +
        decay_slope * (dz[after] - rupture_depth)
    )

    return force


def _simone_pop(dz: np.ndarray, params: list[float]) -> np.ndarray:
    """
    Modelo Simone-Okamura.

    F = F0 + k * dz

    hasta alcanzar Fr.

    Luego cae instantáneamente a 0.5 N.
    """

    f0, k, fr = params

    rupture_depth = (fr - f0) / k

    force = f0 + k * dz

    force[dz >= rupture_depth] = 0.5

    return force


# ============================================================
# REGISTRO DE FORMULAS
# ============================================================

FORMULAS: dict[str, FormulaDefinition] = {
    "constant": FormulaDefinition(
        name="constant",
        parameter_names=["C"],
        bounds=[(0.0, 10.0)],
        default_values=[0.0],
        evaluator=lambda dz, p:
        np.full_like(dz, p[0], dtype=float),
    ),

    "linear": FormulaDefinition(
        name="linear",
        parameter_names=["F0", "m"],
        bounds=[
            (0.0, 15.0),
            (-10.0, 10.0),
        ],
        default_values=[1.0, 0.5],
        evaluator=lambda dz, p:
        p[0] + p[1] * dz,
    ),

    "polynomial2": FormulaDefinition(
        name="polynomial2",
        parameter_names=["a", "b", "c"],
        bounds=[(-15.0, 15.0)] * 3,
        default_values=[0.0, 0.1, 0.0],
        evaluator=lambda dz, p:
        p[0] + p[1] * dz + p[2] * dz * dz,
    ),

    "polynomial3": FormulaDefinition(
        name="polynomial3",
        parameter_names=["a", "b", "c", "d"],
        bounds=[(-15.0, 15.0)] * 4,
        default_values=[0.0, 0.1, 0.0, 0.0],
        evaluator=lambda dz, p:
        p[0]
        + p[1] * dz
        + p[2] * dz * dz
        + p[3] * dz ** 3,
    ),

    "exponential": FormulaDefinition(
        name="exponential",
        parameter_names=["F0", "a", "rate"],
        bounds=[
            (-5.0, 15.0),
            (-10.0, 10.0),
            (-3.0, 3.0),
        ],
        default_values=[0.0, 0.5, 0.3],
        evaluator=lambda dz, p:
        p[0]
        + p[1]
        * np.exp(np.clip(p[2] * dz, -30, 30)),
    ),

    "sigmoid": FormulaDefinition(
        name="sigmoid",
        parameter_names=["L", "rate", "x0"],
        bounds=[
            (0.0, 15.0),
            (0.01, 10.0),
            (0.0, 55.0),
        ],
        default_values=[5.0, 1.0, 2.0],
        evaluator=lambda dz, p:
        p[0]
        / (
            1 +
            np.exp(
                np.clip(
                    -p[1] * (dz - p[2]),
                    -30,
                    30
                )
            )
        ),
    ),

    "kv_rupture": FormulaDefinition(
        name="kv_rupture",
        parameter_names=[
            "k",
            "Fr",
            "decay_slope"
        ],
        bounds=[
            (0.1, 30.0),
            (0.1, 15.0),
            (-30.0, 0.0),
        ],
        default_values=[
            3.0,
            5.0,
            -4.0
        ],
        evaluator=_kv_rupture,
    ),

    "saturating_exp": FormulaDefinition(
        name="saturating_exp",
        parameter_names=[
            "F0",
            "Finf",
            "alpha"
        ],
        bounds=[
            (0.0, 15.0),
            (0.0, 15.0),
            (0.001, 5.0),
        ],
        default_values=[
            6.0,
            8.0,
            0.3
        ],
        evaluator=lambda dz, p:
        p[1]
        - (
            (p[1] - p[0])
            * np.exp(-p[2] * dz)
        ),
    ),

    "simone_pop": FormulaDefinition(
        name="simone_pop",
        parameter_names=[
            "F0",
            "k",
            "Fr"
        ],
        bounds=[
            (0.0, 10.0),
            (0.1, 30.0),
            (0.5, 15.0),
        ],
        default_values=[
            0.0,
            3.0,
            5.0
        ],
        evaluator=_simone_pop,
    ),
}


# ============================================================
# HELPERS
# ============================================================

def get_formula(name: str) -> FormulaDefinition:
    """
    Obtiene una familia por nombre.
    """

    return FORMULAS[name]


def get_default_params(name: str) -> list[float]:
    """
    Devuelve una copia de los parámetros por defecto.
    """

    return FORMULAS[name].default_values.copy()


def validate_params(
    family_name: str,
    values: list[float]
) -> bool:
    """
    Verifica que todos los parámetros
    estén dentro de límites.
    """

    formula = FORMULAS[family_name]

    if len(values) != len(formula.bounds):
        return False

    for value, (minimum, maximum) in zip(
        values,
        formula.bounds
    ):
        if not minimum <= value <= maximum:
            return False

    return True