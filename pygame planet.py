import heapq
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Define a Planet class
class Planet:
    def __init__(self, name, x, y, fuel_station=False, no_fly_zone=False, fuel_capacity=0):
        self.name = name
        self.x = x
        self.y = y
        self.fuel_station = fuel_station
        self.no_fly_zone = no_fly_zone
        self.fuel_capacity = fuel_capacity

# Define a Node class for A* search
class Node:
    def __init__(self, planet, parent=None, distance=0, fuel_consumption=0):
        self.planet = planet
        self.parent = parent
        self.distance = distance
        self.fuel_consumption = fuel_consumption

    def __lt__(self, other):
        return self.fuel_consumption < other.fuel_consumption

# Define the A* search function
def astar_search(start_planet, end_planet, planets, terrain):
    # Create a priority queue
    queue = []
    heapq.heappush(queue, Node(start_planet))

    # Create a set to keep track of visited planets
    visited = set()

    while queue:
        # Dequeue the node with the lowest fuel consumption
        node = heapq.heappop(queue)

        # If the node is the end planet, return the path
        if node.planet == end_planet:
            path = []
            while node:
                path.append(node.planet)
                node = node.parent
            return path[::-1]

        # Mark the planet as visited
        visited.add(node.planet)

        # Get the neighbors of the planet
        neighbors = []
        for planet in planets:
            if planet != node.planet and not planet.no_fly_zone:
                # Calculate the distance and fuel consumption to the neighbor
                dx = abs(planet.x - node.planet.x)
                dy = abs(planet.y - node.planet.y)
                distance = dx + dy
                fuel_consumption = node.fuel_consumption
                for i in range(dx):
                    x = node.planet.x + i if planet.x > node.planet.x else node.planet.x - i
                    y = node.planet.y
                    fuel_consumption += terrain[(x, y)]
                for i in range(dy):
                    x = planet.x
                    y = node.planet.y + i if planet.y > node.planet.y else node.planet.y - i
                    fuel_consumption += terrain[(x, y)]
                if planet.fuel_station:
                    fuel_consumption = max(0, fuel_consumption - planet.fuel_capacity)
                neighbors.append(Node(planet, node, distance, fuel_consumption))

        # Add the neighbors to the queue
        for neighbor in neighbors:
            if neighbor.planet not in visited:
                heapq.heappush(queue, neighbor)

    # If no path is found, return None
    return None

# Define a function to draw all objects on the screen
def draw_objects(planets, terrain):
    fig, ax = plt.subplots()
    for planet in planets:
        if planet.fuel_station:
            ax.add_patch(patches.Circle((planet.x, planet.y), 0.2, color='g'))
        elif planet.no_fly_zone:
            ax.add_patch(patches.Circle((planet.x, planet.y), 0.2, color='r'))
        else:
            ax.add_patch(patches.Circle((planet.x, planet.y), 0.2, color='b'))
    for pos, cost in terrain.items():
        if cost == 1:
            ax.add_patch(patches.Rectangle((pos[0], pos[1]), 1, 1, color='y'))
        elif cost == 100:
            ax.add_patch(patches.Rectangle((pos[0], pos[1]), 1, 1, color='k'))
        elif cost == 0:
            ax.add_patch(patches.Rectangle((pos[0], pos[1]), 1, 1, color='c'))
    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.show()

# Test the program
planets = [
    Planet("Earth", 0, 0, fuel_station=True, fuel_capacity=10),
    Planet("Mars", 3, 0),
    Planet("Jupiter", 2, 2, no_fly_zone=True),
    Planet("Saturn", 4, 4),
    Planet("Uranus", 1, 3, fuel_station=True, fuel_capacity=5),
    Planet("Neptune", 8, 8)
]

terrain = {}
for i in range(10):
    for j in range(10):
        if random.random() < 0.1:
            terrain[(i, j)] = 100  # blackhole
        elif random.random() < 0.2:
            terrain[(i, j)] = 0  # nebula
        else:
            terrain[(i, j)] = 1  # asteroid

start_planet = planets[0]
end_planet = planets[5]

path = astar_search(start_planet, end_planet, planets, terrain)
if path:
    print("Optimal route:")
    for planet in path:
        print(planet.name)
else:
    print("No path found")

draw_objects(planets, terrain)

