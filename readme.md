# Snake Game Reinforcement Learning Model
from https://www.youtube.com/watch?v=L8ypSXwyBds
run agent.py to start training
### TODO:
* ~~Lower epsilon value when loading file (maybe check len of done?)~~
* Be able to detect own body so it doesn't box itself
* ~~findout <br> Fatal Python error: PyEval_RestoreThread: the function must be called with the GIL held, but the GIL is released (the current Python thread state is NULL)~~ <br> <b>cause because of moving plotter window when trying to plot</b>
* ~~plotter is adding 1 every game cycle~~ <b>(now always start at 0)</b>
* detect collision from bigger area (3x3)
* THE SNAKE IS GETTING WORSE