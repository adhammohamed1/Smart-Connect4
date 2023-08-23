import pygame
from constants import colors

def apply_gradient_on_rect(
        surface: pygame.Surface, left_color: tuple[int, int, int], right_color: tuple[int, int, int], target_rect: pygame.Rect, 
        text: str|None=None, font: str='comicsans', font_size: float=15, font_color: tuple[int, int, int]=colors.BLACK, vertical: bool=False
        ):
    """
    Applies a gradient on a given target rect.

    Parameters:
        surface (pygame.Surface): The surface to draw the gradient on.
        left_colour (tuple[int, int, int]): The left colour of the gradient.
        right_colour (tuple[int, int, int]): The right colour of the gradient.
        target_rect (pygame.Rect): The rect to draw the gradient on.
        text (str, optional): The text to draw on the gradient. Defaults to None.
        font (str, optional): The font to use for the text. Defaults to 'comicsans'.
        font_size (float, optional): The font size to use for the text. Defaults to 15.
        font_color (tuple[int, int, int], optional): The font colour to use for the text. Defaults to BLACK.
        vertical (bool, optional): Whether to draw the gradient vertically or horizontally. Defaults to False.
    """

    # Create a 2x2 gradient surface
    colour_rect = pygame.Surface((2, 2))

    # Determine the direction of the gradient
    first_grad = ( (0, 0), (1, 0) ) if vertical else ( (0, 0), (0, 1) )
    second_grad = ( (1, 1), (0, 1) ) if vertical else ( (1, 0), (1, 1) )

    # Fill the surface with the gradient
    pygame.draw.line(colour_rect, left_color, *first_grad)
    pygame.draw.line(colour_rect, right_color, *second_grad)
    
    # Scale the surface to the target rect size
    colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))
    
    # Draw the scaled surface onto the target rect
    surface.blit(colour_rect, target_rect)

    if text is not None:
        text_font = pygame.font.SysFont(font, font_size)
        text_str = text_font.render(text, True, font_color)
        surface.blit(text_str, (target_rect.x + (target_rect.width / 2 - text_str.get_width() / 2), target_rect.y + (target_rect.height / 2 - text_str.get_height() / 2)))