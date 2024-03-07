# Author: Gigă Ionuț-Cătălin - Group:913
# Game: Planes

# Module Imports
import pygame
import random


# Module Initialization
pygame.init()


# Game Assets and Objects
class Image:
    def __init__(self, path, size, position):
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def draw(self, window):
        window.blit(self.image, self.rect)

class Plane:
    def __init__(self, name, image, position, size):
        self.name = name
        self.set_plane_number()
        self.vertical_image = load_image(image, size)
        self.vertical_image_width = self.vertical_image.get_width()
        self.vertical_image_height = self.vertical_image.get_height()
        self.vertical_image_rect = self.vertical_image.get_rect()
        self.vertical_image_rect.topleft = position
        self.horizontal_image = pygame.transform.rotate(self.vertical_image, -90)
        self.horizontal_image_width = self.horizontal_image.get_width()
        self.horizontal_image_height = self.horizontal_image.get_height()
        self.horizontal_image_rect = self.horizontal_image.get_rect()
        self.horizontal_image_rect.topleft = position
        self.image = self.vertical_image
        self.rect = self.vertical_image_rect
        self.rotation = False
        self.active = False
        self.rotation_angle = 0  # Initial rotation angle
        self.set_plane_shapes()
        self.occupied_cells = []  # List to store the occupied cells

    def set_plane_number(self):
        """Set the plane number"""
        if self.name == 'red_plane':
            self.plane_number = 1
        elif self.name == 'green_plane':
            self.plane_number = 2
        elif self.name == 'purple_plane':
            self.plane_number = 3

    def set_plane_shapes(self):
        """Set specific shapes for each orientation"""
        self.shapes = {
            0: [
                [0, 0, 'C', 0, 0],
                ['P', 'P', 'P', 'P', 'P'],
                [0, 0, 'P', 0, 0],
                [0, 'P', 'P', 'P', 0]
            ],
            90: [
                [0, 0, 'P', 0],
                ['P', 0, 'P', 0],
                ['P', 'P', 'P', 'C'],
                ['P', 0, 'P', 0],
                [0, 0, 'P', 0]
            ],
            180: [
                [0, 'P', 'P', 'P', 0],
                [0, 0, 'P', 0, 0],
                ['P', 'P', 'P', 'P', 'P'],
                [0, 0, 'C', 0, 0]
            ],
            270: [
                [0, 'P', 0, 0],
                [0, 'P', 0, 'P'],
                ['C', 'P', 'P', 'P'],
                [0, 'P', 0, 'P'],
                [0, 'P', 0, 0]
            ]
        }

    @staticmethod
    def snap_to_grid(position):
        """Snap the plane between grid lines"""
        grid_x = round((position[0] - player_game_grid[0][0][0]) / CELL_SIZE) * CELL_SIZE + player_game_grid[0][0][0]
        grid_y = round((position[1] - player_game_grid[0][0][1]) / CELL_SIZE) * CELL_SIZE + player_game_grid[0][0][1]

        # Ensure the snapped position is within the grid boundaries
        grid_x = max(min(grid_x, player_game_grid[-1][-1][0]), player_game_grid[0][0][0])
        grid_y = max(min(grid_y, player_game_grid[-1][-1][1]), player_game_grid[0][0][1])

        return grid_x, grid_y

    def rotate_plane(self):
        """Rotate the plane"""
        self.rotation_angle += 90
        if self.rotation_angle == 360:
            self.rotation_angle = 0

        # Update the image and rect based on the rotation angle
        self.image = pygame.transform.rotate(self.vertical_image, -self.rotation_angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def is_valid_position(self, position):
        # Check if the snapped position is valid for the plane
        return (
                player_game_grid[0][0][0] <= position[0] <= player_game_grid[-1][-1][0] and
                player_game_grid[0][0][1] <= position[1] <= player_game_grid[-1][-1][1] and
                self.is_plane_within_grid() and not self.is_collision(player_game_logic)
        )

    def select_plane_and_move(self):
        """Selects the plane, moves it, and handles rotation on right-click"""
        original_position = self.rect.topleft  # Store the original position

        while self.active:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    self.rect.center = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left-click
                        self.handle_left_click(original_position)
                    elif event.button == 3:  # Right-click
                        self.rotate_plane()

            updateGameScreen(GAME_SCREEN)

        self.update_game_logic()

    def handle_left_click(self, original_position):
        """Handle left-click event"""
        snapped_position = self.snap_to_grid(pygame.mouse.get_pos())

        if self.is_valid_position(snapped_position):
            self.rect.center = snapped_position
            self.horizontal_image_rect.center = snapped_position
            self.active = False
        else:
            self.rect.topleft = original_position
            self.horizontal_image_rect.topleft = original_position
            self.active = False

    def update_game_logic(self):
        """Update the game logic with the plane's position"""
        # Remove the previous placement of the plane from the game logic matrix
        for i, j, plane_type in self.occupied_cells:
            player_game_logic[i][j] = '  '  # Restore the original plane type ('P' or 'C')

        # Clear the occupied cells list before updating
        self.occupied_cells = []

        i_start = round((self.rect.topleft[1] - player_game_grid[0][0][1]) / CELL_SIZE)
        j_start = round((self.rect.topleft[0] - player_game_grid[0][0][0]) / CELL_SIZE)

        plane_shape = self.shapes[self.rotation_angle]
        plane_number = self.plane_number

        for i in range(len(plane_shape)):
            for j in range(len(plane_shape[0])):
                if 0 <= i_start + i < len(player_game_logic) and 0 <= j_start + j < len(player_game_logic[0]):
                    if plane_shape[i][j] == 'P':
                        player_game_logic[i_start + i][j_start + j] = f"P{plane_number}"
                        self.occupied_cells.append((i_start + i, j_start + j, 'P'))
                    elif plane_shape[i][j] == 'C':
                        player_game_logic[i_start + i][j_start + j] = f"C{plane_number}"
                        self.occupied_cells.append((i_start + i, j_start + j, 'C'))

        printGameLogic(player_game_logic)

    def is_plane_within_grid(self):
        """Check if the entire plane is within the grid"""
        i_start = round((self.rect.topleft[1] - player_game_grid[0][0][1]) / CELL_SIZE)
        j_start = round((self.rect.topleft[0] - player_game_grid[0][0][0]) / CELL_SIZE)

        if self.rotation_angle == 0 or self.rotation_angle == 180:
            i_end = i_start + self.vertical_image_height // CELL_SIZE
            j_end = j_start + self.vertical_image_width // CELL_SIZE
        else:
            i_end = i_start + self.vertical_image_width // CELL_SIZE
            j_end = j_start + self.vertical_image_height // CELL_SIZE

        return 0 <= i_start < len(player_game_logic) and 0 <= j_start < len(player_game_logic[0]) and \
            0 <= i_end < len(player_game_logic) and 0 <= j_end < len(player_game_logic[0])

    def is_collision(self, player_game_logic):
        """
        Check for collision with other planes in the game logic matrix.
        Returns True if collision is detected, False otherwise.
        """
        i_start = round((self.rect.topleft[1] - player_game_grid[0][0][1]) / CELL_SIZE)
        j_start = round((self.rect.topleft[0] - player_game_grid[0][0][0]) / CELL_SIZE)

        plane_shape = self.shapes[self.rotation_angle]
        plane_number = self.plane_number

        for i in range(len(plane_shape)):
            for j in range(len(plane_shape[0])):
                if plane_shape[i][j] == 'P' or plane_shape[i][j] == 'C':
                    if 0 <= i_start + i < len(player_game_logic) and 0 <= j_start + j < len(player_game_logic[0]):
                        if player_game_logic[i_start + i][j_start + j] != '  ' and \
                                player_game_logic[i_start + i][j_start + j] != f"P{plane_number}" and \
                                player_game_logic[i_start + i][j_start + j] != f"C{plane_number}":
                            return True  # Collision detected

        return False  # No collision

    def draw(self, window):
        """Draws the plane to the screen"""
        i = round((self.rect.topleft[1] - player_game_grid[0][0][1]) / CELL_SIZE)
        j = round((self.rect.topleft[0] - player_game_grid[0][0][0]) / CELL_SIZE)

        # Ensure that indices are within valid range
        if 0 <= i < len(player_game_grid) and 0 <= j < len(player_game_grid[0]):
            grid_position = player_game_grid[i][j]
            self.rect.topleft = grid_position
            self.horizontal_image_rect.topleft = grid_position

        window.blit(self.image, self.rect)

class Button:
    def __init__(self, image, name, size, position):
        self.image = image
        self.image_larger = self.image
        self.image_larger = pygame.transform.scale(self.image_larger, (size[0] + 8, size[1] + 4))
        self.name = name
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def action_on_press(self):
        if deployment_phase() is False:
            planes_parts = 0
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if (player_game_logic[i][j] == 'P1' or player_game_logic[i][j] == 'P2' or
                            player_game_logic[i][j] == 'P3' or player_game_logic[i][j] == 'C1' or
                            player_game_logic[i][j] == 'C2' or player_game_logic[i][j] == 'C3'):
                        planes_parts += 1

            if self.rect.collidepoint(pygame.mouse.get_pos()) and self.name == 'randomize':
                auto_place_planes()
            elif self.rect.collidepoint(pygame.mouse.get_pos()) and self.name == 'start' and planes_parts == 30:
                global START
                START = True
                print('Start')
                printComputerGameLogic(computer_game_logic)
            else:
                print('You must place all the planes on the grid!')

    def focus_on_button(self, window):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            window.blit(self.image_larger, (self.rect.x - 4, self.rect.y - 2))
        else:
            window.blit(self.image, self.rect)

    def draw(self, window):
        self.focus_on_button(window)

class Token:
    def __init__(self, image, position):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def draw(self, window):
        window.blit(self.image, self.rect)

class Player:
    def __init__(self):
        self.turn = True

    def make_attack(self, grid):
        """When it's the player's turn, the player must make an attacking selection within the computer's grid"""
        poz_x, poz_y = pygame.mouse.get_pos()
        if (grid[0][0][0] <= poz_x <= grid[-1][-1][0] + CELL_SIZE
                and grid[0][0][1] <= poz_y <= grid[-1][-1][1] + CELL_SIZE):
            for row in grid:
                for col in row:
                    if col[0] < poz_x < col[0] + CELL_SIZE and col[1] < poz_y < col[1] + CELL_SIZE:
                        print(f'You have selected the cell {row.index(col) + 1} from the row {grid.index(row) + 1}')
                        if computer_game_logic[grid.index(row)][row.index(col)] == '  ':  # Empty cell
                            TOKENS.append(Token(MISS_TOKEN, (col[0], col[1])))
                            computer_game_logic[grid.index(row)][row.index(col)] = 'M '
                            printComputerGameLogic(computer_game_logic)
                            self.turn = False
                        elif computer_game_logic[grid.index(row)][row.index(col)] == "P1" or \
                                computer_game_logic[grid.index(row)][row.index(col)] == "P2" or \
                                computer_game_logic[grid.index(row)][row.index(col)] == "P3":
                            TOKENS.append(Token(NORMAL_TOKEN, (col[0], col[1])))
                            computer_game_logic[grid.index(row)][row.index(col)] = 'H '
                            printComputerGameLogic(computer_game_logic)
                            self.turn = False
                        elif computer_game_logic[grid.index(row)][row.index(col)] == "C1":
                            TOKENS.append(Token(CABIN_TOKEN, (col[0], col[1])))
                            for i in range(len(computer_game_logic)):
                                for j in range(len(computer_game_logic[0])):
                                    if computer_game_logic[i][j] == "C1" or computer_game_logic[i][j] == "P1":
                                        if computer_game_logic[i][j] == "P1":
                                            TOKENS.append(Token(NORMAL_TOKEN,
                                                    (computer_game_grid[i][j][0], computer_game_grid[i][j][1])))
                                        computer_game_logic[i][j] = 'H '
                            printComputerGameLogic(computer_game_logic)
                            self.turn = False
                        elif computer_game_logic[grid.index(row)][row.index(col)] == "C2":
                            TOKENS.append(Token(CABIN_TOKEN, (col[0], col[1])))
                            for i in range(len(computer_game_logic)):
                                for j in range(len(computer_game_logic[0])):
                                    if computer_game_logic[i][j] == "C2" or computer_game_logic[i][j] == "P2":
                                        if computer_game_logic[i][j] == "P2":
                                            TOKENS.append(Token(NORMAL_TOKEN,
                                                    (computer_game_grid[i][j][0], computer_game_grid[i][j][1])))
                                        computer_game_logic[i][j] = 'H '
                            printComputerGameLogic(computer_game_logic)
                            self.turn = False
                        elif computer_game_logic[grid.index(row)][row.index(col)] == "C3":
                            TOKENS.append(Token(CABIN_TOKEN, (col[0], col[1])))
                            for i in range(len(computer_game_logic)):
                                for j in range(len(computer_game_logic[0])):
                                    if computer_game_logic[i][j] == "C3" or computer_game_logic[i][j] == "P3":
                                        if computer_game_logic[i][j] == "P3":
                                            TOKENS.append(Token(NORMAL_TOKEN,
                                                    (computer_game_grid[i][j][0], computer_game_grid[i][j][1])))
                                        computer_game_logic[i][j] = 'H '
                            printComputerGameLogic(computer_game_logic)
                            self.turn = False
                        else:
                            print('You have already selected this cell')
                            self.turn = True
        return self.turn

class EasyComputer:
    def __init__(self):
        self.turn = False
        self.name = 'Easy Computer'

    def make_attack(self, grid):
        valid_choice = False
        while not valid_choice:
            rowX = random.randint(0, 9)
            colX = random.randint(0, 9)

            if (player_game_logic[rowX][colX] == '  ' or player_game_logic[rowX][colX] == "P1" or
                    player_game_logic[rowX][colX] == "P2" or player_game_logic[rowX][colX] == "P3" or
                    player_game_logic[rowX][colX] == "C1" or player_game_logic[rowX][colX] == "C2" or
                    player_game_logic[rowX][colX] == "C3"):
                valid_choice = True

        if player_game_logic[rowX][colX] == '  ':  # Empty cell
            TOKENS.append(Token(MISS_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            player_game_logic[rowX][colX] = 'M '
            printGameLogic(player_game_logic)
            self.turn = False
        elif player_game_logic[rowX][colX] == "P1" or \
                player_game_logic[rowX][colX] == "P2" or \
                player_game_logic[rowX][colX] == "P3":
            TOKENS.append(Token(NORMAL_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            player_game_logic[rowX][colX] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
        elif player_game_logic[rowX][colX] == "C1":
            TOKENS.append(Token(CABIN_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if player_game_logic[i][j] == "C1" or player_game_logic[i][j] == "P1":
                        if player_game_logic[i][j] == "P1":
                            TOKENS.append(Token(NORMAL_TOKEN,
                                    (player_game_grid[i][j][0], player_game_grid[i][j][1])))
                        player_game_logic[i][j] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
        elif player_game_logic[rowX][colX] == "C2":
            TOKENS.append(Token(CABIN_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if player_game_logic[i][j] == "C2" or player_game_logic[i][j] == "P2":
                        if player_game_logic[i][j] == "P2":
                            TOKENS.append(Token(NORMAL_TOKEN,
                                    (player_game_grid[i][j][0], player_game_grid[i][j][1])))
                        player_game_logic[i][j] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
        elif player_game_logic[rowX][colX] == "C3":
            TOKENS.append(Token(CABIN_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if player_game_logic[i][j] == "C3" or player_game_logic[i][j] == "P3":
                        if player_game_logic[i][j] == "P3":
                            TOKENS.append(Token(NORMAL_TOKEN,
                                    (player_game_grid[i][j][0], player_game_grid[i][j][1])))
                        player_game_logic[i][j] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False

        return self.turn


class HardComputer:
    def __init__(self):
        self.turn = False
        self.name = 'Hard Computer'
        self.hits = []  # Store the positions of successful hits

    def make_attack(self, grid):
        valid_choice = False
        while not valid_choice:
            if not self.hits:
                # If no hits, choose a random position
                rowX = random.randint(0, 9)
                colX = random.randint(0, 9)
            else:
                # If there are hits, prioritize positions around the hits
                rowX, colX = self.choose_target()

            if (player_game_logic[rowX][colX] == '  ' or
                    player_game_logic[rowX][colX] == "P1" or
                    player_game_logic[rowX][colX] == "P2" or
                    player_game_logic[rowX][colX] == "P3" or
                    player_game_logic[rowX][colX] == "C1" or
                    player_game_logic[rowX][colX] == "C2" or
                    player_game_logic[rowX][colX] == "C3"):
                valid_choice = True

        if player_game_logic[rowX][colX] == '  ':  # Empty cell
            TOKENS.append(Token(MISS_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            player_game_logic[rowX][colX] = 'M '
            printGameLogic(player_game_logic)
            self.turn = False
        elif player_game_logic[rowX][colX] == "P1" or \
                player_game_logic[rowX][colX] == "P2" or \
                player_game_logic[rowX][colX] == "P3":
            TOKENS.append(Token(NORMAL_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            player_game_logic[rowX][colX] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
            # Add the hit position to the list of hits
            self.hits.append((rowX, colX))
        elif player_game_logic[rowX][colX] == "C1":
            TOKENS.append(Token(CABIN_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if player_game_logic[i][j] == "C1" or player_game_logic[i][j] == "P1":
                        if player_game_logic[i][j] == "P1":
                            TOKENS.append(Token(NORMAL_TOKEN,
                                    (player_game_grid[i][j][0], player_game_grid[i][j][1])))
                        player_game_logic[i][j] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
            # Clear the hits list after destroying a plane
            self.hits = []
        elif player_game_logic[rowX][colX] == "C2":
            TOKENS.append(Token(CABIN_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if player_game_logic[i][j] == "C2" or player_game_logic[i][j] == "P2":
                        if player_game_logic[i][j] == "P2":
                            TOKENS.append(Token(NORMAL_TOKEN,
                                    (player_game_grid[i][j][0], player_game_grid[i][j][1])))
                        player_game_logic[i][j] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
            self.hits = []
        elif player_game_logic[rowX][colX] == "C3":
            TOKENS.append(Token(CABIN_TOKEN, (player_game_grid[rowX][colX][0], player_game_grid[rowX][colX][1])))
            for i in range(len(player_game_logic)):
                for j in range(len(player_game_logic[0])):
                    if player_game_logic[i][j] == "C3" or player_game_logic[i][j] == "P3":
                        if player_game_logic[i][j] == "P3":
                            TOKENS.append(Token(NORMAL_TOKEN,
                                    (player_game_grid[i][j][0], player_game_grid[i][j][1])))
                        player_game_logic[i][j] = 'H '
            printGameLogic(player_game_logic)
            self.turn = False
            self.hits = []

        return self.turn

    def choose_target(self):
        """
        Choose a target position based on the current hits.
        Prioritize positions around the hits.
        """
        hit = random.choice(self.hits)
        row, col = hit

        # Define possible adjacent positions
        possible_targets = [
            (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)
        ]

        # Filter out invalid positions
        valid_targets = [
            target for target in possible_targets
            if 0 <= target[0] < 10 and 0 <= target[1] < 10
        ]

        # If there are valid targets, choose one randomly
        if valid_targets:
            return random.choice(valid_targets)

        # If no valid targets, choose a random position
        return random.randint(0, 9), random.randint(0, 9)


# Game Utility Functions

def start_screen():
    # Pygame Display Initialization
    start_screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

    # Load start screen background image
    start_background = load_image('assets/images/start_background.png', (SCREENWIDTH, SCREENHEIGHT))

    # Load difficulty buttons
    easy_button = load_image('assets/images/easy_button.png', (300, 150))
    hard_button = load_image('assets/images/hard_button.png', (300, 150))

    DIFFICULTY_BUTTONS = [
        Button(easy_button, "easy", (300, 150), (300, 500)),
        Button(hard_button, "hard", (300, 150), ((SCREENWIDTH - 600), 500))
    ]

    run_start_screen = True
    BACKGROUND_MUSIC.play()
    while run_start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                CLICK_SOUND.play()
                for button in DIFFICULTY_BUTTONS:
                    if button.rect.collidepoint(pygame.mouse.get_pos()):
                        # Set the difficulty based on the button clicked
                        if button.name == "easy":
                            computer = EasyComputer()
                        elif button.name == "hard":
                            computer = HardComputer()

                        # Start the main game loop
                        return True, computer

        start_screen.blit(start_background, (0, 0))
        for button in DIFFICULTY_BUTTONS:
            button.draw(start_screen)

        pygame.display.update()

def display_end_screen(winner):
    if winner == 'player':
        GAME_SCREEN.blit(end_player_screen, (0, 0))
    elif winner == 'computer':
        GAME_SCREEN.blit(end_computer_screen, (0, 0))

    pygame.display.update()
    pygame.time.delay(5000)
    pygame.quit()
    quit()

def createGameGrid(rows, cols, cell_size, pos):
    """Creates a game grid with coordinates for each cell"""
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cell_size
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cell_size
    return coordGrid


def createGameLogic(rows, cols):
    """Updates the game grid with logic, ie - spaces and X for ships"""
    game_logic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append('  ')
        game_logic.append(rowX)
    return game_logic


def showGridOnScreen(window, cell_size, playerGrid, computerGrid):
    """Draws the player and computer grids to the screen"""
    game_grids = [playerGrid, computerGrid]
    for grid in game_grids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (200, 200, 200), (col[0], col[1], cell_size, cell_size), 1)


def printGameLogic(player_game_logic):
    """Prints to the terminal the game logic including plane positions"""
    print('Player Grid'.center(50, '#'))

    for row in player_game_logic:
        print(row)

    print('#' * 50)

def printComputerGameLogic(computer_game_logic):
    """Prints to the terminal the game logic including plane positions"""
    print('Computer Grid'.center(50, '#'))

    for row in computer_game_logic:
        print(row)

    print('#' * 50)


def load_image(path, size):
    """ A function to import the images into memory"""
    image = pygame.image.load(path).convert_alpha()
    image = pygame.transform.scale(image, size)
    return image


def createPlanes():
    """Creates the planes for the game"""
    planes = []
    for name in PLANES.keys():
        planes.append(
            Plane(name,
                  PLANES[name][1],
                  PLANES[name][2],
                  PLANES[name][3])
        )
    return planes


def sort_planes(plane, planes_list):
    """Rearranges the planes in the list so that the selected plane is on top"""
    planes_list.remove(plane)
    planes_list.append(plane)


def updateGameScreen(window):
    """Updates the game screen"""
    window.blit(background, (0, 0))
    showGridOnScreen(window, CELL_SIZE, player_game_grid, computer_game_grid)

    for plane in player_planes:
        plane.draw(window)

    for button in BUTTONS:
        button.draw(window)

    for token in TOKENS:
        token.draw(window)

    GAME_INFO.draw(window)

    pygame.display.update()

def auto_place_planes():
    for plane in player_planes:
        valid_placement = False
        while not valid_placement:
            # Generate random position and orientation
            random_x = random.randint(0, COLS - 1)
            random_y = random.randint(0, ROWS - 1)
            random_orientation = random.choice([0, 90, 180, 270])

            # Set the plane's position and orientation
            plane.rect.topleft = Plane.snap_to_grid((random_x * CELL_SIZE + player_game_grid[0][0][0], random_y *
                                                     CELL_SIZE + player_game_grid[0][0][1]))
            plane.rotation_angle = random_orientation
            plane.image = pygame.transform.rotate(plane.vertical_image, -random_orientation)
            plane.rect = plane.image.get_rect(center=plane.rect.center)

            # Check if the position and orientation are valid
            if plane.is_valid_position(plane.rect.topleft):
                # Check if the position is not occupied by other planes in the logic matrix
                if not plane.is_collision(player_game_logic):
                    valid_placement = True

        # Update the player game logic matrix after placing each plane
        plane.update_game_logic()

    updateGameScreen(GAME_SCREEN)
    printGameLogic(player_game_logic)

def auto_place_planes_computer():
    plane_shape = []
    i_start = 0
    j_start = 0
    number = 1

    for plane in computer_planes:
        valid_placement = False

        while not valid_placement:
            # Generate random position and orientation for the computer's planes
            random_x = random.randint(0, COLS - 1)
            random_y = random.randint(0, ROWS - 1)
            random_orientation = random.choice([0, 90, 180, 270])

            # Set the plane's position and orientation
            i_start = random_y
            j_start = random_x

            plane_shape = plane.shapes[random_orientation]

            # Check if the position and orientation are valid for computer planes
            if (
                0 <= i_start + len(plane_shape) <= ROWS
                and 0 <= j_start + len(plane_shape[0]) <= COLS
                and not any(
                    computer_game_logic[i_start + i][j_start + j] != '  '
                    for i in range(len(plane_shape))
                    for j in range(len(plane_shape[0]))
                )
            ):
                valid_placement = True

        # Update the computer game logic matrix after placing each plane
        for i in range(len(plane_shape)):
            for j in range(len(plane_shape[0])):
                if plane_shape[i][j] == 'P':
                    computer_game_logic[i_start + i][j_start + j] = f"P{number}"
                elif plane_shape[i][j] == 'C':
                    computer_game_logic[i_start + i][j_start + j] = f"C{number}"
        number += 1

    printComputerGameLogic(computer_game_logic)


def deployment_phase():
    if START is False:
        return False
    else:
        return True

def take_turns(player, computer):
    if player.turn is True:
        computer.turn = False
    else:
        computer.turn = True
        if not computer.make_attack(player_game_logic):
            player.turn = True

        # Check if the game is over after the computer's turn
        check_game_over()

def check_game_over():
    """
    Check if the game is over by checking if all planes are destroyed for both player and computer.
    Print the winner to the console.
    """
    winner = None
    player_planes_destroyed = True
    computer_planes_destroyed = True

    for row in player_game_logic:
        for col in row:
            if col == 'P1' or col == 'P2' or col == 'P3' or col == 'C1' or col == 'C2' or col == 'C3':
                player_planes_destroyed = False

    for row in computer_game_logic:
        for col in row:
            if col == 'P1' or col == 'P2' or col == 'P3' or col == 'C1' or col == 'C2' or col == 'C3':
                computer_planes_destroyed = False

    if player_planes_destroyed:
        print('Computer won!')
        updateGameScreen(GAME_SCREEN)
        pygame.time.delay(3000)
        winner = 'computer'
        return winner

    elif computer_planes_destroyed:
        print('Player won!')
        updateGameScreen(GAME_SCREEN)
        pygame.time.delay(3000)
        winner = 'player'
        return winner


# Game Settings and Variables
SCREENWIDTH = 1280
SCREENHEIGHT = 720
ROWS = 10
COLS = 10
CELL_SIZE = 40
START = False

# Pygame Display Initialization
GAME_SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Planes')

# Game Lists/ Dictionaries
PLANES = {
    'red_plane': ['Red Plane', 'assets/images/planes/red_plane.png', (30, 555), (198, 158)],
    'green_plane': ['Green Plane', 'assets/images/planes/green_plane.png', (240, 555), (198, 158)],
    'purple_plane': ['Purple Plane', 'assets/images/planes/purple_plane.png', (450, 555), (198, 158)],
}


# Loading Game Variables
player_game_grid = createGameGrid(ROWS, COLS, CELL_SIZE, (160, 140))
player_game_logic = createGameLogic(ROWS, COLS)
player_planes = createPlanes()

computer_game_grid = createGameGrid(ROWS, COLS, CELL_SIZE, (SCREENWIDTH - (ROWS * CELL_SIZE) - 100, 140))
computer_game_logic = createGameLogic(ROWS, COLS)
computer_planes = createPlanes()
auto_place_planes_computer()

printGameLogic(player_game_logic)

winner = None

# Loading Game Sounds and images
background = load_image('assets/images/background.png', (SCREENWIDTH, SCREENHEIGHT))
end_player_screen = load_image('assets/images/end_player_background.png', (SCREENWIDTH, SCREENHEIGHT))
end_computer_screen = load_image('assets/images/end_computer_background.png', (SCREENWIDTH, SCREENHEIGHT))


start_button = load_image('assets/images/start_button.png', (200, 100))
randomize_button = load_image('assets/images/randomize_button.png', (150, 75))

BUTTONS = [
    Button(start_button, "start", (200, 100), (850, 585)),
    Button(randomize_button, "randomize", (150, 75), (680, 600))
]

TOKENS = []

CABIN_TOKEN = load_image('assets/images/tokens/cabin_hit.png', (CELL_SIZE, CELL_SIZE))
MISS_TOKEN = load_image('assets/images/tokens/miss_hit.png', (CELL_SIZE, CELL_SIZE))
NORMAL_TOKEN = load_image('assets/images/tokens/normal_hit.png', (CELL_SIZE, CELL_SIZE))

GAME_INFO = Image('assets/images/game_info.png', (160, 160), (SCREENWIDTH - 160, 560))

CLICK_SOUND = pygame.mixer.Sound('assets/sounds/click.wav')
CLICK_SOUND.set_volume(0.2)
BACKGROUND_MUSIC = pygame.mixer.Sound('assets/sounds/background_music.wav')
BACKGROUND_MUSIC.set_volume(0.5)

# Initialize player
player = Player()


# Main Game Loop
run_start_screen, computer = start_screen()
RUN_GAME = True
while RUN_GAME:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUN_GAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                CLICK_SOUND.play()
                if START is False:
                    for plane in player_planes:
                        if plane.rect.collidepoint(pygame.mouse.get_pos()):
                            plane.active = True
                            sort_planes(plane, player_planes)
                            plane.select_plane_and_move()

                else:
                    # Check if the game is over after each turn
                    winner = check_game_over()
                    if winner is not None:
                        RUN_GAME = False
                        display_end_screen(winner)

                    player.make_attack(computer_game_grid)
                    updateGameScreen(GAME_SCREEN)

                for button in BUTTONS:
                    button.action_on_press()

    take_turns(player, computer)

    updateGameScreen(GAME_SCREEN)
