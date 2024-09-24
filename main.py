import pygame
import random
import math

# Pygame setup
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Parameters
num_agents = 100
agent_radius = 3
max_speed = 5
max_force = 0.1  # Reduced for smoother, gradual force
collision_distance = 3 * agent_radius  # Collision distance threshold
view_distance = 300  # How far agents can see to align and cohere with each other

# Agent class
class Agent:
    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * max_speed
        self.acceleration = pygame.Vector2(0, 0)

    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > max_speed:
            self.velocity.scale_to_length(max_speed)
        self.position += self.velocity
        self.acceleration *= 0  # Reset acceleration after each frame
        self.wrap_edges()

    def apply_force(self, force):
        if force is not None:
            self.acceleration += force

    def wrap_edges(self):
        if self.position.x < 0:
            self.position.x = width
        elif self.position.x > width:
            self.position.x = 0
        if self.position.y < 0:
            self.position.y = height
        elif self.position.y > height:
            self.position.y = 0

    def avoid_collisions(self, agents):
        separation_force = pygame.Vector2(0, 0)
        count = 0

        for other in agents:
            if other != self:
                dist = distance(self, other)
                if dist < collision_distance and dist > 0:
                    # Compute the repulsion force (away from the other agent)
                    repulsion = (self.position - other.position).normalize() / dist
                    separation_force += repulsion
                    count += 1

        if count > 0:
            separation_force /= count
            if separation_force.length() > 0:
                separation_force = separation_force.normalize() * max_force * 2
            self.apply_force(separation_force)

    def draw(self):
        # Corrected rotation to point in velocity direction
        if self.velocity.length() > 0:
            angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))  # Correct angle

            length = agent_radius * 2
            # Triangle points pointing in the direction of velocity
            points = [
                pygame.Vector2(self.position.x + length * math.cos(math.radians(angle)),
                               self.position.y + length * math.sin(math.radians(angle))),
                pygame.Vector2(self.position.x + length * math.cos(math.radians(angle + 140)),
                               self.position.y + length * math.sin(math.radians(angle + 140))),
                pygame.Vector2(self.position.x + length * math.cos(math.radians(angle - 140)),
                               self.position.y + length * math.sin(math.radians(angle - 140)))
            ]
            pygame.draw.polygon(screen, (255, 255, 255), [(int(p.x), int(p.y)) for p in points])

def distance(a, b):
    return pygame.Vector2(a.position - b.position).length()

def apply_flocking_rules(agents):
    for agent in agents:
        separation = pygame.Vector2(0, 0)
        alignment = pygame.Vector2(0, 0)
        cohesion = pygame.Vector2(0, 0)
        count = 0

        for other in agents:
            if other != agent:
                d = distance(agent, other)
                if d < view_distance:  # Consider only agents within view distance
                    if d > 0 and d < collision_distance:
                        # Separation: steer away from nearby agents
                        separation_vector = (agent.position - other.position)
                        separation += separation_vector.normalize() / d
                    # Alignment: steer towards average velocity of nearby agents
                    alignment += other.velocity
                    # Cohesion: steer towards the center of nearby agents
                    cohesion += other.position
                    count += 1

        if count > 0:
            # Separation
            if separation.length() > 0:
                separation = separation.normalize() * max_force * 2

            # Alignment
            alignment /= count
            alignment = (alignment.normalize() * max_speed) - agent.velocity
            alignment = alignment.scale_to_length(max_force)

            # Cohesion
            cohesion = (cohesion / count) - agent.position
            if cohesion.length() > 0:
                cohesion = cohesion.normalize() * max_speed
            cohesion = cohesion - agent.velocity
            cohesion = cohesion.scale_to_length(max_force)

            # Apply forces
            agent.apply_force(separation * 1.5)  # Separation is more important
            agent.apply_force(alignment)
            agent.apply_force(cohesion)

def main():
    global agents
    agents = [Agent(random.randint(0, width), random.randint(0, height)) for _ in range(num_agents)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()

        screen.fill((0, 0, 0))

        apply_flocking_rules(agents)

        for agent in agents:
            # Make agents move towards the mouse
            direction_to_mouse = pygame.Vector2(mouse_x, mouse_y) - agent.position
            if direction_to_mouse.length() > 0:
                direction_to_mouse = direction_to_mouse.normalize() * max_speed
                steering_force = direction_to_mouse - agent.velocity
                if steering_force.length() > 0:
                    steering_force = steering_force.normalize() * max_force
                agent.apply_force(steering_force)

            # Handle collision avoidance
            agent.avoid_collisions(agents)
            agent.update()
            agent.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
