import pytest
from simulation import Simulation
from models import Robot, Task
from allocators import ALGORITHMS
import random

@pytest.mark.parametrize("alg", list(ALGORITHMS.keys()))
def test_all_tasks_finish(alg):
    robots = [Robot(0, 0, 0), Robot(1, 5, 5)]
    tasks = [Task(i, i * 2, i * 3) for i in range(4)]
    s = Simulation(robots, tasks, alg)
    for _ in range(300):
        s.step()
    assert s.done



def test_single_robot_by_hand():
    s = Simulation([Robot(0, 0, 0)], [Task(0, 3, 4, workload=2)], "greedy")
    while not s.done:
        s.step()
    assert s.tick == 9
    assert s.state()["metrics"]["energy"] == 11


@pytest.mark.parametrize("alg", ["greedy", "auction", "hungarian", "nash"])
def test_obvious_assignment(alg):
    # each task is right next to one robot, so a sensible algorithm must pick that robot
    robots = [Robot(0, 0, 0), Robot(1, 10, 10)]
    tasks = [Task(0, 1, 0), Task(1, 10, 9)]
    Simulation(robots, tasks, alg)
    assert tasks[0].robot == 0
    assert tasks[1].robot == 1


@pytest.mark.parametrize("alg", list(ALGORITHMS.keys()))
def test_each_task_assigned_exactly_once(alg):
    random.seed(1)
    robots = [Robot(i, random.randrange(15), random.randrange(15)) for i in range(3)]
    tasks = [Task(i, random.randrange(15), random.randrange(15)) for i in range(10)]
    Simulation(robots, tasks, alg)
    assigned = sorted(tid for r in robots for tid in r.queue)
    assert assigned == sorted(t.id for t in tasks)   # none lost, none duplicated