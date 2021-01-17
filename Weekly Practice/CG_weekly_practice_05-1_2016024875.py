import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def drawUnitCube():
    glBegin(GL_QUADS)

    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f( 0.5, 0.5, 0.5)

    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f( 0.5,-0.5,-0.5)

    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)

    glVertex3f( 0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5,-0.5)

    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5,-0.5)
    glVertex3f(-0.5,-0.5,-0.5)
    glVertex3f(-0.5,-0.5, 0.5)

    glVertex3f( 0.5, 0.5,-0.5)
    glVertex3f( 0.5, 0.5, 0.5)
    glVertex3f( 0.5,-0.5, 0.5)
    glVertex3f( 0.5,-0.5,-0.5)

    glEnd()

def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i,j,-k-1)
                glScalef(.5,.5,.5)
                drawUnitCube()
                glPopMatrix()

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

def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
    glLoadIdentity()

    myOrtho(-5,5, -5,5, -8,8)
    myLookAt(np.array([5,3,5]), np.array([1,1,-1]), np.array([0,1,0]))

    # Above two lines must behaves exactly same as the below two lines

    # glOrtho(-5,5, -5,5, -8,8)
    # gluLookAt(5,3,5, 1,1,-1, 0,1,0)

    drawFrame()

    glColor3ub(255, 255, 255)
    drawCubeArray()

def myOrtho(left, right, bottom, top, near, far):

    orthMatrix = np.identity(4)

    orthMatrix[0][0] = 2 / (right - left)
    orthMatrix[1][1] = 2 / (top - bottom)
    orthMatrix[2][2] = -2 / (far - near)
    orthMatrix[3] = [-(right + left) / (right - left), -(top + bottom) / (top - bottom), -(far + near) / (far - near), 1.]

    print(orthMatrix)

    glMultMatrixf(orthMatrix)

def myLookAt(eye, at, up):
    # camera located in eye point(x, y, z)
    # the target of the camera: look-at point(x, y, z)
    # camera up-vector up(x, y, z)

    # determine the forward vector and normalize it
    eyeFwd = eye - at
    eyeFwd = eyeFwd / np.sqrt( np.dot(eyeFwd, eyeFwd) )

    # determine eye-side vector and normalize it
    eyeSide = np.cross(up, eyeFwd)
    eyeSide = eyeSide / np.sqrt( np.dot(eyeSide, eyeSide) )

    # determine eye-up vector and normalize it
    eyeUp = np.cross(eyeFwd, eyeSide)
    eyeUp = eyeUp / np.sqrt( np.dot(eyeUp, eyeUp) )

    pos = np.array([-eye.dot(eyeSide), -eye.dot(eyeUp), -eye.dot(eyeFwd)])

    viewMatrix = np.array([[eyeSide[0], eyeUp[0], eyeFwd[0], 0.],
                            [eyeSide[1], eyeUp[1], eyeFwd[1], 0.],
                            [eyeSide[2], eyeUp[2], eyeFwd[2], 0.],
                            [pos[0], pos[1], pos[2], 1.]])

    glMultMatrixf(viewMatrix)

def main():
    if not glfw.init():
        return
		
    window = glfw.create_window(480, 480, "GG_weekly_practice_05-1_2016024875", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
	
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
		
    glfw.terminate()

if __name__ == "__main__":
    main()
