'''
AA: 

Module will calculate an efficency frontier. Point to whatever file path
contains the data in csv format.

Data should have NO header, but be in order of label, x, y

I use y and x as used in an ICER calculation (y/x) (cost / qaly, for example)

I use this code a lot, so it's accesible in a more generic form on:
https://github.com/namyaila/efficiency_frontier_health_economics
'''

import numpy as np


def format_results(results, strategies):
    data = []
    for label in strategies:
        y = results['Costs'][label]
        x = results['QALYs'][label]
        data.append([label, x, y])
    return data


def get_icers(data):
    icers = []
    for i in range(1, len(data)):
        icers.append(
            (data[i][2] - data[i - 1][2]) / (data[i][1] - data[i - 1][1]))
    return icers


def get_optimal(results, strategies, threshold):

    data = format_results(results, strategies)

    # sort inplace by the y and x values
    data.sort(key=lambda x: (x[1], x[2]))

    # Then, iteratively go through dataframe dropping strategies that are
    # dominated; i.e. strategies where the y value is lower than the one before
    # it (we already know that the x value is higher)

    while True:
        end = False
        for index in range(len(data)):
            if index == len(data) - 1:
                end = True
                break
            else:
                if (data[index][1] >= data[index + 1][1]
                        and data[index][2] < data[index + 1][2]):
                    # Del instead of pop because we don't care what was deleted
                    del data[index + 1]
                    # Restart from the top
                    break
        if end is True:
            break

    # Now comes a tricky part. We calculate ICERs between adjacent pairs and
    # drop the strategies where the ICER is greater than the next pair
    while True:
        end = False
        icers = get_icers(data)
        # length of ICER's is 1 less than the length of data
        for index in range(len(icers)):
            if index == len(icers) - 1:
                end = True
                break
            else:
                if icers[index] > icers[index + 1]:
                    # Del instead of pop because we don't care what was deleted
                    # This is a little tricky, but assume we have icers like this:
                    # 2 vs 1 -> 100
                    # 3 vs 2 -> 300
                    # 4 vs 3 --> 200
                    # Then because 3 vs 2 is greater than 4 vs 3, we delete
                    # the third strategy which is index 1 in our ICERs BUT is
                    # actually index 2 in our data
                    del data[index + 1]
                    # Restart from the top
                    break
        if end is True:
            # Append ICER's
            data[0].append('N/A')
            for i in range(1, len(data)):
                data[i].append(icers[i - 1])
            break

    for ICER in reversed(data):
        if ICER[-1] == 'N/A':
            results['Optimal Location'] = ICER[0]
            return
        if ICER[-1] < threshold:
            results['Optimal Location'] = ICER[0]
            return
