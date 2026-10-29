"""Show the search: a terminal text map, a PNG image, or an animated GIF.

Matplotlib is imported only when a picture is requested, so the text
output works without it installed.
"""

import numpy as np

COLORS = {
    "open": (1.0, 1.0, 1.0),
    "wall": (0.15, 0.15, 0.15),
    "explored": (0.70, 0.85, 1.00),
    "path": (1.00, 0.30, 0.20),
    "start": (0.20, 0.75, 0.30),
    "goal": (1.00, 0.70, 0.00),
}


def _build_image(grid, explored, path, start, goal):
    img = np.ones((grid.rows, grid.cols, 3))
    for cell in grid.walls:
        img[cell] = COLORS["wall"]
    for cell in explored:
        img[cell] = COLORS["explored"]
    for cell in path:
        img[cell] = COLORS["path"]
    img[start] = COLORS["start"]
    img[goal] = COLORS["goal"]
    return img


def _figure_size(grid):
    return (7, max(3, 7 * grid.rows / grid.cols))


def render_text(grid, result, start, goal):
    """ASCII map: S start, G goal, * path, . explored, # wall."""
    path = set(result.path)
    explored = set(result.explored)
    lines = []
    for r in range(grid.rows):
        row = []
        for c in range(grid.cols):
            cell = (r, c)
            if cell == start:
                row.append("S")
            elif cell == goal:
                row.append("G")
            elif cell in grid.walls:
                row.append("#")
            elif cell in path:
                row.append("*")
            elif cell in explored:
                row.append(".")
            else:
                row.append(" ")
        lines.append("".join(row))
    return "\n".join(lines)


def plot_result(grid, result, start, goal, out_path):
    """Save a PNG showing explored cells and the final path."""
    import matplotlib.pyplot as plt

    img = _build_image(grid, result.explored, result.path, start, goal)
    fig, ax = plt.subplots(figsize=_figure_size(grid))
    ax.imshow(img)
    ax.set_title(f"Explored {len(result.explored)} cells, path length {result.steps} steps")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def save_animation(grid, result, start, goal, out_path, frames=60):
    """Save a GIF that reveals the explored cells one batch at a time, then the path."""
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    total = len(result.explored)
    step = max(1, total // frames)
    counts = list(range(step, total + 1, step))

    fig, ax = plt.subplots(figsize=_figure_size(grid))
    im = ax.imshow(_build_image(grid, [], [], start, goal))
    ax.set_xticks([])
    ax.set_yticks([])

    def update(i):
        if i < len(counts):
            img = _build_image(grid, result.explored[:counts[i]], [], start, goal)
        else:
            img = _build_image(grid, result.explored, result.path, start, goal)
        im.set_data(img)
        return [im]

    # Extra frames at the end so the final path stays on screen for a moment.
    anim = FuncAnimation(fig, update, frames=len(counts) + 10, interval=100)
    anim.save(out_path, writer=PillowWriter(fps=10))
    plt.close(fig)


def build_figure(grid, explored, path, start, goal, rooms=None):
    """Return a matplotlib Figure for display in the Streamlit app.

    `rooms` is an optional {name: (row, col)} dict; room names are drawn on the map.
    """
    import matplotlib.pyplot as plt

    img = _build_image(grid, explored, path, start, goal)
    fig, ax = plt.subplots(figsize=_figure_size(grid))
    ax.imshow(img)
    ax.set_xticks([])
    ax.set_yticks([])
    for name, (r, c) in (rooms or {}).items():
        ax.text(c, r, name.split()[0], ha="center", va="center",
                fontsize=7, color="black", fontweight="bold")
    return fig
