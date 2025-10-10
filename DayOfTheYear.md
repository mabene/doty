# DOTY AI Solver: Goal, algorithms, source code

This solver is primarily an **educational AI project** demonstrating **literate programming** and **SAT-based** problem modeling/solving. The code is **intentionally verbose and pedagogical** rather than optimized for production use: for each line of code, there are approximately three lines of comments.

The full source code of the solver [is here](./DayOfTheYear.py). An appendix with supplementary (PhD-level) material [is here](./Appendix.md).

*Note* **¬🤖**: **No AI assistants** were used in writing this AI script! Every line of code and piece of documentation is human-written.

## 1. The nature of this puzzle

The DOTY puzzle is a special case of the [tiling](https://en.wikipedia.org/wiki/Tessellation) problem: covering a 7x8 rectangular region that contains some fixed (6) and some variable (3) holes, using 7 specific [free pentominoes](https://en.wikipedia.org/wiki/Pentomino) (from the set of 12) and 3 specific [free tetrominoes](https://en.wikipedia.org/wiki/Tetromino) (from the set of 5).

This falls under the broader class of problems involving tiling regions of the plane with sets of polyominoes—a problem that was [proved to be NP-complete](https://link.springer.com/article/10.1007/s00373-007-0713-4) in 2007.

Many variants of this puzzle exist. A famous example, known since the 1930s and formalized in the 1950s by [Solomon W. Golomb](https://en.wikipedia.org/wiki/Solomon_W._Golomb), is to tile a 6×10 rectangle with all twelve [free pentominoes](https://en.wikipedia.org/wiki/Pentomino). This and other variants were later published in Golomb's classic [book](https://en.wikipedia.org/wiki/Polyominoes:_Puzzles,_Patterns,_Problems,_and_Packings) in 1965.

## 2. Goal of the code

The primary goal of the code is to produce a [polynomial Karp reduction](https://en.wikipedia.org/wiki/Polynomial-time_reduction) (in both time and space) of DOTY-like puzzles to the [NP-complete](https://en.wikipedia.org/wiki/NP-completeness) Boolean satisfiability problem ([SAT](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)), for which "efficient" [solvers](https://en.wikipedia.org/wiki/SAT_solver) exist, based on decades of AI research.

In practice, the ``DayOfTheYear.py`` script transforms (or: *reduces*; *encodes*) any puzzle instance into an "equivalent" propositional formula. It then uses a SAT solver to determine the satisfiability of this formula and extract its model(s), thereby addressing the core combinatorial challenge of the puzzle.

This is a formal, deductive approach that stands in contrast to how, for example, [LLM](https://en.wikipedia.org/wiki/Large_language_model)-based systems operate. Instead of relying on "[Chain of Thought](https://en.wikipedia.org/wiki/Prompt_engineering#Chain-of-thought)" (CoT) or other "reasoning" techniques built around probabilistic, autoregressive text generation engines, we work within a rigorous "[Knowledge Representation & Reasoning](https://en.wikipedia.org/wiki/Knowledge_representation_and_reasoning)" (KRR) framework, where strict logical inference guarantees both correctness and completeness in the solution process.

## 3. Coding Style

This code is written in the [literate programming](https://en.wikipedia.org/wiki/Literate_programming) style. The script is designed to be read sequentially from top to bottom as a "**computer science story**," (or lecture?) with thorough documentation explaining both the problem-solving approach and implementation details.

The script is **self-contained** and deliberately avoids external libraries except for SAT solving, making the entire solution process transparent and educational.

NOTE: The literate programming style, with its **linear storytelling approach**, forces at times ackward choices about how you structure and lay out code: A minor sacrifice for a literarily satisfying outcome that elegantly wraps around executable code.

## 4. Code Size

The puzzle solver is contained in [**one single** Python source file](https://github.com/mabene/doty/blob/main/DayOfTheYear.py), which is approximately **one thousand** lines long. Only about **1/4** of the script is actual executable code (**~250** lines). The remaining **3/4** is made of comments and explanations: it's the *story* of how we solve the puzzle in plain English.

The core part of the script, where the problem is encoded into a SAT instance (Sections 5.2 and 5.3, see below), is just **20 lines** of code. The rest is about dealing with the input and specification of the problem, pretty printing the output, bookmarking, statistics, and support functions (see next section).
  
## 5. Code Structure

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

## 6. SAT Encoding & Solving

- **One-hot encoding**: Each variable represents "piece Pk covers cell (i,j)", for k in 1...10, i in 1...8, j in 1...7
- **Constraints**: No overlaps, respect blocked cells, exactly one position per piece, all pieces on the board
- **Optimization**: Tseytin transformation avoids exponential clause explosion
- **Solver**: [CaDiCaL 1.9.5](https://github.com/arminbiere/cadical) (state-of-the-art CDCL SAT solver) wrapped by [pysat 1.8.DEV23](https://pysathq.github.io)

### 7. Advanced Commandline Flags

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

See the [Appendix](./Appendix.md) for detailed component descriptions.

## 8. Solving Performance

The encoding and solving process are fully sequential, so they are executed in a single-process, single-thread mode. On a standard modern (2020-25) laptop machine:

- **Solution finding**: Typically 1-3 seconds
- **Solution enumeration**: Typically 30s to 1 minute; it varies (some dates have thousands of solutions)
- **Formula construction**: Negligible overhead

Timing breakdown is available with the `-v` flag.

## 8. Code Features

- **Modular** board/piece definitions (easily customizable; see next section for an example)
- **Flexible date** input parsing (multiple formats accepted)
- **Solution enumeration** (find all solutions for a given date)
- **ASCII art** visualization of solved puzzles
- **DIMACS** export for SAT instances
- **Detailed timing** statistics
- **Configurable formula** components (for experts)

## 9. Solver Generality

The code **dynamically** extracts all relevant information about the shape, size, content, and dimensions of the board and the polyominoes from the visual representations given in Section 2—specifically, from the variables ``board`` and ``pieces``. It then operates parametrically with respect to all this information.

This means that if you change those "drawings", you can generate and play with and solve any **alternative layout or variant** of the "day of the year" puzzle.

For example, the classical [Golomb](https://en.wikipedia.org/wiki/Solomon_W._Golomb)'s problem about tiling a 6×10 rectangle with all twelve [free pentominoes](https://en.wikipedia.org/wiki/Pentomino) can be solved by our script setting the inputs as follows:

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

**Note**: *A future version of the script may move such input representations to external files for parsing, enabling the solver to handle the full class of tiling problems with polyominoes over rectangular regions with fixed and/or movable holes.*
