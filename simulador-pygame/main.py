from distutils.command.config import config
from SimContext import SimContext


config = {
    'p': 0.001,
    'n': 100,
    's': 200,
    'tr': 10.0,
    'beta': 0.001
}


sim = SimContext(sim_config=config)


sim.run()