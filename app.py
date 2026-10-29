"""A* Pathfinding Explorer: a Streamlit web app.

Run with:  streamlit run app.py
"""

import random
import tempfile
from pathlib import Path


import matplotlib.pyplot as plt
import streamlit as st

from maze_solver.astar import astar
from maze_solver.floorplan import find_room, load_floor_plan, route_directions
from maze_solver.grid import generate_maze
from maze_solver.heuristics import HEURISTICS
from maze_solver.visualize import build_figure

ROOT = Path(__file__).parent
SAMPLE_PLAN = ROOT / "examples" / "office.txt"
HEURISTIC_HELP = {
    "manhattan": "Counts grid steps (up/down/left/right). Best for this grid.",
    "euclidean": "Straight-line distance. Still correct, but explores more cells.",
    "none": "No estimate. A* becomes Dijkstra's algorithm and explores the most.",
}

st.set_page_config(page_title="A* Pathfinding Explorer", page_icon="🧭", layout="wide")
st.title("🧭 A* Pathfinding Explorer")
st.caption("Shortest-path search on random mazes and on real building floor plans.")

# ---------------- Sidebar controls ----------------
with st.sidebar:
    st.header("Setup")
    mode = st.radio("Problem", ["Random maze", "Floor plan"])
    heuristic_name = st.selectbox("Heuristic", list(HEURISTICS), index=0)
    st.caption(HEURISTIC_HELP[heuristic_name])

    if mode == "Random maze":
        height = st.slider("Height (cells)", 4, 25, 10)
        width = st.slider("Width (cells)", 4, 40, 15)
        if "seed" not in st.session_state:
            st.session_state.seed = 7
        if st.button("🎲 Generate new maze"):
            st.session_state.seed = random.randint(0, 9999)
        st.caption(f"Maze seed: {st.session_state.seed}")
    else:
        plan_source = st.radio("Floor plan", ["Sample office", "Upload my own"])
        uploaded = None
        if plan_source == "Upload my own":
            uploaded = st.file_uploader("Upload a floor plan (.txt)", type="txt")

# ---------------- Build the problem ----------------
if mode == "Random maze":
    grid = generate_maze(height, width, seed=st.session_state.seed)
    start, goal = (1, 1), (grid.rows - 2, grid.cols - 2)
    title = f"Random maze, {height} × {width}"
    src_name = dst_name = None
else:
    if plan_source == "Upload my own" and uploaded is None:
        st.info("Upload a floor plan in the sidebar, or switch to the sample office.")
        st.stop()
    plan_file = SAMPLE_PLAN
    if uploaded is not None:
        plan_file = Path(tempfile.gettempdir()) / "uploaded_floor_plan.txt"
        plan_file.write_bytes(uploaded.getvalue())
    try:
        grid = load_floor_plan(plan_file)
    except ValueError as err:
        st.error(f"Could not read the floor plan: {err}")
        st.stop()

    rooms = sorted(grid.rooms)
    if len(rooms) < 2:
        st.error("The floor plan needs at least two rooms.")
        st.stop()
    col1, col2 = st.columns(2)
    src_name = col1.selectbox("Start room", rooms, index=rooms.index("Lobby") if "Lobby" in rooms else 0)
    dst_name = col2.selectbox("Destination room", rooms, index=len(rooms) - 1)
    start, goal = find_room(grid, src_name), find_room(grid, dst_name)
    title = "Floor plan" if uploaded is None else f"Floor plan: {uploaded.name}"

# ---------------- Run A* ----------------
heuristic = HEURISTICS[heuristic_name]
result = astar(grid, start, goal, heuristic)

if not result.found:
    st.error("No route exists between these two points.")
    st.stop()

m1, m2, m3 = st.columns(3)
m1.metric("Shortest path", f"{result.steps} steps")
m2.metric("Cells explored by A*", len(result.explored))
m3.metric("Heuristic", heuristic_name)

st.subheader(title)
total = len(result.explored)
if total > 1:
    shown = st.slider("Search progress: cells expanded so far", 1, total, total,
                      help="Drag left to watch A* explore, then reach the path at the end.")
else:
    shown = total

finished = shown == total
fig = build_figure(
    grid,
    result.explored[:shown],
    result.path if finished else [],
    start, goal,
    rooms=grid.rooms if mode == "Floor plan" else None,
)
st.pyplot(fig)
plt.close(fig)
st.caption("🟩 start   🟧 goal   🟥 shortest path   🟦 cells explored by A*   ⬛ walls")

# ---------------- Directions (floor plan only) ----------------
if mode == "Floor plan":
    st.subheader(f"Walking directions: {src_name} → {dst_name}")
    for i, step in enumerate(route_directions(result.path), 1):
        st.write(f"{i}. {step}")

# ---------------- Heuristic comparison ----------------

# ---------------- Heuristic comparison ----------------

# ---------------- Heuristic comparison ----------------
st.subheader("Compare heuristics on this problem")

rows = []

for name, h in HEURISTICS.items():
    r = astar(grid, start, goal, h)

    rows.append({
        "Heuristic": name,
        "Path steps": r.steps,
        "Cells explored": len(r.explored),
    })

# Show comparison without Pandas-dependent chart or table functions
max_explored = max(row["Cells explored"] for row in rows)

for row in rows:
    st.markdown(f"**{row['Heuristic'].capitalize()}**")
    st.write(f"Path steps: {row['Path steps']}")
    st.write(f"Cells explored: {row['Cells explored']}")

    # Visualize relative exploration using a progress bar
    if max_explored > 0:
        st.progress(row["Cells explored"] / max_explored)

    st.divider()

st.caption(
    "Every heuristic finds a shortest path of the same length. "
    "The number of cells explored shows how much searching was required."
)

with st.expander("How A* works"):
    st.markdown(
        "A* keeps a list of frontier cells and always expands the one with the lowest "
        "**f = g + h**. **g** is the number of steps taken so far, and **h** is the "
        "heuristic's estimate of the steps still needed. Because the estimate never "
        "overshoots, the first time A* reaches the goal, the path is guaranteed shortest."
    )


