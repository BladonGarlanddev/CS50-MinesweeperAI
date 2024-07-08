import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count, is_mine):
        self.cells = set(cells)
        self.count = count
        self.is_mine = is_mine

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"(status: {'mine' if self.is_mine else 'safe'}{self.cells} = {self.count})"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = {}

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        print(f"running add knowledge for a known mine at {cell}")
        self.add_knowledge(cell, 0, True) 

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)

    def add_knowledge(self, cell, count, is_mine):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print(f"add_knowledged evoked for cell: {cell}")
        self.moves_made.add(cell)
        x, y = cell
        neighbors = set()
        mines = set()
        for i in range(max(0, x-1), min(self.width, x+2)):
            for j in range(max(0, y-1), min(self.height, y+2)):
                neighbor = (i, j)
                neighbors.add((i,j))
                print(f"Neighbor: {neighbor}")
                if neighbor in self.knowledge:
                    sentence = self.knowledge[(i,j)]
                    if sentence.is_mine == True:
                        print(f"Count reduced for self at {cell} to {count - 1}")
                        if count:
                            count -= 1
                    else:
                        print(
                            f"Setence for {neighbor} was read as not a mine. Actual sentence: {sentence}"
                        )

                    if cell in sentence.cells:

                        sentence.cells.remove(cell)

                        if is_mine:
                            print(
                                f"reduced {neighbor} count from {sentence.count} to {sentence.count - 1}"
                            )
                            sentence.count -= 1
                            if sentence.count == 0:
                                print(f"Safe space(s) added from sentence: {sentence}")
                                for item in sentence.cells:
                                    print(f"CELL: {item} MARKED AS SAFE")
                                    self.mark_safe(item)
                            continue
                        else:
                            print(f"is_mine read as False for {neighbor}")
                            if len(sentence.cells) == sentence.count and len(sentence.cells) > 0:
                                discovered_mines = sentence.cells.copy()
                                print(f"Recognized mines: {discovered_mines} by square: {neighbor}")
                                for mine in discovered_mines:
                                    print(f"Mine: {mine}")
                                    mines.add(mine)

                    else:
                        print(f"Did not find self within knowledge keys: {self.knowledge.keys()} at: {neighbor}")
                else:
                    print(f"No sentence exists for neighbor: {neighbor}")

        neighbors = neighbors - self.moves_made - self.mines

        self.knowledge[cell] = Sentence(neighbors, count, is_mine)
        print(f"original sentence for {cell}: {self.knowledge[cell]}")

        if len(neighbors) == count and count:
            print(f"Recognized mines: {neighbors} by cell: {cell}")
            for neighbor in neighbors:
                print(f"Mark mine called for: {neighbor}")
                mines.add(neighbor)
        elif count == 0 and not is_mine:
            for neighbor in neighbors:
                print(f"cell: {neighbor} marked as safe")
                self.mark_safe(neighbor)

        for mine in mines:
            self.mark_mine(mine)

        print('\n\n\n')

    def make_safe_move(self):
        unexplored_safes = self.safes - self.moves_made
        if unexplored_safes:
            safe_move = random.sample(unexplored_safes, 1)[0]
            print(f"safe move played at: {safe_move}")
            return safe_move

    def make_random_move(self):
        for i in range(0,7):
            for j in range(0,7):
                if not (i, j) in self.moves_made:
                    return (i,j)
