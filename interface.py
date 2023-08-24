import sys
sys.path.insert(1, 'constants')
sys.path.insert(2, 'components')

from constants import colors, window_config as wc, tree_visualizer_constants as tvc
from components.button import Button
from components.general import apply_gradient_on_rect
from components import component_constants as cc

import numpy as np
import math

import pygame
import tkinter as tk
from tkinter import messagebox, simpledialog

import engine

win = tk.Tk()
win.withdraw()


#   Player Variables    #
PIECE_COLORS = (colors.GREY, colors.RED, colors.GREEN)
PLAYER1 = 1
PLAYER2 = 2
EMPTY_CELL = 0

#   Game-Dependent Global Variables    #
TURN = 1
GAME_OVER = False
PLAYER_SCORE = [0, 0, 0]
GAME_BOARD = [[]]
usePruning = True
useTranspositionTable = False
screen = pygame.display.set_mode(wc.WINDOW_SIZE)
GAME_MODE = -1
gameInSession = False
moveMade = False
HEURISTIC_USED = 1

AI_PLAYS_FIRST = False  # Set to true for AI to make the first move

nodeStack = []

minimaxCurrentMode = "MAX"

#   Game Modes  #
SINGLE_PLAYER = 1
TWO_PLAYERS = 2
WHO_PLAYS_FIRST = -2
MAIN_MENU = -1

# Developer Mode: facilitates debugging during GUI development
DEVMODE = False


class GameWindow:
    def switch(self):
        self.refreshGameWindow()
        self.gameSession()

    def setupGameWindow(self):
        """
        Initializes the all components in the frame
        """
        global GAME_BOARD
        GAME_BOARD = self.initGameBoard(EMPTY_CELL)
        pygame.display.set_caption('Smart Connect4 :)')
        self.refreshGameWindow()

    def refreshGameWindow(self):
        """
        Refreshes the screen and all the components
        """
        pygame.display.flip()
        refreshBackground()
        self.drawGameBoard()
        self.drawGameWindowButtons()
        self.drawGameWindowLabels()

    ######   Labels    ######

    def drawGameWindowLabels(self):
        """
        Draws all labels on the screen
        """
        titleFont = pygame.font.SysFont("Sans Serif", 40, False, True)
        mainLabel = titleFont.render("Smart Connect4", True, colors.WHITE)
        screen.blit(mainLabel, (wc.BOARD_FRAME_END_X + 20, 20))

        if not GAME_OVER:
            captionFont = pygame.font.SysFont("Arial", 15)
            player1ScoreCaption = captionFont.render("Player1", True, colors.BLACK)
            player2ScoreCaption = captionFont.render("Player2", True, colors.BLACK)
            screen.blit(player1ScoreCaption, (wc.BOARD_FRAME_END_X + 48, 210))
            screen.blit(player2ScoreCaption, (wc.BOARD_FRAME_END_X + 170, 210))

            if GAME_MODE == SINGLE_PLAYER:
                global statsPanelY
                depthFont = pygame.font.SysFont("Serif", math.ceil(23 - len(str(engine.BOARD.getDepth())) / 4))
                depthLabel = depthFont.render("k = " + str(engine.BOARD.getDepth()), True, colors.BLACK)

                tempWidth = wc.WINDOW_WIDTH - (wc.BOARD_FRAME_END_X + 10)
                centerX = wc.BOARD_FRAME_END_X + 10 + (tempWidth / 2 - depthLabel.get_width() / 2)
                screen.blit(depthLabel, (centerX, 294))
                statsPanelY = 320

                if usePruning:
                    depthFont = pygame.font.SysFont("Arial", 16)
                    depthLabel = depthFont.render("Using alpha-beta pruning", True, colors.GOLD)
                    centerX = wc.BOARD_FRAME_END_X + 10 + (tempWidth / 2 - depthLabel.get_width() / 2)
                    screen.blit(depthLabel, (centerX, 320))
                    statsPanelY += 20

                if useTranspositionTable:
                    depthFont = pygame.font.SysFont("Arial", 16)
                    depthLabel = depthFont.render("Using transposition table", True, colors.DARK_GREEN)
                    centerX = wc.BOARD_FRAME_END_X + 10 + (tempWidth / 2 - depthLabel.get_width() / 2)
                    screen.blit(depthLabel, (centerX, statsPanelY))
                    statsPanelY += 20

        else:
            if PLAYER_SCORE[PLAYER1] == PLAYER_SCORE[PLAYER2]:
                verdict = 'DRAW :)'
            elif PLAYER_SCORE[PLAYER1] > PLAYER_SCORE[PLAYER2]:
                verdict = 'Player 1 Wins!'
            else:
                verdict = 'Player 2 Wins!'

            verdictFont = pygame.font.SysFont("Serif", 40)
            verdictLabel = verdictFont.render(verdict, True, colors.GOLD)
            screen.blit(verdictLabel, (wc.BOARD_BEGIN_X + wc.BOARD_END_X / 3, wc.BOARD_BEGIN_Y / 3))

        self.refreshScores()
        self.refreshStats()

    def refreshScores(self):
        """
        Refreshes the scoreboard
        """
        if GAME_OVER:
            scoreBoard_Y = wc.BOARD_BEGIN_Y
        else:
            scoreBoard_Y = 120

        pygame.draw.rect(screen, colors.BLACK, (wc.BOARD_FRAME_END_X + 9, scoreBoard_Y - 1, 117, 82), 0)
        player1ScoreSlot = pygame.draw.rect(screen, wc.BOARD_FRAME_BACKGROUND,
                                            (wc.BOARD_FRAME_END_X + 10, scoreBoard_Y, 115, 80))

        pygame.draw.rect(screen, colors.BLACK, (wc.BOARD_FRAME_END_X + 134, scoreBoard_Y - 1, 117, 82), 0)
        player2ScoreSlot = pygame.draw.rect(screen, wc.BOARD_FRAME_BACKGROUND,
                                            (wc.BOARD_FRAME_END_X + 135, scoreBoard_Y, 115, 80))

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

    def mouseOverMainLabel(self):
        return 20 <= pygame.mouse.get_pos()[1] <= 45 and 810 <= pygame.mouse.get_pos()[0] <= 1030

    def refreshStats(self):
        """
        Refreshes the analysis section
        """
        global statsPanelY
        if GAME_MODE == SINGLE_PLAYER:
            if GAME_OVER:
                statsPanelY = showStatsButton.y + showStatsButton.height + 5
            pygame.draw.rect(
                screen, colors.BLACK,
                (wc.BOARD_FRAME_END_X + 9, statsPanelY + 5, wc.WINDOW_WIDTH - wc.BOARD_FRAME_END_X - 18, 267 + (370 - statsPanelY)),
                0)
            pygame.draw.rect(
                screen, colors.GREY,
                (wc.BOARD_FRAME_END_X + 10, statsPanelY + 6, wc.WINDOW_WIDTH - wc.BOARD_FRAME_END_X - 20, 265 + (370 - statsPanelY)))

    ######   Buttons    ######

    def drawGameWindowButtons(self):
        """
            Draws all buttons on the screen
            """
        global showStatsButton, contributorsButton, \
            playAgainButton, settingsButton, homeButton
        global settingsIcon, settingsIconAccent, homeIcon, homeIconAccent

        settingsIcon = pygame.image.load('GUI/settings-icon.png').convert_alpha()
        settingsIconAccent = pygame.image.load('GUI/settings-icon-accent.png').convert_alpha()
        homeIcon = pygame.image.load('GUI/home-icon.png').convert_alpha()
        homeIconAccent = pygame.image.load('GUI/home-icon-accent.png').convert_alpha()

        contributorsButton = Button(surface=screen, color=colors.LIGHT_GREY, x=wc.BOARD_FRAME_END_X + 10, y=650,
            width=wc.WINDOW_WIDTH - wc.BOARD_FRAME_END_X - 20, height=30, text="Contributors", outline_color=colors.BLACK)
        contributorsButton.draw()

        settingsButton = Button(surface=screen, color=(82, 82, 82), x=wc.WINDOW_WIDTH - 48, y=wc.BOARD_BEGIN_Y - 38, width=35, height=35)
        homeButton = Button(surface=screen, color=(79, 79, 79), x=wc.WINDOW_WIDTH - 88, y=wc.BOARD_BEGIN_Y - 38, width=35, height=35)
        self.reloadSettingsButton(settingsIcon)
        self.reloadHomeButton(homeIcon)

        showStatsButton_Y = 250
        if GAME_OVER:
            showStatsButton_Y = 330

            playAgainButton = Button(
                surface=screen, color=colors.GOLD, x=wc.BOARD_FRAME_END_X + 10, y=wc.BOARD_BEGIN_Y + 100, width=wc.WINDOW_WIDTH - wc.BOARD_FRAME_END_X - 20, height=120, text="Play Again")
            playAgainButton.draw()

        if GAME_MODE == SINGLE_PLAYER:
            if moveMade:
                statsButtonColor = colors.LIGHT_GREY
            else:
                statsButtonColor = colors.DARK_GREY
            showStatsButton = Button(
                surface=screen, color=statsButtonColor, x=wc.BOARD_FRAME_END_X + 10, y=showStatsButton_Y, 
                width=wc.WINDOW_WIDTH - wc.BOARD_FRAME_END_X - 20, height=30, text="Observe decision tree", outline_color=colors.BLACK
                )
            showStatsButton.draw()

    def reloadSettingsButton(self, icon):
        settingsButton.draw()
        screen.blit(icon, (settingsButton.x + 2, settingsButton.y + 2))

    def reloadHomeButton(self, icon):
        homeButton.draw()
        screen.blit(icon, (homeButton.x + 2, homeButton.y + 2))

    ######   Game Board  ######

    def initGameBoard(self, initialCellValue):
        """
        Initializes the game board with the value given.
        :param initialCellValue: Value of initial cell value
        :return: board list with all cells initialized to initialCellValue
        """
        global GAME_BOARD
        GAME_BOARD = np.full((wc.ROW_COUNT, wc.COLUMN_COUNT), initialCellValue)
        return GAME_BOARD

    def printGameBoard(self):
        """
        Prints the game board to the terminal
        """
        print('\n-\n' +
              str(GAME_BOARD) +
              '\n Player ' + str(TURN) + ' plays next')

    def drawGameBoard(self):
        """
        Draws the game board on the interface with the latest values in the board list
        """
        pygame.draw.rect(screen, colors.BLACK, (0, 0, wc.BOARD_FRAME_END_X, wc.WINDOW_HEIGHT), 0)
        boardLayout = pygame.draw.rect(
            screen, wc.BOARD_FRAME_BACKGROUND, (0, 0, wc.BOARD_FRAME_END_X - 1, wc.WINDOW_HEIGHT))
        apply_gradient_on_rect(surface=screen, left_color=colors.DARKER_GREY, right_color=colors.DARK_GREY, target_rect=boardLayout)
        for c in range(wc.COLUMN_COUNT):
            for r in range(wc.ROW_COUNT):
                col = wc.BOARD_BEGIN_X + (c * wc.SQUARE_SIZE)
                row = wc.BOARD_BEGIN_Y + (r * wc.SQUARE_SIZE)
                piece = GAME_BOARD[r][c]
                pygame.draw.rect(
                    screen, wc.CELL_BORDER_COLOR, (col, row, wc.SQUARE_SIZE, wc.SQUARE_SIZE))
                pygame.draw.circle(
                    screen, PIECE_COLORS[piece], (int(col + wc.SQUARE_SIZE / 2), int(row + wc.SQUARE_SIZE / 2)), wc.PIECE_RADIUS)
        pygame.display.update()

    def hoverPieceOverSlot(self):
        """
        Hovers the piece over the game board with the corresponding player's piece color
        """
        boardLayout = pygame.draw.rect(screen, wc.BOARD_FRAME_BACKGROUND,
                                       (0, wc.BOARD_BEGIN_Y - wc.SQUARE_SIZE, wc.BOARD_WIDTH + wc.SQUARE_SIZE / 2, wc.SQUARE_SIZE))
        apply_gradient_on_rect(surface=screen, left_color=colors.DARKER_GREY, right_color=colors.DARK_GREY, target_rect=boardLayout)
        posx = pygame.mouse.get_pos()[0]
        if wc.BOARD_BEGIN_X < posx < wc.BOARD_END_X:
            pygame.mouse.set_visible(False)
            pygame.draw.circle(screen, PIECE_COLORS[TURN], (posx, int(wc.SQUARE_SIZE / 2)), wc.PIECE_RADIUS)
        else:
            pygame.mouse.set_visible(True)

    def dropPiece(self, col, piece) -> tuple:
        """
        Drops the given piece in the next available cell in slot 'col'
        :param col: Column index where the piece will be dropped
        :param piece: Value of the piece to be put in array.
        :returns: tuple containing the row and column of piece position
        """
        row = self.getNextOpenRow(col)
        GAME_BOARD[row][col] = piece

        return row, col

    def hasEmptyCell(self, col) -> bool:
        """
        Checks if current slot has an empty cell. Assumes col is within array limits
        :param col: Column index representing the slot
        :return: True if slot has an empty cell. False otherwise.
        """
        return GAME_BOARD[0][col] == EMPTY_CELL

    def getNextOpenRow(self, col):
        """
        Gets the next available cell in the slot
        :param col: Column index
        :return: If exists, the row of the first available empty cell in the slot. None otherwise.
        """
        for r in range(wc.ROW_COUNT - 1, -1, -1):
            if GAME_BOARD[r][col] == EMPTY_CELL:
                return r
        return None

    def boardIsFull(self) -> bool:
        """
        Checks if the board game is full
        :return: True if the board list has no empty slots, False otherwise.
        """
        for slot in range(wc.COLUMN_COUNT):
            if self.hasEmptyCell(slot):
                return False
        return True

    def getBoardColumnFromPos(self, posx):
        """
        Get the index of the board column corresponding to the given position
        :param posx: Position in pixels
        :return: If within board bounds, the index of corresponding column, None otherwise
        """
        column = int(math.floor(posx / wc.SQUARE_SIZE))
        if 0 <= column < wc.COLUMN_COUNT:
            return column
        return None

    def buttonResponseToMouseEvent(self, event):
        """
        Handles button behaviour in response to mouse events influencing them
        """
        if event.type == pygame.MOUSEMOTION:
            if GAME_MODE == SINGLE_PLAYER and showStatsButton.is_mouse_over():
                if moveMade and not GAME_OVER:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    alterButtonAppearance(showStatsButton, colors.WHITE, colors.BLACK)
            elif contributorsButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(contributorsButton, colors.WHITE, colors.BLACK)
            elif settingsButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.reloadSettingsButton(settingsIconAccent)
            elif homeButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.reloadHomeButton(homeIconAccent)
            elif GAME_OVER and playAgainButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(
                    button=playAgainButton, color=colors.GOLD, outlineColor=colors.BLACK, hasGradBackground=True,
                    gradLeftColor=colors.WHITE, gradRightColor=colors.GOLD, fontSize=22)
            elif self.mouseOverMainLabel():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if GAME_MODE == SINGLE_PLAYER:
                    if moveMade and not GAME_OVER:
                        alterButtonAppearance(showStatsButton, colors.LIGHT_GREY, colors.BLACK)
                    else:
                        alterButtonAppearance(showStatsButton, colors.DARK_GREY, colors.BLACK)
                alterButtonAppearance(contributorsButton, colors.LIGHT_GREY, colors.BLACK)
                self.reloadSettingsButton(settingsIcon)
                self.reloadHomeButton(homeIcon)
                if GAME_OVER:
                    alterButtonAppearance(playAgainButton, colors.GOLD, colors.BLACK)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if GAME_MODE == SINGLE_PLAYER and not GAME_OVER and showStatsButton.is_mouse_over() and moveMade:
                alterButtonAppearance(showStatsButton, colors.CYAN, colors.BLACK)
            elif contributorsButton.is_mouse_over():
                alterButtonAppearance(contributorsButton, colors.CYAN, colors.BLACK)
            elif GAME_OVER and playAgainButton.is_mouse_over():
                alterButtonAppearance(
                    button=playAgainButton, color=colors.GOLD, outlineColor=colors.BLACK, hasGradBackground=True,
                    gradLeftColor=colors.GOLD, gradRightColor=colors.CYAN)
            elif self.mouseOverMainLabel() or homeButton.is_mouse_over():
                self.resetEverything()
                mainMenu.setupMainMenu()
                mainMenu.show()
            elif settingsButton.is_mouse_over():
                settingsWindow = SettingsWindow()
                settingsWindow.setupSettingsMenu()
                settingsWindow.show()

        if event.type == pygame.MOUSEBUTTONUP:
            if GAME_MODE == SINGLE_PLAYER and not GAME_OVER and showStatsButton.is_mouse_over() and moveMade:
                alterButtonAppearance(showStatsButton, colors.LIGHT_GREY, colors.BLACK)
                treevisualizer = TreeVisualizer()
                treevisualizer.switch()
            elif contributorsButton.is_mouse_over():
                alterButtonAppearance(contributorsButton, colors.LIGHT_GREY, colors.BLACK)
                self.showContributors()
            elif GAME_OVER and playAgainButton.is_mouse_over():
                alterButtonAppearance(
                    button=playAgainButton, color=colors.GOLD, outlineColor=colors.BLACK, hasGradBackground=True,
                    gradLeftColor=colors.WHITE, gradRightColor=colors.GOLD, fontSize=22)
                self.resetEverything()

        if DEVMODE:
            pygame.draw.rect(screen, colors.BLACK, (wc.BOARD_FRAME_END_X + 20, 70, wc.WINDOW_WIDTH - wc.BOARD_FRAME_END_X - 40, 40))
            pygame.mouse.set_visible(True)
            titleFont = pygame.font.SysFont("Sans Serif", 20, False, True)
            coordinates = titleFont.render(str(pygame.mouse.get_pos()), True, colors.WHITE)
            screen.blit(coordinates, (wc.BOARD_FRAME_END_X + 100, 80))

    def showContributors(self):
        """
        Invoked at pressing the contributors button. Displays a message box Containing names and IDs of contributors
        """
        messagebox.showinfo('Contributors', "6744   -   Adham Mohamed Aly\n"
                                            "6905   -   Mohamed Farid Abdelaziz\n"
                                            "7140   -   Yousef Ashraf Kotp\n")

    def gameSession(self):
        """
        Runs the game session
        """
        global GAME_OVER, TURN, GAME_BOARD, gameInSession, moveMade, AI_PLAYS_FIRST
        gameInSession = True
        nodeStack.clear()

        while True:

            if AI_PLAYS_FIRST and not moveMade:
                switchTurn()
                self.player2Play()
                moveMade = True

            pygame.display.update()

            if not GAME_OVER:
                self.hoverPieceOverSlot()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                self.buttonResponseToMouseEvent(event)

                if not GAME_OVER and event.type == pygame.MOUSEBUTTONDOWN:
                    posx = event.pos[0] - wc.BOARD_BEGIN_X
                    column = self.getBoardColumnFromPos(posx)

                    if column is not None:
                        if self.hasEmptyCell(column):
                            self.dropPiece(column, TURN)
                            self.computeScore()
                            switchTurn()
                            self.refreshGameWindow()

                            moveMade = True

                            if not self.boardIsFull():
                                self.player2Play()

                            if self.boardIsFull():
                                GAME_OVER = True
                                pygame.mouse.set_visible(True)
                                self.refreshGameWindow()
                                break

    def player2Play(self):
        if GAME_MODE == SINGLE_PLAYER:
            self.computerPlay()
        elif GAME_MODE == TWO_PLAYERS:
            pass

    def computerPlay(self):
        global GAME_BOARD, parentState
        for i in range(wc.ROW_COUNT):
            for j in range(wc.COLUMN_COUNT):
                GAME_BOARD[i][j] -= 1

        flippedGameBoard = np.flip(m=GAME_BOARD, axis=0)  # Flip about x-axis
        numericState = engine.convertToNumber(flippedGameBoard)
        boardState = engine.nextMove(alphaBetaPruning=usePruning, state=numericState, heuristic=HEURISTIC_USED)
        flippedNewState = engine.convertToTwoDimensions(boardState)
        newState = np.flip(m=flippedNewState, axis=0)  # Flip about x-axis

        for i in range(wc.ROW_COUNT):
            for j in range(wc.COLUMN_COUNT):
                GAME_BOARD[i][j] += 1
                newState[i][j] += 1

        newC = self.getNewMove(newState=newState, oldState=GAME_BOARD)

        boardLayout = pygame.draw.rect(screen, wc.BOARD_FRAME_BACKGROUND,
                                       (0, wc.BOARD_BEGIN_Y - wc.SQUARE_SIZE, wc.BOARD_WIDTH + wc.SQUARE_SIZE / 2, wc.SQUARE_SIZE))
        for i in range(wc.BOARD_BEGIN_X, math.ceil(wc.BOARD_BEGIN_X + newC * wc.SQUARE_SIZE + wc.SQUARE_SIZE / 2), 2):
            apply_gradient_on_rect(surface=screen, left_color=colors.DARKER_GREY, right_color=colors.DARK_GREY, target_rect=boardLayout)
            pygame.draw.circle(
                screen, PIECE_COLORS[TURN], (i, int(wc.SQUARE_SIZE / 2)), wc.PIECE_RADIUS)
            pygame.display.update()
        self.refreshGameWindow()

        self.hoverPieceOverSlot()

        GAME_BOARD = newState
        self.computeScore()

        switchTurn()
        self.refreshGameWindow()

    def resetEverything(self):
        """
        Resets everything back to default values
        """
        global GAME_BOARD, PLAYER_SCORE, GAME_OVER, TURN, moveMade
        PLAYER_SCORE = [0, 0, 0]
        GAME_OVER = False
        TURN = 1
        moveMade = False
        self.setupGameWindow()

    def getNewMove(self, newState, oldState) -> int:
        """
        :return: New move made by the AI
        """
        for r in range(wc.ROW_COUNT):
            for c in range(wc.COLUMN_COUNT):
                if newState[r][c] != oldState[r][c]:
                    return c

    def computeScore(self):
        """
        Computes every player's score and stores it in the global PLAYER_SCORES list
        :returns: values in PLAYER_SCORES list
        """
        global PLAYER_SCORE
        PLAYER_SCORE = [0, 0, 0]
        for r in range(wc.ROW_COUNT):
            consecutive = 0
            for c in range(wc.COLUMN_COUNT):
                consecutive += 1
                if c > 0 and GAME_BOARD[r][c] != GAME_BOARD[r][c - 1]:
                    consecutive = 1
                if consecutive >= 4:
                    PLAYER_SCORE[GAME_BOARD[r][c]] += 1

        for c in range(wc.COLUMN_COUNT):
            consecutive = 0
            for r in range(wc.ROW_COUNT):
                consecutive += 1
                if r > 0 and GAME_BOARD[r][c] != GAME_BOARD[r - 1][c]:
                    consecutive = 1
                if consecutive >= 4:
                    PLAYER_SCORE[GAME_BOARD[r][c]] += 1

        for r in range(wc.ROW_COUNT - 3):
            for c in range(wc.COLUMN_COUNT - 3):
                if GAME_BOARD[r][c] == GAME_BOARD[r + 1][c + 1] \
                        == GAME_BOARD[r + 2][c + 2] == GAME_BOARD[r + 3][c + 3]:
                    PLAYER_SCORE[GAME_BOARD[r][c]] += 1

        for r in range(wc.ROW_COUNT - 3):
            for c in range(wc.COLUMN_COUNT - 1, 2, -1):
                if GAME_BOARD[r][c] == GAME_BOARD[r + 1][c - 1] \
                        == GAME_BOARD[r + 2][c - 2] == GAME_BOARD[r + 3][c - 3]:
                    PLAYER_SCORE[GAME_BOARD[r][c]] += 1

        return PLAYER_SCORE

    def isWithinBounds(self, mat, r, c) -> bool:
        """
        :param mat: 2D matrix to check in
        :param r: current row
        :param c: current column
        :return: True if coordinates are within matrix bounds, False otherwise
        """
        return 0 <= r <= len(mat) and 0 <= c <= len(mat[0])


class MainMenu:
    def switch(self):
        self.setupMainMenu()
        self.show()

    def show(self):
        while GAME_MODE == MAIN_MENU:
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                self.buttonResponseToMouseEvent(event)

        if GAME_MODE == WHO_PLAYS_FIRST:
            WhoPlaysFirstMenu().switch()
        else:
            startGameSession()

    def setupMainMenu(self):
        """
        Initializes the all components in the frame
        """
        global GAME_MODE, gameInSession
        GAME_MODE = MAIN_MENU
        gameInSession = False
        pygame.display.flip()
        pygame.display.set_caption('Smart Connect4 :) - Main Menu')
        self.refreshMainMenu()

    def refreshMainMenu(self):
        """
        Refreshes the screen and all the components
        """
        pygame.display.flip()
        refreshBackground(colors.BLACK, colors.GREY)
        self.drawMainMenuButtons()
        self.drawMainMenuLabels()

    def drawMainMenuButtons(self):
        global singlePlayerButton, multiPlayerButton, SettingsButton_MAINMENU
        singlePlayerButton = Button(
            surface=screen, color=colors.LIGHT_GREY, x=wc.WINDOW_WIDTH / 3, y=wc.WINDOW_HEIGHT / 3, width=wc.WINDOW_WIDTH / 3, height=wc.WINDOW_HEIGHT / 6,
            has_gradient_core=True, core_left_color=colors.GREEN, core_right_color=colors.BLUE, text='PLAY AGAINST AI', outline_color=colors.BLACK)

        multiPlayerButton = Button(
            surface=screen, color=colors.LIGHT_GREY, x=wc.WINDOW_WIDTH / 3, y=wc.WINDOW_HEIGHT / 3 + wc.WINDOW_HEIGHT / 5, width=wc.WINDOW_WIDTH / 3, height=wc.WINDOW_HEIGHT / 6,
            has_gradient_core=True, core_left_color=colors.GREEN, core_right_color=colors.BLUE, text='TWO-PLAYERS', outline_color=colors.BLACK)

        SettingsButton_MAINMENU = Button(
            surface=screen, color=colors.LIGHT_GREY, x=wc.WINDOW_WIDTH / 3, y=wc.WINDOW_HEIGHT / 3 + wc.WINDOW_HEIGHT / 2.5, width=wc.WINDOW_WIDTH / 3, height=wc.WINDOW_HEIGHT / 6,
            has_gradient_core=True, core_left_color=colors.GREEN, core_right_color=colors.BLUE, text='GAME SETTINGS', outline_color=colors.BLACK)

        singlePlayerButton.draw()
        multiPlayerButton.draw()
        SettingsButton_MAINMENU.draw()

    def drawMainMenuLabels(self):
        titleFont = pygame.font.SysFont("Sans Serif", 65, False, True)
        mainLabel = titleFont.render("Welcome to Smart Connect4 :)", True, colors.WHITE)
        screen.blit(mainLabel, (wc.WINDOW_WIDTH / 5, wc.WINDOW_HEIGHT / 8))

    def buttonResponseToMouseEvent(self, event):
        """
        Handles button behaviour in response to mouse events influencing them
        """
        if event.type == pygame.MOUSEMOTION:
            if singlePlayerButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(singlePlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.WHITE, gradRightColor=colors.BLUE)
            elif multiPlayerButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(multiPlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.WHITE, gradRightColor=colors.BLUE)
            elif SettingsButton_MAINMENU.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(SettingsButton_MAINMENU, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.WHITE, gradRightColor=colors.BLUE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                alterButtonAppearance(singlePlayerButton, colors.LIGHT_GREY, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                alterButtonAppearance(multiPlayerButton, colors.LIGHT_GREY, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                alterButtonAppearance(SettingsButton_MAINMENU, colors.LIGHT_GREY, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if singlePlayerButton.is_mouse_over():
                alterButtonAppearance(singlePlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GOLD, gradRightColor=colors.BLUE)
            elif multiPlayerButton.is_mouse_over():
                alterButtonAppearance(multiPlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GOLD, gradRightColor=colors.BLUE)
            elif SettingsButton_MAINMENU.is_mouse_over():
                alterButtonAppearance(SettingsButton_MAINMENU, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GOLD, gradRightColor=colors.BLUE)

        if event.type == pygame.MOUSEBUTTONUP:
            global GAME_MODE
            if singlePlayerButton.is_mouse_over():
                alterButtonAppearance(singlePlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                setGameMode(WHO_PLAYS_FIRST)
            elif multiPlayerButton.is_mouse_over():
                alterButtonAppearance(multiPlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                setGameMode(TWO_PLAYERS)
            elif SettingsButton_MAINMENU.is_mouse_over():
                alterButtonAppearance(multiPlayerButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                settingsWindow = SettingsWindow()
                settingsWindow.switch()


class WhoPlaysFirstMenu:
    def switch(self):
        self.setupWPFMenu()
        self.show()

    def show(self):
        while GAME_MODE == WHO_PLAYS_FIRST:
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                self.buttonResponseToMouseEvent(event)

        startGameSession()

    def setupWPFMenu(self):
        """
        Initializes the all components in the frame
        """
        pygame.display.flip()
        pygame.display.set_caption('Smart Connect4 :) - Who Plays First?')
        self.refreshWPFMenu()

    def refreshWPFMenu(self):
        """
        Refreshes the screen and all the components
        """
        pygame.display.flip()
        refreshBackground(colors.BLACK, colors.GREY)
        self.drawWPFButtons()
        self.drawWPFLabels()

    def reloadBackButton(self, icon):
        backButton.draw()
        screen.blit(icon, (backButton.x + 2, backButton.y + 2))

    def drawWPFButtons(self):
        global playerFirstButton, computerFirstButton
        global backButton, backIcon, backIconAccent

        backIconAccent = pygame.image.load('GUI/back-icon.png').convert_alpha()
        backIcon = pygame.image.load('GUI/back-icon-accent.png').convert_alpha()

        backButton = Button(surface=screen, color=(81, 81, 81), x=wc.WINDOW_WIDTH - 70, y=20, width=52, height=52)
        self.reloadBackButton(backIcon)

        playerFirstButton = Button(
            surface=screen, color=colors.LIGHT_GREY, x=wc.WINDOW_WIDTH / 2 - 220, y=wc.WINDOW_HEIGHT / 2, width=200, height=wc.WINDOW_HEIGHT / 6,
            has_gradient_core=True, core_left_color=colors.GREEN, core_right_color=colors.BLUE, text='HUMAN', outline_color=colors.BLACK)

        computerFirstButton = Button(
            surface=screen, color=colors.LIGHT_GREY, x=wc.WINDOW_WIDTH / 2 + 20, y=wc.WINDOW_HEIGHT / 2, width=200, height=wc.WINDOW_HEIGHT / 6,
            has_gradient_core=True, core_left_color=colors.GREEN, core_right_color=colors.BLUE, text='COMPUTER', outline_color=colors.BLACK)

        playerFirstButton.draw()
        computerFirstButton.draw()

    def drawWPFLabels(self):
        titleFont = pygame.font.SysFont("Sans Serif", 65, True, True)
        mainLabel = titleFont.render("Who Plays First ?", True, colors.LIGHT_GREY)
        screen.blit(mainLabel, (wc.WINDOW_WIDTH / 2 - mainLabel.get_width() / 2, wc.WINDOW_HEIGHT / 3 - mainLabel.get_height() / 2))

    def buttonResponseToMouseEvent(self, event):
        """
        Handles button behaviour in response to mouse events influencing them
        """
        if event.type == pygame.MOUSEMOTION:
            if playerFirstButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(playerFirstButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.WHITE, gradRightColor=colors.BLUE)
            elif computerFirstButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(computerFirstButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.WHITE, gradRightColor=colors.BLUE)
            elif backButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.reloadBackButton(backIconAccent)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                alterButtonAppearance(playerFirstButton, colors.LIGHT_GREY, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                alterButtonAppearance(computerFirstButton, colors.LIGHT_GREY, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                self.reloadBackButton(backIcon)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if playerFirstButton.is_mouse_over():
                alterButtonAppearance(playerFirstButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GOLD, gradRightColor=colors.BLUE)
            elif computerFirstButton.is_mouse_over():
                alterButtonAppearance(computerFirstButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GOLD, gradRightColor=colors.BLUE)
            elif backButton.is_mouse_over():
                MainMenu().switch()

        if event.type == pygame.MOUSEBUTTONUP:
            global GAME_MODE, AI_PLAYS_FIRST
            if playerFirstButton.is_mouse_over():
                alterButtonAppearance(playerFirstButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                AI_PLAYS_FIRST = False
                setGameMode(SINGLE_PLAYER)
            elif computerFirstButton.is_mouse_over():
                alterButtonAppearance(computerFirstButton, colors.WHITE, colors.BLACK,
                                      hasGradBackground=True, gradLeftColor=colors.GREEN, gradRightColor=colors.BLUE)
                AI_PLAYS_FIRST = True
                setGameMode(SINGLE_PLAYER)


class TreeVisualizer:
    def switch(self):
        self.setupTreeVisualizer()
        self.show()

    def show(self):
        while True:
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                self.buttonResponseToMouseEvent(event)

    def setupTreeVisualizer(self):
        global minimaxCurrentMode
        minimaxCurrentMode = 'MAX'
        pygame.display.flip()
        pygame.display.set_caption('Smart Connect4 :) - Tree Visualizer')
        self.refreshTreeVisualizer(rootNode=None)

    def refreshTreeVisualizer(self, rootNode=None):
        refreshBackground()
        self.drawTreeNodes(rootNode)
        self.drawTreeVisualizerButtons()
        self.drawTreeVisualizerLabels()
        self.drawMiniGameBoard()
        pygame.display.update()

    def drawTreeNodes(self, parent):
        global parentNodeButton, rootNodeButton, child1Button, child2Button, child3Button, child4Button, child5Button, child6Button, child7Button
        global root, child1, child2, child3, child4, child5, child6, child7
        child1 = child2 = child3 = child4 = child5 = child6 = child7 = None

        parentNodeButton = Button(surface=screen, color=colors.DARK_GREY, x=wc.WINDOW_WIDTH / 2 - 70, y=10, width=140, height=100, 
                                  text='BACK TO PARENT', shape='ellipse', outline_color=colors.BLACK)
        parentNodeButton.draw()

        if parent is None:
            root = engine.BOARD.lastState
            nodeStack.append(root)
            rootValue = engine.BOARD.getValueFromMap(engine.BOARD.lastState)
        else:
            root = nodeStack[-1]
            rootValue = engine.BOARD.getValueFromMap(root)

        rootNodeButton = Button(surface=screen, color=colors.LIGHT_GREY, x=wc.WINDOW_WIDTH / 2 - 70, y=parentNodeButton.y + 200, width=140,
                                height=100, text=str(rootValue),
                                shape='ellipse')

        children = engine.BOARD.getChildrenFromMap(root)

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 1:
            child1 = children[0]
            color, txt = self.styleNode(child1)
        child1Button = Button(surface=screen, color=color, x=40, y=rootNodeButton.y + 300, width=140, height=100,
                              text=txt, shape='ellipse')

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 2:
            child2 = children[1]
            color, txt = self.styleNode(child2)
        child2Button = Button(surface=screen, color=color, x=180, y=rootNodeButton.y + 200, width=140, height=100,
                              text=txt, shape='ellipse')

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 3:
            child3 = children[2]
            color, txt = self.styleNode(child3)
        child3Button = Button(surface=screen, color=color, x=320, y=rootNodeButton.y + 300, width=140, height=100,
                              text=txt, shape='ellipse')

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 4:
            child4 = children[3]
            color, txt = self.styleNode(child4)
        child4Button = Button(surface=screen, color=color, x=460, y=rootNodeButton.y + 200, width=140, height=100,
                              text=txt, shape='ellipse')

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 5:
            child5 = children[4]
            color, txt = self.styleNode(child5)
        child5Button = Button(surface=screen, color=color, x=600, y=rootNodeButton.y + 300, width=140, height=100,
                              text=txt, shape='ellipse')

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 6:
            child6 = children[5]
            color, txt = self.styleNode(child6)
        child6Button = Button(surface=screen, color=color, x=740, y=rootNodeButton.y + 200, width=140, height=100,
                              text=txt, shape='ellipse')

        color, txt = colors.GREY, ''
        if children is not None and len(children) >= 7:
            child7 = children[6]
            color, txt = self.styleNode(child7)
        child7Button = Button(surface=screen, color=color, x=880, y=rootNodeButton.y + 300, width=140, height=100,
                              text=txt, shape='ellipse')

        pygame.draw.rect(screen, colors.WHITE, (
            rootNodeButton.x + rootNodeButton.width / 2, rootNodeButton.y + rootNodeButton.height + 10, 2, 80))
        pygame.draw.rect(screen, colors.WHITE,
                         (
                             rootNodeButton.x + rootNodeButton.width / 2,
                             parentNodeButton.y + parentNodeButton.height + 10,
                             2, 80))
        horizontalRule = pygame.draw.rect(screen, colors.WHITE,
                                          (child1Button.x + child1Button.width / 2,
                                           rootNodeButton.y + rootNodeButton.height + 50,
                                           wc.WINDOW_WIDTH - (child1Button.x + child1Button.width / 2)
                                           - (wc.WINDOW_WIDTH - (child7Button.x + child7Button.width / 2)), 2))
        pygame.draw.rect(screen, colors.WHITE, (child2Button.x + child2Button.width / 2, horizontalRule.y, 2, 40))
        pygame.draw.rect(screen, colors.WHITE, (child6Button.x + child6Button.width / 2, horizontalRule.y, 2, 40))
        pygame.draw.rect(screen, colors.WHITE,
                         (child1Button.x + child1Button.width / 2, horizontalRule.y, 2, 40 + child2Button.height))
        pygame.draw.rect(screen, colors.WHITE,
                         (child7Button.x + child7Button.width / 2, horizontalRule.y, 2, 40 + child2Button.height))
        pygame.draw.rect(screen, colors.WHITE,
                         (child3Button.x + child3Button.width / 2, horizontalRule.y, 2, 40 + child2Button.height))
        pygame.draw.rect(screen, colors.WHITE,
                         (child5Button.x + child5Button.width / 2, horizontalRule.y, 2, 40 + child2Button.height))

        rootNodeButton.draw()
        child1Button.draw()
        child2Button.draw()
        child3Button.draw()
        child4Button.draw()
        child5Button.draw()
        child6Button.draw()
        child7Button.draw()

    def styleNode(self, state):
        if self.isNull(state):
            return colors.GREY, ''
        if self.isPruned(state):
            return colors.DARK_RED, '*PRUNED*'
        value = engine.BOARD.getValueFromMap(state)
        return colors.DARK_GREEN, str(value)

    def navigateNode(self, node, rootNode, nodeButton):
        global root
        if node is not None and engine.BOARD.getChildrenFromMap(node) is not None:
            nodeStack.append(node)
            self.toggleMinimaxCurrentMode()

            rootY, nodeY = rootNodeButton.y, nodeButton.y
            rootX, nodeX = rootNodeButton.x, nodeButton.x
            while nodeX not in range(int(rootX) - 3, int(rootX) + 3) \
                    or nodeY not in range(int(rootY) - 3, int(rootY) + 3):
                if nodeX < rootX and nodeX not in range(int(rootX) - 3, int(rootX) + 3):
                    nodeX += 2
                elif nodeX > rootX and nodeX not in range(int(rootX) - 3, int(rootX) + 3):
                    nodeX -= 2
                if nodeY > rootY and nodeY not in range(int(rootY) - 3, int(rootY) + 3):
                    nodeY -= 2
                color = colors.DARK_GREEN
                if math.sqrt(pow(rootX - nodeX, 2) + pow(rootY - nodeY, 2)) <= 200:
                    color = colors.LIGHT_GREY
                tempNodeButton = Button(surface=screen, color=color, x=nodeX, y=nodeY, width=140, height=100, text=nodeButton.text, shape='ellipse')
                refreshBackground()
                tempNodeButton.draw()
                pygame.display.update()
            pygame.time.wait(100)
            self.refreshTreeVisualizer(rootNode)

    def goBackToParent(self):
        if len(nodeStack) <= 1:
            return None
        nodeStack.pop()
        self.toggleMinimaxCurrentMode()

        rootY, parentY = rootNodeButton.y, parentNodeButton.y
        rootX = rootNodeButton.x
        while rootY not in range(int(parentY) - 3, int(parentY) + 3):
            if rootY > parentY:
                rootY -= 3
            color = colors.DARK_GREEN
            tempRootButton = Button(surface=screen, color=color, x=rootX, y=rootY, width=140, height=100,
                                    text=rootNodeButton.text, shape='ellipse')
            refreshBackground()
            tempRootButton.draw()
            pygame.display.update()
        pygame.time.wait(100)
        self.refreshTreeVisualizer(0)

    def drawMiniGameBoard(self, state=None):
        """
        Draws the game board on the interface with the latest values in the board list
        """
        if state is None:
            flippedGameBoard = engine.convertToTwoDimensions(state=root)
            gameBoard = np.flip(m=flippedGameBoard, axis=0)
        else:
            flippedGameBoard = engine.convertToTwoDimensions(state=state)
            gameBoard = np.flip(m=flippedGameBoard, axis=0)
        for i in range(wc.ROW_COUNT):
            for j in range(wc.COLUMN_COUNT):
                gameBoard[i][j] += 1

        MINISQUARESIZE = 30
        MINI_PIECE_RADIUS = MINISQUARESIZE / 2 - 2
        layout = pygame.draw.rect(surface=screen, color=colors.BLACK,
                                  rect=(0, 0, MINISQUARESIZE * 7 + 40, MINISQUARESIZE * 6 + 40))
        apply_gradient_on_rect(surface=screen, left_color=(40, 40, 40), right_color=(25, 25, 25), target_rect=layout)
        pygame.draw.rect(screen, colors.BLACK, (20, 20, MINISQUARESIZE * 7, MINISQUARESIZE * 6), 0)
        for c in range(wc.COLUMN_COUNT):
            for r in range(wc.ROW_COUNT):
                col = 20 + c * MINISQUARESIZE
                row = 20 + r * MINISQUARESIZE
                piece = gameBoard[r][c]
                pygame.draw.rect(
                    screen, wc.CELL_BORDER_COLOR, (col, row, MINISQUARESIZE, MINISQUARESIZE))
                pygame.draw.circle(
                    screen, PIECE_COLORS[piece],
                    (int(col + MINISQUARESIZE / 2), int(row + MINISQUARESIZE / 2)), MINI_PIECE_RADIUS)
        pygame.display.update()

    def drawTreeVisualizerButtons(self):
        global backButton, backIcon, backIconAccent

        backIconAccent = pygame.image.load('GUI/back-icon.png').convert_alpha()
        backIcon = pygame.image.load('GUI/back-icon-accent.png').convert_alpha()

        backButton = Button(surface=screen, color=(81, 81, 81), x=wc.WINDOW_WIDTH - 70, y=20, width=52, height=52)
        self.reloadBackButton(backIcon)

    def drawTreeVisualizerLabels(self):
        labelFont = pygame.font.SysFont("Sans Serif", 55, False, True)
        modeLabel = labelFont.render(minimaxCurrentMode, True, colors.BLACK)
        screen.blit(modeLabel,
                    (rootNodeButton.x + rootNodeButton.width + 20,
                     rootNodeButton.y + rootNodeButton.height / 2 - modeLabel.get_height() / 2))

    def toggleMinimaxCurrentMode(self):
        global minimaxCurrentMode
        if minimaxCurrentMode == "MAX":
            minimaxCurrentMode = "MIN"
        else:
            minimaxCurrentMode = "MAX"

    def reloadBackButton(self, icon):
        backButton.draw()
        screen.blit(icon, (backButton.x + 2, backButton.y + 2))

    def buttonResponseToMouseEvent(self, event):

        if event.type == pygame.MOUSEMOTION:
            if backButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.reloadBackButton(backIconAccent)
            elif parentNodeButton.is_mouse_over():
                if len(nodeStack) > 1:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    parentNodeButton.outline_color, parentNodeButton.text_color = colors.WHITE, colors.WHITE
                    parentNodeButton.draw()
                    pygame.display.update()
            elif rootNodeButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.hoverOverNode(nodeButton=rootNodeButton, nodeState=root)
            elif child1Button.is_mouse_over():
                if child1 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child1Button, nodeState=child1)
            elif child2Button.is_mouse_over():
                if child2 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child2Button, nodeState=child2)
            elif child3Button.is_mouse_over():
                if child3 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child3Button, nodeState=child3)
            elif child4Button.is_mouse_over():
                if child4 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child4Button, nodeState=child4)
            elif child5Button.is_mouse_over():
                if child5 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child5Button, nodeState=child5)
            elif child6Button.is_mouse_over():
                if child6 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child6Button, nodeState=child6)
            elif child7Button.is_mouse_over():
                if child7 is not None:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    self.hoverOverNode(nodeButton=child7Button, nodeState=child7)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                self.reloadBackButton(backIcon)
                self.refreshTreeVisualizer(rootNode=0)
                pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if backButton.is_mouse_over():
                gameWindow = GameWindow()
                gameWindow.switch()
            if parentNodeButton.is_mouse_over():
                self.goBackToParent()
            elif child1Button.is_mouse_over() and self.isNavigable(child1Button.text):
                self.navigateNode(node=child1, rootNode=root, nodeButton=child1Button)
            elif child2Button.is_mouse_over() and self.isNavigable(child2Button.text):
                self.navigateNode(node=child2, rootNode=root, nodeButton=child2Button)
            elif child3Button.is_mouse_over() and self.isNavigable(child3Button.text):
                self.navigateNode(node=child3, rootNode=root, nodeButton=child3Button)
            elif child4Button.is_mouse_over() and self.isNavigable(child4Button.text):
                self.navigateNode(node=child4, rootNode=root, nodeButton=child4Button)
            elif child5Button.is_mouse_over() and self.isNavigable(child5Button.text):
                self.navigateNode(node=child5, rootNode=root, nodeButton=child5Button)
            elif child6Button.is_mouse_over() and self.isNavigable(child6Button.text):
                self.navigateNode(node=child6, rootNode=root, nodeButton=child6Button)
            elif child7Button.is_mouse_over() and self.isNavigable(child7Button.text):
                self.navigateNode(node=child7, rootNode=root, nodeButton=child7Button)

            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONUP:
            pass

    def hoverOverNode(self, nodeButton, nodeState=None):
        nodeButton.color = colors.CYAN
        nodeButton.text = str(nodeState)
        
        if nodeState is not None and self.isPruned(nodeState):
            nodeButton.color = tvc.PRUNED_NODE_COLOR

        old_font_size = nodeButton.font_size
        nodeButton.font_size = 10
        nodeButton.draw()
        nodeButton.font_size = old_font_size
        
        self.drawMiniGameBoard(nodeState)
        pygame.display.update()

    def isPruned(self, state):
        return state == '*PRUNED*' or int(state) & int('1000000000000000000000000000000000000000000000000000000000000000', 2) == 0

    def isNull(self, state):
        return state is None or state == ''

    def isNavigable(self, state):
        return not self.isNull(state) and not self.isPruned(state)


class SettingsWindow:
    def switch(self):
        self.setupSettingsMenu()
        self.show()

    def show(self):
        while True:
            pygame.display.update()

            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    sys.exit()

                self.buttonResponseToMouseEvent(event)

            global HEURISTIC_USED
            selectedOption = heuristicComboBox.update(event_list)
            heuristicComboBox.draw(screen)
            if selectedOption != HEURISTIC_USED:
                HEURISTIC_USED = selectedOption if selectedOption != -1 else HEURISTIC_USED
                self.refreshSettingsMenu()

    def setupSettingsMenu(self):
        """
        Initializes the all components in the frame
        """
        pygame.display.flip()
        pygame.display.set_caption('Smart Connect4 :) - Game Settings')
        self.setupSettingsMenuButtons()
        self.refreshSettingsMenu()

    def refreshSettingsMenu(self):
        """
        Refreshes the screen and all the components
        """
        pygame.display.flip()
        refreshBackground(colors.BLACK, colors.BLUE)
        self.drawSettingsMenuButtons()
        self.drawSettingsMenuLabels()

    def drawSettingsMenuButtons(self):
        self.reloadBackButton(backIcon)
        self.togglePruningCheckbox(toggle=False)
        self.toggleTranspositionCheckbox(toggle=False)
        modifyDepthButton.draw()
        heuristicComboBox.draw(screen)

    def setupSettingsMenuButtons(self):
        global backButton, modifyDepthButton, pruningCheckbox, \
            transpositionCheckbox, backIcon, backIconAccent, heuristicComboBox

        backIconAccent = pygame.image.load('GUI/back-icon.png').convert_alpha()
        backIcon = pygame.image.load('GUI/back-icon-accent.png').convert_alpha()

        backButton = Button(surface=screen, color=(26, 26, 120), x=wc.WINDOW_WIDTH - 70, y=20, width=52, height=52)
        self.reloadBackButton(backIcon)

        pruningCheckbox = Button(screen, color=colors.WHITE, x=30, y=320, width=30, height=30, text="", outline_color=colors.WHITE,
                                 has_gradient_core=usePruning, core_left_color=colors.DARK_GOLD, core_right_color=colors.GOLD, 
                                 has_gradient_outline=True, outline_left_color=colors.LIGHT_GREY, outline_right_color=colors.GREY)
        self.togglePruningCheckbox(toggle=False)

        transpositionCheckbox = Button(
            screen, color=colors.LIGHT_GREY,
            x=30, y=pruningCheckbox.y + pruningCheckbox.height + 20,
            width=30, height=30, text="",
            has_gradient_core=useTranspositionTable, core_left_color=colors.DARK_GOLD, core_right_color=colors.GOLD,
            has_gradient_outline=True, outline_left_color=colors.LIGHT_GREY, outline_right_color=colors.GREY)
        self.toggleTranspositionCheckbox(toggle=False)

        modifyDepthButton = Button(surface=screen, color=colors.LIGHT_GREY, x=30, y=transpositionCheckbox.y + transpositionCheckbox.height + 20, 
                                   width=200, height=50, text="Modify search depth k", outline_color=colors.BLACK)
        modifyDepthButton.draw()

        heuristicComboBox = OptionBox(x=30, y=modifyDepthButton.y + modifyDepthButton.height + 20,
                                      width=200, height=50, color=colors.LIGHT_GREY, highlight_color=colors.GOLD,
                                      selected=HEURISTIC_USED,
                                      font=pygame.font.SysFont("comicsans", 15),
                                      option_list=['V1 (faster)', 'V2 (more aware)'])
        heuristicComboBox.draw(screen)

    def reloadBackButton(self, icon):
        backButton.draw()
        screen.blit(icon, (backButton.x + 2, backButton.y + 2))

    def togglePruningCheckbox(self, toggle=True):
        global usePruning
        if toggle:
            usePruning = pruningCheckbox.isChecked = pruningCheckbox.has_gradient_core = not usePruning

        pruningCheckbox.outline_thickness = 4 if usePruning else 2
        pruningCheckbox.draw()

    def toggleTranspositionCheckbox(self, toggle=True):
        global usePruning, useTranspositionTable
        if toggle:
            useTranspositionTable = transpositionCheckbox.isChecked \
                = transpositionCheckbox.has_gradient_core = not useTranspositionTable

        transpositionCheckbox.outline_thickness = 4 if useTranspositionTable else 2
        transpositionCheckbox.draw()

    def drawSettingsMenuLabels(self):
        global aiSettingsHR

        titleFont = pygame.font.SysFont("Sans Serif", 65, False, True)
        subTitleFont = pygame.font.SysFont("Sans Serif", 50, False, True)
        captionFont1_Arial = pygame.font.SysFont("Arial", 16)
        captionFont2_Arial = pygame.font.SysFont("Arial", 23)
        captionFont2_SansSerif = pygame.font.SysFont("Sans Serif", 23)

        mainLabel = titleFont.render("Game Settings", True, colors.WHITE)
        aiSettingsSubtitle = subTitleFont.render("AI Settings", True, colors.WHITE)
        pruningCaption = captionFont1_Arial.render("Use alpha-beta pruning", True, colors.WHITE)
        transpositionCaption = captionFont1_Arial.render("Use transposition table", True, colors.GREY)
        depthCaption = captionFont2_Arial.render("k = " + str(engine.BOARD.getDepth()), True, colors.WHITE)
        heuristicCaption = captionFont2_Arial.render("Heuristic in use", True, colors.WHITE)
        backLabel = captionFont2_SansSerif.render("BACK", True, colors.WHITE)

        screen.blit(backLabel, (backButton.x + 5, backButton.y + backButton.height + 8))

        screen.blit(mainLabel, (wc.WINDOW_WIDTH / 2 - mainLabel.get_width() / 2, wc.WINDOW_HEIGHT / 8))

        screen.blit(aiSettingsSubtitle, (20, 250))
        aiSettingsHR = pygame.draw.rect(
            surface=screen,
            color=colors.GREY,
            rect=(10, 250 + aiSettingsSubtitle.get_height() + 10, 600, 4))

        screen.blit(pruningCaption,
                    (pruningCheckbox.x + pruningCheckbox.width + 10,
                     pruningCheckbox.y + pruningCaption.get_height() / 3))

        screen.blit(transpositionCaption,
                    (transpositionCheckbox.x + transpositionCheckbox.width + 10,
                     transpositionCheckbox.y + transpositionCaption.get_height() / 3))

        screen.blit(depthCaption,
                    (modifyDepthButton.x + modifyDepthButton.width + 10,
                     modifyDepthButton.y + depthCaption.get_height() / 3))

        screen.blit(heuristicCaption,
                    (heuristicComboBox.rect.x + heuristicComboBox.rect.width + 10,
                     heuristicComboBox.rect.y + depthCaption.get_height() / 3))

    def buttonResponseToMouseEvent(self, event):
        """
        Handles button behaviour in response to mouse events influencing them
        """
        if event.type == pygame.MOUSEMOTION:
            if modifyDepthButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                alterButtonAppearance(modifyDepthButton, colors.WHITE, colors.BLACK, 4)
            elif pruningCheckbox.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            elif transpositionCheckbox.is_mouse_over():
                # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                pass
            elif backButton.is_mouse_over():
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.reloadBackButton(backIconAccent)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                alterButtonAppearance(modifyDepthButton, colors.LIGHT_GREY, colors.BLACK)
                self.reloadBackButton(backIcon)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if modifyDepthButton.is_mouse_over():
                alterButtonAppearance(modifyDepthButton, colors.CYAN, colors.BLACK)
            elif pruningCheckbox.is_mouse_over():
                self.togglePruningCheckbox()
            elif transpositionCheckbox.is_mouse_over():
                # self.toggleTranspositionCheckbox()
                pass
            elif backButton.is_mouse_over():
                if gameInSession:
                    gameWindow = GameWindow()
                    gameWindow.switch()
                else:
                    mainMenu.switch()

        elif event.type == pygame.MOUSEBUTTONUP:
            if modifyDepthButton.is_mouse_over():
                alterButtonAppearance(modifyDepthButton, colors.LIGHT_GREY, colors.BLACK)
                self.takeNewDepth()

    def takeNewDepth(self):
        """
        Invoked at pressing modify depth button. Displays a simple dialog that takes input depth from user
        """
        temp = simpledialog.askinteger('Enter depth', 'Enter depth k')
        if temp is not None and temp > 0:
            engine.BOARD.setDepth(temp)
        self.refreshSettingsMenu()


class OptionBox:

    def __init__(self, x, y, width, height, color, highlight_color, option_list, font, selected=0):
        self.color = color
        self.highlight_color = highlight_color
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.option_list = option_list
        self.selected = selected
        self.draw_menu = False
        self.menu_active = False
        self.active_option = -1

    def draw(self, surf):
        pygame.draw.rect(surf, self.highlight_color if self.menu_active else self.color, self.rect)
        pygame.draw.rect(surf, (0, 0, 0), self.rect, 2)
        msg = self.font.render(self.option_list[self.selected], 1, (0, 0, 0))
        surf.blit(msg, msg.get_rect(center=self.rect.center))

        if self.draw_menu:
            for i, text in enumerate(self.option_list):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                pygame.draw.rect(surf, self.highlight_color if i == self.active_option else self.color, rect)
                msg = self.font.render(text, 1, (0, 0, 0))
                surf.blit(msg, msg.get_rect(center=rect.center))
            outer_rect = (
                self.rect.x, self.rect.y + self.rect.height, self.rect.width, self.rect.height * len(self.option_list))
            pygame.draw.rect(surf, (0, 0, 0), outer_rect, 2)

    def update(self, event_list):
        mpos = pygame.mouse.get_pos()
        self.menu_active = self.rect.collidepoint(mpos)

        self.active_option = -1
        if self.draw_menu:
            for i in range(len(self.option_list)):
                rect = self.rect.copy()
                rect.y += (i + 1) * self.rect.height
                if rect.collidepoint(mpos):
                    self.active_option = i
                    break

        if not self.menu_active and self.active_option == -1:
            self.draw_menu = False

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.menu_active:
                    self.draw_menu = not self.draw_menu
                elif self.draw_menu and self.active_option >= 0:
                    self.selected = self.active_option
                    self.draw_menu = False
                    return self.active_option
        return -1


def alterButtonAppearance(button, color, outlineColor, outlineThickness=cc.BUTTON_DEFAULT_OUTLINE_THICKNESS,
                          hasGradBackground=False, gradLeftColor=None, gradRightColor=None, fontSize=15):
    """
    Alter button appearance with given colors
    """
    button.color = color
    button.outline_color, button.outline_thickness = outlineColor, outlineThickness
    buttonRect = button.draw()
    if hasGradBackground:
        apply_gradient_on_rect(screen, gradLeftColor, gradRightColor, buttonRect, button.text, 'comicsans', fontSize)


def refreshBackground(leftColor=colors.BLACK, rightColor=colors.GREY):
    """
    Refreshes screen background
    """
    apply_gradient_on_rect(screen, leftColor, rightColor, pygame.draw.rect(screen, wc.SCREEN_BACKGROUND, (0, 0, wc.WINDOW_WIDTH, wc.WINDOW_HEIGHT)))


def switchTurn():
    """
    Switch turns between player 1 and player 2
    """
    global TURN
    if TURN == 1:
        TURN = 2
    else:
        TURN = 1


def startGameSession():
    gameWindow = GameWindow()
    gameWindow.setupGameWindow()
    gameWindow.gameSession()


def setGameMode(mode):
    global GAME_MODE
    GAME_MODE = mode


if __name__ == '__main__':
    pygame.init()
    mainMenu = MainMenu()
    mainMenu.setupMainMenu()
    mainMenu.show()
