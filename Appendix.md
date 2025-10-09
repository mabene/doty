# DOTY Appendix

This section contains supplementary material which the reader can safely skip if interested in how to solve the puzzle only. These notes deal with non-obvious choices that went into building the project, and reflect on alternative modeling/solving choices that could have been made at several junctures.

---
## Section 2 of the code
### About the (subtle) assumptions and modeling choices we made
---

The puzzle/board/pieces representations presented in Section 2 seems fairly general, reasonable, and assumption-free. 
In fact, a few assumptions we DID make, deliberate if subtle.
Let us explicitate and contemplate them for a second (key concepts in uppercase letters):

- [**a1**] We modeled the board as an ABSTRACT, FULL GRID of 8 columns and 7 rows, hence 56 CELLS...
- [**a2**]. of which 6, ALTOUGH REPRESENTED, must stay UNUSED...
- [**a3**]. while the other 50 cells sport their own STRING-represented, puzzle-specific CONTENT;
- [**a4**]. We captured the shapes of the pieces in terms of which CONTIGUOUS CELLS they occupy on the board, CELL-ALIGNED...
- [**a5**]. exhibiting the pieces in only ONE specific but totally ARBITRARY LAYOUT...
- [**a6**]. assuming the rest (their ROTATIONS, FLIPS, and exact POSITIONING) will be taken care of "automatically" ELSEWHERE.

We could have represented our knowledge of the problem in very different ways. E.g., we could have specifyed the pieces in terms of their geometric perimeter in some 2D space coordinates (or 3D, if we wanted the representation to be closed w.r.t. flips); the same is true of the board layout; we could have put the board in a file as a jpeg image to load and process; we could have separated the board layout and shape from its content; we could have represented the board not as a complete grid with certain unused cell but as an asymetric object with a peculiar shape.

*Bottom line*: The act of modeling a problem is always packed with sometimes subtle but quite consequential choices!

---
## Section 4 of the code
### About some alternatives choices we could have made
---

 We chose the simplest logic framework that can reasonably capture and solve our puzzle: propositional logic. In short, we turn all the rules governing the puzzle - and those determining what a solution is - into a big propositional formula, whose "model(s)" or "satisfying assignment(s)" is/are solution(s) to our puzzle. Then, we enlist an external, state-of-the-art SAT solver to find all such model(s).

 Yet, even once have decided to "**speak propositionally**" to the AI, several degrees of freedom still exist for the "knowledge engineer". In particular, the "propositional landscape" is as follows:

1. there are several ways in which we could have represented the problem space as a set of propositions (i.e., a set of symbols whose interpretation can only be "True" or "False"). We chose to work with a one-hot encoding, a set of 7x8x10 = 560 propositions representing the fact that "piece Pk covers cell (i,j)", for k in 1...10, i in 1...8, j in 1...7. We could have chosen to allocate just 4 propositions/bits to each cell, whose truth values encode the state of affairs for a cell as a binary index encoding:
    - FFFF➜no piece covers this cell
    - FFFT➜piece #1 covers this cell
    - FFTF➜piece #2 covers this cell
    - ... 
    - TFTF➜piece #10 covers this cell
    - the remaining combinations - TFTT and TT\*\* - would stay unused

    It would have been impossible to express overlappings, so certain constraints would have come for free here; there would be only 7x8x4=224 propositions total; other parts of the theory would become much less "natively clausal" though;

2.  there are several slightly different propositional frameworks in terms of, e.g., which kind of formulas and connectives are part of the core semantics of the language; 

3. we've to decide whether or not we want to directly produce some standard aka "normal" form for the target formula, typically a CNF (Conjunctive Normal Form), which is the input most SAT solvers expect; or, we are ok with formulas having an arbitrary syntax, which will then be either translated into CNF automatically or handed over to one of the (fewer) solvers that understands generic non-clausal syntactic structures, e.g., as an AIGER input; 

4. we could have used solvers that also known about - and have optimized reasoning/propagation strategies for - non-standard connectives, such as the "at most" or "xor" (those would come handy in our formalization), or we stand by the default "and", "or", "not".

---
## Section 5 of the code
### On the role of required VS optional theory components (core VS derived  knowledge)
---

We've seen that the puzzle theory is made of several "components", some of which are labeled as optional, all of which can be enabled/disabled at commandline. Why is it so?


Let's briefly comment on the required components first:

- [**T.1**] is there to avoid covering the same cell with multiple pieces, a circumstance that with certain alternative encodings may be simply impossible to specify/emerge; think, e.g., of encoding, with a few bits per cell, the index of the piece at each cell: The constraint [T.1] would be unnecessary, but then other incricacies would arise...

- [**T.2**] is a plain "local" constraint, that rules out certain configurations/assignments. These constraints would exist, in one form or another, in any conceivable encodings and even in different logic/constraint formalisms.

- [**T.3.1**] is the hearth of our encoding (and the largest one in size): For each one of the 10 pieces, we are specifying all the positions where, disregarding the other pieces, it can conceivably be positioned in the board - possibly rotated and/or flipped over, i.e., remapped from one free polyomino to all its fixed variants - and we're asserting that one of these positions/layouts have to be chosen. Of course, we're not telling which one to chose, because that is THE task the external solver is engaged to work on.

This is all we need! All the valid ways to place all pieces on the board to cover all but three cells emerge from the interplay among the previous 3 theory components, applied to our finite board of known dimension and to our 10 pieces.

**Note**: *[T.3.1] alone would be insufficient to characterize the puzzle rules, because it allows to place the same piece on the board (a) twice or more, and (b) in possibly self-overlapping configurations; the no-overlap condition emerges because the solver has to comply with [T.1]; the no-piece-reuse restriction surfaces for a more subtle reason: There is no [T.2]-compliant way to complete this specific board if you replace any piece with a copy of another piece. So, in non-overlapping configurations, all the pieces will have to be used.*

Once we have our **core theory** (T.1 + T.2 + T.3.1), it is sufficient to add the "core instance encoding" (I.1) to obtain a complete SAT instance whose models decode to all and only the valid solutions for the target puzzle.

So why don't we just keep the theory **short and essential**, by getting rid of additional/optional components? 

First, let's observe that such optional components "make no damage"; they express obvious (to us, "domain experts"), true, easy, implied, "derived" properties any solution to any puzzle would have to exhibit anyway. It is all obvious stuff from a human point of view. In particular:

- [**T.3.2**]: We know we'll be having only one copy of each piece in each solution; wherever the piece is going to be put, no other copy of that piece will be present elsewhere on the board (see discussion at [T.3.1]).

- [**T.4**]:   We know we'll be having one copy of each piece in each solution, so all the pieces will have to be used anyway.

- [**I.2**]: We know the set of all pieces, once coherently interlocked, will cover 47 of the 50 available cells (all but the 3 target/solution/date ones); so we know that, safe those 3 cells, there will be a piece everywhere; so we don't need to assert that the current piece is nowhere else.

- [**E.1.2**]: The [E.1.1] ("at least one") constraint is consistent with the placement of several copies of the same piece; but we know no solution exists that, e.g., reuses one piece and sets aside another one; so the "exactly one" version that emerges when [E.1.2] is added to the mix is something every solution will abide by anyway.

- [**E.2.2**]: This is a more subtle one; having only half the Tseytin transformation in place is something you can do when models where (a) the subformula represented by the auxiliary variable (1 full placement/configuration of 1 piece in our context) is True but (b) the auxiliary variable itself is False, are either non-existent or acceptable. We are in the former case: No model has more than 1 positioning conjunct true for the same piece.

Back to the question: Should we be injecting these optional components into the formula we hand over to the solver? All of them? Some of them? Why?

It turns out this is an **unclear trade-off**, a matter of KRR engineering and optimisation:

- These additional constraints are not free to handle: They add one hundred thousand clauses and more! And even more propagation and learning, after that. So they may **slow down** the solver.

- dually, having extra if redundant clauses/constraints may help the solver to work faster; their presence may help the reasoner to **prune the search space** (by, e.g., foretelling conflicts) and work/infer faster, more than their handling slows things down.

Empirically, it turns out that adding **some but not all** of the extra theory components helps the solver more than it hurts. The speed-up is substantial: **2** orders of magnitude. We selected the "fastest theory composition" as our default, trying all combinations first. Of course, this is entirely accidental and depends on the solver implementation, data structures, reasoning/search algorithms, etc.

Are we working too hard here, shouldering responsibilities that should be passed over to the external solver? Are we betraying the minimalistic declarative approach we were after? Yes! And No:

- [**Yes**]: The solver would be able (in principle) to infer/derive/learn on its own all the clauses in all the optional constraints, starting from the clauses present in the core/minimal 3-component puzzle theory (in practice, it will derive only those necessary to find/count models). After all, the optional constraints are made of entailed clauses by their nature; they can be derived by any complete proof system; in the case of a SAT solver such as ours, they (or, some of them) will appear as learned clauses or as unit-derived clauses or by other in/pre-processing tool. It may just take a lot of time to (re)discover the obvious...
     
- [**No**]: The key, complex part of the puzzle, its combinatorial core, is handed to the solver, unaltered, across the conceptual instance_declaration > instance_solution interface. Indeed, all the optional constraints are generated in low-polynomial space & time (linear or quadratic). Our reduction is still polynomial! (the only way we would have entered non-polynomial territory in producing the propositional problem theory+instance would have been to use a direct CNF-ization of the disjunctions of conjunctions in Section 4.3, employing no auxiliary variables). But the real work of interlocking all pieces around our 3 target cells, finding a solution in a space of tens of millions of combinations, is still shouldered by the external solver. 

Overall, it costs very little to us to foreworn the machine of all the above implied constraints whereas that's gold for the solver, provided we do not overwhelm it with information, as confirmed by the much longer running time it incurs if we abstain from adding *any* extra material at all. 

Given how difficult it is for us to solve any specific puzzle, either by hand, one by one, or by writing a dedicated puzzle-specific code... handing some implied knowledge over to our companion SAT reasoner looks like a **win-win cooperation**.

 ---
## Section 6 of the code
### About some alternatives choices we could have made
---

 (5) there are several state-of-the-art SAT solvers available and several ways to interact with them, from dumping to file
 a DIMACS representation of the CNF and launching the solver externally on it, to using the APIs of solvers who expose one,
 to import a (Python) framework that wraps solvers and does the plumbing for us.

 Our choices are as follows: We use the excellent "pysat" framework to wrap and call the external solver and retrieve 
 solution(s) from it; we ask pysat to use the "cadical" solver in particular, because it proved the most effective on our puzzle instances.
 "pysat" has several advanced features, such as: auto-CNF-ization procedures; solvers that support extended non-clausal 
 formats and non-standard connectives; Python-native objects to construct propositional formulas as first-class Python 
 expressions rather than as content of generic Python data structures; and more. We use NONE of these advanced features, 
 i.e., we do a minimal use of pysat: We build ourself a plain CNF as a list (conjunction) of lists (clauses) of integers 
 (literals), hand it to pysat (1 line of pysat code) which in turn hands it to the solver (1 line of pysat code), and 
 then asks the solver to find model(s) for it (1 line of pysat code).
 So, just 3 lines of code to engage the external solver: All our attention can be focused on representing the puzzle.


