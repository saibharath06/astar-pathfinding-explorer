"""A* search on a Grid.

A* keeps a priority queue of frontier cells ordered by
    f = g + h
where g is the cost so far and h is the heuristic estimate to the goal.
It always expands the cell with the lowest f, so it finds the shortest path
without exploring the whole grid when the heuristic is good.
"""

import heapq
import itertools
from dataclasses import dataclass, field

from .heuristics import manhattan


@dataclass
class SearchResult:
    found: bool
    path: list = field(default_factory=list)      # start -> goal, inclusive
    explored: list = field(default_factory=list)  # cells in the order they were expanded
    cost: int = None                              # number of steps in the path

    @property
    def steps(self):
        return len(self.path) - 1 if self.found else None


def astar(grid, start, goal, heuristic=manhattan):
    """Return a SearchResult with the shortest path from start to goal."""
    if not grid.is_open(start):
        raise ValueError(f"start {start} is not an open cell")
    if not grid.is_open(goal):
        raise ValueError(f"goal {goal} is not an open cell")

    tie = itertools.count()  # breaks ties so heap entries never compare cells
    frontier = [(heuristic(start, goal), 0, next(tie), start)]
    best_g = {start: 0}
    parent = {start: None}
    closed = set()
    explored = []

    while frontier:
        _, _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue  # stale entry: this cell was already expanded more cheaply
        closed.add(current)
        explored.append(current)

        if current == goal:
            path = _rebuild_path(parent, goal)
            return SearchResult(True, path, explored, len(path) - 1)

        g = best_g[current]
        for nxt in grid.neighbors(current):
            new_g = g + 1
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                parent[nxt] = current
                f = new_g + heuristic(nxt, goal)
                heapq.heappush(frontier, (f, new_g, next(tie), nxt))

    return SearchResult(False, [], explored, None)


def _rebuild_path(parent, node):
    path = []
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path
