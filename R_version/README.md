## R version of SI simulation

Files:
* `SI.R` this is the code, commented heavily
* `R_adj.csv.gz` this is an edgelist in the form of a simple dataframe with i and j headers, edges are only listed in one direction. **ATTENTION: the numbering of nodes has to be from 0...N-1!!!! Or 1...N, but then correct the code in `init()`!!!**
* `R_seed.csv.gz` initial infected node indices. **ATTENTION: the numbering of nodes has to be from 0...N-1!!!! Or 1...N, but then correct the code in `init()`!!!**
* `R_karate.csv` Zachary's karate club edgelist, it goes from 1...34, so R eats it, you can see there are no +1s in `init()`.
* You also have to set how many nodes you have in the variable `N`, it does not automatically come from the edgelist (you might have isolated nodes).