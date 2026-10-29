"""Grid world model and random maze generation."""

import random

# Up, down, left, right. Diagonal moves are not allowed.
DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))


class Grid:
    """A rectangular grid where each cell is either open or a wall.

    Cells are (row, col) tuples. `rooms` maps a room name to its cell and is
    only used for floor plans.
    """

    def __init__(self, rows, cols, walls=(), rooms=None):
        self.rows = rows
        self.cols = cols
        self.walls = set(walls)
        self.rooms = dict(rooms or {})

    def in_bounds(self, cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_open(self, cell):
        return self.in_bounds(cell) and cell not in self.walls

    def neighbors(self, cell):
        r, c = cell
        for dr, dc in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if self.is_open(nxt):
                yield nxt


def generate_maze(height, width, seed=None):
    """Create a perfect maze (exactly one route between any two cells).

    Uses the recursive backtracker: walk randomly until stuck, then back up
    to the last cell with an unvisited neighbor. The result is a Grid of size
    (2*height+1) x (2*width+1). The start is (1, 1) and the far corner is
    (rows-2, cols-2).
    """
    rng = random.Random(seed)
    rows, cols = 2 * height + 1, 2 * width + 1

    walls = {(r, c) for r in range(rows) for c in range(cols)}
    start = (1, 1)
    walls.discard(start)
    visited = {start}
    stack = [start]

    while stack:
        r, c = stack[-1]
        options = []
        for dr, dc in DIRECTIONS:
            nr, nc = r + 2 * dr, c + 2 * dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and (nr, nc) not in visited:
                options.append((dr, dc))
        if options:
            dr, dc = rng.choice(options)
            nr, nc = r + 2 * dr, c + 2 * dc
            walls.discard((r + dr, c + dc))  # knock down the wall between cells
            walls.discard((nr, nc))
            visited.add((nr, nc))
            stack.append((nr, nc))
        else:
            stack.pop()

    return Grid(rows, cols, walls)
