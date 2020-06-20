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

gDogCurrPos = np.array([10., 0., 0.])
gSnowPos = np.array([0., 0., 15.])
gSnowMode = 0 # 0 for stop, 1 for bounced
gCollideTime = None
gMainTrans = np.identity(4)
gRecentMove = np.zeros(4)
gP = (np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3))

gViewMode = 0 # 0 is mouse, 1 is FPS, 2 is Quarter

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
    global gMainTrans, gViewMode, gRecentMove
    if action==glfw.PRESS or action==glfw.REPEAT:
        if key==glfw.KEY_Q:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., -1.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
            gRecentMove = np.array([-1., 0., 0., 0.])
        elif key==glfw.KEY_W:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 1.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
            gRecentMove = np.array([1., 0., 0., 0.])
        elif key==glfw.KEY_A:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., -1.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
            gRecentMove = np.array([0., -1., 0., 0.])
        elif key==glfw.KEY_S:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 1.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
            gRecentMove = np.array([0., 1., 0., 0.])
        elif key==glfw.KEY_Z:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., -1.],
                                                [0., 0., 0., 1.]])
            gRecentMove = np.array([0., 0., -1., 0.])
        elif key==glfw.KEY_X:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 1.],
                                                [0., 0., 0., 1.]])
            gRecentMove = np.array([0., 0., 1., 0.])
        elif key==glfw.KEY_E:
            ang = np.radians(-10)
            gMainTrans = gMainTrans @ np.array([[1., 0.,           0.,          0.],
                                                [0., np.cos(ang), -np.sin(ang), 0.],
                                                [0., np.sin(ang),  np.cos(ang), 0.],
                                                [0., 0.,           0.,          1.]])
        elif key==glfw.KEY_R:
            ang = np.radians(10)
            gMainTrans = gMainTrans @ np.array([[1., 0.,           0.,          0.],
                                                [0., np.cos(ang), -np.sin(ang), 0.],
                                                [0., np.sin(ang),  np.cos(ang), 0.],
                                                [0., 0.,           0.,          1.]])
        elif key==glfw.KEY_D:
            ang = np.radians(-10)
            gMainTrans = gMainTrans @ np.array([[np.cos(ang),  0., np.sin(ang), 0.],
                                                [0.,           1., 0.,          0.],
                                                [-np.sin(ang), 0., np.cos(ang), 0.],
                                                [0.,           0., 0.,          1.]])
        elif key==glfw.KEY_F:
            ang = np.radians(10)
            gMainTrans = gMainTrans @ np.array([[np.cos(ang),  0., np.sin(ang), 0.],
                                                [0.,           1., 0.,          0.],
                                                [-np.sin(ang), 0., np.cos(ang), 0.],
                                                [0.,           0., 0.,          1.]])
        elif key==glfw.KEY_C:
            ang = np.radians(-10)
            gMainTrans = gMainTrans @ np.array([[np.cos(ang), -np.sin(ang), 0., 0.],
                                                [np.sin(ang),  np.cos(ang), 0., 0.],
                                                [0.,           0.,          1., 0.],
                                                [0.,           0.,          0., 1.]])
        elif key==glfw.KEY_V:
            ang = np.radians(10)
            gMainTrans = gMainTrans @ np.array([[np.cos(ang), -np.sin(ang), 0., 0.],
                                                [np.sin(ang),  np.cos(ang), 0., 0.],
                                                [0.,           0.,          1., 0.],
                                                [0.,           0.,          0., 1.]])
        elif key==glfw.KEY_T:
            gMainTrans = gMainTrans @ np.array([[1., -.1, 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_Y:
            gMainTrans = gMainTrans @ np.array([[1., .1, 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_U:
            gMainTrans = gMainTrans @ np.array([[1., 0., -.1, 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_I:
            gMainTrans = gMainTrans @ np.array([[1., 0., .1, 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_G:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [-.1, 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_H:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [.1, 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_J:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., -.1, 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_K:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., .1, 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_B:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [-.1, 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_N:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [.1, 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_M:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., -.1, 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_COMMA:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., .1, 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_O:
            gMainTrans = gMainTrans @ np.array([[0.9, 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_P:
            gMainTrans = gMainTrans @ np.array([[1.1, 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_L:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 0.9, 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_SEMICOLON:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1.1, 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_PERIOD:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 0.9, 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_SLASH:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1.1, 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_1:
            gMainTrans = gMainTrans @ np.array([[-1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_2:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., -1., 0., 0.],
                                                [0., 0., 1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_3:
            gMainTrans = gMainTrans @ np.array([[1., 0., 0., 0.],
                                                [0., 1., 0., 0.],
                                                [0., 0., -1., 0.],
                                                [0., 0., 0., 1.]])
        elif key==glfw.KEY_0:
            gViewMode = (gViewMode + 1) % 3


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
    

def render(t):
    global gAzimuth, gElevation, gDistance, gAt, gMainTrans, gDogCurrPos, gSnowPos, gViewMode, gSnowMode, gCollideTime, gP

    glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)


    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, .001, 1500)


    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if gViewMode == 0:
        eyePoint = (gDistance*np.cos(gElevation)*np.sin(gAzimuth),gDistance*np.sin(gElevation),gDistance*np.cos(gElevation)*np.cos(gAzimuth)) + gAt

        gluLookAt(*(eyePoint),
                *(gAt),
                0,1*(1 - 2 * (np.cos(gElevation) < 0)),0)
    elif gViewMode == 1:
        lookMatrix = (gMainTrans @ np.array([[0.,0.,0.],
                                            [0.,0.,1.],
                                            [0.,1.,0.],
                                            [1.,1.,0.]]))[:3]
        gluLookAt(*lookMatrix.T.reshape(9))
    elif gViewMode == 2:
        targetPoint = (gMainTrans @ np.array([0.,0.,0.,1.]))[:3]
        eyePoint = targetPoint + np.array([10.,10.,10.])
        gluLookAt(*eyePoint, *targetPoint, 0, 1, 0)


    drawGrid()

    # Lighting and Shading is used.
    glEnable(GL_LIGHTING)

    glEnable(GL_LIGHT5)
    glEnable(GL_LIGHT6)
    glEnable(GL_NORMALIZE)

    glLightfv(GL_LIGHT5, GL_POSITION, (1., -1., -.5, 0.))
    glLightfv(GL_LIGHT6, GL_POSITION, (np.sin(t), 1., np.cos(t), 0.))

    glLightfv(GL_LIGHT5, GL_AMBIENT, (.1, .1, .1, 1.))
    glLightfv(GL_LIGHT6, GL_AMBIENT, (.1, .1, .1, 1.))

    glLightfv(GL_LIGHT5, GL_DIFFUSE, (1., 1., 1., 1.))
    glLightfv(GL_LIGHT6, GL_DIFFUSE, (1., 1., 1., 1.))

    glLightfv(GL_LIGHT5, GL_SPECULAR, (1., 1., 1., 1.))
    glLightfv(GL_LIGHT6, GL_SPECULAR, (1., 1., 1., 1.))


    # main object
    if gViewMode != 1:

        glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.392156862745098, 0.584313725490196, 0.929411764705882, 1.))

        glPushMatrix()
        glMultMatrixf(gMainTrans.T)

        # Body
        glPushMatrix()
        glScalef(1,2,.5)
        drawCube()
        glPopMatrix()

        # head
        glPushMatrix()
        glTranslatef(0,3,0)
        drawSphere()
        glPopMatrix()

        # left arm
        glPushMatrix()
        glTranslatef(1.25, 1.5, 0)
        glRotatef(30*np.sin(5*t), 1, 0, 0)
        glTranslatef(0., -1., 0)

        # draw left arm
        glPushMatrix()
        glScalef(0.25, 1, 0.25)
        drawCube()
        glPopMatrix()
        # end draw

        # left hand
        glPushMatrix()
        glTranslatef(0., -1.25, 0.)
        glScalef(0.25, 0.25, 0.25)
        drawSphere()
        glPopMatrix()

        # end of left arm
        glPopMatrix()

        # right arm
        glPushMatrix()
        glTranslatef(-1.25, 1.5, 0)
        glRotatef(-30*np.sin(5*t), 1, 0, 0)
        glTranslatef(0., -1., 0)
        # draw right arm
        glPushMatrix()
        glScalef(0.25, 1, 0.25)
        drawCube()
        glPopMatrix()
        # end draw

        # right hand
        glPushMatrix()
        glTranslatef(0., -1.25, 0.)
        glScalef(0.25, 0.25, 0.25)
        drawSphere()
        glPopMatrix()

        # end of right arm
        glPopMatrix()


        # left leg
        glPushMatrix()
        glTranslatef(.5, -2., 0)
        glRotatef(-30*np.sin(5*t), 1, 0, 0)
        glTranslatef(0., -1., 0)

        # draw leg
        glPushMatrix()
        glScalef(.25, 1., .25)
        drawCube()
        glPopMatrix()


        # left foot
        glPushMatrix()
        glTranslatef(0., -1.125, 0.25)
        glScalef(0.25, 0.125, 0.5)
        drawCube()
        glPopMatrix()

        # end of left leg
        glPopMatrix()


        # right leg
        glPushMatrix()
        glTranslatef(-.5, -2., 0)
        glRotatef(30*np.sin(5*t), 1, 0, 0)
        glTranslatef(0., -1., 0)

        # draw leg
        glPushMatrix()
        glScalef(.25, 1., .25)
        drawCube()
        glPopMatrix()


        # right foot
        glPushMatrix()
        glTranslatef(0., -1.125, 0.25)
        glScalef(0.25, 0.125, 0.5)
        drawCube()
        glPopMatrix()

        # end of right leg
        glPopMatrix()

        # end of main object
        glPopMatrix()

    # rest objects

    # dog
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.729411764705882, 0.333333333333333, 0.827450980392157, 1.))

    if np.linalg.norm(gDogCurrPos - gMainTrans[:3,3]) > 10.:
        vec = (gDogCurrPos - gMainTrans[:3,3]) / np.linalg.norm(gDogCurrPos - gMainTrans[:3,3])
        vec *= 10.
        gDogCurrPos = gMainTrans[:3,3] + vec

    # body
    glPushMatrix()
    glTranslatef(*gDogCurrPos)

    # draw body
    glPushMatrix()
    glScalef(0.5, 0.5, 1.)
    drawCube()
    glPopMatrix()


    # head
    glPushMatrix()
    glTranslatef(0., 1.175, .75)
    glScalef(.675, .675, .675)
    drawSphere()
    glPopMatrix()

    # front left leg
    glPushMatrix()
    glTranslatef(.25, -.5, .7)
    glRotatef(30*np.sin(20*t), 1, 0, 0)
    glTranslatef(0., -.5, 0.)
    glScalef(.125, .5, .125)
    drawCube()
    glPopMatrix()

    # front right leg
    glPushMatrix()
    glTranslatef(-.25, -.5, .7)
    glRotatef(-30*np.sin(20*t), 1, 0, 0)
    glTranslatef(0., -.5, 0.)
    glScalef(.125, .5, .125)
    drawCube()
    glPopMatrix()

    # back left leg
    glPushMatrix()
    glTranslatef(.25, -.5, -.5)
    glRotatef(30*np.sin(20*t), 1, 0, 0)
    glTranslatef(0., -.5, 0.)
    glScalef(.125, .5, .125)
    drawCube()
    glPopMatrix()

    # back right leg
    glPushMatrix()
    glTranslatef(-.25, -.5, -.5)
    glRotatef(-30*np.sin(20*t), 1, 0, 0)
    glTranslatef(0., -.5, 0.)
    glScalef(.125, .5, .125)
    drawCube()
    glPopMatrix()

    # end of body
    glPopMatrix()

    # end of dog
    glPopMatrix()
    

    # snowman
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (1., 1., 1., 1.))

    if gSnowMode == 1:
        if t - gCollideTime < 1.:
            param = t - gCollideTime
            p0, p1, p2, p3 = gP
            gSnowPos = (-p0 + 3*p1 - 3*p2 + p3) * param**3 + (3*p0 - 6*p1 + 3*p2) * param**2 + (-3*p0 + 3*p1) * param + p0
        else:
            gSnowMode = 0
    elif np.linalg.norm(gSnowPos - gMainTrans[:3,3]) <= 5:
        movement = gMainTrans @ gRecentMove
        p0 = gSnowPos
        p3 = gSnowPos + movement[:3] * 20
        p1 = p0 * 0.75 + p3 * 0.25 + (gMainTrans @ np.array([0., 10., 0., 0.]))[:3]
        p2 = p0 * 0.25 + p3 * 0.75 + (gMainTrans @ np.array([0., 10., 0., 0.]))[:3]
        gP = (p0, p1, p2, p3)
        gCollideTime = t
        gSnowMode = 1

    glTranslatef(*gSnowPos)

    # draw body
    glPushMatrix()
    glScalef(2., 2., 2.)
    drawSphere()
    # end draw
    glPopMatrix()

    # head
    glPushMatrix()

    glTranslatef(0., 3., 0.)
    glScalef(1.5, 1.5, 1.5)
    drawSphere()

    # end of head
    glPopMatrix()

    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, (0.545098039215686, 0.270588235294118, 0.074509803921569, 1.))
    # left arm
    glPushMatrix()
    glRotatef(45, 0, 0, 1)
    glTranslatef(0., 2., 0.)
    glRotatef(15*np.sin(5*t), 0, 0, -1)
    glTranslatef(0., 1., 0.)
    glScalef(.1, 1., .1)
    drawCube()
    # end of left arm
    glPopMatrix()

    # right arm
    glPushMatrix()
    glRotatef(45, 0, 0, -1)
    glTranslatef(0., 2., 0.)
    glRotatef(15*np.sin(5*t), 0, 0, 1)
    glTranslatef(0., 1., 0.)
    glScalef(.1, 1., .1)
    drawCube()
    # end of right arm
    glPopMatrix()

    # end of snowman
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

        t = glfw.get_time()

        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()
