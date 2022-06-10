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
 * \param currentNode The current node
 */
int least(int indexNode)
{
    int nc = 999, min = 999;
    int kmin;

    for (int i = 0; i < nbNodes; i++)
    {
        if ((costMatrix[indexNode][i] != 0) && (completed[i] == 0))
            if (costMatrix[indexNode][i] + costMatrix[i][indexNode] < min)
            {
                min = costMatrix[i][0] + costMatrix[indexNode][i];
                kmin = costMatrix[indexNode][i];
                nc = i;
            }
    }

    if (min != 999)
        minCost += kmin;

    return nc;
}

/** \brief Recursive function that calculates the shortest path to visit all the nodes, as well as the minimum cost of the path
 * \param currentNode The current node
 */
void mincost(int node)
{
    int i, nNode;

    completed[node] = 1;

    // printf("%d--->", node + 1);
    result[resultIteration++] = node + 1;
    nNode = least(node);

    if (nNode == 999)
    {
        nNode = 0;
        // printf("%d", nNode + 1);
        minCost += costMatrix[node][nNode];

        return;
    }

    mincost(nNode);
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

    mincost(0); // calling the recursive function

    return result;
}
