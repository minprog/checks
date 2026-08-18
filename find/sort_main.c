// Calls the student's sort() directly, to see whether it behaves like a
// Counting Sort. Compiled together with the student's helpers.c.

#include <stdio.h>
#include <sys/resource.h>

#include "helpers.h"

#define CHECK_BIG 8000
#define CHECK_FLOOR_US 50000L
#define CHECK_TINY_CAP 5000
#define CHECK_BIG_CAP 200

static unsigned int check_seed = 20260814u;

static unsigned int check_rand(void)
{
    check_seed = check_seed * 1103515245u + 12345u;
    return check_seed >> 8;
}

// Processor time used by this program, so that other work on the machine
// cannot influence the measurement
static long check_cpu_us(void)
{
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    return (long) usage.ru_utime.tv_sec * 1000000L + (long) usage.ru_utime.tv_usec
         + (long) usage.ru_stime.tv_sec * 1000000L + (long) usage.ru_stime.tv_usec;
}

// Sorted, and still exactly the same numbers as before? The sum and the sum of
// squares do not depend on the order, so together they catch numbers that got
// lost, duplicated or invented.
static int check_sorted(int values[], int n, unsigned long long sum,
                        unsigned long long squares)
{
    unsigned long long total = 0;
    unsigned long long total_squares = 0;

    for (int i = 0; i < n; i++)
    {
        if (i > 0 && values[i - 1] > values[i])
        {
            return 0;
        }
        total += (unsigned long long) values[i];
        total_squares += (unsigned long long) values[i] * (unsigned long long) values[i];
    }

    return total == sum && total_squares == squares;
}

int main(void)
{
    // Two numbers, but as far apart as they can be: a counting sort has to walk
    // past every possible value in between, however few numbers there are
    static int tiny_master[2] = {65535, 0};
    static int tiny[2];
    static int big_master[CHECK_BIG];
    static int big[CHECK_BIG];

    unsigned long long tiny_sum = 0, tiny_squares = 0, big_sum = 0, big_squares = 0;

    for (int i = 0; i < 2; i++)
    {
        tiny_sum += (unsigned long long) tiny_master[i];
        tiny_squares += (unsigned long long) tiny_master[i] * (unsigned long long) tiny_master[i];
    }
    for (int i = 0; i < CHECK_BIG; i++)
    {
        big_master[i] = (int) (check_rand() % 65536u);
        big_sum += (unsigned long long) big_master[i];
        big_squares += (unsigned long long) big_master[i] * (unsigned long long) big_master[i];
    }

    // Keep sorting until enough time has been used to measure it reliably. An
    // expensive sort is over the floor after one go; a cheap one needs many.
    int tiny_ok = 1;
    long tiny_us = 0;
    int tiny_reps = 0;
    while (tiny_us < CHECK_FLOOR_US && tiny_reps < CHECK_TINY_CAP)
    {
        // Copying happens outside the measurement
        tiny[0] = tiny_master[0];
        tiny[1] = tiny_master[1];

        long started = check_cpu_us();
        sort(tiny, 2);
        tiny_us += check_cpu_us() - started;
        tiny_reps++;

        if (!check_sorted(tiny, 2, tiny_sum, tiny_squares))
        {
            tiny_ok = 0;
            break;
        }
    }

    int big_ok = 1;
    long big_us = 0;
    int big_reps = 0;
    while (big_us < CHECK_FLOOR_US && big_reps < CHECK_BIG_CAP)
    {
        // Also restore this one every time: an array that is already sorted is
        // much easier for some sorting algorithms
        for (int i = 0; i < CHECK_BIG; i++)
        {
            big[i] = big_master[i];
        }

        long started = check_cpu_us();
        sort(big, CHECK_BIG);
        big_us += check_cpu_us() - started;
        big_reps++;

        if (!check_sorted(big, CHECK_BIG, big_sum, big_squares))
        {
            big_ok = 0;
            break;
        }
    }

    printf("TINY_OK %d\n", tiny_ok);
    printf("BIG_OK %d\n", big_ok);
    printf("TINY_REPS %d\n", tiny_reps);
    printf("TINY_US %ld\n", tiny_us);
    printf("BIG_REPS %d\n", big_reps);
    printf("BIG_US %ld\n", big_us);
}
