import pygame
from pygame.locals import *
import sys
from classesForGrid import Pathfinding, PathNode, Grid, Button


def renderBasicFont(text:str=''):
    font = pygame.font.SysFont('Corbel', 30)
    text = font.render(text, True, (255, 255, 255))
    return text


def reset():
    startPos = None
    endPos = None
    path = None
    closedList = []
    openList = []
    return startPos, endPos, path, closedList, openList, False


def reset_nodes(grid: Grid):
    for x in range(grid.width):
        for y in range(grid.height):
            pathNode: PathNode = grid.GetGridObject(x, y)
            assert pathNode is not None, 'Error with code'
            pathNode.gCost = 23000
            pathNode.CalculateFCost()
            pathNode.cameFromNode = None


def drawGrid(grid: Grid, displaySurface):
    color = (155, 155, 155)
    cellSize = grid.cellSize
    width = grid.width
    height = grid.height

    for x in range(width):
        for y in range(height):
            if grid.GetGridObject(x, y).isWalkable is False:
                posX1, posY1 = grid.GetWorldPosition(x, y)
                rect = pygame.Rect(posX1, posY1, cellSize, cellSize)
                pygame.draw.rect(displaySurface, (0, 0, 0), rect)
            pygame.draw.line(displaySurface, color, grid.GetWorldPosition(x, y),
                             grid.GetWorldPosition(x, y + 1))
            pygame.draw.line(displaySurface, color, grid.GetWorldPosition(x, y),
                             grid.GetWorldPosition(x + 1, y))

    pygame.draw.line(displaySurface, color, grid.GetWorldPosition(0, height), grid.GetWorldPosition(width, height))
    pygame.draw.line(displaySurface, color, grid.GetWorldPosition(width, 0), grid.GetWorldPosition(width, height))


def test():
    global gameState
    if gameState == 1:
        gameState = 0
    else:
        gameState = 1
    print('clicked the text')


def displayButtons(buttons: list[:Button], mousePos, clicked: bool):
    for button in buttons:
        if button.displayButton(mousePos) and clicked:
            button.function()


def toggleWalkable(grid, pos):
    x, y = grid.GetXY(pos[0], pos[1])
    if grid.ValidateLocation(x, y):
        grid.GetGridObject(x, y).isWalkable = not grid.GetGridObject(x, y).isWalkable


def mainloop():
    global gameState
    pygame.init()

    def resetGrid():
        global startPos, endPos, path, openList, closedList, pathfinding, blues
        for x in range(grid.width):
            for y in range(grid.height):
                thingi: PathNode = grid.GetGridObject(x, y)
                thingi.isWalkable = True
        startPos, endPos, path, openList, closedList, pathfinding = reset()
        blues = None

    cellSize = 5
    grid = Grid(140, 105, cellSize, PathNode)

    HEIGHT = grid.height * cellSize
    WIDTH = grid.width * cellSize + 150
    FPS = 60

    clock = pygame.time.Clock()

    displaySurface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")
    debugging = False

    pathfind = Pathfinding(grid)

    color = (155, 155, 155)
    blues = None

    startPos, endPos, path, openList, closedList, pathfinding = reset()

    gameState = 1
    learningControls = 0
    choosingPath = 1
    #      saveGrid(grid, 'test.json')
    endNode = None
    # button1 = Button(50, 50, 150, 50, "yo", 'er', displaySurface)
    font = pygame.font.SysFont('Corbel', 32)

    tutorialText = [
        "left click once anywhere on the grid to set start position,",
        "then left click once again somewhere else to set end position",
        "Right click to set if a node can be paththrough or not (is draggable)",
        "'q': to change modes",
        "the modes are; pathfind normally or ",
        "               show how pathfinding program works",
        "'r': to reset and begin again"
    ]
    textToBlit = []
    for i in tutorialText:
        textToBlit.append(font.render(i,True, (255, 255, 255)))

    switchView = Button(755, 50, 140, 50, 'Switch Vew', test, displaySurface)
    resetButton = Button(775, 200, 100, 50, 'Reset', resetGrid, displaySurface)
    exitButton = Button(775, 500, 100, 50, 'Exit', sys.exit, displaySurface)
    genericButtons = [switchView, resetButton, exitButton]
    clicked = False
    dragging = False
    speedy = True
    alreadyDraggedAcross = []
    while True:
        pos = pygame.mouse.get_pos()
        pygame.display.update()
        if not speedy:
            clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if gameState == learningControls:
                    continue
                if event.key == pygame.K_r:
                    startPos, endPos, path, openList, closedList, pathfinding = reset()
                    blues = None
                if event.key == pygame.K_q:
                    startPos, endPos, path, openList, closedList, pathfinding = reset()
                    debugging = not debugging
                    blues = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    dragging = True
            if event.type == pygame.MOUSEBUTTONUP:

                clicked = True
                if gameState == choosingPath:
                    if event.button == 1:
                        x, y = grid.GetXY(pos[0], pos[1])
                        if not grid.ValidateLocation(x, y):
                            continue

                        if startPos is None:
                            startPos = pos
                        elif endPos is None:
                            endPos = pos
                            if not debugging:
                                try:
                                    path = pathfind.FindPath((startPos[0], startPos[1]),
                                                             (endPos[0], endPos[1]))
                                except ValueError as e:
                                    print(e)
                            else:
                                x, y = grid.GetXY(startPos[0], startPos[1])
                                startNode = grid.GetGridObject(x, y)
                                x, y = grid.GetXY(endPos[0], endPos[1])
                                endNode = grid.GetGridObject(x, y)
                                openList = [startNode]
                                closedList = []
                                pathfinding = True

                                reset_nodes(grid)

                                startNode.gCost = 0
                                startNode.hCost = pathfind.CalculateDistanceCost(startNode, endNode)
                                startNode.CalculateFCost()
                    if event.button == 3:
                        dragging = False
                        alreadyDraggedAcross = []

        displaySurface.fill((50, 50, 50))
        if gameState == learningControls:
            displayButtons(genericButtons, pos, clicked)
            for i in range(len(textToBlit)):
                displaySurface.blit(textToBlit[i], (40, 50*i))
        elif gameState == choosingPath:
            #drawGrid(grid, displaySurface)
            displayButtons(genericButtons, pos, clicked)
            if (path is not None) or (blues is not None):
                stateText = renderBasicFont('Found Path!')
            elif endPos is not None:
                stateText = renderBasicFont('Pathfinding...')
            elif startPos is not None:
                stateText = renderBasicFont('Choosing end node')
            elif startPos is None:
                stateText = renderBasicFont('Chossing Start node')
            else:
                stateText = renderBasicFont('NONEs')
            displaySurface.blit(stateText, (600, 300))
            x, y = grid.GetXY(pos[0], pos[1])
            if dragging and grid.ValidateLocation(x, y):
                nodeOn = grid.GetGridObject(x, y)
                if nodeOn not in alreadyDraggedAcross:
                    toggleWalkable(grid, pos)
                    alreadyDraggedAcross.append(nodeOn)

            if pathfinding:
                for node in closedList:
                    x, y = node.x, node.y
                    x, y = grid.GetWorldPosition(x, y)
                    rect = pygame.Rect(x, y, cellSize, cellSize)
                    pygame.draw.rect(displaySurface, (0, 0, 155), rect)
                for node in openList:
                    x, y = node.x, node.y
                    x, y = grid.GetWorldPosition(x, y)
                    rect = pygame.Rect(x, y, cellSize, cellSize)
                    pygame.draw.rect(displaySurface, (0, 155, 0), rect)

            if path is not None:

                for i in range(len(path) - 1):
                    x = path[i][0]
                    x1 = path[i + 1][0]
                    y = path[i][1]
                    y1 = path[i + 1][1]

                    x = x - cellSize * 0.5
                    x1 = x1 - cellSize * 0.5
                    y = y - cellSize * 0.5
                    y1 = y1 - cellSize * 0.5

                    pygame.draw.line(displaySurface, color, (x, y), (x1, y1))

            if pathfinding and len(openList) > 0:
                currentNode = pathfind.GetLowestFCostNode(openList)
                if currentNode == endNode:
                    blues = pathfind.CalculatePath(endNode)
                    pathfinding = False
                openList.remove(currentNode)
                closedList.append(currentNode)
                for neighbourNode in pathfind.GetNeighbourList(currentNode):
                    if neighbourNode in closedList:
                        continue
                    if not neighbourNode.isWalkable:
                        closedList.append(neighbourNode)
                        continue
                    tentativeGCost = currentNode.gCost + pathfind.CalculateDistanceCost(currentNode, neighbourNode)
                    if tentativeGCost < neighbourNode.gCost:
                        neighbourNode.cameFromNode = currentNode
                        neighbourNode.gCost = tentativeGCost
                        neighbourNode.hCost = pathfind.CalculateDistanceCost(neighbourNode, endNode)
                        neighbourNode.CalculateFCost()
                        if neighbourNode not in openList:
                            openList.append(neighbourNode)

            if blues is not None:

                for i in range(len(blues) - 1):
                    x, y = grid.GetWorldPosition(blues[i].x, blues[i].y)
                    x1, y1 = grid.GetWorldPosition(blues[i + 1].x, blues[i + 1].y)

                    x = x + cellSize * 0.5
                    x1 = x1 + cellSize * 0.5
                    y = y + cellSize * 0.5
                    y1 = y1 + cellSize * 0.5

                    pygame.draw.line(displaySurface, (255, 0, 0), (x, y), (x1, y1))
        clicked = False


if __name__ == "__main__":
    mainloop()
