import glfw
from OpenGL.GL import *
import numpy as np

gComposedM = []

def key_callback(window, key, scancode, action, mods):
    if action == glfw.RELEASE:
        return

    valid_key = {glfw.KEY_Q, glfw.KEY_E, glfw.KEY_A, glfw.KEY_D}

    if key in valid_key:
        gComposedM.insert(0, key)
    elif key == glfw.KEY_1:
        gComposedM.clear()
    


def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    
    glColor3ub(255, 255, 255)
    
    for x in gComposedM:
        if x == glfw.KEY_Q:
            glTranslatef(-.1, 0., 0.)
        elif x == glfw.KEY_E:
            glTranslatef(.1, 0., 0.)
        elif x == glfw.KEY_A:
            glRotatef(10, 0, 0, 1)
        elif x == glfw.KEY_D:
            glRotatef(-10, 0, 0, 1)

    drawTriangle()
 
def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0.,.5]))
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([.5,0.]))
    glEnd()

def main():
    if not glfw.init():
        return
    window = glfw.create_window(480, 480, "2018008659", None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
