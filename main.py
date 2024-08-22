import pygame
import random
import math

# Pygame setup
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Parameters
num_agents = 50
agent_radius = 5
max_speed = 4
max_force = 0.05
collision_distance = 3 * agent_radius  # Collision distance threshold

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
        self.acceleration *= 0
        self.wrap_edges()
        self.avoid_collisions()

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

    def avoid_collisions(self):
        for other in agents:
            if other != self:
                dist = distance(self, other)
                if dist < collision_distance:
                    # Move agent away from the other agent
                    overlap = collision_distance - dist
                    direction = (self.position - other.position).normalize()
                    self.position += direction * (overlap / 2)  # Adjust position to avoid overlap
                    other.position -= direction * (overlap / 2)  # Adjust the other agent's position

    def draw(self):
        # Draw agent as "<" shape
        angle = self.velocity.as_polar()[1]  # Get direction of movement
        length = agent_radius * 2
        points = [
            pygame.Vector2(self.position.x + length * math.cos(math.radians(angle - 90)),
                           self.position.y + length * math.sin(math.radians(angle - 90))),
            pygame.Vector2(self.position.x + length * math.cos(math.radians(angle + 90)),
                           self.position.y + length * math.sin(math.radians(angle + 90))),
            pygame.Vector2(self.position.x + length * math.cos(math.radians(angle)),
                           self.position.y + length * math.sin(math.radians(angle)))
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
                if d < 50:
                    if d > 0:
                        separation_vector = (agent.position - other.position)
                        separation += separation_vector.normalize() / d
                    alignment += other.velocity
                    cohesion += other.position
                    count += 1
        
        if count > 0:
            separation_length = separation.length()
            if separation_length > 0:
                separation = separation.normalize() * min(separation_length, max_force)

            alignment = (alignment / count).normalize() * max_speed
            cohesion = ((cohesion / count) - agent.position).normalize() * max_speed
            alignment -= agent.velocity
            cohesion -= agent.velocity

            separation = separation.scale_to_length(max_force)
            alignment = alignment.scale_to_length(max_force)
            cohesion = cohesion.scale_to_length(max_force)

            agent.apply_force(separation)
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
            direction_to_mouse = pygame.Vector2(mouse_x, mouse_y) - agent.position
            if direction_to_mouse.length() > 0:
                direction_to_mouse.normalize_ip()
                direction_to_mouse *= max_speed
                force = direction_to_mouse - agent.velocity
                force_length = force.length()
                if force_length > 0:
                    force = force.normalize() * min(force_length, max_force)
                agent.apply_force(force)
            
            agent.update()
            agent.draw()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
