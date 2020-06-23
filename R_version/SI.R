library(data.table)
library(Matrix)
library(tictoc)

mode <- "iwiw"

init <- function(){
# This is the function, where we can set up the global parameters of the whole simulation.

    # parameter 'p' of the Bass model
    p_par <<- 0.000104
    # parameter 'q' of the Bass model
    q_par <<- 0.12
    # number of timesteps
    stop_par <<- 128

    # total number of runs with the above parameter settings
    num_runs <<- 1

    # creating necessary tables
    if (mode == "karate"){
        # this is the mode where we read the Zachary network edgelist for educational/debugging purposes
        # number of nodes
        N <<- 34
        elist <<- fread("R_karate.csv")
        # the edgelist only lists edges once, to create a full adj matrix, we have to give the reverse column
        # order as well to the sparse matrix constructor
        A <<- sparseMatrix(c(elist$V1,elist$V2),c(elist$V2,elist$V1),dims=c(N,N))
        # initial infected nodes
        seed <<- as.vector(c(1,2))
    }
    
    # R indexes from 1!!!
    if (mode == "iwiw"){
        # iwiw sample network
        N <<- 271941
        elist <- fread("R_adj.csv.gz")
        A <<- sparseMatrix(
            c(elist$i+1,elist$j+1),
            c(elist$j+1,elist$i+1),
            dims=c(N,N)
        )
        seed <<- as.vector(fread("R_seed.csv.gz")$V1)+1

    }
    
}

restart <- function(){
# This function restarts the simulation: it sets only the seeds as infected, everyone else susceptible, and resets the time counter to 1.
# Also, it empties the time_infected list that stores the infection time of the nodes.

    # init new simulation
    time_counter <<- 1

    # creating infected and susceptible lists
    infected <<- logical(N)
    # initial infection
    infected[seed] <<- TRUE
    # initial susceptibles, aka everybody who's not infected
    susceptible <<- !infected

    # storing the infection time for the nodes, setting infected nodes times to 1
    time_infected <<- numeric(N)
    time_infected[seed] <<- 1

    # storing number of infected neighbors for nodes
    node_neighborhood_num_infected <<- numeric(N)
    node_neighborhood_num_neighbors <<- rowSums(A)
    # adding 1 for isolated nodes to avoid division by 0
    node_neighborhood_num_neighbors <<- replace(
        node_neighborhood_num_neighbors,
        node_neighborhood_num_neighbors==0,
        1    
    )
    # counting number of infected neighbors for initial infection
    node_neighborhood_num_infected <<- node_neighborhood_num_infected + rowSums(A[,infected])

}

step_time <- function(){
# This is a function that forwards the simulation by 1 timestep.

    # init stopper
    tic()

    # increment time counter
    time_counter <<- time_counter + 1

    # fraction of infected neighbors vs total neighbors
    a <- node_neighborhood_num_infected/node_neighborhood_num_neighbors
    # uniform random number between 0 and 1
    r <- runif(N)
    # calculating threshold, comparing random number to threshold
    mask <- r < p_par + q_par*a
    # infect nodes where random number is smaller than the threshold and that are susceptible
    new_infected <- susceptible & mask

    # store infection time for newly infected nodes
    time_infected[which(new_infected)] <<- time_counter
    # union of old and new infections
    infected <<- infected | new_infected
    # decreasing the susceptibles with the newly infected nodes
    susceptible <<- susceptible & !new_infected
    # incrementing the counters in the array storing the number of infected neighbors
    if (sum(new_infected)==1){
        node_neighborhood_num_infected <<- node_neighborhood_num_infected + rowSums(as.matrix(A[,new_infected]))
    }else{
        node_neighborhood_num_infected <<- node_neighborhood_num_infected + rowSums(A[,new_infected])
    }

    # end stopper
    toc()
    # output time, new infected, overall infected
    cat(paste0(time_counter," ",sum(new_infected)," ",sum(infected)))
    cat("\n")

}


## main code
init()
restart()

if (mode=="iwiw"){
    for (i in 2:stop_par){
    step_time()
    }
}

# result
plot(table(time_infected))
plot(cumsum(table(time_infected)))

