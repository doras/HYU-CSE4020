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
gVarr = None # vertex array
gVNarr = None # vertex normal pool
gIarr = None # vertex index array, 0-based index
gNIarr = None # normal index array indicated by face info, 0-based index
gNarr = None # actual normal array with duplicate for glDrawArrays function
gVarrdup = None # vertex array with duplicate for glDrawArrays function
gForcedShading = False # whether forced shading is on or off
gRenderMode = GL_FILL # whether render mode is solid or wireframe
gVertexNormalarr = None

def setup_smooth_shading():
    global gVarrdup, gVertexNormalarr, gVarr, gIarr

    gVertexNormalarr = np.zeros((int(gVarr.size / 3), 3), 'float32')

    for vertices, indices in zip(gVarrdup, gIarr):
        v1 = vertices[1] - vertices[0]
        v2 = vertices[2] - vertices[0]
        faceNormal = np.cross(v1, v2)
        faceNormal = faceNormal / np.linalg.norm(faceNormal)

        for idx in indices:
            gVertexNormalarr[idx] += faceNormal
        
    for idx, norm in enumerate(gVertexNormalarr):
        gVertexNormalarr[idx] = norm / np.linalg.norm(norm)
    
    print(gVertexNormalarr)

def drop_callback(window, paths):
    global gVarr, gIarr, gVNarr, gNIarr, gNarr, gVarrdup, gVertexNormalarr
    f = open(paths[0], 'r')

    gVarr = list()
    gVNarr = list()
    gIarr = list()
    gNIarr = list()
    gNarr = None
    notNormal = False
    gVertexNormalarr = None

    faceCount = 0
    triFaceCount = 0
    quadFaceCount = 0
    nFaceCount = 0

    for line in f:
        fields = line.split()

        if len(fields) == 0:
            continue
        
        if fields[0] == 'v':
            gVarr.append(tuple(float(x) for x in fields[1:]))
        elif fields[0] == 'vn':
            gVNarr.append(tuple(float(x) for x in fields[1:]))
        elif fields[0] == 'f':
            faceCount += 1
            numVertex = len(fields) - 1

            if numVertex == 3:
                triFaceCount += 1
            elif numVertex == 4:
                quadFaceCount += 1
            else:
                nFaceCount += 1

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
            gIarr.append(indexItem)
            gNIarr.append(normalIndexItem)



    gVarrdup = list()
    for indices in gIarr:
        gVarrdup.append(list(gVarr[n] for n in indices))
    gVarrdup = np.array(gVarrdup, 'float32')

    if not notNormal:
        gNarr = list()
        for indices in gNIarr:
            gNarr.append(list(gVNarr[n] for n in indices))
        gNarr = np.array(gNarr, 'float32')
    
    gVarr = np.array(gVarr, 'float32')
    gIarr = np.array(gIarr)


    print( 'File name: %s' % f.name, 'Total number of faces: %d' % faceCount, 
            'Number of faces with 3 vertices: %d' % triFaceCount, 
            'Number of faces with 4 vertices: %d' % quadFaceCount, 
            'Number of faces with more than 4 vertices: %d' % nFaceCount, sep='\n')

    # print('notNormal:', notNormal)
    # print('gVarr: ', gVarr)
    # print('gNarr: ', gNarr)
    # print('gIarr: ', gIarr)
    # print('gVarrdup: ', gVarrdup)

    f.close()


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
    global gRenderMode, gForcedShading
    if action==glfw.PRESS:
        if key==glfw.KEY_Z:
            if gRenderMode == GL_FILL:
                gRenderMode = GL_LINE
            else:
                gRenderMode = GL_FILL
        if key==glfw.KEY_S:
            gForcedShading = not gForcedShading

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
    global gAzimuth, gElevation, gDistance, gAt, gVarr, gIarr, gNarr, gVarrdup, gRenderMode, gForcedShading, gVertexNormalarr

    glPolygonMode( GL_FRONT_AND_BACK, gRenderMode )

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

    # Lighting and Shading is used only when using solid mode not wireframe mode.
    if gRenderMode == GL_FILL:
        glEnable(GL_LIGHTING)

        # glEnable(GL_LIGHT0)
        # # glEnable(GL_LIGHT1)
        # glEnable(GL_LIGHT2)
        # # glEnable(GL_LIGHT3)
        # glEnable(GL_LIGHT4)
        # # glEnable(GL_LIGHT5)
        glEnable(GL_LIGHT6)
        glEnable(GL_NORMALIZE)

        glLightfv(GL_LIGHT0, GL_POSITION, (1., 0., 0., 0.))
        glLightfv(GL_LIGHT1, GL_POSITION, (-1., 0., 0., 0.))
        glLightfv(GL_LIGHT2, GL_POSITION, (0., 1., 0., 0.))
        glLightfv(GL_LIGHT3, GL_POSITION, (0., -1., 0., 0.))
        glLightfv(GL_LIGHT4, GL_POSITION, (0., 0., 1., 0.))
        glLightfv(GL_LIGHT5, GL_POSITION, (0., 0., -1., 0.))
        glLightfv(GL_LIGHT6, GL_POSITION, (1., 1., 1., 0.))

        glLightfv(GL_LIGHT0, GL_AMBIENT, (.1, .1, .1, 1.))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (.1, .1, .1, 1.))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (.1, .1, .1, 1.))
        glLightfv(GL_LIGHT3, GL_AMBIENT, (.1, .1, .1, 1.))
        glLightfv(GL_LIGHT4, GL_AMBIENT, (.1, .1, .1, 1.))
        glLightfv(GL_LIGHT5, GL_AMBIENT, (.1, .1, .1, 1.))
        glLightfv(GL_LIGHT6, GL_AMBIENT, (.1, .1, .1, 1.))

        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT3, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT4, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT5, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT6, GL_DIFFUSE, (1., 1., 1., 1.))

        glLightfv(GL_LIGHT0, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT2, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT3, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT4, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT5, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT6, GL_SPECULAR, (1., 1., 1., 1.))

        glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1., 1., 1., 1.))


    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)

    # glNormalPointer(GL_FLOAT, 3*gNarr.itemsize, gNarr)
    # glVertexPointer(3, GL_FLOAT, 3*gVarr.itemsize, gVarr)
    # glDrawElements(GL_TRIANGLES, gIarr.size, GL_UNSIGNED_INT, gIarr)

    if gForcedShading and gVarr is not None:
        if gVertexNormalarr is None:
            setup_smooth_shading()
        glNormalPointer(GL_FLOAT, 3*gVertexNormalarr.itemsize, gVertexNormalarr)
        glVertexPointer(3, GL_FLOAT, 3*gVarr.itemsize, gVarr)
        glDrawElements(GL_TRIANGLES, gIarr.size, GL_UNSIGNED_INT, gIarr)
    else:
        # File is set and normal vector is used.
        if gNarr is not None:
            glNormalPointer(GL_FLOAT, 3*gNarr.itemsize, gNarr)
            glVertexPointer(3, GL_FLOAT, 3*gVarrdup.itemsize, gVarrdup)
            glDrawArrays(GL_TRIANGLES, 0, int(gVarrdup.size/3))
        # File is set and but normal vector is NOT used.
        elif gVarr is not None:
            glDisableClientState(GL_NORMAL_ARRAY)
            glVertexPointer(3, GL_FLOAT, 3*gVarr.itemsize, gVarr)
            glDrawElements(GL_TRIANGLES, gIarr.size, GL_UNSIGNED_INT, gIarr)
        # If file is NOT set, do nothing.

    glDisable(GL_LIGHTING)

    
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
    glfw.set_drop_callback(window, drop_callback)
    glfw.set_key_callback(window, key_callback)

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
