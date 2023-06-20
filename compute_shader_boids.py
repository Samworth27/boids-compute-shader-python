"""
Compute shader with buffers
"""
import random
from array import array
import math

import arcade
from arcade.gl import BufferDescription

# Window dimensions
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

# Size of performance graphs
GRAPH_WIDTH = 200
GRAPH_HEIGHT = 120
GRAPH_MARGIN = 5


class MyWindow(arcade.Window):

    def __init__(self):
        # Call parent constructor
        # Ask for OpenGL 4.3 context, as we need that for compute shader support.
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT,
                         "Compute Shader",
                         gl_version=(4, 3),
                         resizable=True)
        self.center_window()
        self.mouse_pos = (0,0)
        # --- Class instance variables

        # Number of balls to move
        self.num_balls = 50000

        # This has something to do with how we break the calculations up
        # and parallelize them.
        self.group_x = 256
        self.group_y = 1

        # --- Create buffers

        # Format of the buffer data.
        # 4f = position and size -> x, y, z, radius
        # 4x4 = Four floats used for calculating velocity. Not needed for visualization.
        # 4f = color -> rgba
        buffer_format = "4f 4x4 4f"
        # Generate the initial data that we will put in buffer 1.
        initial_data = self.gen_initial_data()

        # Create data buffers for the compute shader
        # We ping-pong render between these two buffers
        # ssbo = shader storage buffer object
        self.ssbo_1 = self.ctx.buffer(data=array('f', initial_data))
        self.ssbo_2 = self.ctx.buffer(reserve=self.ssbo_1.size)

        # Attribute variable names for the vertex shader
        attributes = ["in_vertex", "in_color"]
        self.vao_1 = self.ctx.geometry(
            [BufferDescription(self.ssbo_1, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )
        self.vao_2 = self.ctx.geometry(
            [BufferDescription(self.ssbo_2, buffer_format, attributes)],
            mode=self.ctx.POINTS,
        )

        # --- Create shaders

        # Load in the shader source code
        file = open("boids_shaders/compute_shader.comp")
        compute_shader_source = file.read()
        file = open("boids_shaders/vertex_shader.vert")
        vertex_shader_source = file.read()
        file = open("boids_shaders/fragment_shader.frag")
        fragment_shader_source = file.read()
        file = open("boids_shaders/geometry_shader.geom")
        geometry_shader_source = file.read()

        # Create our compute shader.
        # Search/replace to set up our compute groups
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_X",
                                                              str(self.group_x))
        compute_shader_source = compute_shader_source.replace("COMPUTE_SIZE_Y",
                                                              str(self.group_y))
        self.compute_shader = self.ctx.compute_shader(
            source=compute_shader_source)

        # Program for visualizing the balls
        self.program = self.ctx.program(
            vertex_shader=vertex_shader_source,
            geometry_shader=geometry_shader_source,
            fragment_shader=fragment_shader_source,
        )

        # --- Create FPS graph

        # Enable timings for the performance graph
        arcade.enable_timings()

        # Create a sprite list to put the performance graph into
        self.perf_graph_list = arcade.SpriteList()

        # Create the FPS performance graph
        graph = arcade.PerfGraph(GRAPH_WIDTH, GRAPH_HEIGHT, graph_data="FPS")
        graph.center_x = GRAPH_WIDTH / 2
        graph.center_y = self.height - GRAPH_HEIGHT / 2
        self.perf_graph_list.append(graph)

    def on_draw(self):
        # Clear the screen
        self.clear()
        # Enable blending so our alpha channel works
        self.ctx.enable(self.ctx.BLEND)

        # Bind buffers
        self.ssbo_1.bind_to_storage_buffer(binding=0)
        self.ssbo_2.bind_to_storage_buffer(binding=1)

        # Set input variables for compute shader
        # These are examples, although this example doesn't use them
        self.compute_shader["window_size"] = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.compute_shader["mouse_position"] = self.mouse_pos
        self.compute_shader["frame_time"] = self.dt

        # Run compute shader
        self.compute_shader.run(group_x=self.group_x, group_y=self.group_y)

        # Draw the balls
        self.vao_2.render(self.program)

        # Swap the buffers around (we are ping-ping rendering between two buffers)
        self.ssbo_1, self.ssbo_2 = self.ssbo_2, self.ssbo_1
        # Swap what geometry we draw
        self.vao_1, self.vao_2 = self.vao_2, self.vao_1

        # Draw the graphs
        self.perf_graph_list.draw()
        
    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = (x,y)
        return super().on_mouse_motion(x, y, dx, dy)

    def update(self, delta_time):
        self.dt = delta_time

    def gen_initial_data(self):
        for i in range(self.num_balls):



            yield random.randrange(0,WINDOW_WIDTH)
            yield random.randrange(0,WINDOW_HEIGHT)
            yield 0.0  # z (padding)
            yield 2

            # Velocity
            yield 0.0  # if not inner else r * math.cos(t)/1000
            yield 0.0  # if not inner else r * math.sin(t)/1000
            yield 0.0  # vz (padding)
            yield 0.0  # vw (padding)

            # Color
            yield 1.0  # r
            yield 0.0  # g
            yield 0.0  # b
            yield 1.0  # a


app = MyWindow()
arcade.run()
