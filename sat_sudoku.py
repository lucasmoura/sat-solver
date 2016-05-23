import pycosat  # noqa
from pprint import pprint

"""
This scripts implements a SAT solver for a sudoku board with
9 X 9 dimension. The solution is based on the paper from Tjark Weber,
that can be accessed via the following link:

https://www.lri.fr/~conchon/mpri/weber.pdf

Also, the code is based on the tutorials from pycosat library as well.
"""

# Since the board is 9 X 9, there will be 81 cells in total
NUM_CELLS = 81

"""
It will be necessary to create clauses that guarantee that the
3 X 3 subset boards all have unique numbers from 1 to 9. That variable
will be used to create the subset boarders easily.
"""
SUDOKU_BOARD_BOUNDARIES = [1, 4, 7]

# Represent the total amount of digits a subset board can have
DIGITS = 9

"""
Since every cell can have a number from 1 to 9, it is necessary
to create a boolean variable for each possibility of each cell
on the sudoku board. Therefore, the amount of variables is:

NUM_CELLS * DIGITS = 729
"""
NUM_VARIABLES = 729


def get_cell_value(row, column, digit):
    """
    This method will receive a cell and transform it in an unique
    numeric representation for the SAT solver.

    For example, the first cell on a board, cell x[1, 1], can be uniquely
    identified by the numbers 1 though 9, depending, of course, on the
    digit value received. For the second board cell, x[1, 2], It can be
    identified by 10 though 19, and so forth.

    :param row: The row of the cell in a given 9 X 9 board
    :param column: The column of the cell in a given 9 X 9 board
    :param digit: The digit value that the cell will represent

    :return: An int variable that represents the unique cell id
    """
    row_id = NUM_CELLS * (row - 1)
    column_id = DIGITS * (column - 1)

    return row_id + column_id + digit


def get_base_clauses():
    '''
    This method is responsible for creating the base clause for every cell
    in the board. The base clause is just the conjuction of every possible
    digit that a single cell can assume, for example, for the cell x[1, 1],
    the clause would be:

    1 or 2 or 3 or 4 or 5 or 6 or 7 or 8 or 9

    :return: A list containg all the base clauses for every cell in the board
    '''
    base_clauses = []

    for row in range(1, DIGITS + 1):
        for column in range(1, DIGITS + 1):
            clauses = [get_cell_value(row, column, digit)
                       for digit in range(1, DIGITS + 1)]
            base_clauses.append(clauses)

    return base_clauses


def get_unique_digit_clauses():
    '''
    In order to guarantee that a cell can just hold one single digit, it
    is necessary to create clauses to guarantee that behavior. This can be
    achieved by a clause with two variables, each of one representing the
    negation of a possible digit in a given cell. For example, the clause:

    ~1 or ~2

    This clause can only be false if both of the variables are true. Therefore,
    it is necessary to create a clause for each possible digit combination for
    each cell in the board.

    :return: A list containg the clauses to guarantee that a cell has only one
             digit associated with it.
    '''
    unique_digits_clauses = []

    for row in range(1, DIGITS + 1):
        for column in range(1, DIGITS + 1):
            for digit in range(1, DIGITS + 1):
                for next_digit in range(digit + 1, DIGITS + 1):
                    unique_digits_clauses.append([
                        -get_cell_value(row, column, digit),
                        -get_cell_value(row, column, next_digit)])

    return unique_digits_clauses


def get_unique_subset_clause(board_subset):
    '''
    This method will receive a subset of the sudoku board and create clauses
    to guarantee that the each cell in that subset has an unique digit
    associated with it. For example, for a 3 X 3 subset of a sudoku board,
    that can be represented by the following list:

    [(1, 1), (1, 2), (1, 3),
     (2, 1), (2, 2), (2, 3),
     (3, 1), (3, 2), (3, 3)]

    The set of clauses for (1, 1) would be:

    (~1 or ~10) and (~1 or ~19) ..

    Where the number are the unique id for cells (1, 1), (1, 2) and (1, 3)
    for the digit 1.

    :param board_subset: A list of tuples represeting a subset of a sudoku
                         board.

    :return: A list of clauses that guarantee that the digits must be unique in
             the subset parameter.
    '''

    subset_clauses = []

    for index, first_tuple in enumerate(board_subset):
        for n_index, n_tuple in enumerate(board_subset):
            if index < n_index:
                for digit in range(1, DIGITS + 1):
                    clause = [-get_cell_value(
                        first_tuple[0], first_tuple[1], digit),
                        -get_cell_value(
                        n_tuple[0], n_tuple[1], digit)]
                    subset_clauses.append(clause)

    return subset_clauses


def get_rows_digits_unique_clauses():
    '''
    This method creates clauses that ensures that the digits
    on a sudoku row are unique.

    :return: A list of clauses.
    '''
    row_unique_clauses = []

    for row in range(1, DIGITS + 1):
        row_unique_clauses.extend(
            get_unique_subset_clause(
                [(row, column) for column in range(1, DIGITS + 1)]))

    return row_unique_clauses


def get_column_digits_unique_clause():
    '''
    This method creates clauses that ensures that the digits
    on a sudoku column are unique.

    :return: A list of clauses.
    '''
    column_unique_clauses = []

    for row in range(1, DIGITS + 1):
        column_unique_clauses.extend(
            get_unique_subset_clause(
                [(column, row) for column in range(1, DIGITS + 1)]))

    return column_unique_clauses


def get_3x3_sub_grid_clauses():
    '''
    This method created clauses that ensures that the digits
    among a 3 X 3 subset are unique.

    :return: A list of clauses.
    '''

    subgrid_clauses = []

    for row in SUDOKU_BOARD_BOUNDARIES:
        for column in SUDOKU_BOARD_BOUNDARIES:
            subgrid_clauses.extend(
                get_unique_subset_clause(
                    [(row + k % 3, column + k // 3) for k in range(9)]))

    return subgrid_clauses


def get_sudoku_clauses():
    '''
    This method is responsible for composing all the clauses
    for a sudoku game.

    :return: A list containg all the sudoku clauses
    '''
    sudoku_clauses = []

    sudoku_clauses.extend(get_base_clauses())
    sudoku_clauses.extend(get_unique_digit_clauses())
    sudoku_clauses.extend(get_rows_digits_unique_clauses())
    sudoku_clauses.extend(get_column_digits_unique_clause())
    sudoku_clauses.extend(get_3x3_sub_grid_clauses())

    return sudoku_clauses


def get_single_clauses(sudoku_grid):
    '''
    This method is responsible for creating single clauses
    based on the already defined digits in the sudoku grid.
    For example, the given board:

    [ 0, 0, 1
      0, 2, 0,
      0, 0, 0 ]

    Will generate single clauses for cells x[1, 3] and x[2, 2], because the
    value for this cells are already known. It also must be said that the 0
    denote that the digit for a given cell is unknown.

    :param sudoku_grid: A 9 X 9 grid representing a sudoku game.

    :return: A list of single clauses for the given board.
    '''

    single_clauses = []

    for row in range(1, DIGITS + 1):
        for column in range(1, DIGITS + 1):
            cell_value = sudoku_grid[row - 1][column - 1]

            if cell_value:
                single_clauses.append(
                    [get_cell_value(row, column, cell_value)])

    return single_clauses


def get_cell_solution(sudoku_solution, row, column):
    '''
    This method is used to verify which digit will match
    the solution found for a given cell in a sudoku grid.

    :param sudolu_solution: A pycosat SAT solution object.
    :param row: The cell row
    :param column: The cell column

    :return: The digit for the given cell that matches the solution
    '''
    for digit in range(1, DIGITS + 1):
        if get_cell_value(row, column, digit) in sudoku_solution:
            return digit

    return -1


def solve_sudoku(sudoku_grid, sudoku_clauses):
    '''
    This method receive a sudoku grid an solve it using
    a sat solver.

    :param sudoku_grid: A 9 X 9 grid representing a sudoku game.
    :param sudoku_clauses: An array containing all the possible clauses
                           for the sudoki board.

    :return: A 9 x 9 grid representing a sudoku solution for
             the given board.
    '''

    single_clauses = get_single_clauses(sudoku_grid)
    sudoku_clauses.extend(single_clauses)

    sudoku_solution = set(pycosat.solve(sudoku_clauses))

    for row in range(1, DIGITS + 1):
        for column in range(1, DIGITS + 1):
            sudoku_grid[row - 1][column - 1] = get_cell_solution(
                sudoku_solution, row, column)

    return sudoku_grid


def main():
    # Sudoku problem on Weber paper
    print('Sudoku problem: ')
    sudoku_problem = [[0, 2, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 6, 0, 0, 0, 0, 3],
                      [0, 7, 4, 0, 8, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 3, 0, 0, 2],
                      [0, 8, 0, 0, 4, 0, 0, 1, 0],
                      [6, 0, 0, 5, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 1, 0, 7, 8, 0],
                      [5, 0, 0, 0, 0, 9, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 4, 0]]
    pprint(sudoku_problem)

    print('\nGenerating sudoku clauses...')
    sudoku_clauses = get_sudoku_clauses()
    print('Number of generated clauses: {}'.format(len(sudoku_clauses)))

    print('\nGenerating solution:')
    sudoku_solution = solve_sudoku(sudoku_problem, sudoku_clauses)

    assert [[1, 2, 6, 4, 3, 7, 9, 5, 8],
            [8, 9, 5, 6, 2, 1, 4, 7, 3],
            [3, 7, 4, 9, 8, 5, 1, 2, 6],
            [4, 5, 7, 1, 9, 3, 8, 6, 2],
            [9, 8, 3, 2, 4, 6, 5, 1, 7],
            [6, 1, 2, 5, 7, 8, 3, 9, 4],
            [2, 6, 9, 3, 1, 4, 7, 8, 5],
            [5, 4, 8, 7, 6, 9, 2, 3, 1],
            [7, 3, 1, 8, 5, 2, 6, 4, 9]] == sudoku_solution

    pprint(sudoku_solution)


if __name__ == '__main__':
    main()
