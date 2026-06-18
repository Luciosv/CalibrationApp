from dataclasses import dataclass


@dataclass(slots=True)
class TissueDefinition:
    name: str
    default_thickness: float
    default_family: str
    color: str
    enabled: bool = True


DEFAULT_TISSUES = [
    TissueDefinition(
        name="Outside",
        default_thickness=4.0,
        default_family="constant",
        color="#FFFFFF",
    ),
    TissueDefinition(
        name="Skin",
        default_thickness=2.8,
        default_family="kv_rupture",
        color="#F4C2C2",
    ),
    TissueDefinition(
        name="Fat",
        default_thickness=2.4,
        default_family="linear",
        color="#FFFF99",
    ),
    TissueDefinition(
        name="Muscle",
        default_thickness=3.2,
        default_family="linear",
        color="#99CCFF",
    ),
    TissueDefinition(
        name="Supraspinous Lig",
        default_thickness=5.0,
        default_family="saturating_exp",
        color="#FFCC99",
    ),
    TissueDefinition(
        name="Interspinous Lig",
        default_thickness=1.0,
        default_family="linear",
        color="#CCCCCC",
    ),
    TissueDefinition(
        name="Ligamentum Flavum",
        default_thickness=3.0,
        default_family="simone_pop",
        color="#CCCCCC",
    ),
    TissueDefinition(
        name="Epidural Space",
        default_thickness=5.0,
        default_family="constant",
        color="#FFFFFF",
    ),
    TissueDefinition(
        name="Dura Mater",
        default_thickness=1.0,
        default_family="kv_rupture",
        color="#F4C2C2",
    ),
    TissueDefinition(
        name="Subarachnoid",
        default_thickness=4.6,
        default_family="constant",
        color="#FFFFFF",
    ),
]