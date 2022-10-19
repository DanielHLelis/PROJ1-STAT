from Machine import Machine
from Vec2 import Vec2
import numpy as np


# TO-DO
# OBS: Se não houver espaço disponivel, a seção dá bug ao tentar inserir uma máquina.


class Section:
    """_summary_
    Essa classe representa uma seção de máquinas, todas com o mesmo estado.
    """
    
    def __init__(self, position = (0, 0), size = (10, 10), state = 'FINE', min_machines = 0, availability = False):
        self.moving = [] # Lista de máquinas em movimento para essa seção
        self.machines = [] # Lista de máquinas estáticas em movimento
        self.position = Vec2(position) 
        self.m = np.asarray(size[0] * [size[1] * [0]]) # Matris de posições ocupadas ou livres
        self.state = 'FINE'
        self.num_machines = 0
    
    # DESENHA TODAS AS MÁQUINAS
    def draw (self, win):
        for machine in self.moving:
            machine.draw(win)
        for machine in self.machines:
            machine.draw(win)
    
    # MOVE TODAS AS MÁQUINAS QUE PRECISAM SE MOVER
    def move (self, delta_time = 1):
        for machine in self.moving:
            machine.move(delta_time)
        return self
    
    # BUSCA O PRÓXIMO ESTADO DISPONÍVEL
    @property
    def next_slot (self):
        tmp = np.where(self.m == 0)
        return (tmp[0][0], tmp[1][0]) if tmp and len(tmp) else None
    
    # RETORNA UMA MÁQUINA
    @property
    def next_machine (self):
        return None if 0 == len(self.machines) else self.machines.pop(0)
    
    # INSERE UMA MÁQUINA
    # O(n2): Ineficiente, eu sei. Mas, funciona por hora.
    def insert (self, machine):
        if isinstance(machine, list) or isinstance(machine, tuple):
            for m in machine:
                self.insert(m)
        
        self.moving.append(machine)
        slot = self.next_slot # Parte ineficiente.
        self.m[slot[0], slot[1]] = machine.id
        machine.coords = slot
        machine.goto(self.gen_machine_position(slot))
        self.num_machines += 1
    
    # GERA A POSIÇÃO QUE UMA MÁQUINA DEVE ASSUMIR
    def gen_machine_position (self, slot):
        return tuple(self.position + (Vec2(Machine.DIMENSIONS) * Vec2([slot[1], slot[0]]) * Vec2(1.0, 1.0)))
    
    # REMOVE UMA MAQUINA
    def remove (self, machine):
        self.m[machine.coords[0]][machine.coords[1]] = 0
        self.num_machines -= 1
    
    # EXTRAI UMA MÁQUINA
    def extract_machine (self):
        machine = self.next_machine
        
        if None == machine:
            return None
        
        self.remove(machine)
        return machine
    
    # ATUALIZA ESTADO E POSIÇÃO DE TODAS AS MÁQUINAS
    def update (self, manager, delta_time):
        if len(self.moving):
            for index, machine in enumerate(self.moving):
                machine.move(delta_time)
                if None == machine.goal or machine.goal == machine.anchor:
                    self.moving.pop(index)
                    self.machines.append(machine)
        
        if len(self.machines):
            for index, machine in enumerate(self.machines):
                machine.update(delta_time)
                if not machine.check_state(self.state):
                    self.machines.pop(index)
                    self.remove(machine)
                    manager.organize(machine)
        
        