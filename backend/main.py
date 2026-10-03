import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import Robot, Task
from simulation import Simulation
from allocators import ALGORITHMS

app = FastAPI(title="Multi-Robot Task Allocation")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])   # lets the frontend call us

sim = None


class Config(BaseModel):
    n_robots: int = 3
    n_tasks: int = 8
    grid: int = 15
    algorithm: str = "auction"
    w_time: float = 0.5
    w_energy: float = 0.5


def need_sim():
    if sim is None:
        raise HTTPException(400, "No simulation yet. Call POST /config first.")
    return sim


@app.get("/algorithms")
def algorithms():
    return list(ALGORITHMS.keys())


@app.post("/config")
def configure(c: Config):
    global sim
    if c.algorithm not in ALGORITHMS:
        raise HTTPException(400, f"Unknown algorithm. Choose from {list(ALGORITHMS)}")
    robots = [Robot(i, random.randrange(c.grid), random.randrange(c.grid))
              for i in range(c.n_robots)]
    tasks = [Task(i, random.randrange(c.grid), random.randrange(c.grid),
                  workload=random.randint(1, 4)) for i in range(c.n_tasks)]
    sim = Simulation(robots, tasks, c.algorithm, (c.w_time, c.w_energy))
    return sim.state()


@app.post("/step")
def step():
    s = need_sim()
    s.step()
    return s.state()


@app.get("/state")
def state():
    return need_sim().state()


@app.get("/negotiation-log")
def negotiation_log():
    return need_sim().log


@app.post("/reset")
def reset():
    global sim
    sim = None
    return {"ok": True}