# BIBLIOTECAS
import pygame
import time


# MÓDULOS E CLASSES
from Manager import Manager
from Section import Section
from Machine import Machine
from Square import Square



# CONFIGURAÇÕES DA SIMULAÇÃO
STD_CONFIG = {
    'p': 0.9,
    'n': 100,
    's': 100,
    'tr': 100.0,
    'beta': 0.0
}



class SimContext:
    """_summary_
    Classe contexto de simulação (ou apenas simulação).
    """
    
    
    def __init__(self, sim_config = STD_CONFIG, win_size = (1000, 1000), title = "Sily simulation.") -> None:
        # ARMAZENANDO AS CONFIGURAÇÕES
        self.config = sim_config
        
        # ARMAZENANDO VARIÁVEIS RELEVANTES
        self.running = False
        self.win_size = tuple(win_size)
        self.title = str(title)
        self.delta_time = 1.0
        self.start_time = time.time()
        self.time_sample = [time.time(), time.time()]
        self.simulating = True
        
        width = win_size[0]
        height = win_size[1]
        
        # CRIANDO O MANAGER 
        bot_size = (int(((2/3) * height - 10) / 20), int((0.5 * width - 10) / 20))
        top_size = (int(((1/3) * height - 10) / 20), int(width / 20))
        
        self.manager = Manager({
            'FINE': Section(position=(10 + width * 0.5, height * (1/3) + 10), size=bot_size, state='FINE'),
            'BROKEN': Section(position=(0, height * (1/3) + 10), size=bot_size, state='BROKEN'),
            'AVAILABLE': Section(position=(0, 0), size=top_size, state='AVAILABLE')
        }, config=self.config)
        
        # INICIALIZANDO AS FUNCIONAIS
        for i in range(self.config['n']):
            self.manager.insert(Machine(state='FINE', config=self.config))
         
        # INICIALIZANDO AS MÁQUINAS DISPONÍVEIS  
        for i in range(self.config['s']):
            self.manager.insert(Machine(state='AVAILABLE', config=self.config))
        
        # CRIANDO BARRAS PARA SEPARAR AS MÁQUINAS
        self.divisors = [
            Square(anchor=(0.5 * width - 10, (1/3) * height), size=(18, (2/3) * height), margin=(1, 1)),
            Square(anchor=(0, (1/3) * height - 10), size=(width, 18), margin=(1, 1))
        ]

        # INICIALIZANDO O PYGAME
        pygame.init()
        self.win = pygame.display.set_mode(self.win_size)
        pygame.display.set_caption(self.title)
        
        
    # MÉTODO PARA ENCERRAR A SIMULAÇÃO PYGAME
    def quit (self):
        pygame.quit()
        
        
    # MÉTODO QUE ENCAPSULA UMA ITERAÇÃO DA SIMULAÇÃO
    def game_loop (self):
        # Recalculando o delta time
        self.calc_delta_time()
        
        # Preenchendo a janela de preto
        self.win.fill((0, 0, 0))
            
        # Atualizando e expondo o manager
        if self.simulating:
            self.manager.update(self.delta_time)
            
        self.manager.draw(self.win)
        
        for divisor in self.divisors:
            divisor.draw(self.win)
        
        # Atualizando o display
        pygame.display.update()
        
        return self
    
    
    # MÉTODO QUE EXECUTA A SIMUÇAÇÃO ATÉ O COLAPSO
    def run (self):
        self.running = True
        
        while self.running:
            for event in pygame.event.get():
                 # Checando se precisamos parar o game loop precossemente
                if event.type == pygame.QUIT:
                    self.running = False
            
            if True == self.manager.collapsed:
                break
            
            self.game_loop()
            
        print('TIME ELAPSED:', self.time_sample[1] - self.start_time , 'seconds')
        
        # Então, quando a simulação colapsa, sempre sobra duas máquinas disponíveis que nunca são usadas.
        # Eu tentei descobrir o motivo, mas eu falhei.
        # manager = self.manager
        # AVAILABLE = manager.sections['AVAILABLE']

        # # goal = AVAILABLE.moving[0].goal 
        # # anchor = AVAILABLE.moving[0].anchor
        
        # print('goal', goal)
        # print('anchor', anchor)
   
    
    # MÉTODO QUE CALCULA O DELTA TIME          
    def calc_delta_time (self):
        print('FPS', 1/self.delta_time)
        
        self.time_sample = [self.time_sample[1], time.time()]
        diff = self.time_sample[1] - self.time_sample[0]
        
        self.delta_time = 0.5 * self.delta_time + 0.5 * diff
        return self.delta_time