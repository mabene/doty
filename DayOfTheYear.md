## DOTY Solver: Goal, algorithms, source code

The full source code of the solver [is here](./DayOfTheYear.py).

This solver is primarily an **educational project** demonstrating **literate programming** and **SAT-based** problem modeling/solving. So the code is **intentionally verbose and pedagogical** rather than optimized for production use. 

**No AI assistants** were used in writing this script. Every line of code and piece of documentation is human-written.

### Goal of the code

The DOTY puzzle can be described as a special case of the problem of [tiling](https://en.wikipedia.org/wiki/Tessellation) a rectangular region (size 7x8) having some fixed (6) and some variable (3) holes, given 7 specific [free pentominoes](https://en.wikipedia.org/wiki/Pentomino) (out of 12) and 3 specific [free tetrominoes](https://en.wikipedia.org/wiki/Tetromino) (out of 5).

This is a special case of the general problem of tiling regions of the plane with sets of polyominoes, which was [proved to be NP-complete](https://link.springer.com/article/10.1007/s00373-007-0713-4), in 2007.

The key goal of the code is thus to generate a [polynomial Karp reduction](https://en.wikipedia.org/wiki/Polynomial-time_reduction) (in time and space) of DOTY-like puzzles onto the the [NP-complete](https://en.wikipedia.org/wiki/NP-completeness) boolean satisfiability problem ([SAT](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)), for which "efficient" [solvers](https://en.wikipedia.org/wiki/SAT_solver) exist, based on decades of AI research.

### Coding Style

This code is written in the [literate programming](https://en.wikipedia.org/wiki/Literate_programming) style. The script is designed to be read sequentially from top to bottom as a "**computer science story**," (or lecture?) with thorough documentation explaining both the problem-solving approach and implementation details.

The script is **self-contained** and deliberately avoids external libraries except for SAT solving, making the entire solution process transparent and educational.

NOTE: The literate programming style, with its **linear storytelling approach**, forces at times ackward choices about how you structure and lay out code: A minor sacrifice for a literarily satisfying outcome that elegantly wraps around executable code.


### Code Size

The puzzle solver is contained in [**one single** Python source file](https://github.com/mabene/doty/blob/main/DayOfTheYear.py), which is **1024** lines long. Only about **26%** of the script is actual executable code (**265** lines). The remaining **74%** is made of comments and explanations: it's the *story* of how we solve the puzzle in plain English.

The core part of the script, where the problem is encoded into a SAT instance (Sections 5.2 and 5.3, see below), is just **20 lines** of code. The rest is about dealing with the input and specification of the problem, pretty printing the output, bookmarking, statistics, and support functions (see next section).
  
### Code Structure

The script is organized into 8 main sections (actual lines of code in brakets):

1. [Introduction and timing setup](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L27-L101) [17]
2. [Puzzle definition (board and pieces)](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L104-L183) [23]
3. [Preprocessing](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L186-L348) [45]
4. [Propositional logic framework](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L351-L469) [24]
5. [SAT encoding (theory + instance)](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L472-L630) [46]
6. [Solving with external SAT solver](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L633-L731) [31]
7. [Solution visualization](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L734-L831) [40]
8. [Statistics and optional output](https://github.com/mabene/doty/blob/318e7d920f4f893d9b29e4ecdcbd9eec0abdafc2/DayOfTheYear.py#L834-L1024) [39]

The actual polynomial **reduction** is executed in Sections **3-5**. The external **solution** process is wrapped by Section **5**. The rest is **input** (Section **1-2**) and **output** (Sections **7-8**) management.

### SAT Encoding & Solving

- **One-hot encoding**: Each variable represents "piece Pk covers cell (i,j)", for k in 1...10, i in 1...8, j in 1...7
- **Constraints**: No overlaps, respect blocked cells, exactly one position per piece, all pieces on the board
- **Optimization**: Tseytin transformation avoids exponential clause explosion
- **Solver**: [CaDiCaL 1.9.5](https://github.com/arminbiere/cadical) (state-of-the-art CDCL SAT solver) wrapped by [pysat 1.8.DEV23](https://pysathq.github.io)

### Advanced Commandline Flags

You can control the SAT encoding by adding/removing formula components, as follows:

```bash
# Remove optional no-piece-here theory component
./DayOfTheYear.py -T.3.2 Mon Jan 1

# Add redundant all-piece-in-use constraint
./DayOfTheYear.py +T.4 Sat Oct 25

# Find any valid piece configuration (no date constraint)
./DayOfTheYear.py -I.1 -I.2
```

Available components:
- **Theory**: `T.1` (required), `T.2` (required), `T.3.1` (required), `T.3.2` (optional), `T.4` (optional)
- **Instance**: `I.1` (required), `I.2` (optional)
- **Encoding**: `E.1.1` (required), `E.1.2` (optional), `E.2.1` (required), `E.2.2` (optional)

See the script's help (`-h`) or source code for detailed component descriptions.

### Solving Performance

The encoding and solving process are fully sequential, so they are executed in a single-process, single-thread mode. On a standard modern (2020-25) laptop machine:

- **Solution finding**: Typically 1-3 seconds
- **Solution enumeration**: Typically a minute or less; it varies (some dates have thousands of solutions)
- **Formula construction**: Negligible overhead

Timing breakdown is available with the `-v` flag.

### Code Features

- **Modular** board/piece definitions (easily customizable; see next section for an example)
- **Flexible date** input parsing (multiple formats accepted)
- **Solution enumeration** (find all solutions for a given date)
- **ASCII art** visualization of solved puzzles
- **DIMACS** export for SAT instances
- **Detailed timing** statistics
- **Configurable formula** components (for experts)

### Code Generality

The code extracts **dynamically** from the visual representations given in Section 2 - in particular, from the variables ``board`` and ``pieces``, all the relevant information about the shape, size, content, and dimension of the board and of the polyominoes.

This means that if you change these "drawings", you can generate and play with and solve any **alternative layout or variant** of the "day of the year" puzzle.

A future version of the script may indeed move such input representations to external files, to be parsed, and solve the full class of tiling problems with polyominoes over rectangular regions with fixed/movable holes.

For example, a typical polyominoes-based puzzle (known since the 30s, formalized in the 50s by [Solomon W.  Golomb](https://en.wikipedia.org/wiki/Solomon_W._Golomb), and later published in a [book](https://en.wikipedia.org/wiki/Polyominoes:_Puzzles,_Patterns,_Problems,_and_Packings) dated 1965, together with many variants) is to tile a 6×10 rectangle with all the twelve free pentominoes; it can be solved by our script setting the inputs as follows:

    board = '''
    ┏━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┓
    ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
    ┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
    ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
    ┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
    ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
    ┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
    ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
    ┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
    ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
    ┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
    ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃   ┃
    ┗━━━┻━━━┻━━━┻━━━┻━━━┻━━━┻━━━┻━━━┻━━━┻━━━┛
    '''

    pieces = '''
    ⬜️🟦🟦 🟦⬜️⬜️ 🟦⬜️⬜️ ⬜️🟦⬜️ 🟦🟦🟦 🟦🟦⬜️ ⬜️🟦 🟦🟦 🟦⬜️ 🟦🟦 🟦🟦 🟦
    🟦🟦⬜️ 🟦🟦⬜️ 🟦⬜️⬜️ 🟦🟦🟦 ⬜️🟦⬜️ ⬜️🟦⬜️ 🟦🟦 🟦⬜️ 🟦🟦 🟦🟦 🟦⬜️ 🟦
    ⬜️🟦⬜️ ⬜️🟦🟦 🟦🟦🟦 ⬜️🟦⬜️ ⬜️🟦⬜️ ⬜️🟦🟦 ⬜️🟦 🟦⬜️ ⬜️🟦 🟦⬜️ 🟦🟦 🟦
    ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️🟦 🟦⬜️ ⬜️🟦 ⬜️⬜️ ⬜️⬜️ 🟦
    ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️ ⬜️⬜️ ⬜️⬜️ ⬜️⬜️ ⬜️⬜️ 🟦
    '''


### Exit Codes

- `0` - Solution found (or help displayed)
- `1` - No solution found

