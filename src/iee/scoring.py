"""Funciones básicas y auditables para normalizar y agregar puntuaciones."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from math import exp, isfinite, log


def bounded_scores(
    values: Sequence[float],
    *,
    lower_bound: float,
    upper_bound: float,
    higher_is_better: bool = True,
) -> list[float]:
    """Normaliza valores a 0–100 con límites metodológicos fijos.

    Los límites se definen fuera de la muestra para que la puntuación conserve
    comparabilidad temporal. Los valores fuera del intervalo se recortan.
    """

    if not values:
        raise ValueError("values no puede estar vacío")

    clean = [float(value) for value in values]
    if not all(isfinite(value) for value in clean):
        raise ValueError("todos los valores deben ser finitos")

    minimum = float(lower_bound)
    maximum = float(upper_bound)
    if not isfinite(minimum) or not isfinite(maximum) or maximum <= minimum:
        raise ValueError("upper_bound debe ser mayor que lower_bound")

    scores = [
        100.0 * (min(max(value, minimum), maximum) - minimum) / (maximum - minimum)
        for value in clean
    ]
    if not higher_is_better:
        scores = [100.0 - score for score in scores]
    return scores


def weighted_geometric_mean(scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Agrega puntuaciones 0–100 limitando la compensación entre dimensiones."""

    _validate_scores_and_weights(scores, weights)
    total_weight = sum(weights.values())
    if any(score == 0.0 and weights[name] > 0.0 for name, score in scores.items()):
        return 0.0
    return 100.0 * exp(
        sum(weights[name] * log(scores[name] / 100.0) for name in scores) / total_weight
    )


def weighted_mean(scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
    """Agrega puntuaciones 0–100 para análisis de sensibilidad."""

    _validate_scores_and_weights(scores, weights)
    total_weight = sum(weights.values())
    return sum(scores[name] * weights[name] for name in scores) / total_weight


def _validate_scores_and_weights(
    scores: Mapping[str, float], weights: Mapping[str, float]
) -> None:
    """Valida entradas compartidas por las funciones de agregación."""

    if not scores:
        raise ValueError("scores no puede estar vacío")
    if set(scores) != set(weights):
        raise ValueError("scores y weights deben contener las mismas claves")

    for name, score in scores.items():
        if not isfinite(score) or not 0.0 <= score <= 100.0:
            raise ValueError(f"puntuación inválida para {name}: {score}")

    for name, weight in weights.items():
        if not isfinite(weight) or weight < 0.0:
            raise ValueError(f"peso inválido para {name}: {weight}")

    if sum(weights.values()) <= 0.0:
        raise ValueError("la suma de pesos debe ser positiva")
