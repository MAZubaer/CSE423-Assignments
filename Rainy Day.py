#TASK01

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import random

# Global variables
sky_color = (0, 0, 0)  
color_change_rate = 0.01
direction = 0
target_direction = 0
drop_length = 40
speed = 2.5
total_drops = 115
rain_drops = []
day_mode = True  # Track day or night transition
transition_active = False  # Track if transition is in progress

window_width = 500
window_height = 500

button_state = None  # To track mouse button state
direction_smoothness = 0.05  # The speed of smooth transition

def draw_lines(x, y, a, b, width=5):
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x, y)
    glVertex2f(a, b)
    glEnd()

def draw_triangles(a, b, c, d, e, f):
    glBegin(GL_TRIANGLES)
    glVertex2f(a, b)
    glVertex2f(c, d)
    glVertex2f(e, f)
    glEnd()

def draw_rectangle(a, b, height, width):
    draw_triangles(a, b, a+width, b, a, b+height)
    draw_triangles(a+width, b, a, b+height, a+width, b+height)

def draw_triangle_single_point(x, y, base=20, height=80):
    c = x + base
    d = y
    e = x + (base // 2)
    f = y + height
    draw_triangles(x, y, c, d, e, f)

def iterate():
    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_width, 0.0, window_height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    global sky_color
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(sky_color[0], sky_color[1], sky_color[2], 1.0)
    glLoadIdentity()
    iterate()
    
    scale_x = window_width / 500
    scale_y = window_height / 500

    # Draw ground
    for i in range(int(270 * scale_y)):
        glColor3f(0.478, 0.357, 0.059)
        draw_lines(0, i, window_width, i, width=10)

    for i in range(int(270 * scale_y), int(350 * scale_y)):
        glColor3f(0.294, 0.180, 0.086)
        draw_lines(0, i, window_width, i, width=10)

    glColor3f(0.0, 0.39, 0.0)
    for i in range(0, window_width, int(50 * scale_x)):
        draw_triangle_single_point(i, 270 * scale_y, base=50 * scale_x, height=80 * scale_y)

    # House body
    glColor3f(0.960, 0.870, 0.700)
    draw_rectangle(100 * scale_x, 180 * scale_y, height=120 * scale_y, width=300 * scale_x)

    # Roof
    glColor3f(0.545, 0.271, 0.075)  # Roof color
    draw_triangles(90 * scale_x, 300 * scale_y, 410 * scale_x, 300 * scale_y, 250 * scale_x, 390 * scale_y)

    # Door
    glColor3f(0.290, 0.000, 0.510)
    draw_rectangle(240 * scale_x, 180 * scale_y, height=80 * scale_y, width=40 * scale_x)

    # Windows
    glColor3f(0.200, 0.100, 0.050)
    edge_distance = 40
    draw_rectangle(140 * scale_x, 220 * scale_y, height=40 * scale_y, width=30 * scale_x)
    draw_rectangle(330 * scale_x, 220 * scale_y, height=40 * scale_y, width=30 * scale_x)

    # Rain effect
    display_rain()

    glutSwapBuffers()

def mouse_handler(button, state, x, y):
    global button_state, target_direction
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        # Left-click: Bend the rain to the left
        button_state = 'left'
        target_direction = -1
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Right-click: Bend the rain to the right
        button_state = 'right'
        target_direction = 1
    elif button == GLUT_LEFT_BUTTON and state == GLUT_UP:
        button_state = None
        target_direction = 0  
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_UP:
        button_state = None
        target_direction = 0

def smooth_direction():
    global direction, target_direction
    if direction != target_direction:
        direction += (target_direction - direction) * direction_smoothness

def display_rain():
    global rain_drops, total_drops, direction, drop_length
    glColor3f(0.5, 0.5, 1.0)
    glLineWidth(.5)
    for i in range(len(rain_drops)):
        x, y = rain_drops[i]
        draw_lines(x, y, x + drop_length * direction, y - drop_length)

def update_position():
    global rain_drops, speed, direction
    for i in range(len(rain_drops)):
        x, y = rain_drops[i]
        x += speed * direction
        y -= speed

        if y <= 0:
            y += window_height
        if x > window_width:
            x %= window_width
        if x < 0:
            x += window_width

        rain_drops[i] = (x, y)

def updater():
    global transition_active
    smooth_direction()  # Smoothly transition the direction of the rain
    update_position()
    if transition_active:
        transition_background()
    glutPostRedisplay()

def transition_background():
    global sky_color, day_mode, transition_active
    r, g, b = sky_color

    if day_mode:  # Transition to day
        r = min(1.0, r + color_change_rate)
        g = min(1.0, g + color_change_rate)
        b = min(1.0, b + color_change_rate)
    else:  # Transition to night
        r = max(0.0, r - color_change_rate)
        g = max(0.0, g - color_change_rate)
        b = max(0.0, b - color_change_rate)

    sky_color = (r, g, b)
    
    if sky_color == (1.0, 1.0, 1.0) or sky_color == (0.0, 0.0, 0.0):
        transition_active = False

def keyboard_handler(key, x, y):
    global day_mode, transition_active

    if key == b'd':  # Transition to day
        day_mode = True
        transition_active = True  
    elif key == b'n':  # Transition to night
        day_mode = False
        transition_active = True

def reshape_handler(width, height):
    global window_width, window_height, rain_drops, total_drops
    window_width = width
    window_height = height

    # Update the number of raindrops based on window size
    total_drops = int(window_width * window_height / 10000)  # Increase raindrop density for more rain
    rain_drops = [(random.randint(0, window_width), random.randint(0, window_height)) for _ in range(total_drops)]

    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, window_width, 0.0, window_height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(900, 700)
glutInitWindowPosition(0, 0)
glutCreateWindow(b"Interactive Rainy house with smooth rain bending")
glutDisplayFunc(showScreen)

# Animate
glutIdleFunc(updater)

# Keyboard and Mouse control
glutKeyboardFunc(keyboard_handler)
glutMouseFunc(mouse_handler)
glutReshapeFunc(reshape_handler)

glutMainLoop()





#TASK02
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

W_Width, W_Height = 1300, 700
points = [((800, 400), (1, 1), (0.0, 0.0, 0.8))]
speed = 0.1
black_mode = False
frozen = False

def draw_points(x, y):
    glPointSize(6)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_lines(x, y, a, b):
    glLineWidth(5)
    glBegin(GL_LINES)
    glVertex2f(x, y)
    glVertex2f(a, b)
    glEnd()

def draw_triangles(a, b, c, d, e, f):
    glBegin(GL_TRIANGLES)
    glVertex2f(a, b)
    glVertex2f(c, d)
    glVertex2f(e, f)
    glEnd()

def iterate():
    glViewport(0, 0, W_Width, W_Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, W_Width, 0.0, W_Height, 0.0, 1.0) 
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    for point in points:
        x, y = point[0]
        original_color = point[2]
        
        if black_mode:
            glColor3f(0, 0, 0)  
        else:
            glColor3f(original_color[0], original_color[1], original_color[2]) 
        
        draw_points(x, y)

    glutSwapBuffers()

def updater():
    if frozen:
        return
    global points, speed
    for i in range(len(points)):
        point = points[i]

        x, y = point[0]
        x_dir, y_dir = point[1]
        r, g, b = point[2]

        x += x_dir * speed
        y += y_dir * speed

        if x <= 0 or x >= W_Width:
            x_dir *= -1
        if y <= 0 or y >= W_Height:
            y_dir *= -1

        points[i] = ((x, y), (x_dir, y_dir), (r, g, b))

    glutPostRedisplay()

def mouse_handler(button, state, x, y):
    global black_mode, points
    if frozen:
        return
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            black_mode = not black_mode  
    elif button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            c_x, c_y = convert_coordinate(x, y)
            x_dir = 1 if random.randint(0, 1000) % 2 else -1
            y_dir = 1 if random.randint(0, 1000) % 2 else -1
            r = random.random()
            g = random.random()
            b = random.random()
            points.append(((c_x, c_y), (x_dir, y_dir), (r, g, b)))

def special_key_handler(key, x, y):
    if frozen:
        return
    global speed
    if key == GLUT_KEY_UP:
        speed *= 2
    if key == GLUT_KEY_DOWN:
        speed /= 2

def keyboard_handler(key, x, y):
    global frozen
    if key == b' ':
        frozen = not frozen

def convert_coordinate(x, y):
    global W_Width, W_Height
    return x, W_Height - y  # Keep the x-coordinate the same, flip the y-coordinate

def reshape_handler(width, height):
    global W_Width, W_Height
    W_Width = width
    W_Height = height
    glViewport(0, 0, W_Width, W_Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, W_Width, 0.0, W_Height, 0.0, 1.0)  # Dynamically adjust the projection
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(1300, 700)
glutInitWindowPosition(0, 0)
glutCreateWindow(b"Points & Dynamics")
glutDisplayFunc(showScreen)

# Animate
glutIdleFunc(updater)

# Mouse and Keyboard control
glutMouseFunc(mouse_handler)
glutSpecialFunc(special_key_handler)
glutKeyboardFunc(keyboard_handler)

glutReshapeFunc(reshape_handler)

glutMainLoop()
"""