import os
import json
from collections import defaultdict

from . import consts

from typing import NamedTuple, Union, List, Tuple

"""
TO-DO:
    - Documentate simulation params
"""


class SimulationConfigsType(NamedTuple):
    """Simulation Configs JSON-like structure"""
    n: int
    p0: float
    s0: int
    tr: int
    beta: float
    seed: Union[int, str]


class SimulationResultsType(NamedTuple):
    """Simulation Results JSON-like structure"""
    trial_count: int
    configs: SimulationConfigsType
    results: List[int]
    results_z: List[int]


def load_simulation_json(path: str) -> Union[SimulationResultsType, None]:
    """Load simulation results from a JSON file

    Args:
        path (str): Target simulation results JSON path

    Returns:
        Any[SimulationResultsType, None]: simulation data, may return None on failure
    """

    # Check if file exists
    if not os.path.isfile(path):
        return None

    # Load JSON data
    try:
        with open(path, 'r') as f:
            data = json.load(f)

            data['results_delta'] = [r - z for r,
                                     z in zip(data['results'], data['results_z'])]

            return data
    except Exception:
        return None


def load_or_generate_simulation(
    trial_count: int,
    n: int,
    p0: int,
    s: int,
    tr: int = int(2 ** 31 - 1),
    beta: float = 0.0,
    salt: str = 'default',
    force_recreation: bool = False,
    datasets_path=consts.AUTO_GENERATED_DATASETS_DIR,
    simulator_cmd=consts.SIMULATOR_EXECUTABLE_PATH,
) -> Union[SimulationResultsType, None]:
    file_name = f'{trial_count}-{n}-{p0}-{s}-{tr}-{beta}-{salt}.json'
    file_path = os.path.join(datasets_path, file_name)

    # Ensure datasets directory exists
    os.makedirs(datasets_path, exist_ok=True)

    # Generate new dataset (if necessary)
    if force_recreation or not os.path.isfile(file_path):
        os.system(
            f'{simulator_cmd} {trial_count} {n} {p0} {s} {tr} {beta} > {file_path} 2> /dev/null')

    # Load and return simulation results
    return load_simulation_json(file_path)


def build_pmf(
    data: SimulationResultsType,
    field: str = 'results'
) -> Tuple[List[int], List[float]]:
    counts = defaultdict(lambda: 0)
    tot = len(data[field])

    for el in data[field]:
        counts[el] += 1

    xs = list(range(min(counts.keys()), max(counts.keys()) + 1))
    ys = [counts[x] / tot for x in xs]

    return xs, ys
