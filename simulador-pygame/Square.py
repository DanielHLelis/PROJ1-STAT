import pygame
from Vec2 import Vec2

class Square:
    def __init__ (self, anchor = (0, 0), size = (0, 0), color = (255, 255, 255), margin = (0, 0)):
        self.anchor = Vec2(anchor)
        self.size = Vec2(size)
        self.color = tuple(color)
        self.margin = Vec2(margin)

    @property
    def descriptors (self):
        position = list(self.anchor + self.margin)
        size = list(self.size)
        return tuple(position + size)
    
    def draw (self, win):
        pygame.draw.rect(win, self.color, self.descriptors)
        return self
        