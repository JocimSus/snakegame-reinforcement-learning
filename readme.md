# Snake Game Reinforcement Learning Model
from https://www.youtube.com/watch?v=L8ypSXwyBds
run agent.py to start training
### TODO:
* ~~Lower epsilon value when loading file (maybe check len of done?)~~
* Be able to detect own body so it doesn't box itself
* findout <br>
Fatal Python error: PyEval_RestoreThread: the function must be called with the GIL held, but the GIL is released (the current Python thread state is NULL)
Python runtime state: initialized
Current thread 0x00003598 (most recent call first):
  File "c:\Users\User\Desktop\Code\snakegame-reinforcement-learning\game.py", line 155 in play_step
  File "c:\Users\User\Desktop\Code\snakegame-reinforcement-learning\agent.py", line 115 in train
  File "c:\Users\User\Desktop\Code\snakegame-reinforcement-learning\agent.py", line 144 in \<module>
<br> 
cause because of moving plotter window when trying to plot
* plotter is adding 1 every game cycle
* detect collision from bigger area (3x3)