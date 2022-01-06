# graduation_project_OR_ANAC
 Project developed for completion of graduation in Production Engineering at the University of Brasília (UNB). A comparison of Python, Jullia, AIMMS and LINGO software was developed using an Integer Programming (PI) model for allocation of inspectors from the National Civil Aviation Agency (ANAC).
 
####  **Abstract**
The evolution of technologies and computational systems has allowed greater use of
decision support models formulated through mathematical programming. Among
them, those that use Integer Programming (IP) stand out, as their solution process is
more complex, requiring greater computational effort and time for large problems.
Considering the importance of these types of models and the diversity of methods and
tools used to solve them, this research sought to identify the methods and techniques
adopted to solve Integer Programming models, through a systematic review of the
literature, and to carry out a comparison between the use of some methods and tools
to implement a large model. Thus, to compare available softwares taking into account
the solution time, the research used the study developed in the Safety Oversight
Project at the National Civil Aviation Agency (ANAC), which consists of a problem of
allocation of servants located in different Brazilian States carrying out inspections at
the various airports, considering time, cost and activity. Two models are then
implemented in Python language with the aid of the “Pyomo” library and CPLEX and
Gurobi solvers, and 6 scenarios were tested. The test results were consolidated in a
table showing the execution time and the Objective Function (OF) found for each
instance, comparing the algorithm implemented in Python with the models developed
in the literature in LINGO, AIMMS, Julia and heuristics (Tabu Search, Simulated
Annealing and Hybrid). It is then observed that both tested softwares are viable and
capable of solving most scenarios in the entire programming problem of ANAC's
servants allocation, minimizing the cost of airfare in inspections. Finally, the
performance of the open source language Python with the Gurobi solver stands out for
being able to solve all implemented scenarios, obtaining the best performance in two
of them compared to the other software
 
 The model considers the skills and availability of inspectors, the quantity and specification of each inspection, and the objective was to minimize the cost of airfare for transporting inspectors to carry out inspections.
 
 The graduation dissertation is presented in file [PG_MILP_ANAC_GabrielGuth](https://github.com/guthgabriel/graduation_project_OR_ANAC/blob/main/PG_MILP_ANAC_GabrielGuth.pdf "PG_MILP_ANAC_GabrielGuth"). 
 
 The codes developed in Python, Julia, LINGO and Heuristics for the model are in folder [Modelos](https://github.com/guthgabriel/graduation_project_OR_ANAC/tree/main/Modelos "Modelos").
