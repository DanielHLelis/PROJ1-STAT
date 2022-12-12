import os
import json
import time
from collections import defaultdict

import numpy as np

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
    max_cycles: int = 50000,
    seed: Union[int, None] = None,
    datasets_path=consts.AUTO_GENERATED_DATASETS_DIR,
    simulator_cmd=consts.SIMULATOR_EXECUTABLE_PATH,
    enable_rusty: bool = False,
) -> Union[SimulationResultsType, None]:
    if seed is None:
        seed = int(time.time() * 1000)

    file_name = f'{trial_count}-{n}-{p0}-{s}-{tr}-{beta}-{salt}.json'
    file_path = os.path.join(datasets_path, file_name)

    # Ensure datasets directory exists
    os.makedirs(datasets_path, exist_ok=True)

    # Generate new dataset (if necessary)
    if force_recreation or not os.path.isfile(file_path):
        if enable_rusty:
            from rustysimulator import simulate
            results = simulate(trial_count, n, p0, s0,
                               tr, beta, seed, max_cycles)
            with open(file_path, 'w') as f:
                f.write(results)
        else:
            os.system(
                f'SIM_MAX_CYCLES={int(max_cycles)} {simulator_cmd} {trial_count} {n} {p0} {s} {tr} {beta} > {file_path} 2> /dev/null')

    # Load and return simulation results
    return load_simulation_json(file_path)


def sim_s_search(n: int, p: float, tr: int, beta: float, starting_s: int = 0, ending_s: int = 100, quantile: float = 0.01, target: int = 10000, trials: int = 1000, verbose: bool = False, **kwargs) -> Tuple[int, SimulationResultsType]:
    simulations = {}
    cur_simulation = None

    s_low = starting_s
    s_high = ending_s

    while s_low < s_high:
        cur_s = (s_high + s_low) // 2
        if verbose:
            print(f"Trying {cur_s}")
        cur_simulation = load_or_generate_simulation(
            trials, n, p, cur_s, tr, beta, max_cycles=target * 2, **kwargs)
        simulations[cur_s] = cur_simulation
        quantile_val = np.quantile(cur_simulation['results'], quantile)
        if verbose:
            print(f"{cur_s} quantile: {quantile_val}")

        if quantile_val < target:
            s_low = cur_s + 1
        else:
            s_high = cur_s

    return s_low, simulations[s_low]


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
