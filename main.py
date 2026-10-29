#!/usr/bin/env python3
"""Command-line interface for the A* solver.

Examples:
    python main.py random --height 12 --width 20 --seed 7 --map
    python main.py random --heuristic none --plot dijkstra.png
    python main.py floorplan examples/office.txt --list-rooms
    python main.py floorplan examples/office.txt --from Lobby --to "Server Room" --map
"""

import argparse
import sys

from maze_solver.astar import astar
from maze_solver.floorplan import find_room, load_floor_plan, route_directions
from maze_solver.grid import generate_maze
from maze_solver.heuristics import HEURISTICS
from maze_solver import visualize


def add_shared_options(sub):
    sub.add_argument("--heuristic", choices=list(HEURISTICS), default="manhattan",
                     help="distance estimate used by A* (default: manhattan)")
    sub.add_argument("--map", action="store_true", help="print an ASCII map of the search")
    sub.add_argument("--plot", metavar="FILE.png", help="save a PNG of the search")
    sub.add_argument("--animate", metavar="FILE.gif", help="save an animated GIF of the search")


def build_parser():
    parser = argparse.ArgumentParser(description="A* pathfinding: random mazes and floor plans.")
    modes = parser.add_subparsers(dest="mode", required=True)

    rnd = modes.add_parser("random", help="solve a randomly generated maze")
    rnd.add_argument("--height", type=int, default=10, help="maze height in cells (default: 10)")
    rnd.add_argument("--width", type=int, default=15, help="maze width in cells (default: 15)")
    rnd.add_argument("--seed", type=int, help="random seed for a reproducible maze")
    add_shared_options(rnd)

    fp = modes.add_parser("floorplan", help="find walking directions between rooms")
    fp.add_argument("plan", help="path to a floor plan text file")
    fp.add_argument("--from", dest="src", help="starting room name")
    fp.add_argument("--to", dest="dst", help="destination room name")
    fp.add_argument("--list-rooms", action="store_true", help="list the rooms and exit")
    add_shared_options(fp)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.mode == "random":
        grid = generate_maze(args.height, args.width, seed=args.seed)
        start, goal = (1, 1), (grid.rows - 2, grid.cols - 2)
        print(f"Generated a {args.height}x{args.width} maze "
              f"({grid.rows}x{grid.cols} grid, seed={args.seed}).")
    else:
        grid = load_floor_plan(args.plan)
        if args.list_rooms:
            print("Rooms in this building:")
            for name in sorted(grid.rooms):
                print(f"  - {name}")
            return 0
        if not (args.src and args.dst):
            parser.error("floorplan mode needs --from and --to (or --list-rooms)")
        try:
            start = find_room(grid, args.src)
            goal = find_room(grid, args.dst)
        except KeyError as err:
            print(f"Error: {err.args[0]}", file=sys.stderr)
            return 1

    result = astar(grid, start, goal, HEURISTICS[args.heuristic])

    if not result.found:
        print("No route exists between those two points.")
        return 1

    print(f"Shortest path: {result.steps} steps")
    print(f"Cells explored by A*: {len(result.explored)} (heuristic: {args.heuristic})")

    if args.mode == "floorplan":
        print("\nDirections:")
        for i, step in enumerate(route_directions(result.path), 1):
            print(f"  {i}. {step}")

    if args.map:
        print()
        print(visualize.render_text(grid, result, start, goal))

    if args.plot:
        visualize.plot_result(grid, result, start, goal, args.plot)
        print(f"\nSaved image to {args.plot}")

    if args.animate:
        visualize.save_animation(grid, result, start, goal, args.animate)
        print(f"Saved animation to {args.animate}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
