import pygame
from boid import Boid
import vector
import random

class Env:
    flocks = []
    
    def __init__(self, window_size, fps):
        self.window_size = window_size
        self.fps = fps
        
    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Boids")
        
        flock = Boid

        for i in range(20):
            _ = Boid(self, vector.obj(x=random.randint(100,400),y=random.randint(100,400)),2, (255,0,0))
        run = True
        
        while(run):
            screen.fill('black')
            dt = clock.tick(self.fps)/ 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    match event.button:
                        case 1:
                            pass
                        case 3:
                            pass
            flock.calculate_steering_all(dt)
            flock.update_position_all(dt)
            flock.draw_all(screen)
            print(f"fps: {1000/(dt*1000)}",end='\r')
            pygame.display.flip()


        pygame.quit()