import sys
from SimContext import SimContext


# CRIANDO AS CONFIGURAÇÕES
config = {
    'p': float(sys.argv[1]) if 2 <= len(sys.argv) else 0.01,
    'n': int(sys.argv[2]) if 3 <= len(sys.argv) else 100,
    's': int(sys.argv[3]) if 4 <= len(sys.argv) else 25,
    'tr': float(sys.argv[4]) if 5 <= len(sys.argv) else 10.0,
    'beta': float(sys.argv[5]) if 6 <= len(sys.argv) else 0.001,
}


# CRIANDO CONTEXTO DE SIMULAÇÃO
sim = SimContext(sim_config=config)


# RODANDO A SIMULAÇÃO
sim.run()
