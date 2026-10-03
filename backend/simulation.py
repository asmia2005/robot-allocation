from allocators import ALGORITHMS


class Simulation:
    def __init__(self, robots, tasks, algorithm="auction", w=(0.5, 0.5)):
        self.robots, self.tasks = robots, tasks
        self.tbi = {t.id: t for t in tasks}
        self.tick = 0
        self.done = False
        self.log = ALGORITHMS[algorithm](robots, tasks, w, self.tbi)

    def step(self):
        if self.done:
            return
        self.tick += 1
        for r in self.robots:
            if r.energy <= 0 or not r.queue:
                continue
            t = self.tbi[r.queue[0]]
            if (r.x, r.y) != (t.x, t.y):           # move one cell
                if r.x != t.x:
                    r.x += 1 if t.x > r.x else -1
                else:
                    r.y += 1 if t.y > r.y else -1
                r.energy -= 1
                r.energy_used += 1
            else:                                   # execute task
                if r.work_left == 0:
                    r.work_left = t.workload
                r.work_left -= 1
                r.energy -= 2
                r.energy_used += 2
                if r.work_left <= 0:
                    r.work_left = 0
                    t.status = "done"
                    r.queue.pop(0)
        self.done = all(t.status == "done" for t in self.tasks)

    def state(self):
        return {
            "tick": self.tick,
            "done": self.done,
            "robots": [{"id": r.id, "x": r.x, "y": r.y,
                        "energy": round(r.energy, 1),
                        "task": r.queue[0] if r.queue else None}
                       for r in self.robots],
            "tasks": [{"id": t.id, "x": t.x, "y": t.y,
                       "status": t.status, "robot": t.robot}
                      for t in self.tasks],
            "metrics": {"time": self.tick,
                        "energy": round(sum(r.energy_used for r in self.robots), 1)},
        }