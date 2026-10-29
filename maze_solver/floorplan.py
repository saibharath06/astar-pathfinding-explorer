"""Load a building floor plan from a text file and produce walking directions.

File format:

    ##########
    #L.....#.#      '#' or a space = wall
    #......#.#      '.' = walkable floor
    ##########      any other character = a room marker
    <blank line>
    [rooms]
    Lobby: L        <room name>: <marker character>
    Server Room: S
"""

from pathlib import Path

from .grid import Grid

DIRECTION_NAMES = {(-1, 0): "north", (1, 0): "south", (0, -1): "west", (0, 1): "east"}


def load_floor_plan(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    if "[rooms]" not in lines:
        raise ValueError(f"{path}: missing a [rooms] section")

    split = lines.index("[rooms]")
    map_lines = lines[:split]
    while map_lines and not map_lines[-1].strip():
        map_lines.pop()
    legend_lines = lines[split + 1:]

    width = max(len(line) for line in map_lines)
    map_lines = [line.ljust(width, "#") for line in map_lines]

    walls = set()
    marker_pos = {}
    for r, line in enumerate(map_lines):
        for c, ch in enumerate(line):
            if ch in "# ":
                walls.add((r, c))
            elif ch != ".":
                marker_pos.setdefault(ch, (r, c))

    rooms = {}
    for line in legend_lines:
        line = line.strip()
        if not line:
            continue
        name, _, marker = line.rpartition(":")
        name, marker = name.strip(), marker.strip()
        if marker not in marker_pos:
            raise ValueError(f"room '{name}' uses marker '{marker}', which is not on the map")
        rooms[name] = marker_pos[marker]

    return Grid(len(map_lines), width, walls, rooms)


def find_room(grid, name):
    """Look up a room by name, ignoring case."""
    wanted = name.strip().lower()
    for room, cell in grid.rooms.items():
        if room.lower() == wanted:
            return cell
    raise KeyError(f"no room named '{name}'. Known rooms: {', '.join(sorted(grid.rooms))}")


def route_directions(path):
    """Turn a list of cells into human-readable instructions.

    Consecutive steps in the same direction are merged, so
    [(0,0),(0,1),(0,2),(1,2)] becomes "Walk east for 2 steps", then
    "Walk south for 1 step".
    """
    if len(path) < 2:
        return ["You are already at the destination."]

    def plural(n):
        return f"{n} step" if n == 1 else f"{n} steps"

    instructions = []
    current, count = None, 0
    for a, b in zip(path, path[1:]):
        move = (b[0] - a[0], b[1] - a[1])
        if move == current:
            count += 1
        else:
            if current is not None:
                instructions.append(f"Walk {DIRECTION_NAMES[current]} for {plural(count)}")
            current, count = move, 1
    instructions.append(f"Walk {DIRECTION_NAMES[current]} for {plural(count)}")
    instructions.append("You have arrived.")
    return instructions
