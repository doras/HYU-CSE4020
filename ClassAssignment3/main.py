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
gJoints = [] # name, offset, channels, channel values, children, parent
gAnimate = False
gMotionData = []
gFrameIdx = 0

def key_callback(window, key, scancode, action, mods):
    global gAnimate
    if action == glfw.PRESS:
        gAnimate = True

def drop_callback(window, paths):
    global gJoints, gAnimate, gMotionData, gFrameIdx
    f = open(paths[0], 'r')

    gJoints = []
    gAnimate = False
    gMotionData = []
    gFrameIdx = 0
    frameCount = 0
    fps = 0

    mode = None # 0 for Hierarchy, 1 for motion
    curJoint = ["", [0., 0., 0.], [], [], [], -1]
    curIdx = -1
    for line in f:
        fields = line.split()

        if len(fields) == 0:
            continue

        if fields[0] == "HIERARCHY":
            mode = 0
        elif fields[0] == "MOTION":
            mode = 1
        else:
            if mode == 0:
                if fields[0] == "OFFSET":
                    if len(fields) < 4:
                        continue
                    curJoint[1] = [float(fields[1]), float(fields[2]), float(fields[3])]
                elif fields[0] == "CHANNELS":
                    if len(fields) < 2:
                        continue
                    curJoint[2] = [x.upper()[:2] for x in fields[2:]]
                    curJoint[3] = [0.] * len(curJoint[2])
                elif fields[0] == "JOINT":
                    if curIdx < 0:
                        curIdx = len(gJoints)
                        gJoints.append(curJoint)
                    curJoint = [fields[1], [0., 0., 0.], [], [], [], curIdx]
                    curIdx = -1
                elif fields[0] == "End":
                    if curIdx < 0:
                        curIdx = len(gJoints)
                        gJoints.append(curJoint)
                    curJoint = [None, [0., 0., 0.], [], [], [], curIdx]
                    curIdx = -1
                elif fields[0] == "}":
                    if curIdx < 0:
                        gJoints.append(curJoint)
                    curIdx = curJoint[-1]
                    if curIdx < 0:
                        curJoint = ["", [0., 0., 0.], [], [], [], -1]
                    else:
                        curJoint = gJoints[curIdx]
                elif fields[0] == "ROOT":
                    curJoint = [fields[1], [0., 0., 0.], [], [], [], -1]
                    curIdx = -1
                    parentIdx = -1
            else:
                # MOTION mode
                if fields[0] == "Frames:":
                    frameCount = int(fields[1])
                elif fields[0] == "Frame" and fields[1] == "Time:":
                    fps = 1 / float(fields[2])
                else:
                    gMotionData.append(line)


    numJoints = 0
    for i, joint in enumerate(gJoints):
        numJoints += joint[0] is not None # counting except end site

        if joint[-1] < 0:
            continue
        
        gJoints[joint[-1]][-2].append(i)
    
    if len(gJoints) > 0:
        gJoints[0][1] = [0.] * 3 # ignore offset of root


    print( 'File name: %s' % f.name, 'Number of frames: %d' % frameCount, 
            'FPS: %f' % fps, 
            'Number of joints: %d' % numJoints, sep='\n')
    print("List of all joint names: [")

    for joint in gJoints:
        if joint[0] is not None:
            print(joint[0])
    print("]")

    f.close()

    # for i, joint in enumerate(gJoints):
    #     print(i, joint)



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
    global gAzimuth, gElevation, gDistance, gAt, gAnimate, gMotionData, gFrameIdx, gJoints

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

    gChannels = []

    if len(gJoints) == 0:
        return

    glColor3ub(128, 128, 255)
    if not gAnimate:
        # render t-pose
        renderJoint(0)
    else:
        # animate
        values = gMotionData[gFrameIdx].split()
        channelIndex = 0
        for joint in gJoints:
            if joint[0] is None:
                continue
            for i in range(len(joint[3])):
                joint[3][i] = float(values[channelIndex])
                channelIndex += 1
        gFrameIdx = (gFrameIdx + 1) % len(gMotionData)

        renderJoint(0)
            


def renderJoint(idx):
    global gJoints

    if len(gJoints) < idx + 1:
        return

    curJoint = gJoints[idx]

    if curJoint[-1] >= 0:
        glBegin(GL_LINES)
        glVertex3f(0,0,0)
        glVertex3fv(curJoint[1])
        glEnd()
    glPushMatrix()

    glTranslatef(*curJoint[1]) # translate for offset
    
    for i, chan in enumerate(curJoint[2]):
        if chan == "XR":
            glRotatef(curJoint[3][i], 1, 0, 0)
        elif chan == "YR":
            glRotatef(curJoint[3][i], 0, 1, 0)
        elif chan == "ZR":
            glRotatef(curJoint[3][i], 0, 0, 1)
        elif chan == "XP":
            glTranslatef(curJoint[3][i], 0, 0)
        elif chan == "YP":
            glTranslatef(0, curJoint[3][i], 0)
        elif chan == "ZP":
            glTranslatef(0, 0, curJoint[3][i])

    for childIdx in curJoint[-2]:
        renderJoint(childIdx)

    glPopMatrix()


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
