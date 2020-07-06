import numpy as np
import random
from tkinter import *

# Jonathan Lin: jkl130
# Jacob Brown: jab860

clear = 0
bomb = 1
# TOGGLE THIS TO TRUE FOR DETAILED PRINTOUTS OF EACH MOVE IN COMMAND PROMPT
# TOGGLE THIS TO FALSE TO PREVENT PRINTOUTS AFTER EACH MOVE
DEBUG = True
PRINTFEEDBACK = False
PRINTALLRESULTS = False
PRINTFINALRESULTS = True
playback = []
results = []
guiActive = False


class mine:

    def __init__(self, dim, numBombs):
        global bomb, clear
        # Create a 2D array to represent graph
        realgrid = np.array([[clear for j in range(0,dim)] for i in range(0,dim)])
        guesses = np.array([[clear for j in range(0,dim)] for i in range(0,dim)])

        temp = numBombs
        if temp > (dim*dim):
            temp = (dim*dim)
            numBombs = (dim*dim)
        while temp > 0:
            i = int(random.random() * dim)
            j = int(random.random() * dim)
            if realgrid[i, j] != bomb:
                realgrid[i,j] = bomb
                guesses[i,j] = bomb
                temp -= 1
        dist = np.array([[0 for j in range(0,dim)] for i in range(0,dim)])
        for i in range(0,dim):
            for j in range(0,dim):
                neighbors = [(i-1,j-1),(i-1,j),(i-1,j+1),
                             (i,j-1),(i,j),(i,j+1),
                             (i+1,j-1),(i+1,j),(i+1,j+1)]
                count = 0
                for adj in neighbors:
                    if 0 <= adj[0] < dim and 0 <= adj[1] < dim:
                        if realgrid[adj] == bomb:
                            count += 1
                dist[i,j] = count
        guigrid = np.array([[None for j in range(0, dim)] for i in range(0, dim)])
        agent = {
            "safe": [],
            "mine": [],
            "mark": [],
            "safeAndMarked": [],
            "mineButMarked": [],
            "yellowMark": [],
            "hidden": [],
            "uncovered": [],
            "inferSafe": [],
            "inferMine": [],
            "inferHidden": []
        }
        for i in range(0, dim):
            for j in range(0,dim):
                agent['hidden'].append((i,j))
        #print(agent)
        self.realgrid = realgrid
        self.dist = dist
        self.dim = dim
        self.guigrid = guigrid
        self.guesses = guesses
        self.basicAgent = agent
        self.improvedBool = False
        self.totalMines = numBombs


    # Prompted by the Display button on the GUI
    # Command prompt prints out the entire grid including all of the bomb locations.
    # Purpose: Used primarily for testing. Not meant for normal gameplay.
    def display(self):
        print(self.realgrid)
        #print(self.dist)
        #print(self.guigrid)


    # Prompted by the Restart button on the GUI
    # Closes the program and reopens another board to be played.
    def restart(self):
        global state
        state = True
        self.root.destroy()

    # Prompted by the Reveal button on the GUI
    # Reveals all of the cells on the board
    def revealAll(self):
        for i in range(0,self.dim):
            for j in range(0,self.dim):
                if self.realgrid[i, j] == 0:
                    self.guigrid[i, j].config(bg="lime", text=self.dist[i, j])
                    self.guesses[i, j] = 2
                    #print(self.guesses)
                else:
                    self.guigrid[i, j].config(bg="salmon", text="BOMB")
                    self.guesses[i, j] = 3


    # Prompted upon choosing any cell, regardless if it's revealed or not.
    def pickle(self, i, j):
        if DEBUG:
            print("Node is " + str(i) + ", " + str(j))
        if "Pick " + str((i, j)) not in playback:
            playback.append("Pick " + str((i, j)))
        check = 0
        if self.realgrid[i, j] == 0:
            if guiActive:
                self.guigrid[i, j].config(bg="lime", text=self.dist[i, j])
            self.guesses[i, j] = 1
        else:
            if guiActive:
                self.guigrid[i, j].config(bg="salmon", text="BOMB")
            check = 1
        # BASIC ALGORITHM
        neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                     (i, j - 1), (i, j + 1),
                     (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
        totalNeighbors = 0
        for adj in neighbors:
            if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim:
                totalNeighbors += 1
        if self.dist[i, j] == 0:
            for adj in neighbors:
                if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim and adj not in self.basicAgent['uncovered']:
                    removeFrom = ""
                    if adj in self.basicAgent['hidden']:
                        #removeFrom = 'hidden'
                        #self.basicAgent[removeFrom].remove(adj)
                        self.basicAgent['safe'].append(adj)
                        #self.basicAgent['uncovered'].append(adj)
        elif check != 1:
            numHidden = 0
            numRevealed = 0
            numSafe = 0
            numBombs = 0
            for adj in neighbors:
                if adj in self.basicAgent['uncovered']:
                    numRevealed += 1
                    if self.realgrid[adj] == bomb:
                        numBombs += 1
                    elif self.realgrid[adj] == clear:
                        numSafe += 1
                if adj in self.basicAgent['hidden']:
                    numHidden += 1
                if adj in self.basicAgent['mark']:
                    numBombs += 1
            if DEBUG:
                print(str(numHidden) + " hidden, " + str(numRevealed) + " revealed, and " + str(numSafe) + " safe")
                print("There are " + str(self.dist[i, j] - numBombs) + " potentially hidden bombs, " + str(numHidden) + " total hidden bombs")
            # if, for a given cell, the total number of mines (the clue) minus the number of revealed mines
            # is the number of hidden neighbors, every hidden neighbor is a mine
            if (self.dist[i, j] - numBombs) == numHidden:
                for adj in neighbors:
                    if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim and adj in self.basicAgent['hidden'] and adj not in self.basicAgent['mine']:
                        self.basicAgent['mark'].append(adj)
                        self.basicAgent['hidden'].remove(adj)
            # if, for a given cell, the total number of safe neighbors (8 - clue) minus the number of revealed
            # safe neighbors is the number of hidden neighbors, every hidden neighbor is safe
            elif ((totalNeighbors - self.dist[i, j]) - numSafe) == numHidden:
                for adj in neighbors:
                    if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim and adj in self.basicAgent['hidden']:
                        self.basicAgent['safe'].append(adj)
        if (i, j) in self.basicAgent['safe']:
            self.basicAgent['safe'].remove((i, j))
            self.basicAgent['safeAndMarked'].append((i, j))
        if (i, j) in self.basicAgent['mineButMarked']:
            self.basicAgent['mineButMarked'].remove((i, j))
        if (i, j) in self.basicAgent['hidden']:
            self.basicAgent['hidden'].remove((i, j))
        if self.realgrid[i, j] == bomb:
            self.basicAgent['mine'].append((i, j))
            self.basicAgent['uncovered'].append((i, j))
        else:
            self.basicAgent['uncovered'].append((i, j))
        self.basicAgent['safe'] = list(set(self.basicAgent['safe']))
        self.basicAgent['mine'] = list(set(self.basicAgent['mine']))
        self.basicAgent['hidden'] = list(set(self.basicAgent['hidden']))
        self.basicAgent['uncovered'] = list(set(self.basicAgent['uncovered']))
        self.basicAgent['safeAndMarked'] = list(set(self.basicAgent['safeAndMarked']))
        if DEBUG:
            print("Safe: " + str(self.basicAgent['safe']))
            print("SafeMarked: " + str(self.basicAgent['safeAndMarked']))
            print("Mine: " + str(self.basicAgent['mine']))
            print("Mark: " + str(self.basicAgent['mark']))
            print("YellowMark: " + str(self.basicAgent['yellowMark']))
            print("Hidden: " + str(self.basicAgent['hidden']))
            print("Uncovered: " + str(self.basicAgent['uncovered']))
            print("================================================")
        self.improvedBool = False


    # Prompted when using the Min Risk method
    def infer(self, i, j, k, type):
        check = 0
        # BASIC ALGORITHM
        neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                     (i, j - 1), (i, j + 1),
                     (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
        totalNeighbors = 0
        for adj in neighbors:
            if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim:
                totalNeighbors += 1
        if self.dist[i, j] == 0:
            for adj in neighbors:
                if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim and adj not in self.basicAgent['uncovered']:
                    removeFrom = ""
                    if adj in self.basicAgent['hidden'] and not (adj == k):
                        self.basicAgent['infer' + type[0].upper() + type[1:]].append(adj)
        elif check != 1:
            numHidden = 0
            numRevealed = 0
            numSafe = 0
            numBombs = 0
            for adj in neighbors:
                if adj in self.basicAgent['uncovered'] or (adj == k and type == 'safe'):
                    numRevealed += 1
                    if self.realgrid[adj] == bomb or (adj == k and type == 'mine'):
                        numBombs += 1
                    elif self.realgrid[adj] == clear or (adj == k and type == 'safe'):
                        numSafe += 1
                if adj in self.basicAgent['hidden'] and adj != k:
                    numHidden += 1
                if adj in self.basicAgent['mark']:
                    numBombs += 1
            # if, for a given cell, the total number of mines (the clue) minus the number of revealed mines
            # is the number of hidden neighbors, every hidden neighbor is a mine
            if (self.dist[i, j] - numBombs) == numHidden:
                for adj in neighbors:
                    if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim and adj in self.basicAgent['hidden'] and adj != k:
                        self.basicAgent['infer' + type[0].upper() + type[1:]].append(adj)
                        #self.mark(adj[0], adj[1])
            # if, for a given cell, the total number of safe neighbors (8 - clue) minus the number of revealed
            # safe neighbors is the number of hidden neighbors, every hidden neighbor is safe
            elif ((totalNeighbors - self.dist[i, j]) - numSafe) == numHidden:
                for adj in neighbors:
                    if 0 <= adj[0] < self.dim and 0 <= adj[1] < self.dim and adj in self.basicAgent['hidden'] and adj != k:
                        self.basicAgent['infer' + type[0].upper() + type[1:]].append(adj)
                        #self.mark(adj[0], adj[1])
                        #self.basicAgent['hidden'].remove(adj)


    # Prompted by right-clicking on any cell.
    # Fails if a cell that is already revealed is called by mark()
    def mark(self, i, j):
        if (i, j) not in self.basicAgent['uncovered']:
            if "Mark " + str((i, j)) not in playback:
                playback.append("Mark " + str((i, j)))
            if guiActive:
                self.guigrid[i, j].config(bg="yellow", text="MARKED")
            self.basicAgent['mineButMarked'].append((i, j))
            if (i, j) in self.basicAgent['mark']:
                self.basicAgent['mark'].remove((i, j))
            if (i, j) in self.basicAgent['hidden']:
                self.basicAgent['hidden'].remove((i, j))
            self.basicAgent['uncovered'].append((i, j))
            self.basicAgent['yellowMark'].append((i, j))


    # Prompted by the Quit button.
    # Simply quits the game and exits the program.
    def quit(self):
        global state
        state = False
        self.root.destroy()


    # 2.1 A Basic Agent Algorithm for Comparison
    # Prompted by the Basic AI button and the Full Basic button.
    # Note: Parts of the Basic Agent Algorithm is incoporated into the function called pickle()
    def basicAIalgo(self):
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        # if no hidden cell can be conclusively identified as a mine or safe, pick a cell to reveal at random
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) > 0:
            self.pickle(self.basicAgent['safe'][len(self.basicAgent['safe'])-1][0], self.basicAgent['safe'][len(self.basicAgent['safe'])-1][1])
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " revealed mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)


    def improvedHelper(self, i, j):
        neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                     (i, j - 1), (i, j + 1),
                     (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
        totalScore = 0
        for adj in neighbors:
            if adj in self.basicAgent['uncovered'] and adj not in self.basicAgent['mineButMarked']:
                totalScore += self.dist[adj]
        return totalScore


    # An Improved Agent
    # Prompted by the Improved AI button and the Full Improved button.
    # Note: Parts of the Basic Agent Algorithm is incorporated into the function called pickle()
    def improvedAIalgo(self):
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['uncovered']) == 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        elif len(self.basicAgent['safe']) > 0:
            self.basicAgent['safe'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
            self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
        # if no hidden cell can be conclusively identified as a mine or safe, do one of the following:
        # 1) search through all revealed safe cells and find safe and marked cells
        # 2)
        # 3) if no safe and marked cells can be added to the query, then choose a cell at random
        # Notes: Scenario 2 will most definitely happen at the start of the game and moves in which
        # a clue of 0 has not been found yet.
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            searchElsewhere = []
            for r in self.basicAgent['uncovered']:
                if self.realgrid[r] != bomb:
                    i = r[0]
                    j = r[1]
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['hidden']:
                            searchElsewhere.append((i, j))
                            break
            if len(searchElsewhere) > 0:
                searchElsewhere.sort(key=lambda x: self.dist[x])
                for r in searchElsewhere:
                    self.pickle(r[0], r[1])
            # Scenario 1
            if len(self.basicAgent['mark']) > 0:
                self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
            elif len(self.basicAgent['safe']) > 0:
                self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
            # End of Scenario 1
            # Scenario 2
            elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0:
                self.basicAgent['hidden'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
                self.pickle(self.basicAgent['hidden'][0][0], self.basicAgent['hidden'][0][1])
            # End of Scenario 2
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)
        if PRINTFEEDBACK:
            print(playback)


    # Minimized Cost
    # Prompted by the Min Cost button and the Full Min Cost button.
    # Note: Parts of the Basic Agent Algorithm is incorporated into the function called pickle()
    def minCost(self):
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['uncovered']) == 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        elif len(self.basicAgent['safe']) > 0:
            self.basicAgent['safe'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
            self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
        # if no hidden cell can be conclusively identified as a mine or safe, do one of the following:
        # 1)  if no safe and marked cells can be added to the query, then assign probabilities to each hidden cell and
        #    choose the cell with the lowest probability
        # Notes: Scenario 2 will most definitely happen at the start of the game and moves in which
        # a clue of 0 has not been found yet.
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            # Scenario 1
            searchElsewhere = []
            for r in self.basicAgent['uncovered']:
                if self.realgrid[r] != bomb:
                    i = r[0]
                    j = r[1]
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['hidden']:
                            searchElsewhere.append((i, j))
                            break
            if len(searchElsewhere) > 0:
                searchElsewhere.sort(key=lambda x: self.dist[x])
                for r in searchElsewhere:
                    self.pickle(r[0], r[1])
            # Scenario 1
            if len(self.basicAgent['mark']) > 0:
                self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
            elif len(self.basicAgent['safe']) > 0:
                self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
            # Scenario 2
            elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0:
                randomKnowledge = dict([(coord, 0.0) for coord in self.basicAgent['hidden']])
                #print(randomKnowledge)
                for r in self.basicAgent['hidden']:
                    totalProb = 0.0
                    i = r[0]
                    j = r[1]
                    #print((i,j))
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['uncovered'] and self.realgrid[adj] != bomb:
                            probability = 1.0
                            numBombs = 0
                            numFoundBombs = 0
                            if self.dist[adj] > 0:
                                k = adj[0]
                                l = adj[1]
                                adjNeighbors = [(k - 1, l - 1), (k - 1, l), (k - 1, l + 1),
                                                (k, l - 1), (k, l + 1),
                                                (k + 1, l - 1), (k + 1, l), (k + 1, l + 1)]
                                #print(adj)
                                for adjAdj in adjNeighbors:
                                    if adjAdj in self.basicAgent['hidden']:
                                        numBombs += 1
                                    elif adjAdj in self.basicAgent['mine'] or adjAdj in self.basicAgent['yellowMark']:
                                        numFoundBombs += 1
                                #print(numBombs)
                                probability = float(numBombs - self.dist[adj] + numFoundBombs) / float(numBombs)
                                #print(probability)
                                if totalProb == 0.0:
                                    totalProb = 1 * probability
                                else:
                                    totalProb = totalProb * probability
                            #if totalProb > 1.0:
                                #print(str(r) + " / " + str(probability) + " / Hidden: " + str(numBombs) + " / Found Bombs: " + str(numFoundBombs) + "/ Node: " + str(self.dist[adj]))
                    if totalProb != 0.0:
                        randomKnowledge[r] = 1.0 - totalProb
                randomKnowledge = sorted(randomKnowledge.items(), key=lambda kv: kv[1])
                #print(randomKnowledge)
                #print(randomKnowledge[0][0], randomKnowledge[0][1])
                self.pickle(randomKnowledge[0][0][0], randomKnowledge[0][0][1])
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)
        if PRINTFEEDBACK:
            print(playback)


    # Minimized Risk
    # Prompted by the Min Risk button and the Full Min Risk button.
    # Note: Parts of the Basic Agent Algorithm is incorporated into the function called pickle()
    def minRisk(self):
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['uncovered']) == 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        elif len(self.basicAgent['safe']) > 0:
            self.basicAgent['safe'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
            self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
        # if no hidden cell can be conclusively identified as a mine or safe, do one of the following:
        # 1)  if no safe and marked cells can be added to the query, then assign probabilities to each hidden cell and
        #    find the expected number of squares that can be worked out if a given cell were to be clicked on. Finally,
        #    click on the cell with the highest expected number of solvable squares.
        # Notes: Scenario 2 will most definitely happen at the start of the game and moves in which
        # a clue of 0 has not been found yet.
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            # Scenario 1
            searchElsewhere = []
            for r in self.basicAgent['uncovered']:
                if self.realgrid[r] != bomb:
                    i = r[0]
                    j = r[1]
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['hidden']:
                            searchElsewhere.append((i, j))
                            break
            if len(searchElsewhere) > 0:
                searchElsewhere.sort(key=lambda x: self.dist[x])
                for r in searchElsewhere:
                    self.pickle(r[0], r[1])
            # Scenario 1
            if len(self.basicAgent['mark']) > 0:
                self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
            elif len(self.basicAgent['safe']) > 0:
                self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
            # Scenario 2
            elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0:
                randomKnowledge = dict([(coord, 0.0) for coord in self.basicAgent['hidden']])
                inferredCells = dict([(coord, 0) for coord in self.basicAgent['hidden']])
                #print(randomKnowledge)
                for r in self.basicAgent['hidden']:
                    totalProb = 0.0
                    i = r[0]
                    j = r[1]
                    #print((i,j))
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['uncovered'] and self.realgrid[adj] != bomb:
                            probability = 1.0
                            numBombs = 0
                            numFoundBombs = 0
                            if self.dist[adj] > 0:
                                k = adj[0]
                                l = adj[1]
                                adjNeighbors = [(k - 1, l - 1), (k - 1, l), (k - 1, l + 1),
                                                (k, l - 1), (k, l + 1),
                                                (k + 1, l - 1), (k + 1, l), (k + 1, l + 1)]
                                #print(adj)
                                for adjAdj in adjNeighbors:
                                    if adjAdj in self.basicAgent['hidden']:
                                        numBombs += 1
                                    elif adjAdj in self.basicAgent['mine'] or adjAdj in self.basicAgent['yellowMark']:
                                        numFoundBombs += 1
                                #print(numBombs)
                                probability = float(numBombs - self.dist[adj] + numFoundBombs) / float(numBombs)
                                #print(probability)
                                if totalProb == 0.0:
                                    totalProb = 1 * probability
                                else:
                                    totalProb = totalProb * probability
                            #if totalProb > 1.0:
                                #print(str(r) + " / " + str(probability) + " / Hidden: " + str(numBombs) + " / Found Bombs: " + str(numFoundBombs) + "/ Node: " + str(self.dist[adj]))
                    if totalProb != 0.0:
                        randomKnowledge[r] = 1.0 - totalProb
                #randomKnowledge = sorted(randomKnowledge.items(), key=lambda kv: kv[1])
                #print(randomKnowledge)
                # INFERENCE
                for a in self.basicAgent['hidden']:
                    numMines = 0
                    numSafe = 0
                    # WHAT IF ARBITRARY COORDINATE A IS A MINE?
                    self.basicAgent['inferSafe'] = []
                    self.basicAgent['inferMine'] = []
                    searchElsewhere = []
                    for r in self.basicAgent['uncovered']:
                        if self.realgrid[r] != bomb:
                            i = r[0]
                            j = r[1]
                            neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                         (i, j - 1), (i, j + 1),
                                         (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                            for adj in neighbors:
                                if adj in self.basicAgent['hidden']:
                                    searchElsewhere.append((i, j))
                                    break
                    if len(searchElsewhere) > 0:
                        searchElsewhere.sort(key=lambda x: self.dist[x])
                        for r in searchElsewhere:
                            self.infer(r[0], r[1], a, 'mine')
                        numMines = len(self.basicAgent['inferSafe'])
                        for r in searchElsewhere:
                            self.infer(r[0], r[1], a, 'safe')
                        numSafe = len(self.basicAgent['inferMine'])
                    #print("Stuff for " + str(a))
                    #print(randomKnowledge)
                    #print(inferredCells)
                    #print(self.basicAgent['inferMine'])
                    #print(self.basicAgent['inferSafe'])
                    #print(numMines)
                    #print(numSafe)
                    inferredCells[a] = (randomKnowledge[a] * numMines) + ((1.0 - randomKnowledge[a]) * numSafe)
                inferredCells = sorted(inferredCells.items(), key=lambda kv: kv[1], reverse=True)
                # END INFERENCE
                #print(inferredCells)
                self.pickle(inferredCells[0][0][0], inferredCells[0][0][1])
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)
        if PRINTFEEDBACK:
            print(playback)


    # Minimized Cost Improved
    # Prompted by the Min Cost Improved button and the Full Min Cost Improved button.
    # Note: Parts of the Basic Agent Algorithm is incorporated into the function called pickle()
    def minCostImproved(self):
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['uncovered']) == 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        elif len(self.basicAgent['safe']) > 0:
            self.basicAgent['safe'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
            self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
        # if no hidden cell can be conclusively identified as a mine or safe, do one of the following:
        # 1) search through all revealed safe cells and find safe and marked cells
        # 2) if no safe and marked cells can be added to the query, then assign probabilities to each hidden cell and
        #    choose the cell with the lowest probability
        # Notes: Scenario 2 will most definitely happen at the start of the game and moves in which
        # a clue of 0 has not been found yet.
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            searchElsewhere = []
            for r in self.basicAgent['uncovered']:
                if self.realgrid[r] != bomb:
                    i = r[0]
                    j = r[1]
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['hidden']:
                            searchElsewhere.append((i, j))
                            break
            if len(searchElsewhere) > 0:
                searchElsewhere.sort(key=lambda x: self.dist[x])
                for r in searchElsewhere:
                    self.pickle(r[0], r[1])
            # Scenario 1
            if len(self.basicAgent['mark']) > 0:
                self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
            elif len(self.basicAgent['safe']) > 0:
                self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
            # End of Scenario 1
            # Scenario 2
            elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0:
                randomKnowledge = dict([(coord, 0.0) for coord in self.basicAgent['hidden']])
                #print(randomKnowledge)
                for r in self.basicAgent['hidden']:
                    totalProb = 0.0
                    i = r[0]
                    j = r[1]
                    #print((i,j))
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['uncovered'] and self.realgrid[adj] != bomb:
                            probability = 1.0
                            numBombs = 0
                            numFoundBombs = 0
                            if self.dist[adj] > 0:
                                k = adj[0]
                                l = adj[1]
                                adjNeighbors = [(k - 1, l - 1), (k - 1, l), (k - 1, l + 1),
                                                (k, l - 1), (k, l + 1),
                                                (k + 1, l - 1), (k + 1, l), (k + 1, l + 1)]
                                #print(adj)
                                for adjAdj in adjNeighbors:
                                    if adjAdj in self.basicAgent['hidden']:
                                        numBombs += 1
                                    elif adjAdj in self.basicAgent['mine'] or adjAdj in self.basicAgent['yellowMark']:
                                        numFoundBombs += 1
                                #print(numBombs)
                                probability = float(numBombs - self.dist[adj] + numFoundBombs) / float(numBombs)
                                #print(probability)
                                if totalProb == 0.0:
                                    totalProb = 1 * probability
                                else:
                                    totalProb = totalProb * probability
                            #if totalProb > 1.0:
                                #print(str(r) + " / " + str(probability) + " / Hidden: " + str(numBombs) + " / Found Bombs: " + str(numFoundBombs) + "/ Node: " + str(self.dist[adj]))
                    if totalProb != 0.0:
                        randomKnowledge[r] = 1.0 - totalProb
                    else:
                        randomKnowledge[r] = 0.5
                randomKnowledge = sorted(randomKnowledge.items(), key=lambda kv: kv[1])
                #print(randomKnowledge)
                #print(randomKnowledge[0][0], randomKnowledge[0][1])
                self.pickle(randomKnowledge[0][0][0], randomKnowledge[0][0][1])
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)
        if PRINTFEEDBACK:
            print(playback)


    # Minimized Risk Improved
    # Prompted by the Min Risk Improved button and the Full Min Risk Improved button.
    # Note: Parts of the Basic Agent Algorithm is incorporated into the function called pickle()
    def minRiskImproved(self):
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['uncovered']) == 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        elif len(self.basicAgent['safe']) > 0:
            self.basicAgent['safe'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
            self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
        # if no hidden cell can be conclusively identified as a mine or safe, do one of the following:
        # 1) search through all revealed safe cells and find safe and marked cells
        # 2) if no safe and marked cells can be added to the query, then assign probabilities to each hidden cell and
        #    find the expected number of squares that can be worked out if a given cell were to be clicked on. Finally,
        #    click on the cell with the highest expected number of solvable squares.
        # Notes: Scenario 2 will most definitely happen at the start of the game and moves in which
        # a clue of 0 has not been found yet.
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            searchElsewhere = []
            for r in self.basicAgent['uncovered']:
                if self.realgrid[r] != bomb:
                    i = r[0]
                    j = r[1]
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['hidden']:
                            searchElsewhere.append((i, j))
                            break
            if len(searchElsewhere) > 0:
                searchElsewhere.sort(key=lambda x: self.dist[x])
                for r in searchElsewhere:
                    self.pickle(r[0], r[1])
            # Scenario 1
            if len(self.basicAgent['mark']) > 0:
                self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
            elif len(self.basicAgent['safe']) > 0:
                self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
            # End of Scenario 1
            # Scenario 2
            elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0:
                randomKnowledge = dict([(coord, 0.0) for coord in self.basicAgent['hidden']])
                inferredCells = dict([(coord, 0) for coord in self.basicAgent['hidden']])
                #print(randomKnowledge)
                for r in self.basicAgent['hidden']:
                    totalProb = 0.0
                    i = r[0]
                    j = r[1]
                    #print((i,j))
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['uncovered'] and self.realgrid[adj] != bomb:
                            probability = 1.0
                            numBombs = 0
                            numFoundBombs = 0
                            if self.dist[adj] > 0:
                                k = adj[0]
                                l = adj[1]
                                adjNeighbors = [(k - 1, l - 1), (k - 1, l), (k - 1, l + 1),
                                                (k, l - 1), (k, l + 1),
                                                (k + 1, l - 1), (k + 1, l), (k + 1, l + 1)]
                                #print(adj)
                                for adjAdj in adjNeighbors:
                                    if adjAdj in self.basicAgent['hidden']:
                                        numBombs += 1
                                    elif adjAdj in self.basicAgent['mine'] or adjAdj in self.basicAgent['yellowMark']:
                                        numFoundBombs += 1
                                #print(numBombs)
                                probability = float(numBombs - self.dist[adj] + numFoundBombs) / float(numBombs)
                                #print(probability)
                                if totalProb == 0.0:
                                    totalProb = 1 * probability
                                else:
                                    totalProb = totalProb * probability
                            #if totalProb > 1.0:
                                #print(str(r) + " / " + str(probability) + " / Hidden: " + str(numBombs) + " / Found Bombs: " + str(numFoundBombs) + "/ Node: " + str(self.dist[adj]))
                    if totalProb != 0.0:
                        randomKnowledge[r] = 1.0 - totalProb
                    else:
                        randomKnowledge[r] = 0.5
                #randomKnowledge = sorted(randomKnowledge.items(), key=lambda kv: kv[1])
                #print(randomKnowledge)
                # INFERENCE
                for a in self.basicAgent['hidden']:
                    numMines = 0
                    numSafe = 0
                    # WHAT IF ARBITRARY COORDINATE A IS A MINE?
                    self.basicAgent['inferSafe'] = []
                    self.basicAgent['inferMine'] = []
                    searchElsewhere = []
                    for r in self.basicAgent['uncovered']:
                        if self.realgrid[r] != bomb:
                            i = r[0]
                            j = r[1]
                            neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                         (i, j - 1), (i, j + 1),
                                         (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                            for adj in neighbors:
                                if adj in self.basicAgent['hidden']:
                                    searchElsewhere.append((i, j))
                                    break
                    if len(searchElsewhere) > 0:
                        searchElsewhere.sort(key=lambda x: self.dist[x])
                        for r in searchElsewhere:
                            self.infer(r[0], r[1], a, 'mine')
                        numMines = len(self.basicAgent['inferSafe'])
                        for r in searchElsewhere:
                            self.infer(r[0], r[1], a, 'safe')
                        numSafe = len(self.basicAgent['inferMine'])
                    #print("Stuff for " + str(a))
                    #print(randomKnowledge)
                    #print(inferredCells)
                    #print(self.basicAgent['inferMine'])
                    #print(self.basicAgent['inferSafe'])
                    #print(numMines)
                    #print(numSafe)
                    inferredCells[a] = (randomKnowledge[a] * numMines*(1/3)) + ((1.0 - randomKnowledge[a]) * numSafe*(2/3))
                inferredCells = sorted(inferredCells.items(), key=lambda kv: kv[1], reverse=True)
                # END INFERENCE
                #print(inferredCells)
                self.pickle(inferredCells[0][0][0], inferredCells[0][0][1])
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)
        if PRINTFEEDBACK:
            print(playback)


    # Improvements
    # An algorithm created to answer the Improvements section of the write-up report.
    # Note: Parts of the Basic Agent Algorithm is incoporated into the function called pickle()
    def mineKnownAIalgo(self):
        if len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine']) == self.totalMines:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
            # if the entire board is revealed
            if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
                # print("FINAL RESULTS")
                # print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                # print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                results.append((len(self.basicAgent['mineButMarked']),
                                len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
                if PRINTALLRESULTS:
                    print(results)
            return
        # if a cell is identified as a mine, mark it and update your information
        if len(self.basicAgent['mark']) > 0:
            self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['uncovered']) == 0:
            randomCoord = int(random.random() * len(self.basicAgent['hidden']))
            self.pickle(self.basicAgent['hidden'][randomCoord][0], self.basicAgent['hidden'][randomCoord][1])
        # if no hidden cell can be conclusively identified as a mine or safe, do one of the following:
        # 1) search through all revealed safe cells and find safe and marked cells
        # 2) if no safe and marked cells can be added to the query, then choose a cell at random
        # Notes: Scenario 2 will most definitely happen at the start of the game and moves in which
        # a clue of 0 has not been found yet.
        elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) > 0:
            searchElsewhere = []
            for r in self.basicAgent['uncovered']:
                if self.realgrid[r] != bomb:
                    i = r[0]
                    j = r[1]
                    neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                                 (i, j - 1), (i, j + 1),
                                 (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
                    for adj in neighbors:
                        if adj in self.basicAgent['hidden']:
                            searchElsewhere.append((i, j))
                            break
            if len(searchElsewhere) > 0:
                searchElsewhere.sort(key=lambda x: self.dist[x])
                for r in searchElsewhere:
                    self.pickle(r[0], r[1])
            # Scenario 1
            if len(self.basicAgent['mark']) > 0:
                self.mark(self.basicAgent['mark'][0][0], self.basicAgent['mark'][0][1])
            elif len(self.basicAgent['safe']) > 0:
                self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
            # End of Scenario 1
            # Scenario 2
            elif len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0:
                self.basicAgent['hidden'].sort(key=lambda x: self.improvedHelper(x[0], x[1]))
                self.pickle(self.basicAgent['hidden'][0][0], self.basicAgent['hidden'][0][1])
            # End of Scenario 2
        # if a cell is identified as safe, reveal it and update your information
        elif len(self.basicAgent['safe']) > 0:
            self.pickle(self.basicAgent['safe'][0][0], self.basicAgent['safe'][0][1])
        # if the entire board is revealed
        if len(self.basicAgent['safe']) == 0 and len(self.basicAgent['mark']) == 0 and len(self.basicAgent['hidden']) == 0:
            if PRINTFINALRESULTS:
                print("FINAL RESULTS")
                print("You found " + str(len(self.basicAgent['mine'])) + " revealed mines: " + str(self.basicAgent['mine']))
                print("You found " + str(len(self.basicAgent['mineButMarked'])) + " hidden mines: " + str(self.basicAgent['mineButMarked']))
                print("================================================")
            results.append((len(self.basicAgent['mineButMarked']), len(self.basicAgent['mineButMarked']) + len(self.basicAgent['mine'])))
            if PRINTALLRESULTS:
                print(results)
        if PRINTFEEDBACK:
            print(playback)


    # Prompted by the Full Basic button on the GUI
    # This will run through the basic algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph using various dimension and numMines values
    # and record results of the basic agent's algorithm.
    def fullBasic(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.basicAIalgo()


    # Prompted by the Full Improved button on the GUI
    # This will run through the improved algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph using various dimension and numMines values
    # and record results of the improved agent's algorithm.
    def fullImproved(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.improvedAIalgo()


    # Prompted by the Full Min Cost button on the GUI
    # This will run through the improved minimum cost algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph using various dimension and numMines values
    # and record results of the improved agent's algorithm.
    def fullMinCost(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.minCost()


    # Prompted by the Full Min Risk button on the GUI
    # This will run through the improved minimum risk algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph using various dimension and numMines values
    # and record results of the improved agent's algorithm.
    def fullMinRisk(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.minRisk()


    # Prompted by the Full Min Cost Improv button on the GUI
    # This will run through the improved minimum cost algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph using various dimension and numMines values
    # and record results of the improved agent's algorithm.
    def fullMinCostImproved(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.minCostImproved()


    # Prompted by the Full Min Risk Improv button on the GUI
    # This will run through the improved minimum risk algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph using various dimension and numMines values
    # and record results of the improved agent's algorithm.
    def fullMinRiskImproved(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.minRiskImproved()


    # Cannot be prompted through the GUI, as this is only meant to be called when answering
    # the question in the Improvements section of the Write-up
    # This will run through the improved algorithm until all cells have been revealed or marked.
    # Purpose: Use this to create a probability graph with a modified priority queue favoring
    # mines over safe cells.
    def fullMinesAlreadyKnown(self):
        while len(self.basicAgent['safe']) != 0 or len(self.basicAgent['mark']) != 0 or len(self.basicAgent['hidden']) != 0:
            self.mineKnownAIalgo()


    # Opens the GUI to display the entire board.
    def openGUI(self):
        guiActive = True
        playback = []
        self.root = Tk()
        self.root.title("Minesweeper")
        try:
            photo = PhotoImage(file = 'VoltorbIcon.png')
            self.root.iconphoto(False, photo)
        except:
            pass
        for i in range(0,self.dim):
            for j in range(0,self.dim):
                self.guigrid[i, j] = Button(self.root, command=lambda i=i, j=j: self.pickle(i, j), bg="gray", height=4, width=8)
                self.guigrid[i, j].bind('<Button-3>', lambda event, i=i, j=j: self.mark(i, j))
                self.guigrid[i, j].grid(row=i, column=j)
                #guigrid[i, j].config()
        height = 2
        width = 8
        restart = Button(self.root, command=self.restart, text="Restart", height=height, width=width)
        display = Button(self.root, command=self.display, text="Display", height=height, width=width)
        reveal = Button(self.root, command=self.revealAll, text="Reveal", height=height, width=width)
        quit = Button(self.root, command=self.quit, text="Quit", height=height, width=width)
        basicAI = Button(self.root, command=self.basicAIalgo, text="Basic AI", height=height, width=width)
        fullBasic = Button(self.root, command=self.fullBasic, text="Full Basic", height=height, width=width)
        improvedAI = Button(self.root, command=self.improvedAIalgo, text="Improved\nAI", height=height, width=width)
        fullImproved = Button(self.root, command=self.fullImproved, text="Full\nImproved", height=height, width=width)
        minimumCost = Button(self.root, command=self.minCost, text="Min\nCost", height=height, width=width)
        fullMinimumCost = Button(self.root, command=self.fullMinCost, text="Full Min\nCost", height=height, width=width)
        minimumRisk = Button(self.root, command=self.minRisk, text="Min\nRisk", height=height, width=width)
        fullMinimumRisk = Button(self.root, command=self.fullMinRisk, text="Full Min\nRisk", height=height, width=width)
        minimumCostImproved = Button(self.root, command=self.minCostImproved, text="Min\nCost\nImprov", height=height+1, width=width)
        fullMinimumCostImproved = Button(self.root, command=self.fullMinCostImproved, text="Full Min\nCost\nImprov", height=height+1, width=width)
        minimumRiskImproved = Button(self.root, command=self.minRiskImproved, text="Min\nRisk\nImprov", height=height+1, width=width)
        fullMinimumRiskImproved = Button(self.root, command=self.fullMinRiskImproved, text="Full Min\nRisk\nImprov", height=height+1, width=width)
        if self.dim == 1:
            restart.grid(row=self.dim, column=0)
            display.grid(row=self.dim + 1, column=0)
            reveal.grid(row=self.dim + 2, column=0)
            quit.grid(row=self.dim + 3, column=0)
            basicAI.grid(row=self.dim + 4, column=0)
            fullBasic.grid(row=self.dim + 5, column=0)
            improvedAI.grid(row=self.dim + 6, column=0)
            fullImproved.grid(row=self.dim + 7, column=0)
            minimumCost.grid(row=self.dim + 8, column=0)
            fullMinimumCost.grid(row=self.dim + 9, column=0)
            minimumRisk.grid(row=self.dim + 10, column=0)
            fullMinimumRisk.grid(row=self.dim + 11, column=0)
            minimumCostImproved.grid(row=self.dim + 8, column=0)
            fullMinimumCostImproved.grid(row=self.dim + 9, column=0)
            minimumRiskImproved.grid(row=self.dim + 10, column=0)
            fullMinimumRiskImproved.grid(row=self.dim + 11, column=0)
        elif 4 > self.dim > 1:
            restart.grid(row=self.dim, column=0)
            display.grid(row=self.dim, column=1)
            reveal.grid(row=self.dim + 1, column=0)
            quit.grid(row=self.dim + 1, column=1)
            basicAI.grid(row=self.dim + 2, column=0)
            fullBasic.grid(row=self.dim + 2, column=1)
            improvedAI.grid(row=self.dim + 3, column=0)
            fullImproved.grid(row=self.dim + 3, column=1)
            minimumCost.grid(row=self.dim + 4, column=0)
            fullMinimumCost.grid(row=self.dim + 4, column=1)
            minimumRisk.grid(row=self.dim + 5, column=0)
            fullMinimumRisk.grid(row=self.dim + 5, column=1)
            minimumCostImproved.grid(row=self.dim + 6, column=0)
            fullMinimumCostImproved.grid(row=self.dim + 6, column=1)
            minimumRiskImproved.grid(row=self.dim + 7, column=0)
            fullMinimumRiskImproved.grid(row=self.dim + 7, column=1)
        else:
            restart.grid(row=self.dim, column=int(self.dim/2)-2)
            display.grid(row=self.dim, column=int(self.dim/2)-1)
            reveal.grid(row=self.dim, column=int(self.dim/2))
            quit.grid(row=self.dim, column=int(self.dim/2)+1)
            basicAI.grid(row=self.dim + 1, column=int(self.dim/2)-2)
            fullBasic.grid(row=self.dim + 1, column=int(self.dim/2)-1)
            improvedAI.grid(row=self.dim + 1, column=int(self.dim/2))
            fullImproved.grid(row=self.dim + 1, column=int(self.dim/2)+1)
            minimumCost.grid(row=self.dim + 2, column=int(self.dim/2)-2)
            fullMinimumCost.grid(row=self.dim + 2, column=int(self.dim/2)-1)
            minimumRisk.grid(row=self.dim + 2, column=int(self.dim/2))
            fullMinimumRisk.grid(row=self.dim + 2, column=int(self.dim/2)+1)
            minimumCostImproved.grid(row=self.dim + 3, column=int(self.dim/2)-2)
            fullMinimumCostImproved.grid(row=self.dim + 3, column=int(self.dim/2)-1)
            minimumRiskImproved.grid(row=self.dim + 3, column=int(self.dim/2))
            fullMinimumRiskImproved.grid(row=self.dim + 3, column=int(self.dim/2)+1)
        self.root.mainloop()


    # Code for bonus section. Mark the top n cells as clear with respect to numerical hint mismatch
    # Code to be used when we know Ppos is > 0 and Pneg is 0
    def falsePositive(self, Ppos):
        # Called after done processing cells
        priorityQueue = {}
        for bomb in self.basicAgent["mineButMarked"]:
            count = 0
            i = bomb[0]
            j = bomb[1]
            # top left
            if i > 0 and j > 0:
                count += self.dist[i-1, j-1]
            # left
            if j > 0:
                count += self.dist[i, j-1]
            # top
            if i > 0:
                count += self.dist[i-1, j]
            # top right
            if i > 0 and j < self.dim-1:
                count += self.dist[i-1, j+1]
            # bottom
            if i < self.dim-1:
                count += self.dist[i+1, j]
            # right
            if j < self.dist[i, j+1]:
                count += self.dist[i, j+1]
            # bottom right
            if j < self.dim-1 and i < self.dim-1:
                count += self.dist[i+1, j+1]
            # bottom left
            if i < self.dim-1 and j > 0:
                count += self.dist[i+1, j-1]
            priorityQueue[bomb] = count

        numToConvert = round(len(priorityQueue)*Ppos)
        while numToConvert > 0:
            min = min(priorityQueue.keys(), key = lambda ky: priorityQueue[ky])
            self.guesses[priorityQueue[min]] = 0
            del d[min]
            numToConvert -= 1


state = True
maintest = 1
# Opens the GUI to allow for the user to play the game.
if maintest == 1:
    while state:
        guiActive = True
        mazetest = mine(9,15)
        state = False
        mazetest.openGUI()
# Returns two arrays of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the basic agent algorithm and the improved agent algorithm.
elif maintest == 2:
    basicResults = []
    improvResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNumBasic = 0
        totalDenBasic = 0
        totalNumImprov = 0
        totalDenImprov = 0
        for s in range(0,10):
            mazetest = mine(10,r)
            state = False
            mazetest.fullBasic()
            totalNumBasic += results[count][0]
            totalDenBasic += results[count][1]
            count += 1
            mazetest = mine(12,r)
            state = False
            mazetest.fullImproved()
            totalNumImprov += results[count][0]
            totalDenImprov += results[count][1]
            count += 1
        basicResults.append(totalNumBasic / totalDenBasic)
        improvResults.append(totalNumImprov / totalDenImprov)
    print(basicResults)
    print(improvResults)
# Returns an array of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the mine-priority improved agent algorithm.
elif maintest == 3:
    markFirstResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNum = 0
        totalDen = 0
        for s in range(0,10):
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinesAlreadyKnown()
            totalNum += results[count][0]
            totalDen += results[count][1]
            count += 1
        markFirstResults.append(totalNum / totalDen)
    print(markFirstResults)
# Returns two arrays of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the basic agent algorithm and the basic minimizing cost agent algorithm.
elif maintest == 4:
    improvResults = []
    minCostResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNumBasic = 0
        totalDenBasic = 0
        totalNumCost = 0
        totalDenCost = 0
        for s in range(0,10):
            mazetest = mine(10,r)
            state = False
            mazetest.fullImproved()
            totalNumBasic += results[count][0]
            totalDenBasic += results[count][1]
            count += 1
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinCost()
            totalNumCost += results[count][0]
            totalDenCost += results[count][1]
            count += 1
        improvResults.append(totalNumBasic / totalDenBasic)
        minCostResults.append(totalNumCost / totalDenCost)
    print(improvResults)
    print(minCostResults)
# Returns results of a 10x10 with a density of 50%.
# Uses the basic minimizing cost agent algorithm.
elif maintest == 5:
    minCostResults = []
    count = 0
    for r in range(0,25):
        totalNumCost = 0
        totalDenCost = 0
        for s in range(0,10):
            mazetest = mine(10,50)
            state = False
            mazetest.fullImproved()
            totalNumCost += results[count][0]
            totalDenCost += results[count][1]
            count += 1
        minCostResults.append(totalNumCost / totalDenCost)
    print(minCostResults)
# Returns two arrays of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the basic agent algorithm and the basic minimizing risk agent algorithm.
elif maintest == 6:
    improvResults = []
    minRiskResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNumBasic = 0
        totalDenBasic = 0
        totalNumRisk = 0
        totalDenRisk = 0
        for s in range(0,3):
            mazetest = mine(10,r)
            state = False
            mazetest.fullImproved()
            totalNumBasic += results[count][0]
            totalDenBasic += results[count][1]
            count += 1
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinRisk()
            totalNumRisk += results[count][0]
            totalDenRisk += results[count][1]
            count += 1
        improvResults.append(totalNumBasic / totalDenBasic)
        minRiskResults.append(totalNumRisk / totalDenRisk)
    print(improvResults)
    print(minRiskResults)
# Returns one array of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the improved minimizing cost agent.
elif maintest == 7:
    improvResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNum = 0
        totalDen = 0
        for s in range(0,10):
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinCostImproved()
            totalNum += results[count][0]
            totalDen += results[count][1]
            count += 1
        improvResults.append(totalNum / totalDen)
    print(improvResults)
# Returns one array of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the improved minimizing risk agent.
elif maintest == 7:
    improvResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNum = 0
        totalDen = 0
        for s in range(0,10):
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinCostImproved()
            totalNum += results[count][0]
            totalDen += results[count][1]
            count += 1
        improvResults.append(totalNum / totalDen)
    print(improvResults)
# Returns one array of total averages when playing Minesweeper with 0 to 99 bombs present in a 10x10 board 10 times each.
# Uses the improved minimizing risk agent.
elif maintest == 8:
    improvResults = []
    minCostResults = []
    minCostImprovedResults = []
    count = 0
    for r in range(1,100):
        print(str(r) + " bombs")
        totalNumImproved = 0
        totalDenImproved = 0
        totalNumCost = 0
        totalDenCost = 0
        totalNumCostImproved = 0
        totalDenCostImproved = 0
        for s in range(0,10):
            mazetest = mine(10,r)
            state = False
            mazetest.fullImproved()
            totalNumImproved += results[count][0]
            totalDenImproved += results[count][1]
            count += 1
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinCost()
            totalNumCost += results[count][0]
            totalDenCost += results[count][1]
            count += 1
            mazetest = mine(10,r)
            state = False
            mazetest.fullMinCostImproved()
            totalNumCostImproved += results[count][0]
            totalDenCostImproved += results[count][1]
            count += 1
        improvResults.append(totalNumImproved / totalDenImproved)
        minCostResults.append(totalNumCost / totalDenCost)
        minCostImprovedResults.append(totalNumCostImproved / totalDenCostImproved)
    print(improvResults)
    print(minCostResults)
    print(minCostImprovedResults)
