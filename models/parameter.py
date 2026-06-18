"""
Representa un parámetro editable de una ecuación.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Parameter:
    """
    Parámetro individual de una fórmula.

    Ejemplo:
        k = 2.25
        delta = 0.01
    """

    name: str
    value: float
    delta: float = 0.01

    def increment(self) -> None:
        """Incrementa usando el delta configurado."""
        self.value += self.delta

    def decrement(self) -> None:
        """Decrementa usando el delta configurado."""
        self.value -= self.delta