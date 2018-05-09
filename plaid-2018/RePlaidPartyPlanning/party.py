#!/usr/bin/env python2

from pwn import *
import time
import numpy, numpy.ma
import scipy.sparse.csgraph, scipy.optimize, scipy.sparse

tube = remote('pppr.chal.pwning.xxx', 3444)

def read_problem():
    C, R, P = map(int, tube.readline().strip().split())

    problem = {}
    problem['cities'] = C

    for i in range(P):
        problem.setdefault('people', []).append(int(tube.readline().strip()))

    for i in range(P):
        problem.setdefault('food', []).append(int(tube.readline().strip()))

    for i in range(R):
        problem.setdefault('roads', []).append(map(int, tube.readline().strip().split()))

    return problem

def build_graph(problem):
    C = problem['cities']

    graph = numpy.full((C,C), 10**18)

    for r in problem['roads']:
        graph[r[0],r[1]] = r[2]
        graph[r[1],r[0]] = r[2]

    return numpy.ma.masked_equal(graph, 10**18)

def build_cost_matrix(problem, shortest):
    P = len(problem['people'])
    cost_matrix = numpy.zeros((P,P))

    for i,p in enumerate(problem['people']):
        for j,f in enumerate(problem['food']):
            cost_matrix[i][j] = shortest[p][f]
    
    return cost_matrix

def find_city(problem, shortest):
    M,MC = 10**18, None
    for c in range(problem['cities']):
        cost = 0
        for f in problem['food']:
            cost += shortest[f][c]
        if cost < M:
            M = cost
            MC = c

    return M,MC

# Would you like the condensed version? [y/N]
tube.readline()
tube.sendline('y')

Q = int(tube.readline().strip())

for q in range(Q):
    print 'N =',q
    problem = read_problem()

    graph = build_graph(problem)
    shortest = scipy.sparse.csgraph.shortest_path(graph, directed=False, method='J')
    cost_matrix = build_cost_matrix(problem, shortest)
    optimal = scipy.optimize.linear_sum_assignment(cost_matrix)

    p_f_cost = cost_matrix[optimal].sum()
    f_c_cost,city = find_city(problem, shortest)
    cost = int(p_f_cost + f_c_cost)

    tube.sendline('{} {}'.format(city, cost))

print tube.recvline()
