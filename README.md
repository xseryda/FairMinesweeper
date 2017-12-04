# FairMinesweeper
PyQT based fair minesweeper

This is an implementation of a Fair minesweeper.

Specification:
Fair minesweeper is the same as a regular minesweeper with 2 additional rules:
  1. If the player cannot be certain about any box being without a mine (e.g. the start of the game), 
  he can click any box and the mine won't be there.
  2. If the player can be certain about a box being without a mine but chooses to uncover 
  a box he cannot be certain being without a mine the box being uncovered is guaranteed to contain a mine, so the player loses.
 
The game might not work 100% well yet.
 
Bugfixing:
If you encounter any bug, please start an issue here on github and upload the file 'debugSavedPosition.FMS' 
immediatelly after discovering the bug. This file is saved automaticaly and will be rewritten if you start another game before 
sending it. This file should be saved next to your *.py files.

Have fun playing.
  
