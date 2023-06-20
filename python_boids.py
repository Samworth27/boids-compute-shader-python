from environment import Env

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
FPS = 60

if __name__ == '__main__':
    env = Env((WINDOW_WIDTH,WINDOW_HEIGHT),FPS)
    env.run()