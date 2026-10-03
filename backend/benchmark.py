import random
from models import Robot, Task
from simulation import Simulation
from allocators import ALGORITHMS


def run(alg, seed, n_r=4, n_t=12, g=15):
    random.seed(seed)
    robots = [Robot(i, random.randrange(g), random.randrange(g)) for i in range(n_r)]
    tasks = [Task(i, random.randrange(g), random.randrange(g), random.randint(1, 4))
             for i in range(n_t)]
    s = Simulation(robots, tasks, alg)
    while not s.done and s.tick < 1000:
        s.step()
    return s.tick, sum(r.energy_used for r in robots)


if __name__ == "__main__":
    N = 30
    print(f"{'algorithm':10s} {'avg time':>10s} {'avg energy':>12s}")
    for alg in ALGORITHMS:
        res = [run(alg, seed) for seed in range(N)]   # same seeds for every algorithm
        print(f"{alg:10s} {sum(r[0] for r in res)/N:10.1f} {sum(r[1] for r in res)/N:12.1f}")