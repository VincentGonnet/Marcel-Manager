#include <stdio.h>
#include <math.h>

int costMatrix[50][50], completed[50], nbNodes, minCost, result[50], resultIteration;

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

void mincost(int node)
{
    int i, nNode;

    completed[node] = 1;

    printf("%d--->", node + 1);
    result[resultIteration++] = node + 1;
    nNode = least(node);

    if (nNode == 999)
    {
        nNode = 0;
        printf("%d", nNode + 1);
        minCost += costMatrix[node][nNode];

        return;
    }

    mincost(nNode);
}

int *lists(int length, int rawNodes[])
{
    resultIteration = 0;
    minCost = 0;

    nbNodes = length / 2;
    printf("Starting C execution :\n");
    printf("Number of nodes : %d\n", nbNodes);

    int node[nbNodes][2]; // creating the node array

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

    // printing the node array
    printf("Node array :\n");
    for (int i = 0; i < nbNodes; i++)
    {
        printf("%d ", node[i][0]);
        printf("%d ", node[i][1]);
        printf("\n");
    }
    printf("\n");

    // generating a cost matrix
    printf("Cost matrix :\n");
    for (int i = 0; i < nbNodes; i++)
    {
        for (int j = 0; j < nbNodes; j++)
        {
            printf("Distance between [%d;%d] and [%d;%d] : ", node[i][0], node[i][1], node[j][0], node[j][1]);
            costMatrix[i][j] = sqrt(((node[j][0] - node[i][0]) * (node[j][0] - node[i][0])) + ((node[j][1] - node[i][1]) * (node[j][1] - node[i][1])));
            printf("%d\n", costMatrix[i][j]);
        }
        printf("\n");
    }

    // printing the cost matrix
    for (int i = 0; i < nbNodes; i++)
    {
        for (int j = 0; j < nbNodes; j++)
        {
            printf("%d ", costMatrix[i][j]);
        }
        printf("\n");
    }

    printf("\n\n");

    mincost(0);
    printf("\nMinimum cost : %d\n", minCost);

    return result;
}
