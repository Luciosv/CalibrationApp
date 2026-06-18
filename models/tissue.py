from dataclasses import dataclass, field

from models.parameter import Parameter


@dataclass(slots=True)
class Tissue:

    name: str
    thickness: float
    family: str
    color: str = "#666666"

    enabled: bool = True

    parameters: list[Parameter] = field(default_factory=list)

    _start_depth: float = field(
        default=0.0,
        init=False,
        repr=False
    )

    @property
    def parameter_values(self) -> list[float]:
        return [p.value for p in self.parameters]

    @property
    def start_depth(self) -> float:
        return self._start_depth

    @property
    def end_depth(self) -> float:
        return self.start_depth + self.thickness

    def set_start_depth(self, depth: float) -> None:
        self._start_depth = depth