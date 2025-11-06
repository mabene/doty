import re
import sys
import textwrap
from unittest.mock import patch

import pytest


def canonicalize_time_lines(s: str) -> str:
    """
    If a log line does not start with [TIME], returns it unchanged.
    Otherwise, replaces time durations and percentages respectively with
    DURATION_REMOVED and PERCENT_REMOVED
    """
    if not s.startswith("[TIME]"):
        return s
    duration_removed = re.sub(r"(\d+|\d+\.\d+)(s|ms)", "DURATION_REMOVED", s)
    percent_removed = re.sub(r"(\d+\.\d+)%", "PERCENT_REMOVED", duration_removed)
    return percent_removed


@pytest.mark.parametrize(
    (
        "s",
        "expected",
    ),
    [
        (
            "line unchanged: no [TIME] prefix",
            "line unchanged: no [TIME] prefix",
        ),
        (
            "[TIME] Total CPU time: 2.37s",
            "[TIME] Total CPU time: DURATION_REMOVED",
        ),
        (
            "[TIME] - Preprocessing: 20ms (0.85%)",
            "[TIME] - Preprocessing: DURATION_REMOVED (PERCENT_REMOVED)",
        ),
        (
            "[TIME] - SAT setup: 0.39s (16.39%)",
            "[TIME] - SAT setup: DURATION_REMOVED (PERCENT_REMOVED)",
        ),
    ],
)
def test_canonicalize_time_lines(s: str, expected: str) -> None:
    assert canonicalize_doty_output(s) == expected


def canonicalize_doty_output(stdout: str) -> str:
    # DayOfTheYear prints spurious spaces at the end of the lines. We have to compensate for that.
    trailing_stripped = (line.rstrip() for line in stdout.splitlines())
    return "\n".join([canonicalize_time_lines(line) for line in trailing_stripped])


@pytest.mark.parametrize(
    (
        "cmdline_params",
        "expected_stdout",
    ),
    [
        (
            ["random stuff", "-h"],
            textwrap.dedent("""\
                usage: DayOfTheYear.py [OPTIONS] [DATE]

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

                  -rnd            Randomize solver's search. Each run will likely find a
                                  different solution. Without this flag, the solver always
                                  finds the same solution for a given date (deterministic).

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
                  DayOfTheYear.py
                      Solve for today's date and display the solution

                  DayOfTheYear.py Fri Dec 25
                      Solve for Friday, December 25

                  DayOfTheYear.py -count Mon Jan 1
                      Count all solutions for Monday, January 1

                  DayOfTheYear.py -count -show -v Sat Oct 25
                      Find and display all solutions for Saturday, October 25 with verbose
                      output and timing information

                  DayOfTheYear.py -dump -v
                      Solve for today and export the SAT instance to a DIMACS file
                """),
        ),
        (
            ["Mon Jan 1"],
            textwrap.dedent("""\
                Target date: MON JAN 1
                ┏━━━┳━━━━━━━━━━━━━━━┳━━━┓
                ┃JAN┃               ┃   ┃
                ┣━━━┻━━━━━━━┳━━━━━━━┫   ┃
                ┃           ┃       ┃   ┃
                ┣━━━┓       ┣━━━┓   ┃   ┗━━━┓
                ┃  1┃       ┃   ┃   ┃       ┃
                ┣━━━╋━━━━━━━┛   ┃   ┗━━━┳━━━┫
                ┃   ┃           ┃       ┃   ┃
                ┃   ┗━━━┳━━━┓   ┣━━━┳━━━┛   ┃
                ┃       ┃   ┃   ┃   ┃       ┃
                ┣━━━┓   ┃   ┗━━━┛   ┃   ┏━━━┫
                ┃   ┃   ┃           ┃   ┃   ┃
                ┃   ┗━━━┻━━━━━━━┳━━━┫   ┃   ┃
                ┃               ┃MON┃   ┃   ┃
                ┗━━━━━━━━━━━━━━━╋━━━┻━━━┛   ┃
                                ┃           ┃
                                ┗━━━━━━━━━━━┛"""),
        ),
        (
            [" Mon ", " Jan ", " 01 ", "-v"],
            textwrap.dedent("""\
                Target date: MON JAN 1
                [THEORY] Formula components:
                [THEORY] - Included: E.1.1 E.2.1 T.1 T.2 T.3.1 T.3.2 I.1 I.2
                [THEORY] - Excluded: E.1.2 E.2.2 T.4
                [CNF] Formula size:
                [CNF] - variables: 2303
                [CNF] - clauses:   102795
                [CNF] - literals:  207599
                ┏━━━┳━━━━━━━━━━━━━━━┳━━━┓
                ┃JAN┃               ┃   ┃
                ┣━━━┻━━━━━━━┳━━━━━━━┫   ┃
                ┃           ┃       ┃   ┃
                ┣━━━┓       ┣━━━┓   ┃   ┗━━━┓
                ┃  1┃       ┃   ┃   ┃       ┃
                ┣━━━╋━━━━━━━┛   ┃   ┗━━━┳━━━┫
                ┃   ┃           ┃       ┃   ┃
                ┃   ┗━━━┳━━━┓   ┣━━━┳━━━┛   ┃
                ┃       ┃   ┃   ┃   ┃       ┃
                ┣━━━┓   ┃   ┗━━━┛   ┃   ┏━━━┫
                ┃   ┃   ┃           ┃   ┃   ┃
                ┃   ┗━━━┻━━━━━━━┳━━━┫   ┃   ┃
                ┃               ┃MON┃   ┃   ┃
                ┗━━━━━━━━━━━━━━━╋━━━┻━━━┛   ┃
                                ┃           ┃
                                ┗━━━━━━━━━━━┛
                [SAT] Solver stats:
                [SAT] - restarts: 1584
                [SAT] - conflicts: 62863
                [SAT] - decisions: 136198
                [SAT] - propagations: 13381810
                [TIME] Total CPU time: DURATION_REMOVED
                [TIME] - Preprocessing: DURATION_REMOVED (PERCENT_REMOVED)
                [TIME] - Encoding: DURATION_REMOVED (PERCENT_REMOVED)
                [TIME] - SAT setup: DURATION_REMOVED (PERCENT_REMOVED)
                [TIME] - SAT solving: DURATION_REMOVED (PERCENT_REMOVED)
                [TIME] - Printing: DURATION_REMOVED (PERCENT_REMOVED)
                [TIME] - Other: DURATION_REMOVED (PERCENT_REMOVED)"""),
        ),
    ],
)
def test_doty(cmdline_params: list[str], expected_stdout: str, capfd) -> None:
    # capfd captures stdout and stderr of the script, https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html
    with patch.object(sys, "argv", ["argv0"] + cmdline_params):
        with pytest.raises(SystemExit) as wrapped_exit:
            import DayOfTheYear
        assert wrapped_exit.type is SystemExit
        assert wrapped_exit.value.code == 0
        stdout, stderr = capfd.readouterr()
        assert stderr == ""
        assert expected_stdout == canonicalize_doty_output(stdout)
