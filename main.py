import copy
import numpy as np

timeToExit = False
guessState = None

def sudoku_solver(sudoku):
    global timeToExit
    """
    Solves a Sudoku puzzle and returns its unique solution.

    Input
        sudoku : 9x9 numpy array
            Empty cells are designated by 0.

    Output
        9x9 numpy array of integers
            It contains the solution, if there is one. If there is no solution, all array entries should be -1.
    """

    ### YOUR CODE HERE

    sudokuObject = PartialSudokuState(sudoku)
    print("START:", sudoku)
    if(sudokuObject.IsGoal()):
        return sudokuObject.finalValues

    goal = DepthFirstSearch(sudokuObject)
    if goal is None:
        goal = np.full((9, 9), -1.)
    else:
        goal = goal.GetFinalState()
    print("END:",goal)
    timeToExit = False
    return goal


class PartialSudokuState:

    # Takes a 2d 9x9 numpy array representing the initial sudoku state, and creates a possibleValues 9x9 numpy array of numpy arrays
    # If the position on the initial sudoku has a final value, set the position in the possbileValues array to an array length 1 of that value
    # If not, sets the position in the possbileValues array to an array of numbers (1,9)
    def __init__(self, sudoku):

        self.finalValues = sudoku

        # Creates a 9x9 array of arrays of numbers 1-9 to store the possible values each position in the sudoku can take
        self.possibleValues = [[[i for i in range(1, 10)] for _ in range(1, 10)] for _ in range(1, 10)]
        # Sets the values given in the initial sudoku as the only possible value in them places
        # For each new value added, removes that as a possibility from the same row, column, and 3x3 block
        for row in range(9):
            for column in range(9):
                if (sudoku[row][column] != 0):
                    if(sudoku[row][column] in self.possibleValues[row][column]):
                        self.possibleValues[row][column] = [sudoku[row][column]]
                        self.RemoveFromRow(sudoku[row][column], row, column)
                        self.RemoveFromColumn(sudoku[row][column], row, column)
                        self.RemoveFromBlock(sudoku[row][column], row, column)
                    else:
                        self.finalValues = np.full((9, 9), -1.)

    # Method to remove a possible number from all lists of possible values in that row
    def RemoveFromRow(self, number, row, column):
        for everyColumn in range(9):
            if (number in self.possibleValues[row][everyColumn]):
                self.possibleValues[row][everyColumn].remove(number)
        self.possibleValues[row][column]=[number]
        return self.possibleValues
    

    # Method to remove a possible number from all lists of possible values in that column
    def RemoveFromColumn(self, number, row, column):
        for everyRow in range(9):
            if number in self.possibleValues[everyRow][column]:
                self.possibleValues[everyRow][column].remove(number)
        self.possibleValues[row][column] = [number]
        return self.possibleValues

    # Method to remove a possible number from all lists of possible values in that 3x3 block
    def RemoveFromBlock(self, number, row, column):
        a = (row // 3) * 3
        b = (column // 3) * 3
        for everyRow in range(3):
            for everyColumn in range(3):
                if (number in self.possibleValues[everyRow + a][everyColumn + b]):
                    self.possibleValues[everyRow + a][everyColumn + b].remove(number)
        self.possibleValues[row][column] = [number]
        return self.possibleValues
    def IsGoal(self):
        # Returns true if the partial state is a goal state meaning every position in the grid has a final value(1-9) or is an array of -1.
        for row in range (9):
            for column in range (9):
                if(self.finalValues[row][column]==0):
                    return False
        return True

    def IsInvalid(self):
        # Returns true for an invalid partial state if no position has possible values
        for row in range(9):
            for column in range(9):
                if (len(self.possibleValues[row][column]) != 0):
                    return False
        return True

        # def get_singleton_columns(self):

    #   """Returns the columns which have no final value but exactly 1 possible value"""
    #  return [index for index, values in enumerate(self.possibleValues)
    #         if len(values) == 1 and self.final_values[index] == -1]

    def GetPossibleValues(self, row, column):
        return self.possibleValues[row][column].copy()

    def GetFinalState(self):
        if self.IsGoal():
            return self.finalValues
        else:
            return -1

    # def get_singleton_columns(self):
    #    """Returns the columns which have no final value but exactly 1 possible value"""
    #   return [index for index, values in enumerate(self.possibleValues)
    #          if len(values) == 1 and self.final_values[index] == -1]

    def GetSingletonPositions(self):
        positions = []
        for everyRow in range(9):
            for everyColumn in range(9):
                if (len(self.possibleValues[everyRow][everyColumn])==1 and self.finalValues[everyRow][everyColumn]==0):
                    positions.append(everyRow)
                    positions.append(everyColumn)
        return positions

    def setValue(self, row, column, value):
        """Returns a new state with this column set to this row, and the change propagated to other domains"""
        if value not in self.possibleValues[row][column]:

            raise ValueError(f"{row} is not a valid choice for column {column}")

        # create a deep copy: the method returns a new state, does not modify the existing one
        state = copy.deepcopy(self)

        # update this column
        state.possibleValues[row][column] = [value]
        state.finalValues[row][column] = value

        state.RemoveFromRow(value, row, column)
        state.RemoveFromColumn(value, row, column)
        state.RemoveFromBlock(value, row, column)

        # if any other columns with no final value only have 1 possible value, make them final
        # singleton_columns = state.get_singleton_columns()
        # while len(singleton_columns) > 0:
        #   col = singleton_columns[0]
        #  state = state.set_value(col, state.possibleValues[col][0])
        # singleton_columns = state.get_singleton_columns()

        #singletonPositions = state.GetSingletonPositions()
        #while len(singletonPositions) > 0:
        #    state = state.setValue(singletonPositions[0],singletonPositions[1], state.possibleValues[singletonPositions[0]][singletonPositions[1]][0])
        #    singletonPositions = state.GetSingletonPositions()

        return state

    def CreateErrorSudoku(self):
        self.finalValues = np.full((9, 9), -1.)
        return self

# Returns a (row, column) tuple of a position that has only 1 choice
def PickNextPosition(partialState):
    global guessState
    smallestNumber = 1
    while smallestNumber<=9:
        for row in range(9):
            for column in range(9):
                if len(partialState.possibleValues[row][column]) == smallestNumber and partialState.finalValues[row][column] == 0:
                    if smallestNumber != 1:
                        print("A guess is made")
                        guessState = copy.deepcopy(partialState)
                        print("Before: ",guessState.possibleValues[row][column])
                        guessState.possibleValues[row][column].remove(guessState.possibleValues[row][column][0])
                        print("After: ", guessState.possibleValues[row][column])
                        print(row, column)
                    return (row, column)
        smallestNumber = smallestNumber + 1
        print("NUMBER: ",smallestNumber)
    print("OH NO")
    return -1

def DepthFirstSearch(partialState):

    print("POSSIBLE VALUES:")
    print(partialState.possibleValues)

    global timeToExit
    global guessState

    index = PickNextPosition(partialState)



    if (index==-1):
        print("Index is -1")
        print("CHECKING: ",guessState)
        if guessState != None:
            print("Entering guessstate")
            print(partialState.possibleValues)
            print(guessState.possibleValues)
            partialState = guessState
            print(partialState.possibleValues)
            index = PickNextPosition(partialState)
            if index == -1:
                partialState.CreateErrorSudoku()
                timeToExit = True
            else:
                guessState = None
        else:
            partialState.CreateErrorSudoku()
            timeToExit=True

    if timeToExit:
        print("BOUNCE")
        return None

    values = partialState.GetPossibleValues(index[0], index[1])

    for value in values:
        newState = partialState.setValue(index[0], index[1], value)
        if newState.IsGoal():
            return newState
        if not newState.IsInvalid():
            deepState = DepthFirstSearch(newState)
            if deepState is not None and deepState.IsGoal():
                return deepState
    return None


sudoku_solver(np.load(f"data/hard_puzzle.npy")[2])