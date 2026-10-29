# A* Maze and Floor-Plan Navigator

A pathfinding project that starts with a random grid maze and ends with a
practical indoor navigation tool. Given a floor plan, it finds the shortest
walking route between two rooms and prints step-by-step directions.

## What it teaches

- **A\* search:** Expands the cell with the lowest `f = g + h`, where `g` is
  the cost so far and `h` is a heuristic estimate of the remaining distance.
- **Heuristics:** Manhattan and Euclidean distance are admissible, so they
  never change the optimal answer. They only change how many cells are explored.
- **Maze generation:** The recursive backtracker builds a perfect maze with
  exactly one route between any two cells.

## Setup

Requires Python 3.10 or newer.

```bash
pip install -r requirements.txt   # only needed for PNG/GIF output
```

## Usage

Solve a random maze and print it:

```bash
python main.py random --height 12 --width 20 --seed 7 --map
```

Compare heuristics on the same maze. Watch the explored count change:

```bash
python main.py random --seed 7 --heuristic manhattan
python main.py random --seed 7 --heuristic euclidean
python main.py random --seed 7 --heuristic none
```

Save a picture or an animation of the search:

```bash
python main.py random --seed 7 --plot maze.png --animate maze.gif
```

Navigate a building:

```bash
python main.py floorplan examples/office.txt --list-rooms
python main.py floorplan examples/office.txt --from Lobby --to "Server Room" --map
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## Making your own floor plan

Create a text file. `#` or a space is a wall, `.` is floor, and any other
character is a room marker. After a `[rooms]` line, list each room as
`Name: marker`. See `examples/office.txt`.

## Project layout

```
main.py                    command-line interface
maze_solver/
  astar.py                 A* search
  heuristics.py            distance estimates
  grid.py                  grid model and maze generation
  floorplan.py             floor-plan loading and directions
  visualize.py             text map, PNG, and GIF output
examples/office.txt        sample building
tests/test_solver.py       unit tests
```

## Ideas for extending it

- Add a web page with Flask or Streamlit that lets users click two rooms.
- Use real map data with OSMnx, replacing the grid with a road graph.
- Add weighted cells, such as stairs or crowded corridors that cost more.
- Support multiple floors and connect them with elevator nodes.

## Web app (Streamlit)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens at http://localhost:8501. Use the sidebar to pick a random
maze or a floor plan (sample or your own upload), choose a heuristic, and drag
the search-progress slider to watch A* explore the grid.
