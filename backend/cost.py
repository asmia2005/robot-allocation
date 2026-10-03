def dist(a, b):
    """Manhattan distance (robots move on a grid)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def task_cost(robot, task, tasks_by_id, w_time=0.5, w_energy=0.5, rate=1.0):
    """Cost of `robot` doing `task` after its current queue.
    Returns (combined_cost, time, energy)."""
    start = robot.end_pos(tasks_by_id)
    d = dist(start, (task.x, task.y))
    time = d / robot.speed + task.workload
    energy = d * rate + task.workload * 2
    return w_time * time + w_energy * energy, time, energy