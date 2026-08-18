// Calls the student's search() directly, to see whether it behaves like a
// Binary Search. Compiled together with the student's helpers.c.

#include <stdio.h>

#include "helpers.h"

#define CHECK_N 2048

static unsigned int check_seed = 20260814u;

static unsigned int check_rand(void)
{
    check_seed = check_seed * 1103515245u + 12345u;
    return (check_seed >> 16) & 0x7fffu;
}

int main(void)
{
    static int master[CHECK_N];
    static int work[CHECK_N];

    // First an array that really is sorted: every value has to be found
    for (int i = 0; i < CHECK_N; i++)
    {
        master[i] = i;
    }

    int sorted_hits = 0;
    for (int value = 0; value < CHECK_N; value++)
    {
        // Hand over a fresh copy every time, so a search that changes the
        // array cannot make the next call easier
        for (int i = 0; i < CHECK_N; i++)
        {
            work[i] = master[i];
        }
        if (search(value, work, CHECK_N))
        {
            sorted_hits++;
        }
    }

    // Then the same values, shuffled
    for (int i = CHECK_N - 1; i > 0; i--)
    {
        int j = (int) (check_rand() % (unsigned int) (i + 1));
        int swap = master[i];
        master[i] = master[j];
        master[j] = swap;
    }

    int unsorted_hits = 0;
    for (int value = 0; value < CHECK_N; value++)
    {
        for (int i = 0; i < CHECK_N; i++)
        {
            work[i] = master[i];
        }
        if (search(value, work, CHECK_N))
        {
            unsorted_hits++;
        }
    }

    printf("N %d\n", CHECK_N);
    printf("SORTED_HITS %d\n", sorted_hits);
    printf("UNSORTED_HITS %d\n", unsorted_hits);
}
