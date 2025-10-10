#!/usr/bin/python3

########################################################################################################################
# Content: Day-of-the-Year (DOTY) puzzle solver, version 0.2                                                           #
# Author: Marco Benedetti (https://www.linkedin.com/in/marco-benedetti-art)                                            #
#                                                                                                                      #
# Note 1: No AI assistant has been used to produce this script; every line of code and every comment is human-written. #
# Note 2: This script is best viewed with syntax highlight on, and a monospaced (fixed-width) font (e.g., Menlo).      #
########################################################################################################################

'''
Copyright: (c) 2025 - Marco Benedetti

Permission to use, copy, modify, and/or distribute this software for non-commercial academic purposes, with or without 
modification, is hereby granted, provided that the following conditions are met:

1.  **Attribution:** All copies of this software and derivative works must include the above copyright notice, this list
	of conditions, and the following disclaimer.
2.  **Non-Commercial Use:** This software may not be used for any commercial purpose.
3.  **No Warranty:** This software is provided "as is," without warranty of any kind, express or implied, including but 
	not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. 
	In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether 
	in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use 
	or other dealings in the software.
'''

########################################################################################################################
# 1. Introduction                                                                                                      #
########################################################################################################################

'''
This script solves the so-called "Day-of-the-Year (DOTY)" board puzzle (cfr. Section 2), using AI tools produced by the
"automated reasoning" (AR) research community. In particular: SAT solvers (https://en.wikipedia.org/wiki/SAT_solver).

This code is also an exercise in "literate programming" (https://en.wikipedia.org/wiki/Literate_programming), so it 
reads as a short, hopefully gripping "computer science story", meant to be read sequentially from top to bottom.

Code is introduced as the story unfolds, and it is thoroughly documented: It follows the flow of thought used to think
about and solve the problem - rather than the idiosyncrasies of any specific programming language or logic/constraint
framework. It should be comprehensible, at least in broad strokes, to novice programmers and non-programmers alike.

The rest of this script is organized as follows:

- Section 2.  introduces the puzzle and its goal, and defines the board and the pieces used to play it.

- Section 3.  turns the human-oriented puzzle representations from Section 2 into code-friendly data structures, for
              further processing; the first of which is to generate all possible placements of all pieces, by flipping
              and/or rotating and/or translating them, in the assumption our solution method won't handle this natively.

- Section 4.  introduces the formal framework we use to encode and solve the problem: propositional logic. All the
              necessary propositional variables required to represent configurations of pieces are defined, together 
              with auxiliary functions that build the core propositional (sub)formulas we'll need in Section 5. We also
              show how to compactly write certain formulas that may become intractably large if not handled with care.
               
- Section 5.  recasts any puzzle instance into the problem of proving the satisfiability of a specific propositional
              formula (aka SAT problem). To this end: a "Puzzle Theory" is defined (= all the rules governing and
              defining the puzzle are expressed as propositional formulas); required vs. optional components of such
              theory are discussed; the encoding of one specific instance (one date/day of the calendar) is produced.

- Section 6.  solves the puzzle instance from Section 5 using an external SAT solver, bridged via the Python framework
              "pysat"; puzzle solution(s) is (are) then reconstructed from the model(s) of such (satisfiable) formula. 

- Section 7.  pretty-prints to screen/terminal/file/stdout the solved board(s) constructed in Section 6.

- Section 8.  concludes by optionally printing stats, dumping formulas, showing the help page; returns an exit value.

'''

# NOTE: If the user requests the help page by specifying the "-h" commandline switch, then no solution is looked for and
#       we are in "help" mode, which means the execution resumes from Section 8.4, where such help page is printed.
from sys import argv as flags
help = "-h" in flags
if help:
  flags = ["-h"]

########################################################################################################################
# 1.1. Timing the execution of the script                                                                              #
########################################################################################################################

# Before starting with any puzzle-related activity, let us set up a minimal benchmarking system, so we will be able to
# understand where time is spent by the code, doing what. The framework and data structures used to this end are:
import time
t0 = {} # A dictionary that maps an activity name/label to its starting time
elapsed = {} # A dictionary that maps an activity name/label to its duration

# Any section of interest will be enclosed into a start_timer("SECTION_LABEL") / stop_timer("SECTION_LABEL") pair;
# calls to these functions can be nested; the time we are measuring is the CPU time, not the wallclock time.
def start_timer(label):
	t0[label] = time.process_time()
def stop_timer(label):
	now = time.process_time()
	elapsed[label] = (elapsed[label] if label in elapsed else 0.0) + (now - t0[label])
	t0[label] = now
	return elapsed[label]

# And when we need to print some elapsed time, we'll use this rounding/time-unit-adjusting function:
def format_time(time):
	return str(round(time,2))+"s" if time>=0.1 else str(int(round(time*1000,0)))+"ms"

# So let's start with the outermost timing:
start_timer("Total")


########################################################################################################################
# 2. The puzzle: board and pieces                                                                                      #
########################################################################################################################

# The board of our puzzle is as follows:

board = '''
┏━━━┳━━━┳━━━┳━━━┳━━━┳━━━┳━━━┓
┃JAN┃FEB┃MAR┃APR┃MAY┃JUN┃ ╳ ┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃JUL┃AUG┃SEP┃OCT┃NOV┃DEC┃ ╳ ┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃  1┃  2┃  3┃  4┃  5┃  6┃  7┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃  8┃  9┃ 10┃ 11┃ 12┃ 13┃ 14┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃ 15┃ 16┃ 17┃ 18┃ 19┃ 20┃ 21┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃ 22┃ 23┃ 24┃ 25┃ 26┃ 27┃ 28┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃ 29┃ 30┃ 31┃SUN┃MON┃TUE┃WED┃
┣━━━╋━━━╋━━━╋━━━╋━━━╋━━━╋━━━┫
┃ ╳ ┃ ╳ ┃ ╳ ┃ ╳ ┃THU┃FRI┃SAT┃
┗━━━┻━━━┻━━━┻━━━┻━━━┻━━━┻━━━┛
'''

# There are 8 rows and 7 columns overall; the cells marked by "╳" are not available to play with, so we have 7x8-6 = 50
# cells remaining. These cells contain the list of the names of the 12 months of the year, followed by the (up to) 31
# numbers representing the day of the month, followed by the names of the (7) days of the week: 12+31+7 = 50.

# Then we have 10 pieces, or "free polyominoes" (https://en.wikipedia.org/wiki/Polyomino), with the following shapes:

pieces = '''
   L      T      Z      R    J    P    C       r    g   i
🟦⬜️⬜️ 🟦🟦🟦 🟦🟦⬜️ 🟦🟦 🟦⬜️ 🟦🟦 🟦🟦   🟦🟦 🟦⬜️ 🟦
🟦⬜️⬜️ ⬜️🟦⬜️ ⬜️🟦⬜️ 🟦⬜️ 🟦🟦 🟦🟦 🟦⬜️   🟦⬜️ 🟦🟦 🟦
🟦🟦🟦 ⬜️🟦⬜️ ⬜️🟦🟦 🟦⬜️ ⬜️🟦 🟦⬜️ 🟦🟦   🟦⬜️ ⬜️🟦 🟦
⬜️⬜️⬜️ ⬜️⬜️⬜️ ⬜️⬜️⬜️ 🟦⬜️ ⬜️🟦 ⬜️⬜️ ⬜️⬜️   ⬜️⬜️ ⬜️⬜️ 🟦
'''

# We have assigned some reasonably mnemonic name to each piece (header row), in case we need to name them succinctly.
# In particular, we have 7 pentominoes (left, uppercase names) and 3 tetrominoes (right, lowercase names).

# These 10 pieces - flipped on the back and/or rotated by multiples of 90° - are placed somewhere on the board.
# The cumulated surface of all these pieces is 47 cells; so if you manage to put them all on the board (with no overlap 
# between pieces and all pieces positioned within the bounds of the board), then exactly 3 free board cells remain.

# The goal of the puzzle is indeed to place all 10 pieces on the board, with no overlap, in such a way as to cover it 
# entirely (apart from the ╳ cells), leaving 3 cells visible, representing the current (or any given) day of the year.

# For example, if the target day is "Saturday, October 25", we want the 3 cells "SAT", "OCT", "25" to remain visible.
# One possible solution will then be:

__sample_solution_for_Saturday_October_25 = """
┏━━━━━━━┳━━━━━━━┳━━━┳━━━┓       
┃       ┃       ┃   ┃   ┃    
┃       ┃   ┏━━━┫   ┃   ┃       
┃       ┃   ┃OCT┃   ┃   ┃    
┃   ┏━━━┛   ┣━━━┫   ┃   ┗━━━┓   
┃   ┃       ┃   ┃   ┃       ┃
┣━━━┻━━━┳━━━┛   ┃   ┣━━━━━━━┫   
┃       ┃       ┃   ┃       ┃
┃   ┏━━━┫   ┏━━━┻━━━┻━━━┓   ┃   
┃   ┃   ┃   ┃           ┃   ┃
┃   ┃   ┃   ┣━━━┓   ┏━━━┛   ┃   
┃   ┃   ┃   ┃ 25┃   ┃       ┃
┃   ┃   ┗━━━┻━━━┫   ┣━━━━━━━┫   
┃   ┃           ┃   ┃       ┃
┗━━━┻━━━━━━━━━━━╋━━━┛   ┏━━━┫   
                ┃       ┃SAT┃
                ┗━━━━━━━┻━━━┛ 
"""

# So, the puzzle can be alternatively described as a special case of the problem of tiling a rectangular (7x8) region
# with some (6) fixed and some (3) variable holes, given the 7 pentominoes and the 3 tetrominoes in the picture above.

# NICE TO KNOW: The code that follows extracts dynamically from the above visual representations (in particular, from 
# the variables "board" and "pieces" - cfr. Section 3) all the relevant information about the shape, size, content, and 
# dimension of the board and of the pieces/polyominoes. This means that if you change the above "drawings", you can
# generate and play with and solve any alternative layout or variant of the original puzzle!!


########################################################################################################################
# 3. Turning the visual representations from Section 2 into software-friendly data structures, for further processing  #
########################################################################################################################

'''
In Section 2 we made it all very visual and human-friendly. We didn't constrain ourselves at all about:
(a) how the puzzle will be represented, internally to this script, in terms of data structures & co;
(b) how the puzzle will be solved - whether by this script directly or by handing it off to some external tool.

Now it's time to lay out our ideas about how to represent and solve the puzzle. First, some "preprocessing" steps:

- In Section 3.1 we turn the "ASCII image" of the board ("board" variable) into a Python matrix.
- In Section 3.2 we decide which data structure to use internally to handle the shape of the pieces given in "pieces".
- In Section 3.3 we do something more substantial: We posit that the representation language and/or the solution 
  algorithm we will be using to solve the puzzle are not expressive enough to natively capture the fact that pieces
  can be flipped/rotated/translated before use, so we manage all these transformations "manually", here.
'''

# Let's start.
start_timer("Preprocessing")

########################################################################################################################
# 3.1. Data structures (+ helper functions) for the internal representation of the board and its content/features      #
########################################################################################################################

# We turn the string representation of the board into a handy bidimensional array of string elements, where cells[i][j]
# contains the text in the cell at row i (starting from 0) and column j (again: 0-indexed, as they say)
cells = [[txt.strip() \
	for txt in row.split("┃")[1:-1]] \
	for row in filter(lambda x: "━" not in x, 
		board.splitlines())] \
		[1:] # The first line in "board" is empty, not of interest here

# As a result, these are the dimensions of the board (W for width - number of columns, H for height - number of rows)
H = len(cells)
W = len(cells[0]) # We assume a non-jagged (rectangular) array here

# Several times we will need to check whether a given pair of indices, whether expressed separately or as a tuple,
# lies within or outside the limits of the board; so we define a few handy functions here.
def out_of_bounds(i,j):
	return i<0 or j<0 or i>=H or j>=W
def out_of_board(cell):
	(i,j) = cell
	return out_of_bounds(i,j)
def any_cell_is_out_of_board(cells):
	return any([out_of_board(cell) for cell in cells])

# Now, the following list of <text_in_cell,position_of_cell> pairs from the board:
cell_txt_coordinates_couples = [(cells[i][j],(i,j)) for i in range(H) for j in range(W)]
# ... is useful to:

# A. Detect and record all the (coordinates of the) tabu cells (marked with an "╳"), where pieces cannot be placed;
tabu_cell_coordinates = [(i,j) for (txt,(i,j)) in cell_txt_coordinates_couples if txt=='╳']
def is_tabu_cell(cell):
	return cell in tabu_cell_coordinates

# B. Build a dictionary for inverse searches: We map a given text to the position of the cell containing that text.
cell_txt_to_cell_coordinate = dict(filter(lambda x: x[0]!='╳',cell_txt_coordinates_couples))

# Let's now move on to extracting and representing the pieces.

########################################################################################################################
# 3.2. Data structures for the internal representation of the pieces                                                   #
########################################################################################################################

# We get the nicknames for the pieces first, and represent them as a simple array of names:
piece_names = pieces.splitlines()[1].split()

# We then turn the "visual" representation of the pieces from Section 2 into a handy bidimensional array of 1s and 0s.
# In particular, we substitute 1s & 0s for 🟦s & ⬜️s, as these unicode characters look nice, but are not well behaved
# script-wise, as they yield >1 elements in iterations. Then we split and transpose the matrixes of piece components:
pieces = pieces.replace('🟦',"1").replace('⬜️',"0")       # Substitute
pieces = [row.split() for row in pieces.splitlines()][2:] # Split
pieces = list(zip(*pieces))                               # Transpose

# Then, the representation of pieces is a list (one element per piece) of lists (the coordinates of that piece's 🟦s):
pieces = [[(i,j) for i in range(len(piece)) for j in range(len(piece[i])) if piece[i][j]=='1'] for piece in pieces]

# So now we have, e.g., that piece_names[1] is "T" and pieces[1] is [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)].

########################################################################################################################
# 3.3. Computing all possible placements of all pieces, obtained by flipping and/or rotating and/or translating them   #
########################################################################################################################

# By their nature, the 10 pieces of the puzzle are so called *free* polyominoes; this means that, before being used, 
# they can be FLIPPED on the back (i.e., rotated by 180° around any axis on the board plane) and/or ROTATED on the board 
# plane, by multiples of 90°. Once a specific flip/rotation state is decided, the result is called a "fixed polyomino".

# The question is: Which part of the solution process is in charge of "fixing free polyominoes", in all possible ways?

# We posit that the representation language and/or the solution algorithm we will be using to solve the puzzle will not
# be expressive enough, or not willing to, or just not in charge of managing natively all the rotations and flips of the
# pieces on the board. So, we compute all of them ourself, explicitly, here: The rest of this script will deal with
# several "fixed polyominoes", in lieu of the 10 free polyominoes originally defined.

# Let's first deal with the fact that pieces can be FLIPPED on the back:
'''
	 Z         Z'
 🟦🟦⬜️   🟦⬜️⬜️ 
 ⬜️🟦⬜️ ➤ 🟦🟦🟦 
 ⬜️🟦🟦   ⬜️⬜️🟦 
'''

# We represent these mirrored (aka "one-sided") versions by introducing the B-side of each piece as a new virtual piece,
# or "doppleganger". We (arbitrarily) flip around the diagonal by swapping Xs for Ys:
dopplegangers = [[(y,x) for (x,y) in indexes] for indexes in pieces]

# The original pieces are coupled with their dopplegangers for subsequent processing.
pieces_and_dopplegangers = list(zip(pieces,dopplegangers))

# Now we move to consider the possible ROTATIONS of each one-sided piece. Starting with the base/nominal position of one
# piece, we define a function that computes all its 4 rotated variants (rotated by multiples of 90°).
from operator import itemgetter
def all_rotated_variants(idxs):
	# The offset is adjusted after the rotation around (0,0) so as to keep the piece layout in non-negative coordinates.
	def offset_adj(idxs):
		min_xy = [(min(list(map(itemgetter(0), r))), min(list(map(itemgetter(1), r)))) for r in idxs]
		return [[(-min_x+x, -min_y+y) for (x,y) in indexes] for ((min_x,min_y),indexes) in zip(min_xy,idxs)]
	return offset_adj([[(x*cos - y*sin, y*cos + x*sin) for (x,y) in idxs] for (cos,sin) in [(1,0),(0,1),(-1,0),(0,-1)]])

# All fixed rotated variants of all pieces and their dopplegangers are computed, for subsequent processing.
fixed_variants_of_pieces = [all_rotated_variants(piece) + all_rotated_variants(doppleganger) \
																for (piece,doppleganger) in pieces_and_dopplegangers]

# Now that we have dealt with flips and rotations, let us observe that one free polyomino corresponds to at most 8 fixed
# polyominoes (which are also called "its images under the symmetries of the dihedral group D4"). However, those images
# are not necessarily distinct: The more symmetry a free polyomino has, the fewer distinct fixed counterparts it has.

# A puzzle piece that is invariant under some or all symmetries of D4 may correspond to only 4 or 2 fixed polyominoes.
# In particular, some of our pieces are not "chiral", i.e., they have an axis of symmetry (on their own plane), so their 
# dopplegangers are superimposable (via roto-translations) on their mirror images, i.e., are 2D-congruent to their back.
# See, e.g., pieces L and T. Similarly, certain pieces match themselves if rotated twice by 90° (e.g., I).

# So far, we have left all this potential redundancy unchecked because detecting flip- or rotation-invariance with the 
# current data representation is harder than it needs to be. And so we have generated 10x4x2 = 80 fixed pieces.
# But now we can detect and filter out repeated fixed images, thus eliminating redundant dopplegangers and all.
def deduplicated(fixed_variants_idxs):
    return [list(t) for t in set(tuple(sorted(fixed_variant_idxs)) for fixed_variant_idxs in fixed_variants_idxs)]
fixed_variants_of_pieces = [deduplicated(fixed_variants) for fixed_variants in fixed_variants_of_pieces]

# It turn out that in the standard 10-piece set, we move from 80 potential fixed pieces to just 54 distinct ones, with
# contributions by the original pieces as follows: 4(L) + 4(T) + 4(Z) + 8(R) + 8(J) + 8(P) + 4(C) + 8(r) + 4(g) + 2(i).

# Now, let's deal with TRANSLATIONS of pieces, again assuming our target framework won't handle translations natively.
def translate(idxs,di,dj):
	return [(i+di,j+dj) for (i,j) in idxs]

# We basically position each piece (and all its distinct rotated/flipped variants) not only at the "origin" of the board
# but at any horizontal/vertical location where it fits without overshooting the board (independently of the others).
# We call each final version of each piece, after one flip/rotation/translation is applied, a "layout" of that piece.
layouts_of_pieces = \
	[[translate(fixed_variant,di,dj) for di in range(H) for dj in range(W) for fixed_variant in fixed_variants \
		if not any_cell_is_out_of_board(translate(fixed_variant,di,dj)) \
	 ] for fixed_variants in fixed_variants_of_pieces]

# Notice that as we "unfold", "position", "unroll", "exercise" the pieces virtually, so to say, across the entire board,
# via flips/rotations/translations, we perform only a polynomial number of steps in the size of the board and in the 
# number/size of the pieces. So this is a "tractable exercise": The combinatorial core of the puzzle still lays ahead.

# We're done with the preprocessing phase:
stop_timer("Preprocessing")

# Let's move to encoding the problem as a logic statement.


########################################################################################################################
# 4. Propositional logic and SAT solving as a declarative framework wherein to tackle the puzzle                       #
########################################################################################################################

'''
We pick the simplest logic framework that can reasonably capture and solve our puzzle: propositional logic.
See https://en.wikipedia.org/wiki/Propositional_logic for details.

In short, we will turn all the rules governing the puzzle - and those determining what a solution is - into a big 
propositional formula (https://en.wikipedia.org/wiki/Propositional_formula), whose "satisfying assignment(s)" or 
"model(s)" represent(s)/encode(s) solution(s) to our puzzle instance.

Then, we enlist an external, state-of-the-art SAT solver to find all such model(s) - cfr. Section 6.

The actual translation or "encoding" of the problem into a propositional framework will be done in Section 5.
Here we lay the foundations for that to be possible, and choose how exactly to "speak propositionally" to the AI, given
the degrees of freedom that still exist, even once we settle on a "propositional setting".

Among the other things, we resolve to produce not a general propositional formula, but directly one in CNF (Conjunctive
Normal Form), see https://en.wikipedia.org/wiki/Conjunctive_normal_form. The reasons for encoding our problem in CNF are
that (1) most of the puzzle encoding is naturally described as a CNF anyway; (2) most SAT solvers take (only) a CNF as
input; (3) building the CNF directly gives us more control on how it is generated/optimised.
'''

########################################################################################################################
# 4.1. Boolean/propositional variables meant to capture any board configuration (including illegal/impossible ones)    #
########################################################################################################################

# We use a one-hot encoding (https://en.wikipedia.org/wiki/One-hot) to represent pieces on the board, whereby one single
# proposition (aka propositional variable aka bit) represents the presence (if True) or absence (if False) of a specific
# piece on top of a specific cell. In particular, the variable returned by VAR_FOR_PIECE_AT(piece_idx, i, j) is True iff
# piece number #piece_idx covers the cell (i,j) in the board. This representation is quite verbose; and, it allows for
# multiple pieces on the same cell (piece overlaps), a situation that is not valid for our puzzle and will need to be
# ruled out explicitly (see component [T.1] in Section 5.2); still, it gives very good results, experimentally.
def VAR_FOR_PIECE_AT(piece_idx, i, j):
	return 1 + (i*W + j) + (piece_idx*W*H)	

# So the total number of "core" variables/propositions/bits we need to represent a full board/piece configuration for
# the original puzzle (excluding auxiliary variables, see Section 4.3) is equal to... 
CORE_VAR_COUNT = VAR_FOR_PIECE_AT(len(pieces)-1,H-1,W-1) # (7x8)*10 = 560

# Some auxiliary variables will also be generated to keep the theory compact (see Section 4.3); there is only one 
# clause-construction primitive that requires the generation of auxiliary variables (see Section 5.2, component [T.3]).
# It will call this function 1803 times overall (once for each distinct position/orientation/flip of every piece), so
# the total number of variables in any variant of the SAT instances we'll produce is going to be 560+1803 = 2303.
AUX_VAR_IDX = CORE_VAR_COUNT + 1
def NEW_AUX_VAR():
	global AUX_VAR_IDX
	aux = AUX_VAR_IDX
	AUX_VAR_IDX += 1
	return aux

########################################################################################################################
# 4.2. Primitives for building clausal-form constraints                                                                #
########################################################################################################################

# The "at least one of these n propositions is true" concept is rendered very easily in CNF, because that's just what 
# a "clause" means: One of its literals must be true (L1∨L2∨……∨Ln) and this is a constraint we add, or conjunct, to all 
# the rest. The encoding of the concept is a list/CNF (to be appended to the current CNF) containing a single 
# list/clause of the set of literals at least one of which must be true:
def AT_LEAST_ONE(lit_idxs):
	return [lit_idxs]

# The "at most one of these propositions is true" concept is less easily rendered; this is not a standard propositional
# operator; some solvers have an extra/specialized "propagator" for it, but we stick to the vanilla syntax. Whereby it
# takes a quadratic number of binary clauses to capture the semantics. It is a matter of saying that whenever one of the 
# literals is true, all the other ones are false: ∀i≠j.(Li→¬Lj), i.e., ∀i≠j.(¬Li∨¬Lj); that's nx(n-1) binary clauses:
def AT_MOST_ONE(lit_idxs):
	return [[-if_true,-then_false] for if_true in lit_idxs for then_false in [x for x in lit_idxs if x != if_true]]

# Some nice compositional reuse of the two concepts we've just defined:
def EXACTLY_ONE(lit_idxs):
	return  AT_LEAST_ONE(lit_idxs) + AT_MOST_ONE(lit_idxs)

# A concept dual to "AT_LEAST_ONE", which can be rendered via n "unit" clauses, where the literals are negated:
def NONE_OF(lit_idxs):
	return [[-lit] for lit in lit_idxs]

########################################################################################################################
# 4.3. Tractable CNF-ization of disjunctive portions of the puzzle theory                                              #
########################################################################################################################

# The following function gets as input a formula in DNF (Disjunctive Normal Form), i.e., a disjunction of conjunctions
# of literals, e.g., (a∧b) ∨ (d∧¬e) ∨ (¬f∧¬g∧h), and it returns an equivalent (almost... see next) formula in CNF, i.e.,
# a conjunction of disjunctions of literals; in our example, that would be:
# (a∨d∨¬f)∧(a∨d∨¬g)∧(a∨d∨h)∧(a∨¬e∨¬f)∧(a∨¬e∨¬g)∧(a∨¬e∨h)∧(b∨d∨¬f)∧(b∨d∨¬g)∧(b∨d∨h)∧(b∨¬e∨¬f)∧(b∨¬e∨¬g)∧(b∨¬e∨h)
#
# The input DNF expresses the fact that at least one of the conjuncts has to be true; the output CNF expresses the same
# concept as a list of clauses, which turns out to be a much more verbose affair. In general, turning a DNF into an
# equivalent CNF without introducing auxiliary variables (see next) may incur an exponential blowup.
#
# So we use a special case of the Tseytin transformation here (https://en.wikipedia.org/wiki/Tseytin_transformation), by
# (a) introducing 1 auxiliary variable for each conjunct; (b) generating clauses that bind the truth values of such aux
# variables to those of the conjuncts; (c) expressing the "at least one" constraints on the auxiliary variables.
# In so doing, the generation of the CNF stays polynomial in space and time; but, extra variables are introduced.
#
# In our case, this function will be called (from within Section 5.2, component [T.3]) several times (once for each 
# piece of the puzzle), each time with 4...100 conjuncts of >50 literals each (these numbers are proportional to the
# board size). The direct CNF construction obtained by distributing connectors might thus have >50^100 clauses!
# Given that each conjunct represents one positioning of one piece on the board, the use of the Tseytin transformation
# here means that the non-polynomial combinatorial core of the puzzle is dealt with not in the formulation (i.e., in the
# board propositional theory) but in the constraint satisfaction procedure at the heart of the SAT solver.
#
# Both the input DNF and the output CNF are represented as a list of lists of (possibly negative) integers.
def AT_LEAST_ONE_CONJUNCT(DNF):
	# A fresh batch of auxiliary variables we use to denote each conjunct in the input DNF
	auxs = [NEW_AUX_VAR() for _ in range(len(DNF))]
	
	# [E.1] The Tseytin version of the concept "at least one conjunct must be true" (or, optionally, exactly one):
	cnf  = C("E.1.1", AT_LEAST_ONE(auxs)) 
	cnf += C("E.1.2", AT_MOST_ONE(auxs)) # adding this turns the "at least one" constraint into "exactly one" [OPTIONAL]

	# [E.2] The Tseytin way of binding the auxiliary variables' truth value to the conjuncts they stand for:
	# [E.2.1] aux -> disjunct literal, for each literal of a given conjunct
	cnf += C("E.2.1", [[-aux,lit] for (conjunct,aux) in zip(DNF,auxs) for lit in conjunct])
	# [E.2.2] aux <- negated disjunct literals, for each conjunct [OPTIONAL in most encodings, including ours]
	cnf += C("E.2.2", [[aux] + [-lit for lit in conjunct] for (conjunct,aux) in zip(DNF,auxs)])

	return cnf
			

########################################################################################################################
# 5. Encoding the puzzle functioning + a specific puzzle instance into a propositional formula in CNF                  #
########################################################################################################################

'''
Now that we have a set of propositional variables (and their associated semantics) to talk about the position of pieces
on the board (Section 4.1) and the means to write in clausal form all the necessary constraints (Sections 4.2 and 4.3),
let's construct a set of clauses that captures the rules of our puzzle, and what solutions look like.

In particular, we first build a "puzzle theory" here (Section 5.2), i.e., a set of logical statements (list of clauses)
whose models are all and only the legal configurations of all the pieces placed somewhere on the board (independently of
any specific instance we may want to solve). Then we define, again in logical terms, what an "instance" of the problem
is (Section 5.3). Finally, we conjoin the puzzle theory with the instance of interest (e.g., today's date), so that the 
resulting formula's models are all and only the puzzle solutions for that instance (day).

Note that there are multiple ways to write the puzzle theory and the instance, with optional components that can be used
or omitted. This is dealt with in Section 5.1.
'''

# Let's go with the encoding process:
start_timer("Encoding")

########################################################################################################################
# 5.1. Dealing with mandatory/optional portions of the clausal constraints that end up in our formula                  #
########################################################################################################################

# The set of clauses we will accumulate into our final CNF is made of several components, clearly marked in the code:
# - In Section 5.2, the puzzle theory is generated. It is made of 4 components, called: [T.1], [T.2], [T.3], [T.4],
#   where component [T.3] has 2 sub-components: [T.3.1] and [T.3.2];
# - In Section 4.3, the 2 components of each Tseytin encoding used within [T.3], i.e., [E.1] and [E.2], are
#   generated via the code in Section 4.3; both have 2 subcomponents: [E.1.1], [E.1.2] and [E.2.1], [E.2.2];
# - In Section 5.3, the puzzle instance specification is generated; it has 2 components: [I.1] and [I.2].

# We'll see later (Section 5.2 and 5.3) what these individual components mean and represent exactly; now, we need to 
# deal with the fact that some of these components of the overall specification are required for the soundness of our 
# approach and must be present: They constitute a "core/minimal" puzzle theory. Others are optional, redundant:

#           REQUIRED                OPTIONAL
# Theory:   [T.1], [T.2], [T.3.1]   [T.3.2], [T.4]
# Instance: [I.1]                   [I.2]
# Encoding: [E.1.1], [E.2.1]        [E.1.2], [E.2.2]

# By default, the components listed in "default_cfg_OK" will be generated, the ones in "default_cfg_KO" will be skipped:
default_cfg_OK = [ "E.1.1", "E.2.1", "T.1", "T.2", "T.3.1", "T.3.2", "I.1", "I.2" ]
default_cfg_KO = [ "E.1.2", "E.2.2", "T.4" ]

# From the commandline, it is possible to alter such default configuration, by either removing an optional component
# (e.g., "-I.2") or adding an optional component which is not in the default configuration (e.g., "+T.4"); you can also
# remove *REQUIRED* components, but at that point you are no longer solving the original puzzle, but something else.
# For example, by removing the instance specification ("-I.1 -I.2") you are asking for any board with all the pieces
# positioned inside, independently of any date, i.e., independently of which 3 cells are left visible.
config = [X for X in default_cfg_OK if "-"+X not in flags] + [X for X in default_cfg_KO if "+"+X in flags]

# The following auxiliary function will wrap any line of code that produces clauses (see Sections 4.3, 5.2, 5.3), so to
# filter away those belonging to deactivated theory components. "C" is a mnemonic for "Component" or "Constraint".
# At the calling site, invoking this function will declare the theory component as the first argument, thus explicitly
# and visibly associating clauses with the component they belong to.
def C(label,clauses):
	return clauses if label in config else []

# In verbose mode, we tell the user which components have been generated, and which have not.
if "-v" in flags:
	print(f"[THEORY] Formula components:")
	print(f"[THEORY] - Included: {' '.join(config)}")
	print(f"[THEORY] - Excluded: {' '.join([c for c in default_cfg_KO+default_cfg_OK if c not in config])}")

########################################################################################################################
# 5.2. Clausal-form constraints any solution to any instance of the puzzle must comply with, aka, the "puzzle theory"  #
########################################################################################################################

# Into the following "puzzle_theory" list, sets of clauses that define specific aspects/rules/constraints of the game
# will accumulate. At the end, it will contain a formula in CNF that defines our entire puzzle theory.
puzzle_theory = []

# [T.1] Geometric constraints: No overlap among pieces (i.e., no board cell may be covered by more than one piece)
[puzzle_theory.extend( \
	C("T.1",AT_MOST_ONE([VAR_FOR_PIECE_AT(piece_idx,i,j) for piece_idx in range(len(pieces))])) ) \
		for i in range(H) for j in range(W)]

# [T.2] Board shape constraints: No piece on the tabu cells of the board (those marked with ╳)
[puzzle_theory.extend(
	C("T.2",NONE_OF([VAR_FOR_PIECE_AT(piece_idx,i,j) for piece_idx in range(len(pieces))]))) \
		 for (i,j) in tabu_cell_coordinates]

# [T.3] Piece positioning constraints: Given all the valid ways each piece can be positioned on the board (irrespective
# of the others, see Section 3.3) we declare that one such valid position is part of any solution, for every piece:
[puzzle_theory.extend([] if piece_idx<0 else
	AT_LEAST_ONE_CONJUNCT( [\
		# [T.3.1] The following portion of the conjunct specifies explicitly all cells where a piece is
		C("T.3.1",[VAR_FOR_PIECE_AT(piece_idx,i,j) for (i,j) in layout_of_piece]) + \

		# [T.3.2] The following portion of the conjunct specifies explicitly all cells where a piece is not [OPTIONAL]
		C("T.3.2",[-VAR_FOR_PIECE_AT(piece_idx,i,j) for i in range(H) for j in range(W) if (i,j) not in layout_of_piece])
	for layout_of_piece in layouts_of_piece] ) \
) for piece_idx, layouts_of_piece in enumerate(layouts_of_pieces)]

# [T.4] Completion constraints: In any solved puzzle, all pieces must find their location on the board [OPTIONAL]
[puzzle_theory.extend( \
	C("T.4",AT_LEAST_ONE([VAR_FOR_PIECE_AT(piece_idx,i,j) for i in range(H) for j in range(W)])) ) \
		for piece_idx in range(len(pieces))]

# Now, we have characterized how to place all pieces in all possible sound and mutually consistent board positions; what
# is missing is... to specify what exact day/instance we want to target...

########################################################################################################################
# 5.3. Specifying which instance of the problem (i.e., which date/day of the calendar) we want to solve for            #
########################################################################################################################

# By default, the script will solve the puzzle for today's date; so we import the date object, from which we extract the 
# three relevant elements of the current date, and then cast them to the (uppercase, shortened) board format we need.
from datetime import date
today_date_elements = [date_elem.upper()[:3] for date_elem in date.today().strftime('%a %B %-d').split()]

# However, it is possible to provide the script with a custom date as a commandline argument, so let's parse it.
# We want to parse the arguments in a very permissive and forgiving way, so that you can use any format you want,
# like "Mon, Jan 1" or "Monday, January 1" or "MON JAN 01" or other variations, with or without quotes, commas, etc., 
# written everywhere on the commandline, before or after other flags, etc. We do this in 2 steps:
import re
# 1. We split the commandline arguments at any space, comma, semicolon, ignoring and removing quotes and leading zeroes
args = [a.lstrip('0') for a in re.split(r'[;,\s]+', " ".join(flags[1:]))]
# 2. We map the "normalized" version from step (1) into the upper case 3-letter or numeric format used in the board, and
#    we check if/which of the resulting strings appear in our puzzle board:
custom_date_elements = [e for e in [date_elem.upper()[:3] for date_elem in args] if e in cell_txt_to_cell_coordinate]

# If there is a fully specified day provided as input argument, we'll use that; otherwise, we default to today:
date_elements = custom_date_elements if len(custom_date_elements)==3 else today_date_elements
target_cells = [cell_txt_to_cell_coordinate[e] for e in date_elements]

# Now that the target date is known, let us make it clear to the user what solution we're looking for:
if not help:
  print("Target date: " + " ".join(date_elements))

# [I.1] Finally, we construct an "instance" of the problem, i.e., a set of clauses that assert we want to place...
puzzle_instance = C("I.1",NONE_OF([VAR_FOR_PIECE_AT(piece_idx,i,j) # none of... \
					for piece_idx in range(len(pieces))            # the pieces in... \
					for (i,j) in target_cells]))                   # cells that represent the target date.

# Such constraint has a different meaning but a syntactic structure identical to the ╳s' encodings from [T.2]. I.e., 
# there are cells we do not want to overlap with our pieces. In Section 5.2's case it's because they are not part of the
# board to begin with. Here, it's because we want to leave specific labels visible in order to... solve the puzzle!!

# [I.2] Let's also specify the dual instance constraint: that any cell that is not part of the target date (and is not
# a "tabu" cell) will end up with at least one piece covering it. [OPTIONAL]
[puzzle_instance.extend(C("I.2",AT_LEAST_ONE([VAR_FOR_PIECE_AT(piece_idx,i,j) for piece_idx in range(len(pieces))]))) \
		for i in range(H) for j in range(W) if (i,j) not in (tabu_cell_coordinates + target_cells)]

########################################################################################################################
# 5.4. Printing the size of the propositional encoding we've built                                                     #
########################################################################################################################

# In case the user wants to know, this is how big the propositional formula we constructed turned out to be.
if "-v" in flags:
	print(f"[CNF] Formula size:")
	print(f"[CNF] - variables: {AUX_VAR_IDX-1}")
	print(f"[CNF] - clauses:   {len(puzzle_theory + puzzle_instance)}")
	print(f"[CNF] - literals:  {sum([len(clause) for clause in puzzle_theory + puzzle_instance])}")

# The encoding process is completed.
stop_timer("Encoding")


########################################################################################################################
# 6. Solving the puzzle                                                                                                #
########################################################################################################################

'''
Here we are, ready to solve the SAT encoding of our puzzle.

We use the excellent "pysat" framework (https://pysathq.github.io) to wrap and call the external solver and retrieve 
solution(s) from it. In particular, we ask "pysat" to use the "CaDiCaL" solver (https://github.com/arminbiere/cadical), 
because it proves the most effective on our puzzle instances.

NOTE. "pysat" has several advanced features, such as: auto-CNF-ization procedures; solvers that support extended
      non-clausal formats and non-standard connectives; Python-native objects to construct propositional formulas as
      first-class Python expressions rather than as content of generic Python data structures; and more.
      We use NONE of these advanced features, i.e., we do a minimal use of pysat: We've built ourselves a plain CNF as a
      list (conjunction) of lists (clauses) of integers (literals); we hand it to pysat (1 line of pysat code) which in
      turn hands it to the solver (1 line of pysat code), and then asks the solver to find model(s) for it (1 line of
      pysat code). So, just 3 lines of code to engage the external reasoner!
'''

# Let's start by checking what the instructions actually are. We may be either requested to just find one solution (and 
# show it), or to enumerate all solutions to the current puzzle (plus, optionally, showing them all).
enumerate_solutions = "-count" in flags
show_solution = "-show" in flags or not "-count" in flags

########################################################################################################################
# 6.1. An encoding/reduction of the combinatorial core of the problem is handed over to the (external) SAT solver      #
########################################################################################################################

# Let's go:
start_timer("SAT setup")

# The CNF object from the "pysat" package has a constructor that takes as input a formula in CNF, given as a list 
# (conjunction) of lists (disjunctions) of literals, which is exactly what we have built in Section 5.
from pysat.formula import CNF
cnf = CNF(from_clauses = puzzle_theory + puzzle_instance) if not help else None

# This is the solver we are going to use, to which our puzzle theory + instance are given as an input problem.
from pysat.solvers import Solver             
solver = Solver(name = "cadical195", bootstrap_with=cnf) if not help else None

# An interesting detail: The SAT solver will have to make many non-deterministic choices during its search, such as:
# "Should I assign this variable or that one next? Should I set it to True or False first?". If these choices are made
# randomly, the solver's results will differ each time it runs; for example, it could find a different puzzle solution
# on every launch. Depending on your needs, this could be a bug or a feature. To allow both behaviors, the solver uses
# a deterministic pseudo-random generator for its decisions. This generator produces the same (apparently random)
# sequence of choices if started from the same initial "random seed"; each different seed yields a different sequence.
# Therefore, if the "-rnd" flag is given on the command line, we pass the solver a new (pseudo) random seed each time,
# so it will likely generate a different solution for the same puzzle on each run. Otherwise, if "-rnd" is not present,
# we set the seed to a fixed value of zero, making the solver reproducibly find the same solution for any given input.
import random; solver.configure({"seed":random.randint(0, int(2e9)) if "-rnd" in flags else 0, "phase": 0 if "-rnd" in flags else 1})
stop_timer("SAT setup")

# There are often several (even thousands) of models for each formula (problem instance), so we instrument the code to
# enumerate all such models (if asked to find just one single solution, we'll exit the loop after the first iteration).
n_models = 0
models = []

start_timer("SAT solving")
# The execution of the following pysat's enumerator triggers the actual SAT solving process:
for model in solver.enum_models() if not help else []: 
	stop_timer("SAT solving")

	# We count and optionally store all models the SAT solver finds.
	n_models += 1
	if "-dump" in flags:
		models.append(model[:CORE_VAR_COUNT]) # Auxiliary variables deterministically follow the core ones by construction
	
	if enumerate_solutions:
		if show_solution:
			if n_models>1:
				# The special sequence "\33[N]A" goes up N lines in the output and is meant to overwrite in place the
				# previous solution with the next one, in case we are "enumerating & showing" all solutions:
				print(f"\33[{H*2+3}A")
			print(f"Solution #{n_models}:")
		else:
			# This is to print a live update on the number of models/solutions found, as the search goes on; the special
			# sequence "\r\33[K" moves back to the beginning of the current line in the output, so we overwrite it:
			print(f"\r\33[K|solutions| ≥ {n_models}", end="", flush = True)

########################################################################################################################
# 6.2. Reconstructing a puzzle solution from a model of the formula                                                    #
##6#####################################################################################################################

# Now, observe that most of the rest of this script is at level of indentation 1, and not zero, meaning that - as per
# the Python syntactic rules - we are in the scope of the "for" loop above, the one that is enumerating all models. 
# So from now on, we have a fully specified satisfying assignment to the variables in the formula, which we call "model"
# by slightly abusing the term; such model is stored in the "model" variable, and is represented as a list of (possibly 
# negative) integers in 1...CORE_VAR_COUNT; a positive/negative value means the variable is assigned True/False, resp.

# We have to move back from this assignment to the original problem space by "decoding"/interpreting the model. 

	# Auxiliary function first. For each single cell, we check what is there in the current solution:
	def WHATS_AT_CELL(i, j):
		# Either the cell coordinates are out of bounds, so there is nothing there
		if out_of_bounds(i,j):
			return None
		# Or, one of the pieces (the piece number piece_idx) covers that cell
		for piece_idx in range(len(pieces)):
			if VAR_FOR_PIECE_AT(piece_idx,i,j) in model: 
				return piece_idx
		# Or, no piece covers the cell, so the content of the original board cell is visible through the hole:
		return cells[i][j]

	# Overall, our solution is represented as a matrix (list of lists) of values, having the same dimensions as the
	# original board; the value at position (i,j) is either an integer (the ordinal number of the piece covering that 
	# cell, if any); or a string: the corresponding text value from the original board, if not hidden by any piece.
	solution = [[WHATS_AT_CELL(i, j) for j in range(W)] for i in range(H)]
	
	# From now on, having decoded our "model" into a "solution", the code will refer to the "solution" variable only.


########################################################################################################################
# 7. (Pretty) printing the solution                                                                                    #
########################################################################################################################

	# It's time to print the solution for the user to admire! :) But let us first check if we are indeed required to
	# print the solution; in case we are not, we go on with possibly counting how many solutions do exist.
	if not show_solution:
		continue

########################################################################################################################
# 7.1. Auxiliary text & chrome generation functions                                                                    #
########################################################################################################################

	# Before writing the actual code meant to draw the solution (Section 7.2), we define 4 support functions that help
	# us keep the main printing code compact and legible.

	# 1. A small auxiliary function, extracting which piece (idx) is present at a given board position; there is...
	def IDX_OF_PIECE_AT_CELL(i, j):
		# ...no piece outside the board, and no piece where the solution matrix contains strings instead of integers
		# Otherwise, the piece index is the integer value at solution[i][j]
		return None if out_of_bounds(i,j) or not isinstance(solution[i][j],int) else solution[i][j]

	# 2. An aux function that returns True iff the two cells given as input are covered by the same piece in "solution"
	def same_piece_at_cells(cell1,cell2):
		(i1,j1) = cell1
		(i2,j2) = cell2
		idx1 = IDX_OF_PIECE_AT_CELL(i1, j1)
		idx2 = IDX_OF_PIECE_AT_CELL(i2, j2)
		# First, the easy check: If both cells are indeed covered by some piece, and that's the same piece, then fine!
		same_piece = (idx1 is not None and idx2 is not None and idx1==idx2)
		# But, we have to deal with several special/corner cases, where one or both cells are either tabu cells
		# or lie outside the board, or are covered by no piece at all (the 3 cells left visible in each solution).
		# What does it mean to be "covered by the same piece" in these cases? We define that it means to belong to a
		# virtual piece that surrounds the board and absorbs the tabu cells; couples of cells belong to this piece iff
		# they are both outside the board, or they are both tabu cells, or one is a tabu cell and one is out of board.
		same_virtual_piece = \
			any([P1(cell1) and P2(cell2) for P1 in [out_of_board, is_tabu_cell] for P2 in [out_of_board, is_tabu_cell]])
		return same_piece or same_virtual_piece
		
	# 3. What to print inside cell (i,j) when dumping a solution? In most cases, we print nothing, just white spaces
	# inside the cell; if print_piece_name is set to True (just for debug reasons; it defaults to False), we print the
	# name of the piece covering cell (i,j) instead. If no piece is covering the cell and it is an internal board cell,
	# we print the text present in the original board at position (i,j), i.e., the solution date components.
	def text_at_cell(i,j):
		print_piece_name = False
		idx = IDX_OF_PIECE_AT_CELL(i, j)
		return (cells[i][j].rjust(3)         if idx is None        else \
				" " + piece_names[idx] + " " if print_piece_name     else \
				"   ")                       if cells[i][j] != "╳" else "   "
	
	# 4. When we are drawing the crossing at (i,j) we are surrounded by the 4 cells topLeft@(i-1,j-1), topRight@(i-1,j), 
	# botRight@(i,j), botLeft@(i,j-1): What symbol to print? There are 2^4=16 possibilities, depending on which ones of 
	# the 4 adjacent cell couples <topLeft,topRight>, <topRight,botRight>, <botRight,botLeft>, and <botLeft,topLeft>
	# belong to the same piece (if any). The two extreme cases: If all four cells surrounding the crossing belong to 
	# the same piece, we print "nothing", i.e., a space " ". If they belong to 4 different pieces, then the symbol "╋"
	# is selected to neatly separate the four areas; in all the other situations, the proper symbol is as follows:
	def connector_at_crossing(i,j):
		char_idx = sum([2**idx * (1 if same_piece_at_cells(cell1,cell2) else 0) for idx, (cell1,cell2) in enumerate(
		[((i  ,j-1),(i-1,j-1)), # <botLeft ,topLeft>  FTFTFTFTFTFTFTFT # from
		 ((i  ,j  ),(i  ,j-1)), # <botRight,botLeft>  FFTTFFTTFFTTFFTT # four
		 ((i-1,j  ),(i  ,j  )), # <topRight,botRight> FFFFTTTTFFFFTTTT # couples of
		 ((i-1,j-1),(i-1,j  ))] # <topLeft ,topRight> FFFFFFFFTTTTTTTT # adjacent cells we obtain...
		)])                     #                      16 combinations
		return                                       "╋┣┻┗┫┃┛╹┳┏━╺┓╻╸ "[char_idx] # Alternative: "╬╠╩╚╣║╝ ╦╔═ ╗ ╸ "    
		
########################################################################################################################
# 7.2. Drawing the solution as standard text, but still in a visually pleasant way using ASCII-art tricks              #
########################################################################################################################

	# We are ready to print the solution; it is just a matter of printing a full rectangular grid, as big as our 
	# original board in terms of number of rows and columns. But, we will be using special characters along the "chrome" 
	# of the table, i.e., along the lines that separate column from column and row from row, and at each intersection
	# between horizontal and vertical lines.
	# By picking special characters properly here, depending on how pieces are positioned in "solution", the result will
	# be an ASCII-art rendering of the board, depicting all pieces properly interlocked around the solution.

	start_timer("Printing")
	import itertools
	# We iterate by row first; for each row, we consider first the "chrome" (border) of the row and then its content
	for i, _i in itertools.product(range(H+1), ["H_chrome","content"]):
		# The same thing we do - inside each row - for columns and their chrome
		for j, _j in itertools.product(range(W+1), ["V_chrome","content"]):
			# Then we:
			print({
				# Print (or skip via whitespaces) the vertical/horizontal border left/right or above/below each cell.
				# Notice that here and in the rest of the printing, given the aspect ratio of typical monospaced fonts,
				# we use 3 horizontal characters (3 spaces: "   " or 3 dashes: "━━━") for each vertical one (i.e., one
				# space " " or one pipe "┃") to keep the board/grid approximately square:
				("content" ,"V_chrome") : "┃"   if not same_piece_at_cells((i,j-1),(i,j)) else " "   if i<H or j<W else "",
				("H_chrome","content" ) : "━━━" if not same_piece_at_cells((i-1,j),(i,j)) else "   " if i<H or j<W else "",
				# Print the proper connector symbol at each crossing between a vertical and a horizontal grid line
				("H_chrome","V_chrome") : connector_at_crossing(i,j),
				# Print the content of the cells, which is usually nothing, except for the 3 solution cells
				("content" ,"content" ) : "" if i>=H or j>=W else text_at_cell(i,j)
			}[(_i,_j)], end='')        
		print("", end="\n" if i<H else "")
	print("")
	stop_timer("Printing")
	

########################################################################################################################
# 8. Conclusion                                                                                                        #
########################################################################################################################

	# We have found and printed one solution to our puzzle! We may be asked to provide further solutions to the same 
	# puzzle (there are surprisingly many, for each day); in this case we keep looping (see the "for" statement from 
	# Section 6.1), in a process called "model enumeration". Otherwise, we break out of the cycle and conclude.
	if not enumerate_solutions:
		break
	else:
		start_timer("SAT solving")

########################################################################################################################
# 8.1 Optionally printing info & stats about the solution process and its outcome                                      #
########################################################################################################################

# In case we were enumerating models, and we're done, we print the total number of models found:
if enumerate_solutions:
	print(f"\r\33[K|solutions| = {n_models}")
elif n_models == 0 and not help:
	print("No solution found")

# The user may want to dig deeper in what the solver did, so let's print some stats (only if we are in verbose mode):
if "-v" in flags:	
	print("[SAT] Solver stats:")
	print("\n".join([f"[SAT] - {key}: {value}" for key, value in solver.accum_stats().items()]))	

########################################################################################################################
# 8.2 Optionally dumping to file the SAT instance(s) we've been dealing with                                           #
########################################################################################################################

# In case the "-dump" flag is present, we dump to file a DIMACS representation of the SAT instance(s) we've solved.
if "-dump" in flags:
	start_timer("DIMACS dumping")
	if "-v" in flags:
		print("[DIMACS] Dumping instance(s):")

	# First, let's choose a nice name for such instance(s), one that is (a) clear and readable and (b) is such that a
	# lexicographic sorting produces the same order as the underlying temporal ordering of the dates involved.
	# This may come quite handy if several instances are placed in the same directory.
	
	# We start by extracting the (shortened) names for months and week days from the puzzle table
	month_names = cells[0][:6] + cells[1][:6]
	day_names   = cells[6][3:] + cells[7][4:]
	# Using these lists, the name of the month is turned into its ordinal position in [1...12]
	date_elems = [1+month_names.index(X) if X in month_names else X for X in date_elements]
	
	# The three date elements are not sorted, because on the command line, for maximum flexibility, we allowed them to be
	# specified in any order, and the rest of the script didn't require any specific sorting either. Now we need one.
	# So we sort the date components as follows: month number first, then day number, then name of the week day. 
	# The year is assumed to be the current year, and is positioned first.
	sorted_elems = [str(X).zfill(2) for X in sorted(date_elems, key=lambda e: (not isinstance(e, int), e in day_names))]
	prefix = date.today().strftime('%Y') + "_" + "_".join(sorted_elems)
	# The prefix of the file name that comes out of the above manipulations is like this: "2025_04_06_Sunday"
	
	# Short aux function to print the filenames of the instances about to be dumped, if required (with "-v")
	def _print(txt):
		if "-dump" in flags and "-v" in flags:
			print(f"[DIMACS] - '{txt}'")
		return txt
	
	# The instance we have solved is almost always satisfiable (there are a few exceptions)
	cnf.to_file(_print(prefix + "_" + ("UNSAT.cnf" if (n_models==0) else "SAT_multiModel.cnf")))
	# If we have been enumerating all models, there are a couple of interesting extra instances we may want to dump:
	if n_models>0 and enumerate_solutions:
		# (a) One where all models but one are ruled out by adding clauses that block their acceptability.
		#     By construction, this is a satisfiable instance with just one model:
		[cnf.append([-l for l in model]) for model in models[:-1]]		
		cnf.to_file(_print(prefix + "_" + "SAT_singleModel.cnf"))
		# (b) One where also the last remaining model has been ruled out.
		#     By construction, this is an unsatisfiable instance, whose unsatisfiability proves we listed all models.
		cnf.append([-l for l in models[-1]])
		cnf.to_file(_print(prefix + "_" + "UNSAT.cnf"))
	stop_timer("DIMACS dumping")

########################################################################################################################
# 8.3 Optionally printing some stats about how (CPU) time was spent in solving the puzzle                              #
########################################################################################################################

# Now that the computation is done we can check the overall CPU time it has taken.
total = stop_timer("Total")
del elapsed["Total"]
# All the computations not explicitly part of some benchmarked portions of code end up into the "Other" category.
elapsed["Other"] = total - sum([elapsed[label] for label in elapsed])

# If the user wants to know the timing details, e.g., which percentage of the overall running time was spent in
# generating VS solving the instance, we let him/her know.
if "-v" in flags:	
	print(f"[TIME] Total CPU time: {format_time(total)}")
	[print(f"[TIME] - {label}: {format_time(time)} ({round(100.0*time/total,2)}%)") for label, time in elapsed.items()]

########################################################################################################################
# 8.4. Optionally printing the help page and describing the script commandline options                                 #
########################################################################################################################

# In the course of the past 8 sections of code, we've crafted a flexible script for the solution of the DotY puzzle, 
# which accepts a lot of basic and advanced commandline options and flags, in addition to the target date.
# Let's recap for the user the syntax and functioning of the script, and of all its commandline options.
if help:
  print('''\
usage: Year2025.py [OPTIONS] [DATE]

Day-of-the-Year (DotY) puzzle solver.

Solves the DotY board puzzle for a given date by finding valid placements of
10 pieces that leave only the target date visible (month, day number, and
weekday). By default, if DATE is omitted, solves for today's date.

DATE:
  Specify a target date in flexible format. All three components (month, day
  number, weekday) must be provided. Date components can appear in any order
  and with varying formats. Examples:
    Mon Jan 1
    "Monday, January 1"
    MON JAN 01
    1 Jan Monday

OPTIONS:
  -h              Show this help message and exit

  -count          Enumerate all solutions for the target date. Displays the
                  total count when done. Without -show, only prints a running
                  count; with -show, displays each solution in sequence

  -show           Display puzzle solution(s) as ASCII art. Enabled by default
                  unless -count is used alone.

  -v              Verbose mode. Prints additional information including:
                  - Formula components (enabled/disabled)
                  - Formula statistics (variables, clauses, literals)
                  - SAT solver statistics
                  - Timing breakdown by phase

  -dump           Export SAT instance(s) to DIMACS CNF file(s). Files are
                  named by date (YYYY_MM_DD_WEEKDAY) with suffixes:
                  - SAT_multiModel.cnf: original satisfiable instance
                  - SAT_singleModel.cnf: instance with all but one solution
                    blocked (only with -count)
                  - UNSAT.cnf: instance with all solutions blocked, proving
                    completeness of enumeration (only with -count)

ADVANCED OPTIONS:
  Control which constraints are included in the SAT encoding.
  Default configuration solves the standard puzzle efficiently.

  -COMPONENT      Remove a component from the formula
  +COMPONENT      Add a component to the formula

  Available components (see the code for details):
  		REQUIRED: T.1, T.2, T.3.1, I.1, E.1.1, E.2.1
  		OPTIONAL (ON by default): T.3.2, I.2
			OPTIONAL (OFF by default): T.4, E.1.2, E.2.2

  Examples:
    -T.3.2              Remove optional "non-piece" constraints
    +T.4                Add board completion constraint
    -I.1 -I.2           Find any valid piece configuration (no date target)

EXIT STATUS:
  0   Solution found
  1   No solution found (does not occur for valid dates)

EXAMPLES:
  Year2025.py
      Solve for today's date and display the solution

  Year2025.py Fri Dec 25
      Solve for Friday, December 25

  Year2025.py -count Mon Jan 1
      Count all solutions for Monday, January 1

  Year2025.py -count -show -v Sat Oct 25
      Find and display all solutions for Saturday, October 25 with verbose
      output and timing information

  Year2025.py -dump -v
      Solve for today and export the SAT instance to a DIMACS file
  ''')
  
########################################################################################################################
# 8.5 Exiting                                                                                                          #
########################################################################################################################
	
# Finally, the exit/return value of the whole script. It would be a nice touch to return the number of models/solutions
# we found; unfortunately, such number may be in the thousands, whereas the exit code in most Unix environments
# is an 8 bit integer. So we adopt the standard Unix convention for return/exit values of scripts/functions: 0 means 
# "success" and values >=1 imply an "error" condition. Here, 1 means we did not find any solution (a thing that may only 
# happen in corner cases where we ask a puzzle solution which is not a valid date, or when we mess up with the puzzle
# theory), whereas a return value of 0 corresponds to the expected situation where we solved the puzzle successfully.
exit(0 if help or n_models>0 else 1)