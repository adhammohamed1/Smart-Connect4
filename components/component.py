import pygame
from abc import ABC, abstractmethod

class Component(ABC):

    @abstractmethod
    def draw():
        pass

    @abstractmethod
    def update():
        pass

    @abstractmethod
    def is_mouse_over():
        pass

    @abstractmethod
    def mouseClick():
        pass