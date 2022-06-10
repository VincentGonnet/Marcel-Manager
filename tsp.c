/** \file tsp.c

 \brief Traveling Salesman Problem script in C.
 \brief Has to be compiled with the following command in order to use it: gcc -fPIC -shared -o tsp.o tsp.c

 \section libraries_main Libraries
 - <stdio.h>
 - <math.h>

 \author Vincent Gonnet

 \date 2022/06/02
*/

#include <stdio.h>
#include <math.h>

int costMatrix[50][50]; ///< The cost matrix.
int completed[50];      ///< Already visited nodes
int nbNodes;            ///< Number of nodes
int minCost;            ///< Minimum cost
int result[50];         ///< Result array
int resultIteration;    ///< Index of the node being added to the result array

/** \brief Function to calculate the closest node to the current node
 * \param indexNode The current node
 */
int closest(int indexNode)
{
    int nextNode = 999;   // by default, there is no next node
    int lowestCost = 999; // by default, there is no minimum, the value is very high so that it will be replaced by the first iteration

    for (int i = 0; i < nbNodes; i++)
    {
        if ((costMatrix[indexNode][i] != 0) && (completed[i] == 0)) // if the node is not already visited and if the cost is not 0 (there is a connection)

            if (costMatrix[indexNode][i] < lowestCost) // if the cost is lower than the current minimum
            {
                lowestCost = costMatrix[indexNode][i]; // update the minimum
                nextNode = i;                          // update the next node
            }
    }

    if (lowestCost != 999)     // if there is a next node
        minCost += lowestCost; // add the cost of the connection to the global cost

    return nextNode; // return the next node
}

/** \brief Recursive function that calculates the shortest path to visit all the nodes, as well as the minimum cost of the path
 * \param indexNode The current node
 */
void recursiveSolver(int indexNode)
{
    int nextNode; // index of the next node to visit

    completed[indexNode] = 1; // mark the current node as visited

    result[resultIteration++] = indexNode + 1; // add the next node id to the result array

    nextNode = closest(indexNode); // determine the next node to visit using the least function

    if (nextNode == 999) // if there is no next node, we have visited all the nodes, so we return to the warehouse and stop the function
    {
        nextNode = 0; // set the next node to the warehouse

        minCost += costMatrix[indexNode][nextNode]; // add the cost of the path to the warehouse

        return; // stop the function
    }

    recursiveSolver(nextNode); // call the function again with the next node
}

/** \brief Main function : Traveling Salesman Problem (closest neighbor), will be imported in python by ctypes
 * \param lenght The length of the coordinates array
 * \param rawNodes[] The coordinates array
 */
int *tsp(int length, int rawNodes[])
{
    // reset variables (needed in case of multiple calls)
    resultIteration = 0; // Index of the current node being added to the visit order.
    minCost = 0;         // Minimum cost for the complete travel.

    nbNodes = length / 2; // Brief Number of nodes.

    int node[nbNodes][2];

    // seeding the node array
    for (int i = 0; i < (nbNodes); i++)
    {
        node[i][0] = rawNodes[i * 2];
        node[i][1] = rawNodes[(i * 2) + 1];
    }

    // nothing is completed yet
    for (int i = 0; i < nbNodes; i++)
    {
        completed[i] = 0;
    }

    // generating a cost matrix :
    for (int i = 0; i < nbNodes; i++)
    {
        for (int j = 0; j < nbNodes; j++)
        {
            costMatrix[i][j] = sqrt(((node[j][0] - node[i][0]) * (node[j][0] - node[i][0])) + ((node[j][1] - node[i][1]) * (node[j][1] - node[i][1])));
        }
    }

    recursiveSolver(0); // calling the recursive function

    return result;
}
