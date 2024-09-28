# Importing necessary libraries
import pygame as pg  # For game graphics and event handling
import numpy as np   # For handling arrays (game board)
import sys           # For exiting the game

# Constants
n, m = 10, 10  # Grid size (10x10)

# Initialize Pygame and create the game window
pg.init()
SURF = pg.display.set_mode((1450, 1000))  # Set up the window size (1450x1000 pixels)
font = pg.font.SysFont(None, 30)  # Define the font and font size for text rendering

# Color definitions (in French)
gris_clair = (220, 220, 220)  # Light gray
gris = (180, 180, 180)        # Gray
gris_fonce = (150, 150, 150)  # Dark gray

noir = (0, 0, 0)              # Black
rouge = (255, 0, 0)           # Red
bleuf = (0, 0, 139)           # Dark blue (bleu foncé)

# Coordinates for the grid's top-left and bottom-right corners
x0, y0 = 200, 175  # Top-left corner of the grid
x1, y1 = 800, 775  # Bottom-right corner of the grid

# Function to switch between players (alternates between 'j1' and 'j2')
def alt(joueur):
    if joueur == "j1":
        return "j2"  # Switch from player 1 to player 2
    else:
        return "j1"  # Switch from player 2 to player 1


# Game class handles each player's game board (tabj1 for player 1, tabj2 for player 2)
class game():
    def __init__(self, tabj1, tabj2):
        # Initializes the game board for each player
        self.tabj1 = tabj1
        self.tabj2 = tabj2
    
    # Method to retrieve the game board of the current player
    def joueur_to_tab(self, joueur):
        if joueur == "j1":
            return self.tabj1  # Returns player 1's board
        else:
            return self.tabj2  # Returns player 2's board

    # Method to check if the current player has lost (no ships left)
    def lost(self, joueur):
        # Iterate over the player's grid to check for any remaining ships ('C')
        for i in range(n):
            for j in range(m):
                if self.joueur_to_tab(joueur)[i, j] == "C":
                    return False  # The player still has ships
        return True  # No ships left, the player has lost
    
    # Method to draw the game board on the screen
    def draw(self, joueur):
        # Filling the background with light gray
        SURF.fill(gris_clair)
        
        # Display text depending on the game phase (placement or attack)
        if placement_phase:
            img2 = font.render("Phase de placement", noir, True)
        else:
            img2 = font.render("Phase d'attaque", noir, True)
        
        # Display which player's turn it is
        img3 = font.render("Au tour de " + joueur, noir, True)
        SURF.blit(img3, (1000, 400))
        SURF.blit(img2, (1000, 300))
        
        # Get the current player's board
        tab = self.joueur_to_tab(joueur)
        
        # Iterate over the grid to display the correct color for each cell
        for j in range(n):
            for i in range(m):
                # Set the color based on the value in the cell
                if tab[i, j] == "C":
                    color = gris_fonce  # Ship cell
                elif tab[i, j] == "X":
                    color = rouge  # Hit cell
                elif tab[i, j] == "W":
                    color = gris  # Ship being placed (unconfirmed)
                else:
                    color = bleuf  # Water cell
                
                # Draw each cell of the grid
                pg.draw.rect(SURF, color, [x0 + i * (x1 - x0) / (n - 1), y0 + j * (y1 - y0) / (m - 1), (x1 - x0) / n, (y1 - y0) / m])
                
                # Display coordinates (numbers for rows and letters for columns)
                number = font.render(str(i), noir, True)
                SURF.blit(number, (x0 + 10 + i * (x1 - x0) / (n - 1), y0 - 50))
            letter = font.render(chr(j + 65), noir, True)
            SURF.blit(letter, (x0 - 50, y0 + 10 + j * (y1 - y0) / (m - 1)))
        
        # Update the display with the drawn elements
        pg.display.update()


# Converts mouse click coordinates to grid indices
def mouse_to_mat(x, y):
    xc, yc = x0, y0  # Start from the top-left corner of the grid
    # Adjust x-coordinate
    while (xc + (x1 - x0) / (n - 1) < x):
        xc += (x1 - x0) / (n - 1)
    # Adjust y-coordinate
    while (yc + (y1 - y0) / (m - 1) < y):
        yc += (y1 - y0) / (m - 1)
    # Return the grid indices corresponding to the mouse position
    return round((xc - x0) * (n - 1) / (x1 - x0)), round((yc - y0) * (m - 1) / (y1 - y0))


# Initialize the boat dictionaries (size and quantity for each player)
tab_bateaux1 = {2: 3, 3: 2, 4: 1, 5: 1}  # Player 1's ships
tab_bateaux2 = tab_bateaux1.copy()  # Player 2's ships (same as player 1)
tab_bateaux = {"j1": tab_bateaux1, "j2": tab_bateaux2}  # Both players' ships

# Initial game state settings
placement_phase = True  # The game is in the ship placement phase
current_joueur = "j1"  # Player 1 starts
current_ship = 5  # The current ship being placed is size 5
r = 1, 0  # Default ship orientation (horizontal)

# Create an empty game instance (will be filled during the placement phase)
jeu = game(np.full((n, m), " "), np.full((n, m), " "))  # Initialize both players' boards as empty

# Ship placement phase loop
while(placement_phase):
    # Get the current mouse position
    x, y = pg.mouse.get_pos()
    x, y = mouse_to_mat(x, y)  # Convert mouse position to grid indices
    r0, r1 = r  # Ship orientation
    
    # Get the current player's board
    tab = jeu.joueur_to_tab(current_joueur)
    
    # Check if the current ship can be placed at the selected position and orientation
    b = (x in list(range(min(n, n - r0 * current_ship + 1)))) and (y in list(range(min(m, m - r1 * current_ship + 1)))) and \
                all(v == " " or v == "W" for v in tab[x:x + r0 * current_ship, y]) and \
                all(v == " " or v == "W" for v in tab[x, y:y + r1 * current_ship])
    
    # Event handling (mouse clicks, key presses, etc.)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            # Right mouse button to rotate the ship
            if event.button == 3:
                r = 1 - r0, 1 - r1  # Switch between horizontal and vertical orientation
            
            # Left mouse button to place the ship (if it fits)
            elif event.button == 1 and b:
                for i in range(r0 * current_ship):
                    tab[x + i, y] = "C"  # Place horizontal ship
                for j in range(r1 * current_ship):
                    tab[x, y + j] = "C"  # Place vertical ship
                
                # Update the ship dictionary after placing the ship
                if tab_bateaux[current_joueur][current_ship] == 1:
                    # If all ships of the current size are placed
                    if current_ship == 2:  # If the smallest ship is placed
                        if current_joueur == "j2":
                            current_joueur = "j1"  # Switch to player 1
                            placement_phase = False  # End the placement phase
                        else:
                            current_ship = 5  # Reset ship size to 5 for player 2
                            current_joueur = "j2"  # Switch to player 2
                    else:
                        current_ship -= 1  # Move to the next smaller ship
                else:
                    tab_bateaux[current_joueur][current_ship] -= 1  # Decrement the count for the current ship size
        
        # Escape key to quit the game
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                sys.exit()  # Exit the game

    # Redefine b to account for modifications made during the event loop
    b = (x in list(range(min(n, n - r0 * current_ship + 1)))) and (y in list(range(min(m, m - r1 * current_ship + 1)))) and \
                all(v == " " or v == "W" for v in tab[x:x + r0 * current_ship, y]) and \
                all(v == " " or v == "W" for v in tab[x, y:y + r1 * current_ship])

    # Display unconfirmed ship placement in light gray (before placing the ship permanently)
    if b:
        waiting_boat = []
        for i in range(r0 * current_ship):
            tab[x + i, y] = "W"  # Show the possible ship placement in light gray
            waiting_boat.append((x + i, y))
        for i in range(r1 * current_ship):
            tab[x, i + y] = "W"
            waiting_boat.append((x, i + y))
        
        # Clear any previous unconfirmed placements
        for i in range(n):
            for j in range(m):
                if ((i, j) not in waiting_boat) and tab[i, j] == "W":
                    tab[i, j] = " "  # Reset unconfirmed positions

    # Redraw the game board with the current updates
    jeu.draw(current_joueur)

# Game state after placement phase ends
run = True
play = False
pos = [-1, -1]  # Position of the strike input (coordinates)
img = font.render("", noir, True)
adversaire = alt(current_joueur)  # Start with the alternate player (the adversary)
tab_adv = jeu.joueur_to_tab(adversaire)  # Get the adversary's board

# Attack phase loop
while(run):
    # Handle events (keyboard input, quit, etc.)
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                sys.exit()  # Quit the game
            
            # Confirm strike position with the space bar
            elif event.key == pg.K_SPACE:
                play = True
            
            # Handle strike position input (convert keyboard input to grid coordinates)
            else:
                if pos[0] == -1:
                    pos[0] = ord(pg.key.name(event.key)) - 97  # Convert letter to number (a=0, b=1, etc.)
                else:
                    pos[1] = int(pg.key.name(event.key))  # Get the number (row)

    # If strike position is confirmed
    if play:
        play = False  # Reset play flag
        x, y = pos[1], pos[0]  # Get the strike coordinates
        
        # Check if the strike hit a ship
        if tab_adv[x, y] == "C":
            res = "touché"  # Hit
            tab_adv[x, y] = "X"  # Mark the hit on the adversary's board
            
            # Check if the adversary has lost (no ships left)
            if jeu.lost(adversaire):
                print(current_joueur + " a gagné")  # Declare the winner
                sys.exit()  # Exit the game
        else:
            res = "raté"  # Miss
        
        # Switch turns between players
        tab_adv = jeu.joueur_to_tab(current_joueur)
        temp = current_joueur
        current_joueur = adversaire
        adversaire = temp
        
        # Display the result of the strike
        img = font.render(res, noir, True)
        pos = [-1, -1]  # Reset strike position

    # Redraw the game board with the current updates
    jeu.draw(current_joueur)
    SURF.blit(img, (1000, 600))  # Display the strike result
    pg.display.update()  # Update the display with the current board and result
