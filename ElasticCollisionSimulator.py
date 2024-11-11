import numpy as np
import os
import shutil
from PIL import Image
from multiprocessing import Pool, cpu_count
import imageio
import random
from tqdm import tqdm

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction / np.linalg.norm(direction)

class Sphere:
    def __init__(self, center, radius, color, reflectiveness=0, velocity=None, mass=1):
        self.center = np.array(center, dtype=np.float32)
        self.radius = radius
        self.color = np.array(color, dtype=np.float32)
        self.reflectiveness = reflectiveness
        self.velocity = np.array(velocity, dtype=np.float32) if velocity is not None else np.zeros(3, dtype=np.float32)
        self.mass = mass

    def intersect(self, ray):
        oc = ray.origin - self.center
        a = np.dot(ray.direction, ray.direction)
        b = 2.0 * np.dot(oc, ray.direction)
        c = np.dot(oc, oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c

        if discriminant > 0:
            t1 = (-b - np.sqrt(discriminant)) / (2.0 * a)
            t2 = (-b + np.sqrt(discriminant)) / (2.0 * a)
            if t1 > 0.001:
                return t1
            if t2 > 0.001:
                return t2
        return None

class Camera:
    def __init__(self, position, target, fov, aspect_ratio, width, height):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.width = width
        self.height = height
        self.angle = np.tan(np.pi * 0.5 * fov / 180)

        forward = (target - position)
        forward = forward / np.linalg.norm(forward)
        right = np.cross(np.array([0, 1, 0]), forward)
        right = right / np.linalg.norm(right)
        up = np.cross(forward, right)

        self.forward = forward
        self.right = right
        self.up = up

    def get_ray(self, x, y, dx=0, dy=0):
        px = (2 * ((x + dx) / self.width) - 1) * self.angle * self.aspect_ratio
        py = (1 - 2 * ((y + dy) / self.height)) * self.angle
        direction = self.forward + self.right * px + self.up * py
        direction = direction / np.linalg.norm(direction)
        return Ray(self.position, direction)

class Light:
    def __init__(self, position, intensity):
        self.position = np.array(position, dtype=np.float32)
        self.intensity = intensity

def clamp(x, min_value, max_value):
    return max(min_value, min(x, max_value))

def reflect(vector, normal):
    return vector - 2 * np.dot(vector, normal) * normal

def trace_ray(ray, objects, lights, depth, max_depth):
    hit_color = np.array([0, 0, 0], dtype=np.float32)

    if depth > max_depth:
        return hit_color

    nearest_t = float('inf')
    nearest_object = None

    for obj in objects:
        t = obj.intersect(ray)
        if t is not None and t < nearest_t:
            nearest_t = t
            nearest_object = obj

    if nearest_object is None:
        return hit_color

    hit_point = ray.origin + ray.direction * nearest_t
    if isinstance(nearest_object, Sphere):
        normal = (hit_point - nearest_object.center)
        normal = normal / np.linalg.norm(normal)
    elif isinstance(nearest_object, Wall):
        normal = nearest_object.normal

    for light in lights:
        light_dir = (light.position - hit_point)
        light_dir = light_dir / np.linalg.norm(light_dir)

        shadow_ray = Ray(hit_point + normal * 1e-5, light_dir)
        in_shadow = False
        for obj in objects:
            if obj.intersect(shadow_ray):
                in_shadow = True
                break

        if not in_shadow:
            light_intensity = clamp(np.dot(light_dir, normal), 0, 1) * light.intensity
            hit_color += nearest_object.color * light_intensity

    if isinstance(nearest_object, Sphere) and nearest_object.reflectiveness > 0 and depth < max_depth:
        reflected_ray = Ray(hit_point, reflect(ray.direction, normal))
        reflected_color = trace_ray(reflected_ray, objects, lights, depth + 1, max_depth)
        hit_color = (1 - nearest_object.reflectiveness) * hit_color + nearest_object.reflectiveness * reflected_color

    return hit_color

def render_chunk(y_start, y_end, scene, width, height, fov, max_depth, samples_per_pixel):
    camera = scene['camera']
    chunk_image = np.zeros((y_end - y_start, width, 3), dtype=np.uint8)

    for y in range(y_start, y_end):
        for x in range(width):
            color = np.zeros(3, dtype=np.float32)

            for _ in range(samples_per_pixel):
                dx = random.random()
                dy = random.random()
                ray = camera.get_ray(x, y, dx, dy)
                color += trace_ray(ray, scene['objects'], scene['lights'], 0, max_depth)

            color /= samples_per_pixel
            chunk_image[y - y_start, x] = np.clip(color * 255, 0, 255)

    return chunk_image

def render(scene, width, height, fov, max_depth, samples_per_pixel=4):
    num_cores = max(cpu_count() - 2, 1) 
    chunk_size = height // num_cores 

    with Pool(processes=num_cores) as pool:
        tasks = [(i * chunk_size, (i + 1) * chunk_size if i != num_cores - 1 else height, 
                  scene, width, height, fov, max_depth, samples_per_pixel) for i in range(num_cores)]
        chunk_images = pool.starmap(render_chunk, tasks)

    image = np.vstack(chunk_images)
    return Image.fromarray(image)

class Wall:
    def __init__(self, normal, d, color):
        self.normal = normal.normalize()
        self.d = d
        self.color = color

    def intersect(self, ray):
        denom = self.normal.dot(ray.direction)
        if np.abs(denom) > 1e-6:
            t = -(self.normal.dot(ray.origin) + self.d) / denom
            if t >= 0:
                return t
        return None

ZERO_G = False
class ElasticCollisionSimulator:
    def __init__(self, spheres, walls, lights, camera, width, height, max_depth, num_frames, time_step, output_dir='frames'):
        self.spheres = spheres
        self.walls = walls
        self.lights = lights
        self.camera = camera
        self.width = width
        self.height = height
        self.max_depth = max_depth
        self.num_frames = num_frames
        self.time_step = time_step
        self.output_dir = output_dir

        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir)

    def simulate(self):
        for frame in range(self.num_frames):
            P_BAR.update()
            self.update_positions()
            self.handle_collisions()
            self.render_frame(frame)

    def update_positions(self):
        for sphere in self.spheres:
            sphere.center += sphere.velocity * self.time_step

            self.handle_boundary_collision(sphere)

    def handle_boundary_collision(self, sphere):
        min_boundary, max_boundary = -10, 10 

        for i in range(3):
            coord = sphere.center[i]
            velocity = sphere.velocity[i]
            if coord - sphere.radius < min_boundary or coord + sphere.radius > max_boundary:
                sphere.velocity[i] = -velocity

    def handle_collisions(self):
        for i in range(len(self.spheres)):
            for j in range(i + 1, len(self.spheres)):
                if self.are_spheres_colliding(self.spheres[i], self.spheres[j]):
                    self.resolve_collision(self.spheres[i], self.spheres[j])

    def are_spheres_colliding(self, sphere1, sphere2):
        distance = np.linalg.norm(sphere1.center - sphere2.center)
        return distance < (sphere1.radius + sphere2.radius)

    def resolve_collision(self, sphere1, sphere2):
        normal = (sphere1.center - sphere2.center) / np.linalg.norm(sphere1.center - sphere2.center)
        relative_velocity = sphere1.velocity - sphere2.velocity
        velocity_along_normal = relative_velocity.dot(normal)

        if velocity_along_normal > 0:
            return 

        restitution = 1
        impulse_scalar = -(1 + restitution) * velocity_along_normal
        impulse_scalar /= (1 / sphere1.mass + 1 / sphere2.mass)

        impulse = normal * impulse_scalar
        sphere1.velocity += impulse * (1 / sphere1.mass)
        sphere2.velocity -= impulse * (1 / sphere2.mass)
        if not ZERO_G:
            sphere1.velocity = np.array([sphere1.velocity[0], 0, sphere1.velocity[2]]) 
            sphere2.velocity = np.array([sphere2.velocity[0], 0, sphere2.velocity[2]])

    def render_frame(self, frame_number):
        scene = {
            'camera': self.camera,
            'objects': self.spheres + self.walls,
            'lights': self.lights
        }
        image = render(scene, self.width, self.height, self.camera.fov, self.max_depth)
        image.save(f'{self.output_dir}/frame_{frame_number:04d}.png')

    def compile_frames_to_video(self, output_file='output.mp4', fps=30):
        with imageio.get_writer(output_file, fps=fps) as video_writer:
            for frame in range(self.num_frames):
                frame_path = f'{self.output_dir}/frame_{frame:04d}.png'
                video_writer.append_data(imageio.imread(frame_path))
        print(f"Video saved as {output_file}")

P_BAR = None

def main():
    global P_BAR 
    width, height = 800, 608
    fov = 70
    max_depth = 5
    num_frames = 60  
    time_step = 0.05 
    P_BAR = tqdm(range(num_frames))

    camera = Camera(position=np.array([0, 5, -10]), target=np.array([0, 0, 0]), fov=fov, aspect_ratio=width / height, width=width, height=height)
    lights = [Light(position=np.array([5, 5, -5]), intensity=1.5)]
    spheres = [
        Sphere(center=np.array([-2, 0, 0]), radius=1, color=np.array([1, 0, 0]), reflectiveness=0.2, velocity=np.array([1, 0, 0]), mass=1),
        Sphere(center=np.array([2, 0, 0]), radius=1, color=np.array([0, 1, 0]), reflectiveness=0.3, velocity=np.array([-1, 0, 0]), mass=1),
        Sphere(center=np.array([0, 0, 2]), radius=1, color=np.array([0, 0, 1]), reflectiveness=0.4, velocity=np.array([0, 0, -1]), mass=1),
        Sphere(center=np.array([0, 2, -2]), radius=1, color=np.array([1, 1, 0]), reflectiveness=0.1, velocity=np.array([0, -0.5, 1]), mass=1)
    ]
    walls = [] 

    simulator = ElasticCollisionSimulator(spheres, walls, lights, camera, width, height, max_depth, num_frames, time_step)
    simulator.simulate()
    simulator.compile_frames_to_video()

if __name__ == '__main__':
    main()
