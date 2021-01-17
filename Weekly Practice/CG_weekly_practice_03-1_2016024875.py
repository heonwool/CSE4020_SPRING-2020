import glfw
from OpenGL.GL import *
import numpy as np

PRIMITIVE_TYPE = GL_LINE_LOOP

def render(T):
	global PRIMITIVE_TYPE

	glClear(GL_COLOR_BUFFER_BIT)
	glLoadIdentity()
	
	# Draw points
	glBegin(PRIMITIVE_TYPE)
	glColor3ub(255, 255, 255)
	for i in np.linspace(0, 360, 13)[:-1]:
		glVertex2fv( (T @ np.array([np.cos(np.deg2rad(i)), np.sin(np.deg2rad(i)), 1.]))[:-1])
	glEnd()
	
def key_callback(window, key, scancode, action, mods):
	global PRIMITIVE_TYPE

	if key == glfw.KEY_1 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_POINTS
	elif key == glfw.KEY_2 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_LINES
	elif key == glfw.KEY_3 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_LINE_STRIP
	elif key == glfw.KEY_4 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_LINE_LOOP
	elif key == glfw.KEY_5 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_TRIANGLES
	elif key == glfw.KEY_6 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_TRIANGLE_STRIP
	elif key == glfw.KEY_7 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_TRIANGLE_FAN
	elif key == glfw.KEY_8 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_QUADS
	elif key == glfw.KEY_9 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_QUAD_STRIP
	elif key == glfw.KEY_0 and action == glfw.PRESS:
		PRIMITIVE_TYPE = GL_POLYGON
	else:
		return

def main():
	if not glfw.init():
		return
		
	window = glfw.create_window(480, 480, "GG_weekly_practice_03-1_2016024875", None, None)
	if not window:
		glfw.terminate()
		return
		
	glfw.set_key_callback(window, key_callback)
	glfw.make_context_current(window)
	
	glfw.swap_interval(1)
	
	while not glfw.window_should_close(window):
		glfw.poll_events()

		T = np.identity(3)
		render(T)
		
		glfw.swap_buffers(window)
		
	glfw.terminate()

if __name__ == '__main__':
	main()
