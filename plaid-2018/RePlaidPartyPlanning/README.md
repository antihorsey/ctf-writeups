Re: Plaid Party Planning
========================

Re: Plaid Party Planning was an algorithms problem. Given:

1. A set of cities
1. A list of cities with people
1. A list of cities with food
1. A list of distances between cities

we were expected to find the optimal destination city to minimize
the total travel time for each person to leave their starting city,
stop at a unique food city, then travel to the destination city.
The PPP admins clarified in IRC and added to the problem description
that each person had to stop at a different location to pick up food
and every food had to be picked up by some person.

The key insight to solving this problem is that it's actually two
different problems with independent solutions. To explain what I
mean, consider the second half of the problem. No matter how we
choose which people pick up which food and no matter what path they
take, the optimal city will be the one with the minimum total travel
distance from the food cities. Conversely, no matter what the final
destination city is, we need to optimally plan paths from the people
to pick up the food. (Note: This is only because we're interested in
the minimum total travel time. If we were trying to minimize the
longest travel time for any person, then the time at which people
arrived at the food cities would be important for determining the
final destination city.)

Now we can get to solving the two subproblems. We'll start with the
second half of picking the optimal city because it's the easier half.
Picking the right algorithm is important. We'll let C be the number
of cities, P be the number of people (also the number of food), and
R be the number of roads. Looking at the maximum numbers I saw on a
single run for these, I believe the max C is 500, the max P is 500,
and the max R is 10000.

First we'll need the shortest path between all pairs of cities.
There's a number of algorithms you can use. You can run either
[Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
or the
[Bellman-Ford algorithm](https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm)
on every source city, or run the
[Floyd-Warshall algorithm](https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm)
to get all the shortest paths at once. I just used scipy's
[shortest_path](https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.sparse.csgraph.shortest_path.html)
algorithm which picks the best one to use. The complexity for this
should be somewhere around `O(C^3)` at the worst.

Once we have the shortest paths, we can bruteforce the best
destination city. For each of C possible destination cities, we have
to add the distances from F different cities. This gives a complexity
of `O(C*F)`, which is quite doable.

Now to go back to the first half of the problem. The first
straightforward approach might be to try every possible mapping of
people to food. But this gives a complexity of `O(P!)` -- which leads
to ridiculously large numbers for P up to 500
(500! == 1.22 * 10^1134)!

So we need another approach. Thankfully this is a well-studied
problem known as the
[assignment problem](https://en.wikipedia.org/wiki/Assignment_problem).
Given the shortest paths between cities we've already computed, we
can determine the distance from each person to each food city and
use that to create a cost matrix. This cost matrix is effectively a
bipartite graph, which is a graph where the vertices can be broken
down into two groups such that every edge is between a vertex from
both groups. In this case, the one group is the people cities and the
second group is the food cities. Assuming we've already calculated
the shortest paths, creating this cost matrix is `O(C^2)`.

The assignment problem can be solved by the
[Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm),
which can be made to run in `O(C^3)`. Once again, scipy has a
function to calculate this for us:
[linear_sum_assignment](https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.optimize.linear_sum_assignment.html).

So now that we have a plan,  we just have to wire everything together
and let it rip. First things first -- we need to read the problem in
from the server:

```
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
```

Then we need to build the adjacency matrix (a 2-dimensional array
describing all the edges in the graph):

```
def build_graph(problem):
    C = problem['cities']

    graph = numpy.full((C,C), 10**18)

    for r in problem['roads']:
        graph[r[0],r[1]] = r[2]
        graph[r[1],r[0]] = r[2]

    return graph
```

We'll also need to be able to build the cost matrix from the shortest
paths:

```
def build_cost_matrix(problem, shortest):
    P = len(problem['people'])
    cost_matrix = numpy.zeros((P,P))

    for i,p in enumerate(problem['people']):
        for j,f in enumerate(problem['food']):
            cost_matrix[i][j] = shortest[p][f]

    return cost_matrix
```

Finally, we'll need to pick the optimal city:

```
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
```

With all that in place, we just need the glue logic:

```
# Would you like the condensed version? [y/N]
tube.readline()
tube.sendline('y')

Q = int(tube.readline().strip())

for q in range(Q):
    print 'N =',q
    problem = read_problem()

    graph = build_graph(problem)
    shortest = scipy.sparse.csgraph.shortest_path(graph, directed=False)
    cost_matrix = build_cost_matrix(problem, shortest)
    optimal = scipy.optimize.linear_sum_assignment(cost_matrix)

    p_f_cost = cost_matrix[optimal].sum()
    f_c_cost,city = find_city(problem, shortest)
    cost = int(p_f_cost + f_c_cost)
```

Let it rip, and it'll run beautifully for a while. You can make it up
to about to the 30th problem if you're lucky. But you'll eventually
run into this:

> That doesn't look right...

What gives? Why are we suddenly getting wrong answers?

Well it turns out that some of the distances in the problem are 0!
And reading the documentation for scipy we find this little tidbit:

> for dense array representations, non-edges are represented by
  G[i, j] = 0, infinity, or NaN.

0 is used to represent not-connected edges! So scipy would give us
longer paths that avoided the free 0 distance edges.

Solving this problem took a surprisingly long and frustratingly long
time. I tried reading through the numpy MaskedArray documentation but
it was getting late and I was having a hard time following it. I
tried to convert to using some of the scipy sparse matrices like
[csr_matrix](https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.sparse.csr_matrix.html#scipy.sparse.csr_matrix)
or
[dok_matrix](https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.sparse.dok_matrix.html#scipy.sparse.dok_matrix)
but 0 weight edges still weren't working. I turned to a different
implementation of Dijkstra, but it was all written in Python so it
was on the slow side. It also used some custom priority dictionary
data structure that I think slowed it down too. It worked fine on
problems with 0 weight edges, but it started timing out by the 50th
problem or so out of 140.

I tried looking through scipy's Dijkstra implementation to see if I
could see where it was treating 0 weight edges as disconnected.
After looking for about an hour, I finally found it hidden away in a
validation function named `validate_graph`. I changed the code to not
treat 0 as disconnected and waited and waited for scipy to build.

Using the custom build of scipy worked and I finally was able to
solve the right answer for all 140 rounds without timing out and
was rewarded with the flag:

> You did it! PCTF{m1nc0st_b1p4rt1t3_m4tch1ng}

In hindsight, using the masked arrays would have been easier. After
the competition, with a fresh set of eyes I was able to figure out
the documentation enough to get it to work if I also manually
specified Dijkstra's algorithm or Johnson's method (Bellman-Ford
timed out, and Floyd-Warshall which was chosen by default still gave
wrong answers). Here's what `build_graph` looked like when using a
MaskedArray instead:

```
def build_graph(problem):
    C = problem['cities']

    graph = numpy.full((C,C), 10**18)

    for r in problem['roads']:
        graph[r[0],r[1]] = r[2]
        graph[r[1],r[0]] = r[2]

    return numpy.ma.masked_equal(graph, 10**18)
```
