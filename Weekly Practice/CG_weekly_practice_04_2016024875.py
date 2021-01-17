import glfw
from OpenGL.GL import *
import numpy as np

gComposedM = np.identity(3)

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

def key_callback(window, key, scancode, action, mods):
	# Warning: DO NOT USE OpenGL transformation functions.

	global gComposedM
	newM = np.identity(3)

	# global coord. : gComposedM = newM @ gComposedM
	#  local coord. : gComposedM = gComposedM @ newM

	if action == glfw.PRESS or action == glfw.REPEAT:
		# translate -0.1 or 0.1 in x direction w.r.t. global coordinate
		if key == glfw.KEY_Q:
			newM[0, 2] = -.1
			gComposedM = newM @ gComposedM

		elif key == glfw.KEY_E:
			newM[0, 2] = .1
			gComposedM = newM @ gComposedM

		# rotate by 10 degrees ccw or cw w.r.t. local coordinate
		elif key == glfw.KEY_A:
			deg = np.radians(10)
			newM[:2, :2] = [[np.cos(deg), -np.sin(deg)], [np.sin(deg), np.cos(deg)]]
			gComposedM = gComposedM @ newM

		elif key == glfw.KEY_D:			
			deg = np.radians(-10)
			newM[:2, :2] = [[np.cos(deg), -np.sin(deg)], [np.sin(deg), np.cos(deg)]]
			gComposedM = gComposedM @ newM

		# reset the triangle with identity matrix
		elif key == glfw.KEY_1:
			gComposedM = np.identity(3)

		# scale by 0.9 times in x direction w.r.t. global coordinate
		elif key == glfw.KEY_W:
			newM[0, 0] = 0.9
			gComposedM = newM @ gComposedM

		# rotate by 10 degrees ccw w.r.t. global coordinate
		elif key == glfw.KEY_S:
			deg = np.radians(10)
			newM[:2, :2] = [[np.cos(deg), -np.sin(deg)], [np.sin(deg), np.cos(deg)]]
			gComposedM = newM @ gComposedM

def main():
	global gComposedM
	
	if not glfw.init():
		return
		
	window = glfw.create_window(480, 480, "GG_weekly_practice_04_2016024875", None, None)
	if not window:
		glfw.terminate()
		return
		
	glfw.set_key_callback(window, key_callback)
	glfw.make_context_current(window)
	glfw.swap_interval(1)
	
	while not glfw.window_should_close(window):
		glfw.poll_events()
	
		render(gComposedM)
		
		glfw.swap_buffers(window)
		
	glfw.terminate()

if __name__ == '__main__':
	main()
