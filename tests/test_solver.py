"""Tests for the A* solver, maze generation, and floor-plan loading.

Run with:  python -m unittest discover -s tests -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from maze_solver.astar import astar
from maze_solver.floorplan import find_room, load_floor_plan, route_directions
from maze_solver.grid import Grid, generate_maze
from maze_solver.heuristics import euclidean, manhattan, zero


class AStarTests(unittest.TestCase):
    def test_straight_line(self):
        result = astar(Grid(1, 5), (0, 0), (0, 4), manhattan)
        self.assertTrue(result.found)
        self.assertEqual(result.steps, 4)

    def test_detour_around_wall(self):
        # Wall blocks the top route; the only way is down, across, and up.
        grid = Grid(3, 3, walls={(0, 1), (1, 1)})
        result = astar(grid, (0, 0), (0, 2), manhattan)
        self.assertEqual(result.steps, 6)
        self.assertEqual(result.path[0], (0, 0))
        self.assertEqual(result.path[-1], (0, 2))

    def test_unreachable_goal(self):
        grid = Grid(1, 3, walls={(0, 1)})
        result = astar(grid, (0, 0), (0, 2), manhattan)
        self.assertFalse(result.found)
        self.assertEqual(result.path, [])

    def test_blocked_start_raises(self):
        grid = Grid(2, 2, walls={(0, 0)})
        with self.assertRaises(ValueError):
            astar(grid, (0, 0), (1, 1))

    def test_all_heuristics_find_same_optimal_length(self):
        # An admissible heuristic must never change the optimal answer.
        for seed in range(10):
            grid = generate_maze(8, 8, seed=seed)
            start, goal = (1, 1), (grid.rows - 2, grid.cols - 2)
            lengths = {astar(grid, start, goal, h).steps for h in (manhattan, euclidean, zero)}
            self.assertEqual(len(lengths), 1, f"seed {seed} gave different lengths {lengths}")

    def test_informed_search_explores_fewer_cells_than_dijkstra(self):
        grid = generate_maze(15, 15, seed=3)
        start, goal = (1, 1), (grid.rows - 2, grid.cols - 2)
        informed = astar(grid, start, goal, manhattan)
        blind = astar(grid, start, goal, zero)
        self.assertLessEqual(len(informed.explored), len(blind.explored))


class MazeTests(unittest.TestCase):
    def test_every_generated_maze_is_solvable(self):
        for seed in range(20):
            grid = generate_maze(10, 10, seed=seed)
            result = astar(grid, (1, 1), (grid.rows - 2, grid.cols - 2))
            self.assertTrue(result.found, f"seed {seed} produced an unsolvable maze")

    def test_same_seed_gives_same_maze(self):
        a = generate_maze(6, 6, seed=42)
        b = generate_maze(6, 6, seed=42)
        self.assertEqual(a.walls, b.walls)


class FloorPlanTests(unittest.TestCase):
    PLAN = (
        "#####\n"
        "#A..#\n"
        "#.#.#\n"
        "#...#\n"
        "#####\n"
        "\n"
        "[rooms]\n"
        "Room A: A\n"
    )

    def _write_plan(self, text):
        handle = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
        handle.write(text)
        handle.close()
        self.addCleanup(os.remove, handle.name)
        return handle.name

    def test_loads_rooms_and_walls(self):
        grid = load_floor_plan(self._write_plan(self.PLAN))
        self.assertEqual(grid.rooms, {"Room A": (1, 1)})
        self.assertIn((2, 2), grid.walls)
        self.assertNotIn((1, 1), grid.walls)

    def test_room_lookup_ignores_case(self):
        grid = load_floor_plan(self._write_plan(self.PLAN))
        self.assertEqual(find_room(grid, "room a"), (1, 1))
        with self.assertRaises(KeyError):
            find_room(grid, "Nonexistent")

    def test_missing_rooms_section_is_an_error(self):
        with self.assertRaises(ValueError):
            load_floor_plan(self._write_plan("#####\n#.A.#\n#####\n"))

    def test_example_office_routes_between_rooms(self):
        here = os.path.dirname(__file__)
        grid = load_floor_plan(os.path.join(here, "..", "examples", "office.txt"))
        src, dst = find_room(grid, "Lobby"), find_room(grid, "Server Room")
        result = astar(grid, src, dst)
        self.assertTrue(result.found)
        self.assertEqual(result.path[0], src)
        self.assertEqual(result.path[-1], dst)


class DirectionsTests(unittest.TestCase):
    def test_merges_straight_segments(self):
        path = [(0, 0), (0, 1), (0, 2), (1, 2)]
        self.assertEqual(route_directions(path), [
            "Walk east for 2 steps",
            "Walk south for 1 step",
            "You have arrived.",
        ])

    def test_already_there(self):
        self.assertEqual(route_directions([(3, 3)]), ["You are already at the destination."])


if __name__ == "__main__":
    unittest.main()
