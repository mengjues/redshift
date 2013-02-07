#!/usr/bin/env python
#PBS -l walltime=10:00:00,mem=10gb,nodes=1:ppn=6

import os
import sys
import plac
import time
from pathlib import Path


import redshift.parser
import redshift.io_parse

@plac.annotations(
    train_loc=("Training location", "positional"),
    moves_loc=("Training moves location", "positional"),
    solver_alg=("LibLinear solver algorithm (0 for L2, 6 for L1)", "option", "a", int),
    c=("Regularisation penalty", "option", "c", float),
    label_set=("Name of label set to use.", "option", "l", str),
    no_extra_feats=("Remove extra features (never good)", "flag", "x", bool),
    feat_thresh=("Feature pruning threshold", "option", "f", int),
    allow_reattach=("Allow left-clobber", "flag", "r", bool),
    allow_move=("Allow raise/lower", "flag", "m", bool),
)
def main(train_loc, model_loc, moves_loc=None, solver_alg=6, c=1.0,
         no_extra_feats=False, label_set="MALT", feat_thresh=5,
         allow_reattach=False, allow_move=False):
    train_loc = Path(train_loc)
    if allow_reattach:
        grammar_loc = train_loc.parent().join('rgrammar')
    else:
    	grammar_loc = None
    model_loc = Path(model_loc)
    if label_set == 'None':
        label_set = None
    if moves_loc is not None:
        moves_loc = Path(moves_loc)
        if not moves_loc.exists():
            print "Could not find moves; assuming none"
            moves_loc = None
    parser = redshift.parser.Parser(model_loc, clean=True,
                                    solver_type=solver_alg, C=c, add_extra=not no_extra_feats,
                                    label_set=label_set, feat_thresh=feat_thresh,
                                    allow_reattach=allow_reattach, allow_move=allow_move,
                                    grammar_loc=grammar_loc)
    if moves_loc is not None:
        moves = moves_loc.open().read().strip()
    else:
        moves = None
    train = redshift.io_parse.read_conll(train_loc.open().read(), moves=moves)
    parser.train(train)
    print 'Train accuracy:'
    to_parse = redshift.io_parse.read_conll(train_loc.open().read(), moves=moves)
    print parser.add_parses(to_parse, gold=train)
    parser.save()


if __name__ == "__main__":
    plac.call(main)