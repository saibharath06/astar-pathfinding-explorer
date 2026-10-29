"""Heuristic functions that estimate the remaining distance to the goal.

A heuristic must never overestimate the true distance (admissible) for A*
to return the shortest path. All three below are admissible on a grid
where every move costs 1.
"""

import math


def manhattan(a, b):
    """Steps needed if you can only move up, down, left, or right."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    """Straight-line distance. Admissible, but usually explores more cells."""
    return math.dist(a, b)


def zero(a, b):
    """No estimate at all. A* then behaves exactly like Dijkstra's algorithm."""
    return 0


HEURISTICS = {
    "manhattan": manhattan,
    "euclidean": euclidean,
    "none": zero,
}
