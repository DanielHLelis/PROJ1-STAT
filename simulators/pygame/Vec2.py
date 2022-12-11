# Importing Numpy
import numpy as np


# QUÃO PRÓXIMO DOIS FLOATS DEVEM SER PARA QUE SEJAM CONSIDERADOS IGUAIS?
# É O QUE ESSA CONSTANTE DETERMINA
LEVEL_OF_SIGNIFICANCE = 2**(-16)


# CHECA SE DOIS FLOATS SÃO IGUAIS
def EQ_FLOATS (f1, f2):
    return True if (f1 == f2) or (abs(f1 - f2) < LEVEL_OF_SIGNIFICANCE) else False


class Vec2:
    """_summary_
    Vetor de duas dimensões. Apenas existe em decorrencia da minha inabilidade de usar 
    vetores do numpy de maneira apropriada. Então, decidi criar uma classe semelhante
    à classe Vector2 do Unity.
    """
    
    # RETORNA O METOR COM MENOR MAGNITUDE
    @staticmethod
    def min(v1, v2):
        return v1.copy if v1.magnitude < v2.magnitude else v2.copy
    
    def __init__ (self, x = 0.0, y = 0.0) -> None:
        
        ref = None
        
        if None == x:
            ref = [0, 0]
        elif isinstance(x, tuple) or isinstance(x, list):
            ref = list(x) + [0, 0]
            ref = ref[0:2]
        else:
            ref = [x, y]
        
        ref = tuple(map(lambda num : float(num), ref))
        self.__v = np.asarray(ref)
        self.d = 2
    
    # RETORNA CÓPIA DO VETOR NUMPY
    @property
    def v(self):
        return np.copy(self.__v)
    
    # RETORNA O VETOR NUMPY
    @property
    def vec(self):
        return self.v
    
    # RETORNA MAGNITUDE
    @property
    def magnitude (self):
        return np.linalg.norm(self.v)
    
    # RETORNA O VALOR DA COORDENADA X
    @property
    def x (self):
        return self.__v[0]
    
    # RETORNA O VALOR DA COORDENADA Y
    @property
    def y (self):
        return self.__v[1]
    
    # COPIA O VETOR INTEIRO
    @property
    def copy (self):
        return Vec2(self.x, self.y)
    
    # RETORNA UMA CÓPIA NORMALIZADA DO VETOR
    @property
    def normalized (self):
        if 0 == self.magnitude:
            return Vec2()
        else:
            n = self.copy
            n.__v /= self.magnitude
            return n
    
    def __str__ (self):
        return str(self.__v)
    
    def __eq__ (self, other):
        return True if isinstance(other, Vec2) and EQ_FLOATS(self.x, other.x) and EQ_FLOATS(self.y, other.y) else False

    def __add__(self, other):
        n = self.copy
        if isinstance(other, Vec2):
            n.__v += other.__v
        else:
            n.__v += other
        return n
    
    def __sub__(self, other):
        n = self.copy
        if isinstance(other, Vec2):
            n.__v -= other.__v
        else:
            n.__v -= other
        return n
    
    def __neg__(self):
        n = self.copy
        n.__v *= -1
        return n
    
    def __mul__(self, other):
        n = self.copy
        if isinstance(other, Vec2):
            n.__v *= other.__v
        else:
            n.__v *= other
        return n

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if 2 > self.i:
            result = self.__v[self.i]
            self.i += 1
            return result
        else:
            raise StopIteration