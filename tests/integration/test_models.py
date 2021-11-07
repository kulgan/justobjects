from typing import Iterable

import justobjects as jo


@jo.data(typed=True)
class Task:
    name: str


@jo.data(typed=True)
class Step:
    name: str
    tasks: Iterable[Task]


@jo.data(typed=True)
class Job:
    name: str
    steps: Iterable[Step]


def test_instantiation() -> None:
    job_data = {
        "name": "Niko",
        "steps": [
            {
                "name": "select",
                "tasks": [{"name": "prep"}, {"name": "start"}, {"name": "finish"}],
            },
            {"name": "run", "tasks": [{"name": "exec"}]},
        ],
    }
    job = Job(**job_data)
    assert job.name == "Niko"
    assert len(job.steps) == 2
    step_1 = job.steps[0]
    assert isinstance(step_1, Step)
