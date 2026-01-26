from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RangoFechaHora:
    inicio: datetime
    fin: datetime

    def __post_init__(self) -> None:
        if self.fin <= self.inicio:
            raise ValueError("RangoFechaHora inválido: fin debe ser mayor que inicio.")

    def solapa(self, other: "RangoFechaHora") -> bool:
        return self.inicio < other.fin and other.inicio < self.fin
