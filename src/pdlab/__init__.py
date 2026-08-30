"""pdlab: a laboratory for the Prisoner's Dilemma."""

from pdlab.game import C, D, Move, PayoffMatrix
from pdlab.match import MatchResult, play_match
from pdlab.strategies import REGISTRY, Strategy
from pdlab.tournament import TournamentResult, round_robin

__all__ = [
    "REGISTRY",
    "C",
    "D",
    "MatchResult",
    "Move",
    "PayoffMatrix",
    "Strategy",
    "TournamentResult",
    "play_match",
    "round_robin",
]
__version__ = "0.1.0"
