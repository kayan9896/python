import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from tabulate import tabulate

# Constants
G = 6.67430e-11  # gravitational constant

class Bullet:
    def __init__(self, name, initial_velocity, mass, frontal_area, drag_coefficient):
        self.name = name
        self.initial_velocity = initial_velocity
        self.mass = mass
        self.frontal_area = frontal_area
        self.drag_coefficient = drag_coefficient

    def __str__(self):
        data = [['Name', self.name],
                ['Initial Velocity (m/s)', self.initial_velocity],
                ['Mass (kg)', self.mass],
                ['Frontal Area (m^2)', self.frontal_area],
                ['Drag Coefficient', self.drag_coefficient]]
        return tabulate(data, headers=['Property', 'Value'], tablefmt='simple')

class Planet:
    def __init__(self, name, radius, mass, atmospheric_data):
        self.name = name
        self.radius = radius
        self.mass = mass
        self.atmospheric_data = atmospheric_data
        self.atmospheric_density = interp1d(atmospheric_data['Altitude'], atmospheric_data['Air Density'], kind='cubic')

    def __str__(self):
        # Calculate gravity and atmospheric density at the surface
        gravity = self.get_gravity(0)
        atmospheric_density = self.get_atmospheric_density(0)

        data = [['Name', self.name],
                ['Radius (m)', self.radius],
                ['Mass (kg)', self.mass],
                ['Gravity at Surface (m/s^2)', gravity],
                ['Atmospheric Density at Surface (kg/m^3)', atmospheric_density]]

        return tabulate(data, headers=['Property', 'Value'], tablefmt='simple')

    def get_gravity(self, altitude):
        # Calculate gravity based on the formula for planets
        # Gravity = G * mass / radius^2
        # Here, we consider the altitude as a distance from the center of the planet
        return G * self.mass / (self.radius + altitude)**2

    def get_atmospheric_density(self, altitude):
        # Cap the altitude to be within the range of the atmospheric data
        altitude = min(max(altitude, min(self.atmospheric_data['Altitude'])), max(self.atmospheric_data['Altitude']))

        # Return the interpolated air density
        return self.atmospheric_density(altitude)

def simulate_trajectory(bullet, planet, angle, time_step):
    # Convert angle from degrees to radians
    angle = np.deg2rad(angle)

    # Initialize arrays to store position, velocity, and acceleration
    position = np.zeros((1, 2))
    velocity = np.zeros((1, 2))

    # Set initial conditions
    position[0, :] = [0, 0]
    velocity[0, :] = [bullet.initial_velocity * np.cos(angle), bullet.initial_velocity * np.sin(angle)]

    # Simulate trajectory
    i = 0
    while True:
        # Calculate gravity and atmospheric density
        gravity = planet.get_gravity(position[i, 1])
        atmospheric_density = planet.get_atmospheric_density(position[i, 1])

        # Calculate drag force
        drag_force = 0.5 * atmospheric_density * bullet.frontal_area * bullet.drag_coefficient * np.linalg.norm(velocity[i, :])**2

        # Calculate acceleration
        acceleration = np.array([-drag_force * velocity[i, 0] / (bullet.mass * np.linalg.norm(velocity[i, :])), -gravity - drag_force * velocity[i, 1] / (bullet.mass * np.linalg.norm(velocity[i, :]))])

        # Update velocity and position
        velocity = np.vstack((velocity, velocity[i, :] + acceleration * time_step))
        position = np.vstack((position, position[i, :] + velocity[i + 1, :] * time_step))

        # Check if bullet has hit the ground
        if position[i + 1, 1] < 0:
            break

        i += 1

    return position, velocity

def main():
    # Create a Bullet object for an AK-47 bullet
    bullet = Bullet("AK-47 Bullet", 500, 0.1, 0.01, 0.5)
    print(bullet)

    # Create a Planet object for Earth
    earth_atmospheric_data = {
        'Altitude': [0, 1000, 2000, 3000, 5000, 8000, 10000, 15000, 20000, 25000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000],
        'Air Density': [1.225, 1.112, 1.007, 0.9093, 0.7364, 0.5258, 0.4135, 0.1948, 0.08891, 0.04008, 0.01841, 0.003996, 0.001027, 0.0003097, 0.00008283, 0.00001846, 0.00000354, 0.0000008283]
    }
    planet = Planet("Earth", 6371000, 5.972e24, earth_atmospheric_data)
    print(planet)

    # Simulate bullet trajectory
    angle = 45
    time_step = 0.01
    position, velocity = simulate_trajectory(bullet, planet, angle, time_step)

    # Print initial and final velocity magnitudes
    print("Initial Velocity Magnitude: {:.2f} m/s".format(np.linalg.norm(velocity[0, :])))
    print("Final Velocity Magnitude: {:.2f} m/s".format(np.linalg.norm(velocity[-1, :])))

    # Plot trajectory
    plt.figure(figsize=(10, 6))
    plt.plot(position[:, 0], position[:, 1])
    plt.xlabel('Horizontal Distance (m)')
    plt.ylabel('Altitude (m)')
    plt.title('Bullet Trajectory')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
