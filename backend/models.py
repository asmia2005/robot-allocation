from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    id: int
    x: int
    y: int
    workload: float = 1.0          # ticks needed to execute
    status: str = "pending"        # pending / assigned / done
    robot: Optional[int] = None


@dataclass
class Robot:
    id: int
    x: int
    y: int
    speed: float = 1.0
    energy: float = 500.0          # high enough that robots don't stall in benchmarks
    queue: list = field(default_factory=list)   # assigned task ids
    work_left: float = 0.0
    energy_used: float = 0.0

    def end_pos(self, tasks_by_id):
        """Position after finishing all queued tasks (used when bidding)."""
        if self.queue:
            t = tasks_by_id[self.queue[-1]]
            return (t.x, t.y)
        return (self.x, self.y)