import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gAzimuth = np.radians(45)
gElevation = np.radians(45)
gDistance = 5.
gMouseMode = 0 # 0 : no mode, 1 : Left click mode, 2 : Right click mode
gPrevPos = None
gAt = np.zeros(3)
gScrollBuf = 0.

def scroll_callback(window, xoffset, yoffset):
    global gDistance, gScrollBuf

    if yoffset > 10:
        yoffset = 10
    elif yoffset < -10:
        yoffset = -10


    gScrollBuf += yoffset
    gDistance *= 0.995 ** int(gScrollBuf / .1)
    gScrollBuf -= int(gScrollBuf / .1) * .1
    # print(gScrollBuf)
    # gDistance *= 1.0 + 0.06 * (1 - 2 * (yoffset > 0))
    # print(yoffset)


def mouse_button_callback(window, button, action, mods):
    global gAzimuth, gElevation, gMouseMode, gPrevPos
    if action==glfw.PRESS and gMouseMode==0:
        if button==glfw.MOUSE_BUTTON_LEFT:
            gMouseMode = 1
            gPrevPos = glfw.get_cursor_pos(window)
        if button==glfw.MOUSE_BUTTON_RIGHT:
            gMouseMode = 2
            gPrevPos = glfw.get_cursor_pos(window)
    else:
        if button==glfw.MOUSE_BUTTON_LEFT and gMouseMode==1:
            gMouseMode = 0
        if button==glfw.MOUSE_BUTTON_RIGHT and gMouseMode==2:
            gMouseMode = 0


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([1.,0.,0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0.,0.,0.]))
    glVertex3fv(np.array([0.,1.,0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0.,0.,0]))
    glVertex3fv(np.array([0.,0.,1.]))
    glEnd()

def drawGrid():
    global gAt, gDistance

    dist = max(int(gDistance), 100)

    target = (int(gAt[0]), int(gAt[2]))



    varr1 = np.array(list(((-dist + target[0], 0, x), (dist + target[0], 0, x)) for x in range(-dist + target[1], dist + target[1])), 'float32')
    varr2 = np.array(list(((x, 0, -dist + target[1]), (x, 0, dist + target[1])) for x in range(-dist + target[0], dist + target[0])), 'float32')

    glColor3ub(255,255,255)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3 * varr1.itemsize, varr1)
    glDrawArrays(GL_LINES, 0, int(varr1.size / 3))
    glVertexPointer(3, GL_FLOAT, 3 * varr2.itemsize, varr2)
    glDrawArrays(GL_LINES, 0, int(varr2.size / 3))
    

def render():
    global gAzimuth, gElevation, gDistance, gAt

    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE ) # call this at the beginning of your render function

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, .001, 900)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eyePoint = (gDistance*np.cos(gElevation)*np.sin(gAzimuth),gDistance*np.sin(gElevation),gDistance*np.cos(gElevation)*np.cos(gAzimuth)) + gAt

    gluLookAt(*(eyePoint),
              *(gAt),
              0,1*(1 - 2 * (np.cos(gElevation) < 0)),0)

    drawGrid()

    t = glfw.get_time()


    # Body
    glPushMatrix()
    glTranslatef(0, 2 + 1 * np.sin(5*t), 0)


    # Draw blue body
    glPushMatrix()
    glColor3ub(50, 50, 200)
    glScalef(.5, 1., .5)
    drawSphere(24,24)
    glPopMatrix()


    # Head
    glPushMatrix()

    glTranslatef(0, 1.15, 0)
    glRotatef(10 + 10*np.sin(5*t), 0, 0, 1)

    # Draw yellow head
    glPushMatrix()
    glScalef(.3, .3, .3)
    glColor3ub(255, 213, 156)
    drawSphere(24,24)
    glPopMatrix()

    # Draw yellow nose
    glPushMatrix()
    glTranslatef(.2, 0, 0)
    glRotatef(10*np.sin(10*t), 0, 0, 1)
    glTranslatef(.15, 0, 0)
    glScalef(.15, .1, .1)
    drawSphere()
    glPopMatrix()

    # Draw red cap
    glPushMatrix()
    glTranslatef(.1, .5 - 0.2*np.cos(5*t), 0)
    glScalef(.5, .25, .4)
    glColor3ub(255, 0, 0)
    drawSphere(40, 40)
    glPopMatrix()

    glPopMatrix() # Head

    # right arm
    glPushMatrix()

    glTranslatef(0, .5, .5)
    glRotatef(20, -1, 0 ,0)
    glRotatef(45*(np.cos(5*t)-1), 0, 0, 1)
    glTranslatef(0, -.2, 0)
    
    # Draw right upper-arm
    glPushMatrix()
    glScalef(.1, .35, .1)
    glColor3ub(255,0,0)
    drawSphere()
    glPopMatrix()

    # right lower-arm
    glPushMatrix()

    glRotatef(10*(np.cos(5*t) + 1), 1, 0, 0)
    glTranslatef(0, -0.35, .05)
    glRotatef(50*(np.cos(5*t) - 1), 0, 0, -1)
    glTranslatef(0, -0.2, 0)

    # Draw lower-arm
    glPushMatrix()
    glScalef(.1, .3, .1)
    drawSphere()
    glPopMatrix()

    glPopMatrix() # right lower arm

    glPopMatrix() # right arm


    # left arm
    glPushMatrix()

    glTranslatef(0, .5, -.5)
    glRotatef(10*(np.cos(5*t) + 1), 1, 0 ,0)
    glRotatef(67.5*(np.cos(5*t)-1), 0, 0, -1)
    glTranslatef(0, -.2, 0)

    # Draw left upper-arm
    glPushMatrix()
    glScalef(.1, .35, .1)
    glColor3ub(255,0,0)
    drawSphere()
    glPopMatrix()

    # left lower-arm
    glPushMatrix()

    glRotatef(10*(np.cos(5*t) + 1), -1, 0, 0)
    glTranslatef(0, -0.35, -.05)
    glRotatef(22.5*(np.cos(5*t) - 1), 0, 0, -1)
    glTranslatef(0, -0.2, 0)

    # Draw left lower-arm
    glPushMatrix()
    glScalef(.1, .3, .1)
    drawSphere()
    glPopMatrix()

    glPopMatrix() # left lower arm

    glPopMatrix() # left arm


    # right leg
    glPushMatrix()

    glTranslatef(0, -.65, .25)
    glRotatef(22.5*(1 - np.cos(5*t)), 0, 0, -1)
    glTranslatef(0, -.35, 0)

    # Draw right upper-leg
    glPushMatrix()
    glScalef(.15, .35, .15)
    glColor3ub(50, 50, 200)
    drawSphere(24, 24)
    glPopMatrix()

    # right lower-leg
    glPushMatrix()

    glTranslate(0, -.15, 0)
    glRotatef(22.5*(1 - np.cos(5*t)), 0, 0, -1)
    glTranslate(0, -.35, 0)

    # Draw right lower-leg
    glPushMatrix()
    glScalef(.15, .35, .15)
    drawSphere(24,24)
    glPopMatrix()

    # right foot
    glPushMatrix()

    glTranslatef(.1, -.25, 0)
    glRotatef(22.5*(1 - np.cos(5*t)), 0, 0, -1)
    glTranslatef(0, -.15, 0)

    # Draw right foot
    glPushMatrix()
    glScalef(.2, .15, .15)
    glColor3ub(150, 50, 50)
    drawSphere()
    glPopMatrix()

    glPopMatrix() # right foot

    glPopMatrix() # right lower-leg

    glPopMatrix() # right leg

    # left leg
    glPushMatrix()

    glTranslatef(0, -.65, -.25)
    glRotatef(45*(1 - np.cos(5*t)), 0, 0, 1)
    glTranslatef(0, -.35, 0)

    # Draw left upper-leg
    glPushMatrix()
    glScalef(.15, .35, .15)
    glColor3ub(50, 50, 200)
    drawSphere(24, 24)
    glPopMatrix()

    # left lower-leg
    glPushMatrix()

    glTranslate(0, -.15, 0)
    glRotatef(22.5*(1 - np.cos(5*t)), 0, 0, -1)
    glTranslate(0, -.35, 0)

    # Draw left lower-leg
    glPushMatrix()
    glScalef(.15, .35, .15)
    drawSphere(24,24)
    glPopMatrix()

    # left foot
    glPushMatrix()

    glTranslatef(.1, -.25, 0)
    glRotatef(22.5*(1 - np.cos(5*t)), 0, 0, 1)
    glTranslatef(0, -.15, 0)

    # Draw left foot
    glPushMatrix()
    glScalef(.2, .15, .15)
    glColor3ub(150, 50, 50)
    drawSphere()
    glPopMatrix()

    glPopMatrix() # left foot

    glPopMatrix() # left lower-leg

    glPopMatrix() # left leg


    glPopMatrix() # Body


# draw a cube of side 2, centered at the origin.
def drawCube():
    glBegin(GL_QUADS)
    glVertex3f( 1.0, 1.0,-1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f( 1.0, 1.0, 1.0)

    glVertex3f( 1.0,-1.0, 1.0)
    glVertex3f(-1.0,-1.0, 1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f( 1.0,-1.0,-1.0)

    glVertex3f( 1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0,-1.0, 1.0)
    glVertex3f( 1.0,-1.0, 1.0)

    glVertex3f( 1.0,-1.0,-1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f( 1.0, 1.0,-1.0)

    glVertex3f(-1.0, 1.0, 1.0)
    glVertex3f(-1.0, 1.0,-1.0)
    glVertex3f(-1.0,-1.0,-1.0)
    glVertex3f(-1.0,-1.0, 1.0)

    glVertex3f( 1.0, 1.0,-1.0)
    glVertex3f( 1.0, 1.0, 1.0)
    glVertex3f( 1.0,-1.0, 1.0)
    glVertex3f( 1.0,-1.0,-1.0)
    glEnd()

# draw a sphere of radius 1, centered at the origin.
# numLats: number of latitude segments
# numLongs: number of longitude segments
def drawSphere(numLats=12, numLongs=12):
    for i in range(0, numLats + 1):
        lat0 = np.pi * (-0.5 + float(float(i - 1) / float(numLats)))
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)
        
        lat1 = np.pi * (-0.5 + float(float(i) / float(numLats)))
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)

        # Use Quad strips to draw the sphere
        glBegin(GL_QUAD_STRIP)

        for j in range(0, numLongs + 1):
            lng = 2 * np.pi * float(float(j - 1) / float(numLongs))
            x = np.cos(lng)
            y = np.sin(lng)
            glVertex3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr1, y * zr1, z1)

        glEnd()
    
def main():
    global gPrevPos, gAzimuth, gElevation, gMouseMode, gAt

    if not glfw.init():
        return
    window = glfw.create_window(640, 640, "2018008659", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if gMouseMode == 1:
            currPos = glfw.get_cursor_pos(window)
            gAzimuth += .01 * (gPrevPos[0] - currPos[0])
            gElevation += .01 * (currPos[1] - gPrevPos[1])
            gPrevPos = currPos
        elif gMouseMode == 2:
            currPos = glfw.get_cursor_pos(window)

            w = np.array([np.cos(gElevation)*np.sin(gAzimuth),np.sin(gElevation),np.cos(gElevation)*np.cos(gAzimuth)])
            w = w / np.sqrt(w @ w)
            u = np.cross((0,1*(1 - 2 * (np.cos(gElevation) < 0)),0), w)
            u = u / np.sqrt(u @ u)
            v = np.cross(w, u)

            gAt += max(5, gDistance) * .001 * (gPrevPos[0] - currPos[0]) * u + max(5, gDistance) * .001 * (currPos[1] - gPrevPos[1]) * v

            gPrevPos = currPos

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
