import random
import collections
import sys
import os
import time
import json
import multiprocessing


INF = int(2 ** 63 - 1)


class FactorySimulator:
    n: int  # Number of machines required for the system to work
    p0: float  # Initial probability of failure
    s0: int  # Backup Machines
    beta: float  # Failure increase rate
    tr: int  # Machine recovery time

    _rng: random.Random
    _clock: int

    _machines: list  # (id, run_begin, repair_end)
    _running: int
    _idle: collections.deque

    def __init__(self, n: int, p0: float, s0: int, tr: int, beta: float,
                 seed: int = int(1984), *args, **kwargs):
        if n is None:
            raise ValueError("n must not be None")
        if p0 is None:
            raise ValueError("p0 must not be None")
        if s0 is None:
            raise ValueError("s0 must not be None")
        if beta is None:
            raise ValueError("beta must not be None")
        if tr is None:
            raise ValueError("tr must not be None")

        self.n = int(n)
        self.p0 = float(p0)
        self.s0 = int(s0)
        self.beta = float(beta)
        self.tr = int(tr)

        self._clock = int(0)
        self._rng = random.Random(seed)

        running_machines = [[i, 1, 0] for i in range(0, self.n)]
        idle_machines = [[i, 0, 0] for i in range(self.n, self.n + self.s0)]
        self._machines = [*running_machines, *idle_machines]
        self._running = int(self.n)
        self._idle = collections.deque(idle_machines)

    @property
    def machines(self):
        return self._machines

    def _p(self, machine: list) -> float:
        return self.p0 + self.beta * (self._clock - machine[1])

    def _break(self, machine: list) -> bool:
        return self._rng.random() <= self._p(machine)

    def next_state(self):
        self._clock += 1

        n_broken = self.n - self._running
        for machine in self._machines:
            if machine[2] != 0 and machine[2] <= self._clock:
                # print(f"Repair {machine}")
                machine[2] = 0
                self._idle.append(machine)

            if machine[1] != 0 and self._break(machine):
                # print(f"Broken {machine}")
                machine[2] = self._clock + self.tr
                machine[1] = 0
                n_broken += 1

        while n_broken > 0 and len(self._idle) > 0:
            target = self._idle.popleft()
            # print(f"Recovered {target}")
            target[1] = self._clock
            n_broken -= 1

        self._running = self.n - n_broken
        assert self._running <= self.n

        return {
            'clock': self._clock,
            'critical': self._running < self.n
        }


def factory_trial(*args, **kwargs):
    if isinstance(args[0], tuple):
        simulator = FactorySimulator(*args[0])
    else:
        simulator = FactorySimulator(*args, **kwargs)

    n = 0
    z = 0
    while True:
        st = simulator.next_state()

        availability = 0 if simulator.s0 == 0 else len(
            simulator._idle) / simulator.s0
        if z == 0 and availability < 0.2:
            z = simulator._clock

        if st['critical']:
            n = simulator._clock
            break

    if z == 0:
        z = n

    return (n, z)


def multiple_trials(trial_count: int, n: int, p0: float, s0: int, tr: int, beta: float, seed: int, parallel: bool = True, parallel_threshold: int = 10000):
    rng = random.Random(seed)
    seeds = [rng.randint(0, INF) for _ in range(trial_count)]

    if not parallel or trial_count < parallel_threshold:
        results = [factory_trial(n, p0, s0, tr, beta, seed=seeds[i])
                   for i in range(trial_count)]
    else:
        pool = multiprocessing.Pool()
        results = pool.map(
            factory_trial, [(n, p0, s0, tr, beta, s) for s in seeds])

    data = {
        'trial_count': trial_count,
        'configs': {
            'n': n,
            'p0': p0,
            's0': s0,
            'tr': tr,
            'beta': beta,
            'seed': seed
        },
        'results': [r[0] for r in results],
        'results_z': [r[1] for r in results]
    }

    return data


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Args: {trial_count} {n} {p0} {s0} {tr} [beta] [seed]")
        exit(1)

    trial_count = int(sys.argv[1])

    n = int(sys.argv[2])
    p0 = float(sys.argv[3])
    s0 = int(sys.argv[4])

    tr = INF if sys.argv[5].strip().lower().startswith(
        'inf') else int(sys.argv[5])

    beta = 0 if len(sys.argv) < 7 else float(sys.argv[6])
    seed = int(time.time() * 1000) if len(sys.argv) < 8 else int(sys.argv[7])

    data = multiple_trials(trial_count, n, p0, s0, tr, beta, seed)

    def escape(x): return str(x).replace('.', '_')

    try:
        os.mkdir('results')
    except Exception as _:
        pass

    file_name = f'results/{trial_count}-{n}-{escape(p0)}-{s0}-{tr}-{escape(beta)}-{seed}.json'

    with open(file_name, 'w') as f:
        json.dump(data, f)
