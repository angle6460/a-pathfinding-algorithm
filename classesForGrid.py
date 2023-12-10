from math import floor
import pygame


class PathNode:
    def __init__(self, grid, x, y):
        self.grid = grid
        self.x = x
        self.y = y

        self.isWalkable = True

        self.gCost = 0
        self.hCost = 0
        self.fCost = 0

        self.cameFromNode = None

    def CalculateFCost(self):
        self.fCost = self.gCost + self.hCost

    def SetIsWalkable(self, isWalkable):
        self.isWalkable = isWalkable

    def ToggleIsWalkable(self):
        self.isWalkable = not self.isWalkable


class Grid:
    def __init__(self, width, height, cellSize, cellObject):
        self.width = width
        self.height = height
        self.cellSize = cellSize
        self.gridArray = []

        for x in range(self.width):
            self.gridArray.append([])
            for y in range(self.height):
                self.gridArray[x].append(cellObject(self, x, y))

    def SetGridObject(self, x, y, value):
        if x >= 0 & y >= 0 & x <= self.width & y <= self.height:
            self.gridArray[x][y] = value

    def GetGridObject(self, x, y):
        if self.ValidateLocation(x, y):
            return self.gridArray[x][y]
        raise ValueError(f'Cant find the object at ({x}, {y})')

    def ValidateLocation(self, x, y):
        withinXRange = self.width > x >= 0
        withinYRange = self.height > y >= 0
        if withinYRange and withinXRange:
            return True
        return False

    def GetWorldPosition(self, x, y):
        return x * self.cellSize, y * self.cellSize

    def GetXY(self, screenPositionX, screenPositionY):

        x = int(floor(screenPositionX / self.cellSize))
        y = int(floor(screenPositionY / self.cellSize))

        return x, y


class Pathfinding:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.MOVE_DIAGONAL_COST = 14
        self.MOVE_STAIGHT_COST = 10

    def FindPath(self, startWorldPosition, endWorldPosition):
        startX, startY = self.grid.GetXY(startWorldPosition[0], startWorldPosition[1])
        endX, endY = self.grid.GetXY(endWorldPosition[0], endWorldPosition[1])
        print('START', startX, startY, endX, endY)
        path = self.FindPath1(startX, startY, endX, endY)

        if path is None:
            return path
        vectorPath = []
        for pathNode in path:
            pathNodex = pathNode.x * self.grid.cellSize + 1 * self.grid.cellSize
            pathNodey = pathNode.y * self.grid.cellSize + 1 * self.grid.cellSize
            vectorPath.append((pathNodex, pathNodey))
        return vectorPath

    def FindPath1(self, startX: int, startY: int, endX: int, endY: int):
        startNode = self.grid.GetGridObject(startX, startY)
        endNode = self.grid.GetGridObject(endX, endY)
        openList = [startNode]
        closedList = []
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                pathNode: PathNode = self.grid.GetGridObject(x, y)
                if pathNode is None:
                    print("ERRR")
                    continue
                pathNode.gCost = 23000
                pathNode.CalculateFCost()
                pathNode.cameFromNode = None
        startNode.gCost = 0
        startNode.hCost = self.CalculateDistanceCost(startNode, endNode)
        startNode.CalculateFCost()
        while len(openList) > 0:
            currentNode = self.GetLowestFCostNode(openList)
            if currentNode == endNode:
                return self.CalculatePath(endNode)
            openList.remove(currentNode)
            closedList.append(currentNode)
            for neighbourNode in self.GetNeighbourList(currentNode):
                if neighbourNode in closedList:
                    continue
                if not neighbourNode.isWalkable:
                    closedList.append(neighbourNode)
                    continue
                tentativeGCost = currentNode.gCost + self.CalculateDistanceCost(currentNode, neighbourNode)
                if tentativeGCost < neighbourNode.gCost:
                    neighbourNode.cameFromNode = currentNode
                    neighbourNode.gCost = tentativeGCost
                    neighbourNode.hCost = self.CalculateDistanceCost(neighbourNode, endNode)
                    neighbourNode.CalculateFCost()
                    if neighbourNode not in openList:
                        openList.append(neighbourNode)
        print("Could not find any path")
        return None

    def CalculateDistanceCost(self, a: PathNode, b: PathNode):
        xDistance = abs(a.x - b.x)
        yDistance = abs(a.y - b.y)
        remaining = abs(xDistance - yDistance)
        return self.MOVE_DIAGONAL_COST * min(xDistance, yDistance) + self.MOVE_STAIGHT_COST * remaining

    @staticmethod
    def GetLowestFCostNode(pathNodeList: list):
        lowestFCostNode = pathNodeList[0]
        for i in pathNodeList:
            if i.fCost < lowestFCostNode.fCost:
                lowestFCostNode = i
        return lowestFCostNode

    def GetNeighbourList(self, currentNode: PathNode):
        # neighbourList = []
        # if currentNode.x - 1 >= 0:
        #     neighbourList.append(self.GetNode(currentNode.x - 1, currentNode.y))
        #     if currentNode.y - 1 >= 0:
        #         neighbourList.append(self.GetNode(currentNode.x - 1, currentNode.y - 1))
        #     if currentNode.y + 1 < self.grid.height:
        #         neighbourList.append(self.GetNode(currentNode.x - 1, currentNode.y + 1))
        #
        # if currentNode.x + 1 < self.grid.width:
        #     neighbourList.append(self.GetNode(currentNode.x + 1, currentNode.y))
        #     if currentNode.y - 1 >= 0:
        #         neighbourList.append(self.GetNode(currentNode.x + 1, currentNode.y - 1))
        #     if currentNode.y + 1 < self.grid.height:
        #         neighbourList.append(self.GetNode(currentNode.x + 1, currentNode.y + 1))
        # if currentNode.y - 1 >= 0:
        #     neighbourList.append(self.GetNode(currentNode.x, currentNode.y - 1))
        # if currentNode.y + 1 < self.grid.height:
        #     neighbourList.append(self.GetNode(currentNode.x, currentNode.y + 1))
        # return neighbourList
        neighbourList = []

        def add_neighbor(x, y):
            if 0 <= x < self.grid.width and 0 <= y < self.grid.height:
                neighbourList.append(self.GetNode(x, y))

        add_neighbor(currentNode.x - 1, currentNode.y)
        add_neighbor(currentNode.x + 1, currentNode.y)
        add_neighbor(currentNode.x, currentNode.y - 1)
        add_neighbor(currentNode.x, currentNode.y + 1)
        add_neighbor(currentNode.x - 1, currentNode.y - 1)
        add_neighbor(currentNode.x - 1, currentNode.y + 1)
        add_neighbor(currentNode.x + 1, currentNode.y - 1)
        add_neighbor(currentNode.x + 1, currentNode.y + 1)

        return neighbourList

    def GetNode(self, x, y):
        return self.grid.GetGridObject(x, y)

    def CalculatePath(self, endNode: PathNode):
        path = [endNode]
        currentNode = endNode
        while currentNode.cameFromNode is not None:
            path.append(currentNode.cameFromNode)
            currentNode = currentNode.cameFromNode
        path.reverse()
        return path


class Button:
    def __init__(self, x, y, width, height, text, function, displaySurface: pygame.surface.Surface, size: int = 35):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        font = pygame.font.SysFont('Corbel', size)
        self.text = font.render(text, True, (255, 255, 255))

        self.function = function
        self.displaySurface = displaySurface

    def displayButton(self, mousePos):
        withinX = self.x <= mousePos[0] <= self.x + self.width
        withinY = self.y <= mousePos[1] <= self.y + self.height
        if withinX and withinY:
            color = (100, 100, 100)
        else:
            color = (170, 170, 170)
        rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.displaySurface, color, rect)
        self.displaySurface.blit(self.text, (self.x + 3, self.y + 15))
        return withinX and withinY
