import random
import time
import math

# File Format:
# Each line format should be "Order,A,B"
# Ex.
# 1,0.43,0.52
# 2,0.59,0.678
# 3,0.023,0.134
# ...

#--------- Classes -----------#

class Vane:

    def __init__(self, order, A, B):
        self.order = order
        self.A = A
        self.B = B
        
class Ant:
    
    def __init__(self, start):
        self.start = start
        self.current = start
        self.path = []
        self.path_dist = 0
        
    def reset(self):
        self.current = start
        self.path = []
        self.path_dist = 0
    
    def create_path(self, vanes, pheromone, avgArea):
        vanesLeft = list(vanes)
        
        if vanesLeft[self.start].order != self.start:
            print("Unexpected object data error ocurred.")
            raise SystemExit(0)
        
        # Put start vane node at start of the path
        self.path.append(vanesLeft[self.start])
        self.current = vanesLeft[self.start].order
        del vanesLeft[self.start]
        
        while(len(vanesLeft) > 0):
            
            # Calculate the sum of pheromone/(distance, i.e., area) acrross all paths from current vane to every remaining untravelled vane
            prob_denominator = 0
            for i in range(len(vanesLeft)):
                prob_denominator += (pheromone[self.current][vanesLeft[i].order] / get_vane_dist(self.path[-1], vanesLeft[i], avgArea))
            
            # Calculate probabilities for traveling from current node to every other untraveled node
            probabilities = []
            for i in range(len(vanesLeft)):
                probabilities.append((pheromone[self.current][vanesLeft[i].order] / get_vane_dist(self.path[-1], vanesLeft[i], avgArea)) / prob_denominator)
            
            chosen = get_prob_index(probabilities) # index of the vane selected by the weighted randomness
            
            self.path.append(vanesLeft[chosen])
            self.current = vanesLeft[chosen].order
            del vanesLeft[chosen]
        
        # Calculate score (i.e. total deviation from the average) for the constructed set of vanes
        self.path_dist = compute_total_dist(self.path, avgArea)

#-------- Functions ---------#

# Given a list of probabilities (that add up to 1), returns the index of the probability that was chosen by a random generator from 0 to 1
def get_prob_index(probabilities):
    x = random.uniform(0, 1)
    
    for i in range(len(probabilities)):
        if probabilities[i] > x:
            return i
        else:
            x = x - probabilities[i]

# Function to compute the average area between every vane in the given list
def compute_avg_area(vanes):
    totalArea = 0.0
    numVanes = len(vanes)
    
    for i in range(numVanes):
        totalArea += vanes[i].A + vanes[i].B
        
    return totalArea / numVanes

# Function to return the absolute deviation of the area between two vanes, from the given average area between vanes
def get_vane_dist(v1, v2, avgArea):
    return abs(avgArea - v1.A - v2.B)
    
# Function to compute the total deviation from the average area for the given set of vanes
def compute_total_dist(vanes, avgArea):
    score = 0.0
    numVanes = len(vanes)
    
    for i in range(numVanes - 1):
        score += get_vane_dist(vanes[i], vanes[i+1], avgArea)
        
    score += get_vane_dist(vanes[numVanes - 1], vanes[0], avgArea)
    
    return score
    
# Parses the input file to retrieve information for vanes
def get_input_vanes():
    file = input("Enter input file name (press enter to default to \"dataset.txt\"): ")

    if file == "":
        file = "dataset.txt"

    fin = open(file)

    vanes = []

    for line in fin:
        spline = line.split(",")
        vanes.append(Vane(int(spline[0]), float(spline[1]), float(spline[2])))
    
    fin.close()
    
    for i in range(len(vanes)):
        if vanes[i].order != i:
            print("Ensure vanes in the input file start from Order number 0, and are in increasing order")
            raise SystemExit(0)
    
    return vanes

#--------- Program ----------#

vanes = get_input_vanes()

start = time.perf_counter()

avgArea = compute_avg_area(vanes)
numVanes = len(vanes)

bestVanes = []
bestDist = 0
bestAnt = None

#ACO parameters
ant_mult = 5 # Controls the number of ants to test from any given node (per iteration)
pheromone_init = 0.01 # Controls the initial pheromone value along every path
pheromone_decay = 0.1 # Controls how much the pheromone on the trail evapourates by during each iteration
pheromone_incr = 0.1 # Controls how much pheromone is added to the best solution in a given iteration
max_paths = 10000 # Roughly controls the number of paths that are generated (# of paths generated = ceil[max_paths / # of ants])

ants = [] # List of ants available for the algorithm. # of ants = the multiplier times to the number of possible starting vanes

# Creating the ants
for i in range(numVanes * ant_mult):
    ants.append(Ant(i//ant_mult))

num_iterations = int(math.ceil(max_paths / len(ants))) # Number of paths generated by every ant
print("Number of full cycle iterations: " + str(num_iterations))

# Initializing the directional pheromone values from one vane to another
pheromone = [[pheromone_init for x in range(numVanes)] for y in range(numVanes)]

# Ant Cycle iterations
for k in range(num_iterations):
    
    # Generate new paths based on updated pheromones, and track which ant obtains the best solution
    for i in range(len(ants)):
        ants[i].reset()
        ants[i].create_path(vanes, pheromone, avgArea)
        if bestAnt is None or bestAnt.path_dist > ants[i].path_dist:
            bestAnt = ants[i]

    # Pheromone Evaporation
    for i in range(len(pheromone)):
        for j in range(len(pheromone[i])):
            pheromone[i][j] = (1 - pheromone_decay) * pheromone[i][j]
    
    # Enforcing pheromones along the path taken by the selected bestAnt during this iteration
    for i in range(len(bestAnt.path) - 1):
        pheromone[bestAnt.path[i].order][bestAnt.path[i+1].order] += (pheromone_incr / bestAnt.path_dist)

    pheromone[bestAnt.path[-1].order][bestAnt.path[0].order] += (pheromone_incr / bestAnt.path_dist)
    
    # Track new best vanes and distance if best ant in this iteration beats all-time record holder
    if bestDist == 0 or bestDist > bestAnt.path_dist:
        bestDist = bestAnt.path_dist
        bestVanes = list(bestAnt.path)
    
    bestAnt = None # Reset the best ant for the next iteration

end = time.perf_counter()

# Results output

elapsed = "%.12f" % (end - start);

fout = open("output.txt", "wt")
fout.write("Elapsed Time: " + elapsed + " sec\n")
fout.write("Solution's Deviation Score: " + str(bestDist) + "\n")

for i in range(len(bestVanes)):
    fout.write(str(bestVanes[i].order) + "," + str(bestVanes[i].A) + "," + str(bestVanes[i].B) + "\n")
    
fout.close()

print("Results outputted to \"output.txt\"")