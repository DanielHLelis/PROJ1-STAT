from distutils.command.config import config
from SimContext import SimContext


config = {
    'p': 0.001,
    'n': 100,
    's': 10,
    'tr': 5.0,
    'beta': 0.0
}


sim = SimContext(sim_config=config)


sim.run()