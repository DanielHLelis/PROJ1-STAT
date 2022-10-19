import pygame
from Vec2 import Vec2
from Square import Square
from random import random
from scipy.stats import poisson


# CORES
WHITE = (255, 255, 255)
RED = (255, 64, 64)
BLUE = (64, 64, 255)
GREEN = (64, 255, 64)


class Machine(Square):
    """_summary_
    Essa classe representa 
    """
    
    # CONSTANTES DA CLASSE
    VEL = 500
    STATES = ('FINE', 'AVAILABLE', 'BROKEN')
    DIMENSIONS = (20, 20)
    SIZE = (18, 18)
    MARGIN = (1, 1)
    
    # VARIÁVEIS DA CLASSE
    next_id = 1
    
    
    def __init__(self, state, config, anchor = (0, 0), goal = None):
        # INICIALIZANDO CARACTERISTICAS DE UM QUADRADO
        super().__init__(
            anchor = anchor, 
            size = Machine.SIZE, 
            color = WHITE, 
            margin = Machine.MARGIN
        )
        
        # INICIALIZANDO VARIÁVEIS FÍSICAS E INTERNAS
        self.id = Machine.next_id
        Machine.next_id += 1
        self.state = str(state)
        self.dimensions = Vec2(Machine.DIMENSIONS)
        self.goal = None if None == goal else Vec2(goal)
        self.coord = (0, 0)
        
        # INICIALIZANDO VARIÁVEIS DE SIMULAÇÃO
        self.max_p = float(config['p'])
        self.p = self.max_p
        self.beta = float(config['beta'])
        self.max_tr = float(config['tr'])
        self.tr = self.max_tr
        
        self.match_state()
        
        
    # MÉTODO PARA GARANTIR QUE A COR ESTÁ CERTA
    def match_state (self):
        if 'FINE' == self.state:
            self.color = GREEN
        elif 'AVAILABLE' == self.state:
            self.color = BLUE
        elif 'BROKEN' == self.state:
            self.color = RED
            self.max_tr = Machine.TEMPO_DE_REPARO
        
        
    # MÉTODO PARA CALCULAR A PROBABILIDADE EM DETERMINADO INTERVALO
    def get_probability (self, delta_time):
        p = self.p
        not_p = 1 - p
    
        discrete_interval = int(delta_time)
        fractional_interval = delta_time - discrete_interval
        
        not_discrete_p = not_p ** discrete_interval
        fractional_p = p * fractional_interval
        not_fractional_p = 1 -fractional_p
        
        not_total_p = not_discrete_p * not_fractional_p
        total_p = 1 - not_total_p
        
        return total_p
            
            
    # METODO PARA MOVER A MÁQUINA
    def move(self, delta_time):
        if None == self.goal:
            return self
        
        if self.anchor == self.goal:
            self.goal = None
            return self
        
        diff = self.goal - self.anchor
        
        movemment = diff.normalized * Machine.VEL * delta_time
        movemment = Vec2.min(movemment, diff)
        
        self.anchor += movemment
        
        return self


    # MÉTODO PARA DETERMINAR UMA NOVA POSIÇÃO PARA A MÁQUINA
    def goto (self, goal):
        self.goal = Vec2(goal)
        return self
        
        
    # MÉTODO PARA ATUALIZAR O ESTADO DA MÁQUINA
    def update (self, delta_time):
        r = random()
        
        if 'FINE' == self.state:
            if r <= self.get_probability(delta_time):
                self.state = 'BROKEN'
                self.max_tr = self.max_tr
                self.color = RED
            else:
                self.p += self.beta
        elif 'BROKEN' == self.state:
            self.max_tr -= delta_time
            if 0 >= self.max_tr:
                self.p = self.max_p
                self.state = 'AVAILABLE'
                self.color = BLUE
        
        return self
    
    # MÉTODO PARA CHECAR ESTADO DA MÁQUINA
    def check_state (self, state):
        return self.state == state
    
    
        