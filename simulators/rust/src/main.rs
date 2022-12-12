use std::collections::LinkedList;
use std::env;
use std::fs;
use std::process;
use std::time::{SystemTime, UNIX_EPOCH};

extern crate rand;
extern crate rand_pcg;
extern crate rayon;
extern crate serde;
extern crate serde_json;

use rand::prelude::*;
use rayon::prelude::*;
use serde::Serialize;

// Max cycles per simulation
const MAX_CYCLES: i64 = 50000;

// Machine State Data
#[derive(Copy, Clone)]
struct MachineState {
    // id: i64,
    run_begin: i64,
    repair_end: i64,
}

// Simulation Configs
#[derive(Copy, Clone, Serialize)]
struct SimulationConfigs {
    n: i64,
    p0: f64,
    s0: i64,
    tr: i64,
    beta: f64,
    seed: u64,
}

// Simulation State Data
struct SimulationState {
    configs: SimulationConfigs,
    clock: i64,
    running: i64,
    rng: rand_pcg::Pcg64,
    machines: Vec<MachineState>,
    idle: LinkedList<usize>,
}

// Simulation Impl
impl SimulationState {
    fn new(configs: SimulationConfigs) -> SimulationState {
        let mut simulation_state = SimulationState {
            configs: configs,
            clock: 0,
            running: configs.n,
            rng: rand_pcg::Pcg64::seed_from_u64(configs.seed),
            machines: Vec::with_capacity((configs.n + configs.s0).try_into().unwrap()),
            idle: LinkedList::new(),
        };

        for _ in 0..configs.n {
            simulation_state.machines.push(MachineState {
                // id: i,
                repair_end: 0,
                run_begin: 1,
            });
        }

        for i in 0..configs.s0 {
            simulation_state.machines.push(MachineState {
                // id: i + configs.n,
                repair_end: 0,
                run_begin: 0,
            });

            simulation_state
                .idle
                .push_back((i + configs.n).try_into().unwrap());
        }

        return simulation_state;
    }

    fn p(configs: SimulationConfigs, clock: i64, machine: &MachineState) -> f64 {
        (configs.p0 + configs.beta * (clock as f64 - machine.run_begin as f64)).min(1.0)
    }

    pub fn next(&mut self) -> bool {
        self.clock += 1;

        // println!("Clock {}\n", self.clock);

        let mut current_broken = self.configs.n - self.running;
        for (i, machine) in self.machines.iter_mut().enumerate() {
            if machine.repair_end != 0 && machine.repair_end <= self.clock {
                machine.repair_end = 0;
                self.idle.push_back(i);
                // println!("Repaired {}", i);
            }

            if machine.run_begin != 0 {
                // Check Break
                if self
                    .rng
                    .gen_bool(SimulationState::p(self.configs, self.clock, &*machine))
                {
                    machine.run_begin = 0;
                    machine.repair_end = self.clock + self.configs.tr;
                    current_broken += 1;
                    // println!("Broke {}", i);
                }
            }
        }

        while current_broken > 0 && !self.idle.is_empty() {
            let new_idx = self.idle.pop_front().unwrap();
            self.machines[new_idx].run_begin = self.clock;
            current_broken -= 1;
            // println!("Recovered {}", new_idx);
        }

        self.running = self.configs.n - current_broken;

        return self.running < self.configs.n;
    }

    fn run_trial(configs: SimulationConfigs) -> (i64, i64) {
        let mut state: SimulationState = SimulationState::new(configs);

        let mut z: i64 = 0;
        while !state.next() {
            if state.clock >= MAX_CYCLES {
                eprintln!("Exceeded max cycles");
                break;
            }

            // Compute Z
            let availability: f64 = if state.configs.s0 != 0 {
                (state.idle.len() as f64) / (state.configs.s0 as f64)
            } else {
                0.0
            };

            if z == 0 && availability < 0.2 {
                z = state.clock;
            }
        }

        if z == 0 {
            z = state.clock;
        }

        return (state.clock, z);
    }
}

// Result Container
#[derive(Serialize)]
struct Results {
    trial_count: i64,
    configs: SimulationConfigs,
    results: Vec<i64>,
    results_z: Vec<i64>,
}

fn main() {
    let args: Vec<String> = env::args().collect();

    // Validate program args
    if args.len() < 6 {
        println!("{{trial_count}} {{n}} {{p0}} {{s0}} {{tr}} are required");
        process::exit(1);
    }

    // N trials to compute
    let trial_count: i64 = args[1].parse().unwrap();

    // Params
    let n: i64 = args[2].parse().unwrap();
    let p0: f64 = args[3].parse().unwrap();
    let s: i64 = args[4].parse().unwrap();
    let tr: i64 = args[5].parse().unwrap();

    // Beta Value
    let beta: f64 = if args.len() >= 7 {
        args[6].parse().unwrap()
    } else {
        0.0
    };

    // RNG Seeder
    let seed: u64 = if args.len() >= 8 {
        args[7].parse().unwrap()
    } else {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64
    };
    // Seed RNG
    let mut seed_generator = rand_pcg::Pcg64::seed_from_u64(seed);

    // Base configs
    let configs = SimulationConfigs {
        n,
        p0,
        s0: s,
        tr,
        beta,
        seed,
    };

    // Result Struct
    let mut results = Results {
        trial_count,
        configs,
        results: Vec::with_capacity(trial_count as usize),
        results_z: Vec::with_capacity(trial_count as usize),
    };

    // Temporary Vector to store simulation results
    let mut tmp_results: Vec<(i64, i64)> = Vec::with_capacity(trial_count as usize);

    // Parallel Trials
    let seeds: Vec<u64> = (0..trial_count)
        .map(|_| seed_generator.next_u64())
        .collect();
    seeds
        .par_iter()
        .map(|s| {
            let mut current_config = configs;
            current_config.seed = *s;

            return SimulationState::run_trial(current_config);
        })
        .collect_into_vec(&mut tmp_results);

    // Fill results
    for (r, z) in tmp_results.iter() {
        results.results.push(*r);
        results.results_z.push(*z);
    }

    // Try creating dir, ignore any errors
    let _ = fs::create_dir_all("results");
    // Write final JSON
    println!("{}", serde_json::to_string(&results).unwrap());
}
