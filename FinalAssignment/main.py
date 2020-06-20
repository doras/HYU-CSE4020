import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

gAzimuth = np.radians(45)
gElevation = np.radians(45)
gDistance = 5.
gMouseMode = 0 # 0 : no mode, 1 : Left click mode, 2 : Right click mode
gPrevPos = None
gAt = np.zeros(3)
gScrollBuf = 0.
gSphereVarr = None # actual normal array for Sphere with duplicate for glDrawArrays function
gSphereNarr = None # vertex array for Sphere with duplicate for glDrawArrays function
gCubeVarr = None # actual normal array for Cube with duplicate for glDrawArrays function
gCubeNarr = None # vertex array for Cube with duplicate for glDrawArrays function

def drawSphere():
    global gSphereVarr, gSphereNarr
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    # File is set and normal vector is used.
    if gSphereNarr is not None:
        glNormalPointer(GL_FLOAT, 3*gSphereNarr.itemsize, gSphereNarr)
        glVertexPointer(3, GL_FLOAT, 3*gSphereVarr.itemsize, gSphereVarr)
        glDrawArrays(GL_TRIANGLES, 0, int(gSphereVarr.size/3))

def drawCube():
    global gCubeVarr, gCubeNarr
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    # File is set and normal vector is used.
    if gCubeNarr is not None:
        glNormalPointer(GL_FLOAT, 3*gCubeNarr.itemsize, gCubeNarr)
        glVertexPointer(3, GL_FLOAT, 3*gCubeVarr.itemsize, gCubeVarr)
        glDrawArrays(GL_TRIANGLES, 0, int(gCubeVarr.size/3))


def openObj(path):
    f = open(path, 'r')

    varr = np.empty((0,3), 'float32')
    vnarr = list()
    iarr = list()
    niarr = list()
    narr = None
    notNormal = False


    for line in f:
        fields = line.split()

        if len(fields) == 0:
            continue
        
        if fields[0] == 'v':
            varr = np.append(varr, np.array([tuple(float(x) for x in fields[1:])], 'float32'), axis=0)
        elif fields[0] == 'vn':
            vnarr.append(tuple(float(x) for x in fields[1:]))
        elif fields[0] == 'f':
            numVertex = len(fields) - 1

            indexItem = list()
            normalIndexItem = list()
            for x in fields[1:]:
                indices = x.split('/')
                if len(indices) < 3:
                    notNormal = True
                    indexItem.append(int(indices[0]) - 1)
                else:
                    indexItem.append(int(indices[0]) - 1)
                    normalIndexItem.append(int(indices[2]) - 1)


            iarr.append(indexItem)
            niarr.append(normalIndexItem)


    varrdup = np.empty((0,3,3), 'float32')
    for indices in iarr:
        varrdup = np.append(varrdup, np.array([list(varr[n] for n in indices)], 'float32'), axis=0)

    if not notNormal:
        narr = list()
        for indices in niarr:
            narr.append(list(vnarr[n] for n in indices))
        narr = np.array(narr, 'float32')

    f.close()

    return (varrdup, narr)


def scroll_callback(window, xoffset, yoffset):
    global gDistance, gScrollBuf

    if yoffset > 10:
        yoffset = 10
    elif yoffset < -10:
        yoffset = -10


    gScrollBuf += yoffset
    gDistance *= 0.995 ** int(gScrollBuf / .1)
    gScrollBuf -= int(gScrollBuf / .1) * .1


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

def key_callback(window, key, scancode, action, mods):
    pass

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

    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, .001, 1500)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    eyePoint = (gDistance*np.cos(gElevation)*np.sin(gAzimuth),gDistance*np.sin(gElevation),gDistance*np.cos(gElevation)*np.cos(gAzimuth)) + gAt

    gluLookAt(*(eyePoint),
              *(gAt),
              0,1*(1 - 2 * (np.cos(gElevation) < 0)),0)

    drawGrid()

    # Lighting and Shading is used.
    glEnable(GL_LIGHTING)

    glEnable(GL_LIGHT5)
    glEnable(GL_LIGHT6)
    glEnable(GL_NORMALIZE)

    glLightfv(GL_LIGHT5, GL_POSITION, (-1., -1., -1., 0.))
    glLightfv(GL_LIGHT6, GL_POSITION, (1., 1., 1., 0.))

    glLightfv(GL_LIGHT5, GL_AMBIENT, (.1, .1, .1, 1.))
    glLightfv(GL_LIGHT6, GL_AMBIENT, (.1, .1, .1, 1.))

    glLightfv(GL_LIGHT5, GL_DIFFUSE, (1., 1., 1., 1.))
    glLightfv(GL_LIGHT6, GL_DIFFUSE, (1., 1., 1., 1.))

    glLightfv(GL_LIGHT5, GL_SPECULAR, (1., 1., 1., 1.))
    glLightfv(GL_LIGHT6, GL_SPECULAR, (1., 1., 1., 1.))

    glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1., 1., 1., 1.))


    # main object
    glPushMatrix()
    drawSphere()
    glPopMatrix()

    # rest objects
    glPushMatrix()
    glTranslatef(5,0,0)
    drawCube()
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0,0,5)
    drawCube()
    glPopMatrix()

    glDisable(GL_LIGHTING)

    
def main():
    global gPrevPos, gAzimuth, gElevation, gMouseMode, gAt, gSphereVarr, gSphereNarr, gCubeVarr, gCubeNarr

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
    glfw.set_key_callback(window, key_callback)

    gSphereVarr, gSphereNarr = openObj("sphere-tri.obj")
    gCubeVarr, gCubeNarr = openObj("cube-tri.obj")

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
