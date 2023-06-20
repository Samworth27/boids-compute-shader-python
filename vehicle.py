import vector
import math 
class Vehicle:
    def __init__(self,mass,position,velocity,max_force,max_speed,orientation):
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.max_force = max_force
        self.min_speed = 1
        self.max_speed = max_speed
        self.max_turn_speed = math.radians(20)
        self.orientation = orientation
        self.steering_direction = vector.obj(x=0,y=0)
        self.acceleration = vector.obj(x=0,y=0)
    
    @staticmethod
    def truncate(vec, max_value):
        return vector.obj(phi = vec.phi, rho=min(vec.rho, max_value))
    @staticmethod
    def clamp(vec,min_value,max_value):
        return vector.obj(phi = vec.phi, rho=max(min(vec.rho, max_value),min_value))
        
    @staticmethod
    def normalise(vec):
        if abs(vec) == 0:
            return vector.obj(phi = vec.phi, rho=1)
        return vec/abs(vec)
       
    def move(self,dt):
        steering_force = self.truncate(self.steering_direction,self.max_force)
        self.acceleration = steering_force/ self.mass

        self.velocity = self.clamp(self.velocity + self.acceleration, 1, self.max_speed)
        self.velocity *= 0.99
        self.position += self.velocity*dt
        self.orientation = self.normalise(self.velocity).phi