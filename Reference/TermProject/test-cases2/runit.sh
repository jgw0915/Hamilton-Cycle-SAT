#!/bin/bash

PATH_TO_SAT_SOLVER=~/.git/dpll/dpll.py

for i in `ls *.cnf`; do
  echo "Solving ${i}"
  ${PATH_TO_SAT_SOLVER} $i
  echo
  echo
done
