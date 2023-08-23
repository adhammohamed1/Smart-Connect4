import pygame
from general import *
from component import Component
import component_constants as cc
from constants import colors, config


class Button(Component):
    """
    A basic clickable button component
    """

    def __init__(
            self, surface: pygame.Surface, color: tuple[int, int, int], x: int, y: int, width: int, height: int,
            text: str|None=None,  text_font=config.DEFAULT_FONT, font_size=config.DEFAULT_FONT_SIZE, font_color=colors.BLACK, 
            shape: str=cc.SHAPE_RECT, outline_color: tuple[int, int, int]|None=None, outline_thickness: int=cc.BUTTON_DEFAULT_OUTLINE_THICKNESS,
            has_gradient_core: bool=False, core_left_color: tuple[int, int, int]|None=None, core_right_color: tuple[int, int, int]|None=None,
            has_gradient_outline: bool=False, outline_left_color: tuple[int, int, int]|None=None, outline_right_color: tuple[int, int, int]|None=None
            ):
        """
        Creates a button object

        Parameters:
            surface (pygame.Surface): The surface to draw the button on
            color (tuple[int, int, int]): The color of the button
            x (int): The x position of the button (top left corner)
            y (int): The y position of the button (top left corner)
            width (int): The width of the button
            height (int): The height of the button
            text (str): The text to display on the button
            text_font (str): The font to use for the text
            font_size (int): The size of the font
            font_color (tuple[int, int, int]): The color of the font
            shape (str): The shape of the button
            outline_color (tuple[int, int, int]): The color of the outline
            outline_thickness (int): The thickness of the outline
            has_gradient_core (bool): Whether or not the button has a gradient core
            core_left_color (tuple[int, int, int]): The left color of the gradient core
            core_right_color (tuple[int, int, int]): The right color of the gradient core
            has_gradient_outline (bool): Whether or not the button has a gradient outline
            outline_left_color (tuple[int, int, int]): The left color of the gradient outline
            outline_right_color (tuple[int, int, int]): The right color of the gradient outline

        Returns:
            Button: The button object
        """
        self.surface = surface
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text.strip() if text is not None else None
        self.has_gradient_core = has_gradient_core
        self.core_left_color = core_left_color
        self.core_right_color = core_right_color
        self.has_gradient_outline = has_gradient_outline
        self.outline_left_color = outline_left_color
        self.outline_right_color = outline_right_color
        self.shape = shape
        self.outline_color = outline_color
        self.outline_thickness = outline_thickness
        self.text_font = text_font
        self.font_size = font_size
        self.font_color = font_color


    def _draw_outline(self):
        """
        Draws the outline of the button on screen

        Returns:
            pygame.Rect: The outline of the button

        Raises:
            ValueError: If the shape is not recognized. Supported shapes are: rect, ellipse, circle
        """
        if self.shape == cc.SHAPE_RECT:
            return pygame.draw.rect( surface=self.surface, color=self.outline_color, rect=(self.x, self.y, self.width, self.height), width=0)
        if self.shape == cc.SHAPE_ELLIPSE:
            return pygame.draw.ellipse(surface=self.surface, color=self.outline_color, rect=(self.x, self.y, self.width, self.height), width=0)
        if self.shape == cc.SHAPE_CIRCLE:
            return pygame.draw.circle(surface=self.surface, color=self.outline_color, rect=(self.x, self.y, self.width, self.height), width=0)
        
        # If the shape is not recognized, raise an error
        raise ValueError(f'Unrecognized shape: {self.shape}')
    

    def _draw_core(self):
        """
        Draws the core of the button on screen

        Returns:
            pygame.Rect: The core of the button

        Raises:
            ValueError: If the shape is not recognized. Supported shapes are: rect, ellipse, circle
        """
        if self.shape == cc.SHAPE_RECT:
            return pygame.draw.rect(surface=self.surface, color=self.color, 
                rect=(self.x + self.outline_thickness, self.y + self.outline_thickness, self.width - 2 * self.outline_thickness, self.height - 2 * self.outline_thickness), width=0)
        
        if self.shape == cc.SHAPE_ELLIPSE:
            return pygame.draw.ellipse(surface=self.surface, color=self.color,
                rect=(self.x + self.outline_thickness, self.y + self.outline_thickness, self.width - 2 * self.outline_thickness, self.height - 2 * self.outline_thickness), width=0)
        
        if self.shape == cc.SHAPE_CIRCLE:
            return pygame.draw.circle(surface=self.surface, color=self.color, rect=(self.x + self.outline_thickness, self.y + self.outline_thickness, 
                                                                                    self.width - 2 * self.outline_thickness, self.height - 2 * self.outline_thickness), width=0)
        
        # If the shape is not recognized, raise an error
        raise ValueError(f'Unrecognized shape: {self.shape}')


    def draw(self):
        """
        Draws the button on screen

        Returns:
            Button: The button object

        Raises:
            ValueError: If the shape is not recognized. Supported shapes are: rect, ellipse, circle
        """
        # Draw the outline if specified
        if self.outline_color is not None:
            button_outline = self._draw_outline()

            if self.has_gradient_outline and self.shape == cc.SHAPE_RECT:
                apply_gradient_on_rect(surface=self.surface, left_color=self.outline_left_color, right_color=self.outline_right_color, target_rect=button_outline)

        # Draw the button core
        button = self._draw_core()

        # Apply a gradient to the core if specified
        if self.has_gradient_core and self.shape == cc.SHAPE_RECT:
            apply_gradient_on_rect(surface=self.surface, left_color=self.core_left_color, right_color=self.core_right_color, target_rect=button, 
                                   text=self.text, font=self.text_font, font_size=self.font_size)
        
        # Draw the text if specified
        if self.text is not None:
            font = pygame.font.SysFont(self.text_font, self.font_size)
            text = font.render(self.text, True, self.font_color)
            self.surface.blit(text, (self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

        return button


    def is_mouse_over(self):
        """
        Returns True if the mouse cursor is currently over the button, False otherwise
        """
        cursor_x, cursor_y = pygame.mouse.get_pos()

        # Check if the cursor is within the button's boundaries
        if (self.x < cursor_x <  self.x + self.width) and (self.y < cursor_y < self.y + self.height):
            return True
        
        return False


    def update(self):
        pass


    def mouseClick(self):
        pass