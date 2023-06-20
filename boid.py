import vector
import random
import math
import pygame
from collections import namedtuple
from copy import copy
import functools
from vehicle import Vehicle
from multiprocessing import Process, Pool

Bounds = namedtuple('Bounds', ('x0', 'x1', 'y0', 'y1'))


class Boid(Vehicle):
    members: list['Boid'] = []

    def __init__(self, environment, position, size, colour):
        velocity = vector.obj(
            rho=random.randint(1, 5), phi=random.random()*2*math.pi - math.pi)
        super().__init__(size*size, position, velocity, 100, 200, velocity)
        self.size = size
        self.colour = colour
        self.add_to_flock(self)
        self.bounds = Bounds(
            0, environment.window_size[0], 0, environment.window_size[1])
        self.visual_range = 20 * size
        self.avoid_range = 5*size
        self.cohesion_factor = 7
        self.separation_factor = 10
        self.alignment_factor = 10
        self._in_visual_range = set()

    def steering_force(self, desired_velocity):
        return desired_velocity - self.normalise(self.velocity)

    def find_in_visual_range(self):
        self._in_visual_range = set()
        for member in set(self.members) - {self}:
            distance = abs(member.position - self.position)
            if distance < self.visual_range:
                self._in_visual_range.add(member)

    def separation(self, surface=None):
        force = vector.obj(x=0, y=0)
        if len(self._in_visual_range) == 0:
            return force
        count = 0
        for member in self._in_visual_range:
            distance = abs(member.position - self.position)
            if distance < self.avoid_range:
                local_force = self.normalise(self.position - member.position)
                local_force.rho *= 1/local_force.rho
                force += local_force
                if surface:
                    pygame.draw.line(surface, 'green', (self.position.x, self.position.y), (
                        self.position.x + local_force.x*10, self.position.y+local_force.y*10))
                count += 1
        if count == 0:
            return force
        force /= count
        if force.rho > 0:
            force = self.normalise(force)
            force.rho *= self.velocity.rho
            force = self.steering_force(force)
            force = self.truncate(force, self.max_force)
            if surface:
                pygame.draw.line(surface, 'green', (self.position.x, self.position.y), (
                    self.position.x + force.x*10, self.position.y+force.y*10), 2)
        return force

    def alignment(self, surface=None):
        force = vector.obj(x=0, y=0)
        if len(self._in_visual_range) == 0:
            return force
        for member in self._in_visual_range:
            force += member.velocity
            if surface:
                pygame.draw.line(surface, 'purple', (self.position.x, self.position.y), (
                    self.position.x + member.velocity.x*10, self.position.y + member.velocity.y*10))
        force /= len(self._in_visual_range)
        force = self.normalise(force) * self.velocity.rho
        force = self.steering_force(force)
        force = self.truncate(force, self.max_force)
        if surface:
            pygame.draw.line(surface, 'purple', (self.position.x, self.position.y),
                             (self.position.x + force.x*10, self.position.y + force.y*10), 2)
        return force

    def cohesion(self, surface=None):
        force = vector.obj(x=0, y=0)
        if len(self._in_visual_range) == 0:
            return force
        for member in self._in_visual_range:
            force += member.position
            if surface:
                direction = member.position - self.position
                pygame.draw.line(surface, 'blue', (self.position.x, self.position.y), (
                    self.position.x+direction.x, self.position.y + direction.y))
        
        force /= len(self._in_visual_range)
        force = force - self.position
        force = self.normalise(force) * self.max_speed
        force = self.steering_force(force)
        force = self.truncate(force,self.max_force)
        if surface:
            pygame.draw.line(surface, 'blue', (self.position.x, self.position.y), (
                    self.position.x+force.x*20, self.position.y + force.y*20),2)
        return force

    def calculate_steering(self, dt, surface=None):
        self.find_in_visual_range()
        self.steering_direction = vector.obj(x=0, y=0)
        self.steering_direction += self.separation(surface) * self.separation_factor
        self.steering_direction += self.alignment(surface) * self.alignment_factor
        self.steering_direction += self.cohesion(surface) * self.cohesion_factor

    def update_position(self, dt):
        self.move(dt)
        if self.position.x > self.bounds.x1:
            self.position.x = self.bounds.x0
        if self.position.x < self.bounds.x0:
            self.position.x = self.bounds.x1
        if self.position.y > self.bounds.y1:
            self.position.y = self.bounds.y0
        if self.position.y < self.bounds.y0:
            self.position.y = self.bounds.y1

    def draw(self, surface):
        pygame.draw.circle(surface, self.colour,
                           (self.position.x, self.position.y), self.size)
        # pygame.draw.circle(surface, 'grey',
        #                    (self.position.x, self.position.y), self.visual_range, width=1)
        # pygame.draw.circle(surface, 'grey',
        #                    (self.position.x, self.position.y), self.avoid_range, width=1)
        # pygame.draw.line(surface, 'blue', (self.position.x, self.position.y),
        #                  (self.position.x + self.acceleration.x*200, self.position.y + self.acceleration.y*200))
        pygame.draw.line(surface, 'white', (self.position.x, self.position.y),
                         (self.position.x + self.velocity.x*(1/self.size/10), self.position.y + self.velocity.y*(1/self.size/10)))

    @classmethod
    def add_to_flock(cls, member):
        cls.members.append(member)

    @classmethod
    def calculate_steering_all(cls, dt, surface=None):
        # with Pool(1) as pool:
            for member in cls.members:
                member.calculate_steering(dt,surface)

    @classmethod
    def update_position_all(cls, dt):
        for member in cls.members:
            member.update_position(dt)

    @classmethod
    def draw_all(cls, surface):
        for member in cls.members:
            member.draw(surface)
