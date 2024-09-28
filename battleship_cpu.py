import pygame as pg
import numpy as np
import copy
import sys
import random

# Game constants
n, m = 10, 10  # Grid size

# Initialize Pygame and create the display surface
pg.init()
SURF = pg.display.set_mode((1450, 1000))  # Game window size
font = pg.font.SysFont(None, 30)  # Font for text display

# Color definitions (RGB format)
gris_clair = (220, 220, 220)
gris = (180, 180, 180)
gris_fonce = (150, 150, 150)
noir = (0, 0, 0)
rouge = (255, 0, 0)
bleuf = (0, 0, 139)  # Dark blue

# Coordinates for drawing the grids
x0, y0 = 200, 175  # Top-left corner of the grid
x1, y1 = 800, 775  # Bottom-right corner of the grid

# Function to alternate between players
def alt(joueur):
    if joueur == "j1":
        return "cpu"
    else:
        return "j1"

# Game class to handle the board state for each player
class game():
    def __init__(self, tabj1, tabj2):
        self.tabj1 = tabj1  # Player 1's board
        self.tabj2 = tabj2  # Player 2's (CPU) board

    # Retrieve the board of the current player
    def joueur_to_tab(self, joueur):
        if joueur == "j1":
            return self.tabj1
        else:
            return self.tabj2

    # Check if the player has lost (no more ships left)
    def lost(self, joueur):
        for i in range(n):
            for j in range(m):
                if self.joueur_to_tab(joueur)[i, j] == "C":  # "C" represents a ship cell
                    return False
        return True
    
    # Function to draw the grid and game state on the screen
    def draw(self, joueur):
        SURF.fill(gris_clair)  # Clear the screen with light gray
        if placement_phase:
            img2 = font.render("Phase de placement", noir, True)
        else:
            img2 = font.render("Phase d'attaque", noir, True)
        img3 = font.render("Au tour de " + joueur, noir, True)
        SURF.blit(img3, (1000, 400))
        SURF.blit(img2, (1000, 300))

        # Retrieve the current player's grid
        tab = self.joueur_to_tab(joueur)

        # Draw each cell on the grid based on its state
        for j in range(m):
            for i in range(n):
                if tab[i, j] == "C":
                    color = gris_fonce  # Ship
                elif tab[i, j] == "X":
                    color = rouge  # Hit
                elif tab[i, j] == "W":
                    color = gris  # Ship waiting to be placed
                elif tab[i, j] == "M":
                    color = noir  # Miss
                else:
                    color = bleuf  # Empty water cell
                # Draw the grid cells
                pg.draw.rect(SURF, color, [x0 + i * (x1 - x0) / (n - 1), y0 + (j) * (y1 - y0) / (m - 1), (x1 - x0) / n, (y1 - y0) / m])
                number = font.render(str(i), noir, True)  # Numbering rows
                SURF.blit(number, (x0 + 10 + i * (x1 - x0) / (n - 1), y0 - 50))
            letter = font.render(chr(j + 65), noir, True)  # Labeling columns
            SURF.blit(letter, (x0 - 50, y0 + 10 + j * (y1 - y0) / (m - 1)))
        pg.display.update()  # Update the screen to show changes

# Map that keeps track of what the AI knows about the player's board
known_map = np.full((n, m), " ")

# Function to calculate a probability map for the AI to strike
def probability_map(mat):
    res_mat = np.full((n, m), 0)
    for i in range(small_ship, big_ship + 1):  # Loop through the ship sizes
        r0, r1 = 1, 0
        for j in range(2):  # Two orientations: horizontal and vertical
            for k in range(n):
                for l in range(m):
                    # Check if the ship can fit in the given direction
                    b = (k in list(range(min(n, n - r0 * i + 1)))) and (l in list(range(min(m, m - r1 * i + 1)))) and \
                        all(v == " " for v in mat[k:k + r0 * i, l]) and all(v == " " for v in mat[k, l:l + r1 * i])
                    if b:
                        for q in range(r0 * i):  # Increment probability for possible ship positions
                            res_mat[k + q, l] += 1
                        for q in range(r1 * i):
                            res_mat[k, l + q] += 1
            r0, r1 = 1 - r0, 1 - r1  # Switch orientation
    return res_mat

# Converts mouse click coordinates to grid indices
def mouse_to_mat(x, y):
    xc, yc = x0, y0
    while (xc + (x1 - x0) / (n - 1) < x):
        xc += (x1 - x0) / (n - 1)
    while (yc + (y1 - y0) / (m - 1) < y):
        yc += (y1 - y0) / (m - 1)
    return round((xc - x0) * (n - 1) / (x1 - x0)), round((yc - y0) * (m - 1) / (y1 - y0))

# Dictionary of ships and their quantities for both players
tab_bateaux1 = {2: 3, 3: 2, 4: 1, 5: 1}
big_ship = 5  # Largest ship size
small_ship = 2  # Smallest ship size
tab_bateaux2 = tab_bateaux1.copy()
tab_bateaux = {"j1": tab_bateaux1, "cpu": tab_bateaux2}

placement_phase = True  # Indicates if the game is in the ship placement phase
current_joueur = "j1"  # Current player
current_ship = 5  # Current ship being placed
r = 1, 0  # Direction of the ship being placed (1, 0) for horizontal, (0, 1) for vertical

jeu = game(np.full((n, m), " "), np.full((n, m), " "))  # Initialize the game with empty grids for both players

# Ship placement phase loop
while(placement_phase):
    if current_joueur == "j1":
        x, y = pg.mouse.get_pos()
        x, y = mouse_to_mat(x, y)
        r0, r1 = r
    else:
        # AI randomly places a ship
        x, y = random.randint(0, n - 1), random.randint(0, m - 1)
        h = random.randint(0, 1)
        if h == 0:
            r0, r1 = 0, 1
        else:
            r0, r1 = 1, 0

    tab = jeu.joueur_to_tab(current_joueur)
    # Check if the ship can be placed at the selected position
    b = (x in list(range(min(n, n - r0 * current_ship + 1)))) and (y in list(range(min(m, m - r1 * current_ship + 1)))) and \
        all(v == " " or v == "W" for v in tab[x:x + r0 * current_ship, y]) and all(v == " " or v == "W" for v in tab[x, y:y + r1 * current_ship])

    # AI places its ships
    if current_joueur == "cpu" and b:
        for i in range(r0 * current_ship):
            tab[x + i, y] = "C"
        for j in range(r1 * current_ship):
            tab[x, y + j] = "C"
        # Switch to next ship or player after placing a ship
        if tab_bateaux[current_joueur][current_ship] == 1:
            if current_ship == 2:
                if current_joueur == "cpu":
                    current_joueur = "j1"
                    placement_phase = False
                else:
                    current_ship = 5
                    current_joueur = "cpu"
            else:
                current_ship -= 1
        else:
            tab_bateaux[current_joueur][current_ship] -= 1

    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 3:  # Right click to rotate ship
                r = 1 - r0, 1 - r1
            elif (event.button == 1) and b:  # Left click to place ship
                for i in range(r0 * current_ship):
                    tab[x + i, y] = "C"
                for j in range(r1 * current_ship):
                    tab[x, y + j] = "C"
                # Switch to next ship or player after placing a ship
                if tab_bateaux[current_joueur][current_ship] == 1:
                    if current_ship == 2:
                        if current_joueur == "cpu":
                            current_joueur = "j1"
                            placement_phase = False
                        else:
                            current_ship = 5
                            current_joueur = "cpu"
                    else:
                        current_ship -= 1
                else:
                    tab_bateaux[current_joueur][current_ship] -= 1

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:  # Exit the game
                sys.exit()

    # Update the board state for any modifications made
    b = (x in list(range(min(n, n - r0 * current_ship + 1)))) and (y in list(range(min(m, m - r1 * current_ship + 1)))) and \
        all(v == " " or v == "W" for v in tab[x:x + r0 * current_ship, y]) and all(v == " " or v == "W" for v in tab[x, y:y + r1 * current_ship])

    # Display ship placement preview on the board
    if b:
        waiting_boat = []
        for i in range(r0 * current_ship):
            tab[x + i, y] = "W"
            waiting_boat.append((x + i, y))
        for i in range(r1 * current_ship):
            tab[x, i + y] = "W"
            waiting_boat.append((x, i + y))
        for i in range(n):
            for j in range(m):
                if ((i, j) not in waiting_boat) and tab[i, j] == "W":
                    tab[i, j] = " "  # Clear previously previewed ship position

    jeu.draw(current_joueur)  # Update the display


run=True


play=False
pos=[-1,-1]
img=font.render("",noir,True)
adversaire=alt(current_joueur)
tab_adv=jeu.joueur_to_tab(adversaire)
movl,find_dir,origin=[],[],None

#2 cases, if the AI doesn't have moves to play in priority,
#It will calculate probability map of the "known map"
#Will then play move with highest probability
#If it lands on something, it will try to find the remaining
#spots belonging to the discovered boat by searching the adjacent spots

def next_strike(mat):
    global origin
    global find_dir
    global movl
    #Once you found a boat and its orientation
    if movl!=[]:
        x,y=movl.pop(0)
        if mat[x,y]==" ":
            movl=[]
            known_map[x,y]="M"
            origin=None
        else:
            known_map[x,y]="X"
        return x,y
    #To know what is discovered boat's orientation
    elif find_dir!=[]:
        x,y=find_dir.pop(0)
        if mat[x,y]=="C":
            known_map[x,y]="X"
            find_dir=[]
            r0,r1=x-origin[0],y-origin[1]
            i,j=x+r0,y+r1
            while(i in list(range(n)) and j in list(range(m))):
                movl.append((i,j))
                i,j=i+r0,j+r1
        else:
            known_map[x,y]="M"
        return x,y
    #First case scenario
    else:
        pmap=probability_map(known_map)
        def max_tab(mat):
            maxv=-1
            res=-1,-1
            for i in range(n):
                for j in range(m):
                    if mat[i,j]>maxv:
                        maxv=mat[i,j]
                        res=i,j
            return res
        x,y=max_tab(pmap)
        if mat[x,y]=="C":
            known_map[x,y]="X"
            origin=[x,y]
            ml=[(-1,0),(1,0),(0,1),(0,-1)]
            for r1,r2 in ml:
                i,j=x+r1,y+r2 
                if i in list(range(n)) and j in list(range(m)) and known_map[i,j]!="X":
                    find_dir.append((i,j))
        else:
            known_map[x,y]="M"
        return x,y

while(run):
    if play or current_joueur=="cpu":
        if play:
            play=False
            x,y=pos[1],pos[0]
        else:
            x,y=next_strike(jeu.tabj1)
        if tab_adv[x,y]=="C":
            if current_joueur=="j1":
                res="touché"
            tab_adv[x,y]="X"
            if jeu.lost(adversaire):
                print(current_joueur +" a gagné")
                sys.exit()
        else:
            if current_joueur=="j1":
                res="raté"
            tab_adv[x,y]="M"
        tab_adv=jeu.joueur_to_tab(current_joueur)
        temp=current_joueur
        current_joueur=adversaire
        adversaire=temp
        img=font.render(res,noir,True)
        pos=[-1,-1]
    for event in pg.event.get():
        if event.type==pg.KEYDOWN:
            if event.key==pg.K_ESCAPE:
                sys.exit()
            elif event.key==pg.K_SPACE and current_joueur=="j1":
                play=True
            elif current_joueur=="j1":
                if pos[0]==-1:
                    pos[0]=ord(pg.key.name(event.key))-97
                else:
                    pos[1]=int(pg.key.name(event.key))
            
    jeu.draw((current_joueur))
    SURF.blit(img,(1000,600))
    pg.display.update()
    



    

    
            

                

                

        