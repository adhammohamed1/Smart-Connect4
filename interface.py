import math
import sys
from tkinter import messagebox, simpledialog

import numpy as np
import pygame

import Button as btn

#   Window Dimensions   #
WIDTH = 1050
HEIGHT = 700
WINDOW_SIZE = (WIDTH, HEIGHT)

#   Color Values    #
WHITE = (255, 255, 255)
LIGHTGREY = (170, 170, 170)
GREY = (85, 85, 85)
DARKGREY = (50, 50, 50)
DARKER_GREY = (35, 35, 35)
BLACK = (0, 0, 0)
RED = (230, 30, 30)
DARKRED = (150, 0, 0)
GREEN = (30, 230, 30)
DARKGREEN = (0, 190, 0)
BLUE = (30, 30, 122)
CYAN = (30, 230, 230)
GOLD = (225, 185, 0)
DARKGOLD = (165, 125, 0)

#   Component Colors   #
BOARD_LAYOUT_BACKGROUND = DARKGREY
SCREEN_BACKGROUND = LIGHTGREY
FOREGROUND = WHITE
CELL_BORDER_COLOR = BLUE
EMPTY_CELL_COLOR = GREY

#   Board Dimensions #
ROW_COUNT = 6
COLUMN_COUNT = 7

#   Component Dimensions    #
SQUARE_SIZE = 100
PIECE_RADIUS = int(SQUARE_SIZE / 2 - 5)

#   Board Coordinates   #
BOARD_BEGIN_X = 30
BOARD_BEGIN_Y = SQUARE_SIZE
BOARD_END_X = BOARD_BEGIN_X + (COLUMN_COUNT * SQUARE_SIZE)
BOARD_END_Y = BOARD_BEGIN_Y + (ROW_COUNT * SQUARE_SIZE)

BOARD_LAYOUT_END_X = BOARD_END_X + 2 * BOARD_BEGIN_X

#   Board Dimensions    #
BOARD_WIDTH = BOARD_BEGIN_X + COLUMN_COUNT * SQUARE_SIZE
BOARD_LENGTH = ROW_COUNT * SQUARE_SIZE

#   Player Variables    #
PIECE_COLORS = (GREY, RED, GREEN)
PLAYER1 = 1
PLAYER2 = 2
EMPTY_CELL = 0

#   Game-Dependent Global Variables    #
TURN = 1
GAME_OVER = False
PLAYER_SCORE = [0, 0, 0]
depth = 1
board = [[]]
usePruning = True


def setupFrame():
    """
    Initializes the all components in the frame
    """
    global screen, board
    screen = pygame.display.set_mode(WINDOW_SIZE)
    board = createBoard(EMPTY_CELL)
    pygame.display.set_caption('Smart Connect4 :)')
    refreshFrame()


def refreshFrame():
    """
    Refreshes the screen and all the components
    """
    pygame.display.flip()
    refreshBackground()
    drawBoard()
    drawButtons()
    drawLabels()


def refreshBackground():
    """
    Refreshes screen background
    """
    gradientRect(screen, BLACK, GREY, pygame.draw.rect(screen, SCREEN_BACKGROUND, (0, 0, WIDTH, HEIGHT)))


######   Labels    ######

def drawLabels():
    """
    Draws all labels on the screen
    """
    titleFont = pygame.font.SysFont("Sans Serif", 40, False, True)
    mainLabel = titleFont.render("Smart Connect4", True, WHITE)
    screen.blit(mainLabel, (BOARD_LAYOUT_END_X + 20, 30))

    if not GAME_OVER:
        captionFont = pygame.font.SysFont("Arial", 15)
        player1ScoreCaption = captionFont.render("Player1", True, BLACK)
        player2ScoreCaption = captionFont.render("Player2", True, BLACK)
        screen.blit(player1ScoreCaption, (BOARD_LAYOUT_END_X + 48, 210))
        screen.blit(player2ScoreCaption, (BOARD_LAYOUT_END_X + 170, 210))

        depthFont = pygame.font.SysFont("Serif", 23 - len(str(depth)))
        depthLabel = depthFont.render("k = " + str(depth), True, BLACK)
        screen.blit(depthLabel, (WIDTH - 100, 294))

        depthFont = pygame.font.SysFont("Arial", 16)
        depthLabel = depthFont.render("Use alpha-beta pruning", True, BLACK)
        screen.blit(depthLabel, (BOARD_LAYOUT_END_X + 65, 340))

    else:
        if PLAYER_SCORE[PLAYER1] == PLAYER_SCORE[PLAYER2]:
            verdict = 'DRAW :)'
        elif PLAYER_SCORE[PLAYER1] > PLAYER_SCORE[PLAYER2]:
            verdict = 'Player 1 Wins!'
        else:
            verdict = 'Player 2 Wins!'

        verdictFont = pygame.font.SysFont("Serif", 40)
        verdictLabel = verdictFont.render(verdict, True, GOLD)
        screen.blit(verdictLabel, (BOARD_BEGIN_X + BOARD_END_X / 3, BOARD_BEGIN_Y / 3))

    refreshScores()
    refreshStats()


def refreshScores():
    """
    Refreshes the scoreboard
    """
    if GAME_OVER:
        scoreBoard_Y = BOARD_BEGIN_Y
    else:
        scoreBoard_Y = 120

    pygame.draw.rect(screen, BLACK, (BOARD_LAYOUT_END_X + 9, scoreBoard_Y - 1, 117, 82), 0)
    player1ScoreSlot = pygame.draw.rect(screen, BOARD_LAYOUT_BACKGROUND,
                                        (BOARD_LAYOUT_END_X + 10, scoreBoard_Y, 115, 80))

    pygame.draw.rect(screen, BLACK, (BOARD_LAYOUT_END_X + 134, scoreBoard_Y - 1, 117, 82), 0)
    player2ScoreSlot = pygame.draw.rect(screen, BOARD_LAYOUT_BACKGROUND,
                                        (BOARD_LAYOUT_END_X + 135, scoreBoard_Y, 115, 80))

    scoreFont = pygame.font.SysFont("Sans Serif", 80)
    player1ScoreCounter = scoreFont.render(str(PLAYER_SCORE[PLAYER1]), True, PIECE_COLORS[1])
    player2ScoreCounter = scoreFont.render(str(PLAYER_SCORE[PLAYER2]), True, PIECE_COLORS[2])

    player1ScoreLength = player2ScoreLength = 2.7
    if PLAYER_SCORE[PLAYER1] > 0:
        player1ScoreLength += math.log(PLAYER_SCORE[PLAYER1], 10)
    if PLAYER_SCORE[PLAYER2] > 0:
        player2ScoreLength += math.log(PLAYER_SCORE[PLAYER2], 10)

    screen.blit(player1ScoreCounter,
                (player1ScoreSlot.x + player1ScoreSlot.width / player1ScoreLength, scoreBoard_Y + 15))
    screen.blit(player2ScoreCounter,
                (player2ScoreSlot.x + player2ScoreSlot.width / player2ScoreLength, scoreBoard_Y + 15))


def refreshStats():
    """
    Refreshes the analysis section
    """
    pygame.draw.rect(screen, BLACK, (BOARD_LAYOUT_END_X + 9, 369, WIDTH - BOARD_LAYOUT_END_X - 18, 267), 0)
    pygame.draw.rect(screen, GREY, (BOARD_LAYOUT_END_X + 10, 370, WIDTH - BOARD_LAYOUT_END_X - 20, 265))


######   Buttons    ######

def drawButtons():
    """
    Draws all buttons on the screen
    """
    global showStatsButton, contributorsButton, modifyDepthButton, playAgainButton, pruningCheckbox
    contributorsButton = btn.Button(
        screen, color=LIGHTGREY,
        x=BOARD_LAYOUT_END_X + 10, y=650,
        width=WIDTH - BOARD_LAYOUT_END_X - 20, height=30, text="Contributors")
    contributorsButton.draw(BLACK)

    if not GAME_OVER:
        modifyDepthButton = btn.Button(
            screen, color=LIGHTGREY,
            x=BOARD_LAYOUT_END_X + 10, y=290,
            width=WIDTH - BOARD_LAYOUT_END_X - 120, height=30, text="Modify depth k")
        modifyDepthButton.draw(BLACK)

        pruningCheckbox = btn.Button(
            screen, color=WHITE,
            x=BOARD_LAYOUT_END_X + 35, y=340,
            width=20, height=20, text="",
            gradCore=usePruning, coreLeftColor=DARKGOLD, coreRightColor=GOLD,
            gradOutline=True, outLeftColor=LIGHTGREY, outRightColor=GREY)

        pruningCheckbox.draw(WHITE, 4)

        showStatsButton_Y = 250
    else:
        showStatsButton_Y = 330

        playAgainButton = btn.Button(
            screen=screen, color=GOLD, x=BOARD_LAYOUT_END_X + 10, y=BOARD_BEGIN_Y + 100,
            width=WIDTH - BOARD_LAYOUT_END_X - 20, height=120, text="Play Again")
        playAgainButton.draw()

    showStatsButton = btn.Button(
        screen, color=LIGHTGREY,
        x=BOARD_LAYOUT_END_X + 10, y=showStatsButton_Y,
        width=WIDTH - BOARD_LAYOUT_END_X - 20, height=30, text="Show nerdy stats :D")
    showStatsButton.draw(BLACK)


def togglePruningCheckbox():
    global usePruning, pruningCheckbox
    usePruning = pruningCheckbox.isChecked = pruningCheckbox.gradCore = not usePruning
    pruningCheckbox.draw(WHITE, 4)


######   Game Board  ######

def createBoard(initialCellValue):
    """
    Initializes the game board with the value given.
    :param initialCellValue: Value of initial cell value
    :return: board list with all cells initialized to initialCellValue
    """
    global board
    board = np.full((ROW_COUNT, COLUMN_COUNT), initialCellValue)
    return board


def printBoard():
    """
    Prints the game board to the terminal
    """
    print('\n-\n' +
          str(board) +
          '\n Player ' + str(TURN) + ' plays next')


def drawBoard():
    """
    Draws the game board on the interface with the latest values in the board list
    """
    pygame.draw.rect(screen, BLACK, (0, 0, BOARD_LAYOUT_END_X, HEIGHT), 0)
    boardLayout = pygame.draw.rect(
        screen, BOARD_LAYOUT_BACKGROUND, (0, 0, BOARD_LAYOUT_END_X - 1, HEIGHT))
    gradientRect(screen, DARKER_GREY, DARKGREY, boardLayout)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            col = BOARD_BEGIN_X + (c * SQUARE_SIZE)
            row = BOARD_BEGIN_Y + (r * SQUARE_SIZE)
            piece = board[r][c]
            pygame.draw.rect(
                screen, CELL_BORDER_COLOR, (col, row, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(
                screen, PIECE_COLORS[piece], (int(col + SQUARE_SIZE / 2), int(row + SQUARE_SIZE / 2)), PIECE_RADIUS)
    pygame.display.update()


def hoverPiece():
    """
    Hovers the piece over the game board with the corresponding player's piece color
    """
    boardLayout = pygame.draw.rect(screen, BOARD_LAYOUT_BACKGROUND,
                                   (0, BOARD_BEGIN_Y - SQUARE_SIZE, BOARD_WIDTH + SQUARE_SIZE / 2, SQUARE_SIZE))
    gradientRect(screen, DARKER_GREY, DARKGREY, boardLayout)
    posx = pygame.mouse.get_pos()[0]
    if BOARD_BEGIN_X < posx < BOARD_END_X:
        pygame.mouse.set_visible(False)
        pygame.draw.circle(screen, PIECE_COLORS[TURN], (posx, int(SQUARE_SIZE / 2)), PIECE_RADIUS)
    else:
        pygame.mouse.set_visible(True)


def dropPiece(col, piece):
    """
    Drops the given piece in the next available slot in col
    :param col: Column index where the piece will be dropped
    :param piece: Value of the piece to be put in array.
    """
    row = getNextOpenRow(col)
    board[row][col] = piece

    return row, col


def hasEmptySlot(col):
    """
    Checks if current column has an empty slot. Assumes col is within array limits
    :param col: Column index
    :return: True if column has an empty slot. False otherwise.
    """
    return board[0][col] == EMPTY_CELL


def getNextOpenRow(col):
    """
    Gets the next available slot in the column
    :param col: Column index
    :return: If exists, the row of the first available empty slot in the column. None otherwise.
    """
    for r in range(ROW_COUNT - 1, -1, -1):
        if board[r][col] == EMPTY_CELL:
            return r
    return None


def boardIsFull():
    """
    Checks if the board game is full
    :return: True if the board list has no empty slots, False otherwise.
    """
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            if board[r][c] == EMPTY_CELL:
                return False
    return True


def getBoardColumnFromPos(posx):
    """
    Get the index of the board column corresponding to the given position
    :param posx: Position in pixels
    :return: If within board bounds, the index of corresponding column, None otherwise
    """
    column = int(math.floor(posx / SQUARE_SIZE))
    if 0 <= column < COLUMN_COUNT:
        return column
    return None


def switchTurn():
    """
    Switch turns between player 1 and player 2
    """
    global TURN
    if TURN == 1:
        TURN = 2
    else:
        TURN = 1


def alterButtonAppearance(button, color, outline,
                          hasGradBackground=False, gradLeftColor=None, gradRightColor=None, fontSize=15):
    """
    Alter button appearance with given colors
    :param hasGradBackground: Flag which indicates if the button background should be a gradient
    """
    button.color = color
    thisButton, buttonRect = button.draw(outline)
    if hasGradBackground:
        gradientRect(screen, gradLeftColor, gradRightColor, buttonRect, thisButton.text, 'comicsans', fontSize)


def buttonResponseToMouseEvent(event):
    """
    Handles button behaviour in response to mouse events influencing them
    """
    if event.type == pygame.MOUSEMOTION:
        if showStatsButton.isOver(event.pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            alterButtonAppearance(showStatsButton, WHITE, BLACK)
        elif contributorsButton.isOver(event.pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            alterButtonAppearance(contributorsButton, WHITE, BLACK)
        elif not GAME_OVER and modifyDepthButton.isOver(event.pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            alterButtonAppearance(modifyDepthButton, WHITE, BLACK)
        elif not GAME_OVER and pruningCheckbox.isOver(event.pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif GAME_OVER and playAgainButton.isOver(event.pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            alterButtonAppearance(playAgainButton, WHITE, BLACK, True, WHITE, GOLD, 22)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            alterButtonAppearance(showStatsButton, LIGHTGREY, BLACK)
            alterButtonAppearance(contributorsButton, LIGHTGREY, BLACK)
            if not GAME_OVER:
                alterButtonAppearance(modifyDepthButton, LIGHTGREY, BLACK)
            else:
                alterButtonAppearance(playAgainButton, GOLD, BLACK)

    if event.type == pygame.MOUSEBUTTONDOWN:
        if showStatsButton.isOver(event.pos):
            alterButtonAppearance(showStatsButton, CYAN, BLACK)
        elif contributorsButton.isOver(event.pos):
            alterButtonAppearance(contributorsButton, CYAN, BLACK)
        elif not GAME_OVER and modifyDepthButton.isOver(event.pos):
            alterButtonAppearance(modifyDepthButton, CYAN, BLACK)
        elif not GAME_OVER and pruningCheckbox.isOver(event.pos):
            togglePruningCheckbox()
        elif GAME_OVER and playAgainButton.isOver(event.pos):
            alterButtonAppearance(playAgainButton, GOLD, BLACK, True, GOLD, CYAN)

    if event.type == pygame.MOUSEBUTTONUP:
        if showStatsButton.isOver(event.pos):
            alterButtonAppearance(showStatsButton, LIGHTGREY, BLACK)
        elif contributorsButton.isOver(event.pos):
            alterButtonAppearance(contributorsButton, LIGHTGREY, BLACK)
            showContributors()
        elif not GAME_OVER and modifyDepthButton.isOver(event.pos):
            alterButtonAppearance(modifyDepthButton, LIGHTGREY, BLACK)
            takeNewDepth()
        elif GAME_OVER and playAgainButton.isOver(event.pos):
            alterButtonAppearance(playAgainButton, GOLD, BLACK, True, WHITE, GOLD)
            resetEverything()


def takeNewDepth():
    """
    Invoked at pressing modify depth button. Displays a simple dialog that takes input depth from user
    """
    global depth
    temp = simpledialog.askinteger('Enter depth', 'Enter depth k')
    if temp is not None and temp > 0:
        depth = temp
    refreshFrame()


def showContributors():
    """
    Invoked at pressing the contributors button. Displays a message box Containing names and IDs of contributors
    """
    messagebox.showinfo('Contributors', "6744   -   Adham Mohamed Aly\n"
                                        "6905   -   Mohamed Farid Abdelaziz\n"
                                        "7140   -   Yousef Ashraf Kotp\n")


def gameSession():
    """
    Runs the game session
    """
    global GAME_OVER, TURN
    while True:
        if not GAME_OVER:
            hoverPiece()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            buttonResponseToMouseEvent(event)

            if not GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN:
                posx = event.pos[0] - BOARD_BEGIN_X
                column = getBoardColumnFromPos(posx)

                if column is not None:
                    if hasEmptySlot(column):
                        pieceLocation = dropPiece(column, TURN)
                        PLAYER_SCORE[TURN] += sequencesFormed(pieceLocation, TURN)
                        switchTurn()

                        # printBoard()
                        refreshFrame()

                    if boardIsFull():
                        GAME_OVER = True
                        pygame.mouse.set_visible(True)
                        refreshFrame()


def resetEverything():
    global board, PLAYER_SCORE, GAME_OVER, TURN
    PLAYER_SCORE = [0, 0, 0]
    GAME_OVER = False
    TURN = 1
    setupFrame()


def gradientRect(window, left_colour, right_colour, target_rect, text=None, font='comicsans', fontSize=15):
    """
    Draw a horizontal-gradient filled rectangle covering <target_rect>
    """
    colour_rect = pygame.Surface((2, 2))  # tiny! 2x2 bitmap
    pygame.draw.line(colour_rect, left_colour, (0, 0), (0, 1))  # left colour line
    pygame.draw.line(colour_rect, right_colour, (1, 0), (1, 1))  # right colour line
    colour_rect = pygame.transform.smoothscale(colour_rect, (target_rect.width, target_rect.height))  # stretch!
    window.blit(colour_rect, target_rect)

    if text:
        font = pygame.font.SysFont(font, fontSize)
        text = font.render(text, True, (0, 0, 0))
        window.blit(text, (
            target_rect.x + (target_rect.width / 2 - text.get_width() / 2),
            target_rect.y + (target_rect.height / 2 - text.get_height() / 2)))


def sequencesFormed(pieceLocation, piece):
    r, c = pieceLocation[0], pieceLocation[1]
    # Check horizontal locations for win
    count = 0
    if 0 <= c <= COLUMN_COUNT - 4:
        if board[r][c] == piece and board[r][c + 1] == piece and board[r][c + 2] == piece and board[r][c + 3] == piece:
            count += 1

    # Check vertical locations for win
    if 0 <= r <= ROW_COUNT - 4:
        if board[r][c] == piece and board[r + 1][c] == piece and board[r + 2][c] == piece and board[r + 3][c] == piece:
            count += 1

    # Check -> diagonals
    if 0 <= c <= COLUMN_COUNT - 4 and 0 <= r <= ROW_COUNT - 4:
        if board[r][c] == piece and board[r + 1][c + 1] == piece \
                and board[r + 2][c + 2] == piece and board[r + 3][c + 3] == piece:
            count += 1
    if 0 <= c <= COLUMN_COUNT - 4 and 3 <= r:
        if board[r][c] == piece and board[r - 1][c + 1] == piece \
                and board[r - 2][c + 2] == piece and board[r - 3][c + 3] == piece:
            count += 1

    # Check <- diagonals
    if 3 <= c and 0 <= r <= ROW_COUNT - 4:
        if board[r][c] == piece and board[r + 1][c - 1] == piece \
                and board[r + 2][c - 2] == piece and board[r + 3][c - 3] == piece:
            count += 1
    if 3 <= c and 3 <= r:
        if board[r][c] == piece and board[r - 1][c - 1] == piece \
                and board[r - 2][c - 2] == piece and board[r - 3][c - 3] == piece:
            count += 1

    return count


def isWithinBounds(mat, r, c):
    """
    :param mat: 2D matrix to check in
    :param r: current row
    :param c: current column
    :return: True if within matrix bounds, False otherwise
    """
    return 0 <= r <= len(mat) and 0 <= c <= len(mat[0])


if __name__ == '__main__':
    pygame.init()
    setupFrame()
    gameSession()