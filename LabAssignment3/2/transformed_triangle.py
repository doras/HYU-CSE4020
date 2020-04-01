import glfw
from OpenGL.GL import *
import numpy as np

gComposedM = np.identity(3)

def key_callback(window, key, scancode, action, mods):
    rad_10 = np.radians(10)
    switcher = {
        glfw.KEY_W: np.array([[.9, 0., 0.],
                              [0., 1., 0.],
                              [0., 0., 1.]]),
        glfw.KEY_E: np.array([[1.1, 0., 0.],
                              [0.,  1., 0.],
                              [0.,  0., 1.]]),
        glfw.KEY_S: np.array([[np.cos(rad_10), -np.sin(rad_10), 0.],
                              [np.sin(rad_10), np.cos(rad_10),  0.],
                              [0.,             0.,              1.]]),
        glfw.KEY_D: np.array([[np.cos(-rad_10), -np.sin(-rad_10), 0.],
                              [np.sin(-rad_10), np.cos(-rad_10),  0.],
                              [0.,             0.,              1.]]),
        glfw.KEY_X: np.array([[1., -.1, 0.],
                              [0., 1.,  0.],
                              [0., 0.,  1.]]),
        glfw.KEY_C: np.array([[1.,  .1, 0.],
                              [0.,  1., 0.],
                              [0.,  0., 1.]]),
        glfw.KEY_R: np.array([[1., 0.,  0.],
                              [0., -1., 0.],
                              [0., 0.,  1.]])
    }

    if action == glfw.RELEASE:
        return

    global gComposedM
    if key == glfw.KEY_1:
        gComposedM = np.identity(3)
    else:
        newM = switcher.get(key)
        if newM is None:
            return
        gComposedM = newM @ gComposedM
    

def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([1.,0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0.,0.]))
    glVertex2fv(np.array([0.,1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv( (T @ np.array([.0,.5,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.0,.0,1.]))[:-1] )
    glVertex2fv( (T @ np.array([.5,.0,1.]))[:-1] )
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
        render(gComposedM)
        glfw.swap_buffers(window)
    
    glfw.terminate()

if __name__ == "__main__":
    main()
