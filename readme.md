# Chess Engine

This chess engine is developed based on min-max algorithm with alpha-beta pruning as an optimization. 

The model is currently under development and still needs additional optimizations. 

This model is built based on the chess python library which provides a solid foundation of defining the chess game and its essential components.

The current implementation is a game between our model and Stock fish model which is the leading opensource chess engine. 

## Installation
In order to run the model,
1. Install Stockfish https://stockfishchess.org/download/
2. Install python dependencies based on requirements.txt
3. Set environment variable for stockfish path `STOCKFISH_INSTALLATION_PATH`
4. Run the program using command `python game.py`

Current implementation is pointed at min-max alpha beta pruning functions and runs games with incrementing depths of the minmax model.

## Improvements
Currently, a couple of improvements to basic alpha pruning algorithm. 
1. Weighted evaluation function, this weighted evaluation function helps the algorithm to avoid few mistakes like do-undo. This is essentially for the pawn and knight pieces.
2. Parallelization, It takes a lot of time to calculate the score of each and evey move for each and every step. We are using multiprocessing to compute the scores in parallel

