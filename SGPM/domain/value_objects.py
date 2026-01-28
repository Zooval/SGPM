from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict


class RangoFechaHora:
    """Value Object que representa un rango de fecha y hora (inmutable)"""
    __slots__ = ('_inicio', '_fin')

    def __init__(self, inicio: datetime, fin: datetime) -> None:
        if fin <= inicio:
            raise ValueError("RangoFechaHora inválido: fin debe ser mayor que inicio.")
        object.__setattr__(self, '_inicio', inicio)
        object.__setattr__(self, '_fin', fin)

    @property
    def inicio(self) -> datetime:
        return self._inicio

    @property
    def fin(self) -> datetime:
        return self._fin

    def solapa(self, other: "RangoFechaHora") -> bool:
        return self.inicio < other.fin and other.inicio < self.fin

    def __setattr__(self, name, value):
        raise AttributeError("RangoFechaHora es inmutable")

    def __delattr__(self, name):
        raise AttributeError("RangoFechaHora es inmutable")

    def __repr__(self) -> str:
        return f"RangoFechaHora(inicio={self._inicio}, fin={self._fin})"


class FiltroReporteTareas:
    """Value Object que representa un filtro para reportes de tareas (inmutable)"""
    __slots__ = ('_desde', '_hasta', '_asesor_email')

    def __init__(self, desde: datetime, hasta: datetime, asesor_email: Optional[str] = None) -> None:
        object.__setattr__(self, '_desde', desde)
        object.__setattr__(self, '_hasta', hasta)
        object.__setattr__(self, '_asesor_email', asesor_email)

    @property
    def desde(self) -> datetime:
        return self._desde

    @property
    def hasta(self) -> datetime:
        return self._hasta

    @property
    def asesor_email(self) -> Optional[str]:
        return self._asesor_email

    def __setattr__(self, name, value):
        raise AttributeError("FiltroReporteTareas es inmutable")

    def __delattr__(self, name):
        raise AttributeError("FiltroReporteTareas es inmutable")

    def __repr__(self) -> str:
        return f"FiltroReporteTareas(desde={self._desde}, hasta={self._hasta}, asesor_email={self._asesor_email})"


class EstadisticasTareas:
    """Value Object que representa estadísticas de tareas (inmutable)"""
    __slots__ = ('_total_tareas', '_por_estado', '_por_prioridad', '_vencidas_total', '_vencidas_por_asesor', '_completadas_por_asesor')

    def __init__(self, total_tareas: int, por_estado: Dict, por_prioridad: Dict,
                 vencidas_total: int, vencidas_por_asesor: Dict[str, int],
                 completadas_por_asesor: Dict[str, int]) -> None:
        object.__setattr__(self, '_total_tareas', total_tareas)
        object.__setattr__(self, '_por_estado', por_estado)
        object.__setattr__(self, '_por_prioridad', por_prioridad)
        object.__setattr__(self, '_vencidas_total', vencidas_total)
        object.__setattr__(self, '_vencidas_por_asesor', vencidas_por_asesor)
        object.__setattr__(self, '_completadas_por_asesor', completadas_por_asesor)

    @property
    def total_tareas(self) -> int:
        return self._total_tareas

    @property
    def por_estado(self) -> Dict:
        return self._por_estado

    @property
    def por_prioridad(self) -> Dict:
        return self._por_prioridad

    @property
    def vencidas_total(self) -> int:
        return self._vencidas_total

    @property
    def vencidas_por_asesor(self) -> Dict[str, int]:
        return self._vencidas_por_asesor

    @property
    def completadas_por_asesor(self) -> Dict[str, int]:
        return self._completadas_por_asesor

    def __setattr__(self, name, value):
        raise AttributeError("EstadisticasTareas es inmutable")

    def __delattr__(self, name):
        raise AttributeError("EstadisticasTareas es inmutable")

    def __repr__(self) -> str:
        return f"EstadisticasTareas(total_tareas={self._total_tareas})"
