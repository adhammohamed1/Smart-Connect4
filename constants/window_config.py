import colors



#################################################################
#######################  WINDOW CONFIG  #########################
#################################################################

WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 700
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)


#################################################################
#######################  BOARD CONFIG  ##########################
#################################################################

# Slot dimensions
SQUARE_SIZE = 100
PIECE_RADIUS = int(SQUARE_SIZE / 2 - 5)

# Board dimensions (in slots)
ROW_COUNT = 6
COLUMN_COUNT = 7

# Board coordinates
BOARD_BEGIN_X = 30
BOARD_BEGIN_Y = SQUARE_SIZE
BOARD_END_X = BOARD_BEGIN_X + (COLUMN_COUNT * SQUARE_SIZE)
BOARD_END_Y = BOARD_BEGIN_Y + (ROW_COUNT * SQUARE_SIZE)

# Outer board frame coordinates
BOARD_FRAME_END_X = BOARD_END_X + 2 * BOARD_BEGIN_X

# Board dimensions (in pixels)
BOARD_WIDTH = BOARD_BEGIN_X + COLUMN_COUNT * SQUARE_SIZE
BOARD_LENGTH = ROW_COUNT * SQUARE_SIZE


#################################################################
################## COMPONENT COLOR CONFIG #######################
#################################################################
BOARD_FRAME_BACKGROUND = colors.DARK_GREY
SCREEN_BACKGROUND = colors.LIGHT_GREY
FOREGROUND = colors.WHITE
CELL_BORDER_COLOR = colors.BLUE
EMPTY_CELL_COLOR = colors.GREY
