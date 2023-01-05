import copy
import random
import numpy as np


def sudoku_solver(sudoku):
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
    if(sudokuObject.IsGoal()):
        #print("Goal:")
        #print(sudokuObject.finalValues)
        return sudokuObject.finalValues

    goal = DepthFirstSearch(sudokuObject).GetFinalState()
    #print("Goal:")
    #print(goal)

    return goal


class PartialSudokuState:

    # Takes a 2d 9x9 numpy array representing the initial sudoku state, and creates a possibleValues 9x9 numpy array of numpy arrays
    # If the position on the initial sudoku has a final value, set the position in the possbileValues array to an array length 1 of that value
    # If not, sets the position in the possbileValues array to an array of numbers (1,9)
    def __init__(self, sudoku):

        #print("Sudoku:")
        #print(sudoku)

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
                        self.RemoveFromRow(sudoku[row][column], row)
                        self.RemoveFromColumn(sudoku[row][column], column)
                        self.RemoveFromBlock(sudoku[row][column], row, column)
                    else:
                        self.finalValues = np.full((9, 9), -1.)

    # Method to remove a possible number from all lists of possible values in that row
    def RemoveFromRow(self, number, row):
        for column in range(9):
            if (number in self.possibleValues[row][column]):
                self.possibleValues[row][column].remove(number)

    # Method to remove a possible number from all lists of possible values in that column
    def RemoveFromColumn(self, number, column):
        for row in range(9):
            if (number in self.possibleValues[row][column]):
                self.possibleValues[row][column].remove(number)

    # Method to remove a possible number from all lists of possible values in that 3x3 block
    def RemoveFromBlock(self, number, row, column):
        a = (row // 3) * 3
        b = (column // 3) * 3
        for row in range(3):
            for column in range(3):
                if (number in self.possibleValues[row + a][column + b]):
                    self.possibleValues[row + a][column + b].remove(number)

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

    def setValue(self, row, column, value):
        """Returns a new state with this column set to this row, and the change propagated to other domains"""
        if value not in self.possibleValues[row][column]:
            raise ValueError(f"{row} is not a valid choice for column {column}")

        # create a deep copy: the method returns a new state, does not modify the existing one
        state = copy.deepcopy(self)

        # update this column
        state.possibleValues[row][column] = [value]
        state.finalValues[row][column] = value

        state.RemoveFromRow(value, row)
        state.RemoveFromColumn(value, column)
        state.RemoveFromBlock(value, row, column)

        # if any other columns with no final value only have 1 possible value, make them final
        # singleton_columns = state.get_singleton_columns()
        # while len(singleton_columns) > 0:
        #   col = singleton_columns[0]
        #  state = state.set_value(col, state.possibleValues[col][0])
        # singleton_columns = state.get_singleton_columns()

        return state

    def CreateErrorSudoku(self):
        self.finalValues = np.full((9, 9), -1.)
        return self


# Returns a (row, column) tuple of a position that has only 1 choice
def PickNextPosition(partialState):
    for row in range(9):
        for column in range(9):
            if len(partialState.possibleValues[row][column]) == 1:
                return (row, column)


def DepthFirstSearch(partialState):
    """
    This will do a depth first search on partial states, trying
    each possible value for a single column.

    Notice that we do not need to try every column: if we try
    every possible value for a column and can't find a
    solution, then there is no possible value for this column,
    so there is no solution.
    """
    index = PickNextPosition(partialState)
    value = partialState.GetPossibleValues(index[0], index[1])[0]

    newState = partialState.setValue(index[0], index[1], value)
    if newState.IsGoal():
        return newState
    if not newState.IsInvalid():
        deepState = DepthFirstSearch(newState)
        if deepState.finalValues [0][0] != -1 and deepState.IsGoal():
            return deepState
    return partialState.CreateErrorSudoku()


sudoku_solver(np.load(f"data/medium_puzzle.npy")[1])