# connect4
Intelligent Agent to play Connect 4

## Table of Content
- [connect4](#connect4)
  * [Deployment](#deployment)
  * [Actions and States](#actions-and-states)
  * [State Representation](#state-representation)
  * [MiniMax Algorithm](#minimax-algorithm)
  * [Data Structures Used](#data-structures-used)
  * [Optimizations](#optimizations)
    + [Heuristic Pruning](#heuristic-pruning)
    + [Alpha-Beta Pruning](#alpha-beta-pruning)
    + [Exploring Best Moves First](#exploring-best-moves-first)
  * [Analysis for Runtime](#analysis-for-runtime)
    + [Without Pruning](#without-pruning)
    + [With Pruning](#with-pruning)
  * [MiniMax Tree Visualizer](#minimax-tree-visualizer)
  * [Graphical Interface](#graphical-interface)
  * [Contributors](#contributors)

## Deployment

- The project was built using [Python 3.9](https://www.python.org/downloads/release/python-390/), make sure you configure your python interpreter correctly
- You should run the "interface.py" python file, you can do that by running the following command inside the project folder
 ```bash
  python interface.py
 ```


## State Representation
- The simplest way to represent the board is using a 2D array. However, using 2D array uses ($6\times 7\times size of integer). This representation would limits the agent by only reaching short search depth and doesn't enable the agent to go deep in the search tree.
- The board configuration (state) is represented as 64-bit number as each column takes 9 bits and is represented as follows:
    - A 3 bits for each column which points to the last empty location, we can call them last location mask, for example if the three bits is "001" indeicates that the next location is the first row
    - A 6 bits representing each slot inside that column, 0 for the human and 1 for the intelligent agent.
    - The 64th bit indicates whether the state is pruned or not, it is only useful when printing the search tree so we can neglect it in most of our operations (check the [Alpha Beta Pruning](#alpha-beta-pruning) section for a better understanding).
- We can conclude from the previous representation that an empty board will be represented as the bits:
    > 1001000000001000000001000000001000000001000000001000000001000000
- Those bits are equal to the number "10378549747928563776" in decimal.

- Actions are implemented by incrementing the last location mask of every column and upating the bit corresponding to that slot.


## MiniMax Algorithm

- MiniMax Algorihm Pseudocode:
```python
Function MiniMax(maxDepth, currentDepth, isMaxPlayer, state)
    if currentDepth == maxDepth
        return state,heuristic(state)
    if isGameOver(state)
        return state,getFinalScore(state)
    
    children = getChilder(state)
    if isMaxPlayer // if it is the agent's turn
        Initialize maxChild, maxValue with negative infinity
        for child in children
            childValue = MiniMax(maxDepth,currentDepth+1, not isMaxPlayer, child)[1]
            if childValue > maxValue
                maxChild = child, maxValue = childValue
        return maxChild, maxValue
    else
        Initialize minChild, minValue with positive infinity
        for child in children
            childValue = MiniMax(maxDepth,currentDepth+1, not isMaxPlayer, child)[1]
            if childValue < minValue
                minChild = child, minValue = childValue
        return minChild, minValue

```
## Data Structures Used
- Hash map to map from states to its children (next states).
- Hash map to map from states to its values.

## Optimizations
- Since that branching factor in connect-4 is 7, and the depth is 42, then the total number of states to search is 7^42 which is nearly equals 3x10^35 state. The agent needs to use some pruning to enhance the runtime and work in real time.

### Heuristic Pruning

### Alpha-Beta Pruning

### Exploring Best Moves First
- A lot of research regarding the connect-4 game has shown that playing in the middle or near the middle enhances the chances of winning the game, playing in the middle is considered in a lot of time the best choice.
- Exploring a state where we place a piece in the middle firstly has enhanced the alpha-beta pruning quite well especially in early game.

## Analysis for Runtime
- The following anlaysis is done on some random states, so the numbers can varies from one state to another in case of pruning.
- The time is measured in seconds.
### Without Pruning
<table align="center">
  <tr>
    <th>Depth</th>
    <th>States Expanded</th>
    <th>Time Taken</th>

  </tr>
  <tr>
    <td>1</td>
    <td>8</td>
    <td>0.001</td>
  </tr>
  <tr>
    <td>2</td>
    <td>57</td>
    <td>0.007</td>
  </tr>
  <tr>
    <td>3</td>
    <td>400</td>
    <td>0.069</td>
  </tr>
  <tr>
    <td>4</td>
    <td>2775</td>
    <td>0.521</td>
  </tr>
  <tr>
    <td>5</td>
    <td>19608</td>
    <td>3.01</td>
  </tr>
</table>

### With Pruning
 <tr>
    <th>Depth</th>
    <th>States Expanded</th>
    <th>Time Taken</th>

  </tr>
  <tr>
    <td>1</td>
    <td>8</td>
    <td>0.001</td>
  </tr>
  <tr>
    <td>2</td>
    <td>27</td>
    <td>0.005</td>
  </tr>
  <tr>
    <td>3</td>
    <td>84</td>
    <td>0.013</td>
  </tr>
  <tr>
    <td>4</td>
    <td>235</td>
    <td>0.115</td>
  </tr>
  <tr>
    <td>5</td>
    <td>1111</td>
    <td>0.645</td>
  </tr>
</table>

## MiniMax Tree Visualizer

## Graphical Interface

## Contributors

1- [Yousef Kotp](https://github.com/yousefkotp)

2- [Adham Mohammed](https://github.com/adhammohamed1)

3- [Mohammed Farid](https://github.com/MohamedFarid612)
