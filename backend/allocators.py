import random
import numpy as np
from scipy.optimize import linear_sum_assignment
from cost import task_cost, dist


def _assign(robot, task, log, note):
    robot.queue.append(task.id)
    task.status, task.robot = "assigned", robot.id
    log.append({"task": task.id, "winner": robot.id, "note": note})


# 1) Random baseline
def random_alloc(robots, tasks, w, tbi):
    log = []
    for t in tasks:
        _assign(random.choice(robots), t, log, "random")
    return log


# 2) Greedy: each task goes to the cheapest robot, in task order
def greedy_alloc(robots, tasks, w, tbi):
    log = []
    for t in tasks:
        bids = {r.id: round(task_cost(r, t, tbi, *w)[0], 2) for r in robots}
        win = min(robots, key=lambda r: bids[r.id])
        log.append({"task": t.id, "bids": bids})
        _assign(win, t, log, "lowest cost")
    return log


# 3) Auction / Contract Net: best (robot, task) pair wins each round
def auction_alloc(robots, tasks, w, tbi):
    log, pending = [], list(tasks)
    while pending:
        best = None
        round_bids = []
        for t in pending:
            for r in robots:
                c = task_cost(r, t, tbi, *w)[0]
                round_bids.append({"robot": r.id, "task": t.id, "bid": round(c, 2)})
                if best is None or c < best[0]:
                    best = (c, r, t)
        log.append({"announce": [t.id for t in pending], "bids": round_bids})
        _, r, t = best
        _assign(r, t, log, f"won with bid {best[0]:.2f}")
        pending.remove(t)
    return log


# 4) Hungarian: optimal one-to-one matching, repeated in rounds
def hungarian_alloc(robots, tasks, w, tbi):
    log, pending = [], list(tasks)
    while pending:
        M = np.array([[task_cost(r, t, tbi, *w)[0] for t in pending] for r in robots])
        rows, cols = linear_sum_assignment(M)
        for i, j in zip(rows, cols):
            _assign(robots[i], pending[j], log, "optimal matching")
        pending = [t for t in pending if t.status == "pending"]
    return log


# 5) Game-theoretic: start from greedy, robots swap tasks until no one can improve
def _route_cost(robot, tbi):
    pos, time, energy = (robot.x, robot.y), 0.0, 0.0
    for tid in robot.queue:
        t = tbi[tid]
        d = dist(pos, (t.x, t.y))
        time += d / robot.speed + t.workload
        energy += d + t.workload * 2
        pos = (t.x, t.y)
    return time, energy


def _team_cost(robots, tbi, w):
    costs = [_route_cost(r, tbi) for r in robots]
    makespan = max(c[0] for c in costs)          # team finishes when the slowest robot does
    total_energy = sum(c[1] for c in costs)
    return w[0] * makespan + w[1] * total_energy


def nash_alloc(robots, tasks, w, tbi):
    log = greedy_alloc(robots, tasks, w, tbi)
    log.append({"note": "--- negotiation phase: robots try to hand off tasks ---"})
    improved, rounds = True, 0
    while improved and rounds < 100:
        improved, rounds = False, rounds + 1
        for r in robots:
            for tid in list(r.queue):
                for other in robots:
                    if other is r or tid not in r.queue:
                        continue
                    before = _team_cost(robots, tbi, w)
                    idx = r.queue.index(tid)
                    r.queue.remove(tid)
                    other.queue.append(tid)
                    after = _team_cost(robots, tbi, w)
                    if after < before - 1e-9:        # transfer helps the team
                        tbi[tid].robot = other.id
                        log.append({"task": tid, "from": r.id, "to": other.id,
                                    "note": f"transfer lowers team cost {before:.1f} -> {after:.1f}"})
                        improved = True
                    else:                            # undo
                        other.queue.pop()
                        r.queue.insert(idx, tid)
    log.append({"note": f"equilibrium reached after {rounds} rounds"})
    return log


ALGORITHMS = {
    "random": random_alloc,
    "greedy": greedy_alloc,
    "auction": auction_alloc,
    "hungarian": hungarian_alloc,
    "nash": nash_alloc,
}