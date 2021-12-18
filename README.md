# Game of Life
John Conway's Game of Life (python tkinter)

"keyboard" is needed: https://github.com/boppreh/keyboard
```
pip install keyboard
```

![image](https://github.com/HansenH/Game-of-Life/blob/main/Screenshot.png)  

## Instruction
press space to start / pause

press 'r' when paused to randomly initialize the cells

press 'c' when paused to clear the table

click cells when paused to switch their living states

Global constants in gameoflife.py are configurable including:  
- TABLE_COLS = 40
- TABLE_ROWS = 40
- TIME_INTERVAL = 0.2
- NO_BORDER = True        # whether table edges are linked
- WINDOW_WIDTH = 600      # UI window width
- WINDOW_HEIGHT = 600     # UI window height
- GRID_THICK = 2
- GRID_COLOR = '#BBBBBB'
- TABLE_COLOR = '#666666'
- LIFE_COLOR = '#00FF00'
- RANDOM_INIT_PROB = 0.25 # probability of life for randomly initialzing cells
- WINDOW_ADAPT = True  
