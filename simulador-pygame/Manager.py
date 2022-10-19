from Machine import Machine
from Section import Section


class Manager:
    """_summary_
    Classe responsável por gerenciar multiplas seções.
    """
    
    def __init__ (self, sections, config) -> None:
        self.sections = dict(sections)
        self.n = config['n']
        self.collapsed = False
        self.started = False
    
    # INSERE UMA MÁQUINA NA SEÇÃO CORRETA
    def organize (self, machine):
        try:
            self.sections[machine.state].insert(machine)
        except:
            self.sections[machine.state] = Section()
            self.sections[machine.state].insert(machine)
            
    # Mesma coisa que a função a cima, não pergunte, minha cabeça funciona assim. 
    def insert (self, machine):
        self.organize(machine)
        
    # QUANTIDADE DE MAQUINAS VALIDAS    
    @property
    def valid_machines (self):
        return (
            + self.sections['FINE'].num_machines
            + self.sections['AVAILABLE'].num_machines
        )
            
    # ATUALIZA TODAS AS SEÇÕES
    def update (self, delta_time):
        for section in self.sections.values():
            section.update(self, delta_time)
            
        if self.valid_machines < self.n:
            self.collapsed = True
            return self
        
        if self.sections['FINE'].num_machines < self.n:
            machine = self.sections['AVAILABLE'].extract_machine()
            
            if None != machine:
                machine.state = 'FINE'
                machine.match_state()
                self.sections['FINE'].insert(machine)
            
        return self

    # DESENHA TODAS AS SEÇÕES        
    def draw(self, win):
        for section in self.sections.values():
            section.draw(win)