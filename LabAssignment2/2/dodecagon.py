import glfw
from OpenGL.GL import *
import numpy as np

current_primitive = GL_LINE_LOOP

def render():
    shape = np.linspace(0, 2 * np.pi, 13)[:-1]
    vertex = np.column_stack((np.cos(shape), np.sin(shape)))
    
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(current_primitive)
    for x in vertex:
        glVertex2dv(x)
    glEnd()

def key_callback(window, key, scancode, action, mods):
    switcher = {
        glfw.KEY_0: GL_POLYGON,
        glfw.KEY_1: GL_POINTS,
        glfw.KEY_2: GL_LINES,
        glfw.KEY_3: GL_LINE_STRIP,
        glfw.KEY_4: GL_LINE_LOOP,
        glfw.KEY_5: GL_TRIANGLES,
        glfw.KEY_6: GL_TRIANGLE_STRIP,
        glfw.KEY_7: GL_TRIANGLE_FAN,
        glfw.KEY_8: GL_QUADS,
        glfw.KEY_9: GL_QUAD_STRIP
    }

    if action == glfw.PRESS:
        global current_primitive
        current_primitive = switcher.get(key, current_primitive)

def main():
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2018008659", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
