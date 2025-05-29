from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

import math
import random
import time

# Display Settings
DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 800
ARENA_SIZE = 600
view_angle = 120

# Viewpoint variables
view_position = [0, 600, 600]
view_rotation = 0
view_distance = 600
view_elevation = 600

# Game states
first_person_view = False
enable_cheats = False
xray_vision = False
game_ended = False

# Character variables
character_position = [0, 0, 0]
character_rotation = 0
movement_velocity = 10
rotation_velocity = 5
health_points = 5
game_points = 0

# Weapon variables
weapon_cooldown = 0.3
active_projectiles = []
failed_shots = 0
max_misses = 10
projectile_velocity = 1.3

# Cheat system variables
last_shot_time = 0
cheat_delay = 0.7

# Enemy variables
enemies = []
enemy_scale = 1.0
pulse_timer = 0
enemy_speed = 0.025
max_enemies = 5

def display_text(x_pos, y_pos, text_string, font_style = GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, DISPLAY_WIDTH, 0, DISPLAY_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x_pos, y_pos)
    for character in text_string:
        glutBitmapCharacter(font_style, ord(character))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def render_arena():
    glBegin(GL_QUADS)
    
    for i in range(-ARENA_SIZE, ARENA_SIZE + 1, 100):
        for j in range(-ARENA_SIZE, ARENA_SIZE + 1, 100):
            if (i + j) % 200 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)            
            
            glVertex3f(i, j, 0)  # Bottom left
            glVertex3f(i + 100, j, 0) # Bottom right
            glVertex3f(i + 100, j + 100, 0) # Top right
            glVertex3f(i, j + 100, 0)  # Top left

    # Boundary walls
    
    # Left Wall
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(-ARENA_SIZE, -ARENA_SIZE, 0)    # Bottom left
    glVertex3f(-ARENA_SIZE, ARENA_SIZE+100, 0)   # Top left
    glVertex3f(-ARENA_SIZE, ARENA_SIZE+100, 100)   # Top right
    glVertex3f(-ARENA_SIZE, -ARENA_SIZE, 100)   # Bottom right
    
    # Right Wall
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(ARENA_SIZE+100, -ARENA_SIZE, 0)  # Bottom left
    glVertex3f(ARENA_SIZE+100, ARENA_SIZE+100, 0)   # Top left
    glVertex3f(ARENA_SIZE+100, ARENA_SIZE+100, 100)  # Top right
    glVertex3f(ARENA_SIZE+100, -ARENA_SIZE, 100)  # Bottom right
    
    # Bottom Wall
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(-ARENA_SIZE, ARENA_SIZE+100, 0)   # Bottom left
    glVertex3f(ARENA_SIZE+100, ARENA_SIZE+100, 0)  # Top left
    glVertex3f(ARENA_SIZE+100, ARENA_SIZE+100, 100)   # Top right
    glVertex3f(-ARENA_SIZE, ARENA_SIZE+100, 100)    # Bottom right
    
    # Top Wall
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(-ARENA_SIZE, -ARENA_SIZE, 0)    # Bottom left
    glVertex3f(ARENA_SIZE+100, -ARENA_SIZE, 0)   # Top left
    glVertex3f(ARENA_SIZE+100, -ARENA_SIZE, 100)  # Top right
    glVertex3f(-ARENA_SIZE, -ARENA_SIZE, 100)  # Bottom right
    
    glEnd()

def configure_viewpoint():
    global view_position, view_rotation, view_distance, view_elevation, view_angle
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(view_angle, float(DISPLAY_WIDTH) / float(DISPLAY_HEIGHT), 0.1, 1500)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if first_person_view:
        rotation_rad = math.radians(character_rotation)
        
        # First-person view at eye level
        eye_x = character_position[0] + weapon_tip[0] / 2 * math.sin(rotation_rad) - weapon_tip[1] * math.cos(rotation_rad)
        eye_y = character_position[1] - weapon_tip[0] / 2 * math.cos(rotation_rad) - weapon_tip[1] * math.sin(rotation_rad)
        eye_z = character_position[2] + weapon_tip[2] + 20
        
        if xray_vision:
            target_x = eye_x + math.sin(rotation_rad) * 100
            target_y = eye_y + math.cos(rotation_rad) * 100
            target_z = eye_z
        
        else:    
            target_x = eye_x - math.sin(-rotation_rad) * 100
            target_y = eye_y - math.cos(-rotation_rad) * 100
            target_z = eye_z
        
        gluLookAt(eye_x, eye_y, eye_z,
                  target_x, target_y, target_z,
                  0, 0, 1)
    else:
        rotation_rad = math.radians(view_rotation)
        
        x = view_distance * math.sin(rotation_rad)
        y = view_distance * math.cos(rotation_rad)
        z = view_elevation
        
        gluLookAt(x, y, z,  # Camera position
                0, 0, 0,   # Look-at target
                0, 0, 1) # Up vector (z-axis)

def render_character():
    global weapon_tip
        
    glPushMatrix()
    
    # Character Position
    glTranslatef(*character_position)
    glRotatef(character_rotation, 0, 0, 1) # Rotate around z-axis
    
    if game_ended:
        glRotatef(-90, 1, 0, 0)
    
    # Right Leg
    glTranslatef(0, 0, 0)  # At (0, 0, 0)
    glColor3f(0.0, 0.0, 1.0)
    gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Left Leg
    glTranslatef(30, 0, 0)  # At (30, 0, 0)
    glColor3f(0.0, 0.0, 1.0)
    gluCylinder(gluNewQuadric(), 5, 10, 50, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Body
    glTranslatef(-15, 0, 50+20)  # At (15, 0, 70)
    glColor3f(85/255, 108/255, 47/255)
    glutSolidCube(40)
    
    # Head
    glTranslatef(0, 0, 40)   # At (15, 0, 110)
    glColor3f(0.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 20, 10, 10) # radius, slices, stacks
    
    # Left Arm
    glTranslatef(20, -60, -30)  # At (35, -60, 80)
    glRotatef(-90, 1, 0, 0)      
    glColor3f(254/255, 223/255, 188/255)
    gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)   # quadric, base radius, top radius, height, slices, stacks
    
    # Right Arm
    glRotatef(90, 1, 0, 0)   # Reset rotation
    glTranslatef(-40, 0, 0)   # At (-5, -60, 80)
    glRotatef(-90, 1, 0, 0)     
    glColor3f(254/255, 223/255, 188/255)
    gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    # Weapon
    glRotatef(90, 1, 0, 0)   # Reset rotation
    glTranslatef(20, -40, 0)  # At (15, -100, 80)
    glRotatef(-90, 1, 0, 0)     
    glColor3f(192/255, 192/255, 192/255)
    gluCylinder(gluNewQuadric(), 1, 10, 80, 10, 10) # quadric, base radius, top radius, height, slices, stacks
    
    glPopMatrix()
    
    weapon_tip = [30, 15, 80] # y = 15 for Right Leg at Center
    
def render_projectile(x_pos, y_pos, z_pos):
    glPushMatrix()
    
    glTranslatef(x_pos, y_pos, z_pos)  # Weapon Point
    glRotatef(-90, 1, 0, 0)     
    glColor3f(1, 0, 0)
    glutSolidCube(10)
    
    glPopMatrix()

def shoot_projectile():
    global active_projectiles, projectile_velocity, character_position, character_rotation, weapon_tip
    
    if first_person_view:
        rotation_rad = math.radians(character_rotation + 90 / 2)
        
        x_pos = character_position[0] + weapon_tip[0] * math.sin(rotation_rad) - weapon_tip[1] * math.cos(rotation_rad)
        y_pos = character_position[1] - weapon_tip[0] * math.cos(rotation_rad) - weapon_tip[1] * math.sin(rotation_rad)
        z_pos = character_position[2] + weapon_tip[2]

        new_projectile = [x_pos, y_pos, z_pos, character_rotation]
    else:
        rotation_rad = math.radians(character_rotation - 90)
        
        offset_x = weapon_tip[0] * math.cos(rotation_rad) - weapon_tip[1] * math.sin(rotation_rad)
        offset_y = weapon_tip[0] * math.sin(rotation_rad) + weapon_tip[1] * math.cos(rotation_rad)
        
        x_pos = character_position[0] + offset_x
        y_pos = character_position[1] + offset_y
        z_pos = character_position[2] + weapon_tip[2]

        new_projectile = [x_pos, y_pos, z_pos, character_rotation]
        
    active_projectiles.append(new_projectile)
    
def update_projectiles():
    global active_projectiles, failed_shots, enemies, projectile_velocity, max_misses, game_ended
    
    to_remove = []
    
    for projectile in active_projectiles:
        rotation_rad = math.radians(projectile[3] - 90)
        
        projectile[0] += projectile_velocity * math.cos(rotation_rad)
        projectile[1] += projectile_velocity * math.sin(rotation_rad)
        
        if (projectile[0] > ARENA_SIZE + 100
        or projectile[0] < -ARENA_SIZE 
        or projectile[1] > ARENA_SIZE + 100
        or projectile[1] < -ARENA_SIZE):
            to_remove.append(projectile)
            failed_shots += 1
            print(f"Projectile missed: {failed_shots}")
    
    for projectile in to_remove:
        active_projectiles.remove(projectile)

    if failed_shots >= max_misses:
        game_ended = True
    
def check_collisions(projectiles, targets):
    global game_points, active_projectiles, enemies
    
    for projectile in projectiles:
        projectile_x = projectile[0]
        projectile_y = projectile[1]
        
        for target in targets:
            target_x = target[0]
            target_y = target[1]
            
            dx = projectile_x - target_x
            dy = projectile_y - target_y
            distance = (dx**2 + dy**2) ** 0.5
            
            if distance < 60:
                game_points += 1
                projectiles.remove(projectile)
                targets.remove(target)
                spawn_enemies(1)
                break
        
def spawn_enemies(num_enemies = max_enemies):
    global enemies, max_enemies
    for i in range(num_enemies):
        x_pos = random.uniform(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        y_pos = random.uniform(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        z_pos = 0
        while abs(x_pos) < character_position[0] + 200:
            x_pos = random.uniform(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        while abs(y_pos) < character_position[1] + 200:
            y_pos = random.uniform(-ARENA_SIZE + 100, ARENA_SIZE - 100)
        enemies.append([x_pos, y_pos, z_pos])
    
def render_enemy(x_pos, y_pos, z_pos):
    glPushMatrix()
    
    glTranslatef(x_pos, y_pos, z_pos + 35)
    glColor3f(1, 0, 0)
    gluSphere(gluNewQuadric(), 35 * enemy_scale, 10, 10) # quadric, radius, slices, stacks

    glTranslatef(0, 0, 50)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 15 * enemy_scale, 10, 10) # quadric, radius, slices, stacks
    glPopMatrix()

def move_enemies():
    global enemies, enemy_speed, game_ended, health_points
    
    for enemy in enemies:
        dx = character_position[0] - enemy[0]
        dy = character_position[1] - enemy[1]
        distance = (dx**2 + dy**2) ** 0.5
        
        # Health reduction
        if distance < 50:
            health_points -= 1
            print(f"Remaining Health: {health_points}")
            
            if health_points <= 0:
                game_ended = True
                enemies.clear()
                active_projectiles.clear()
                break
            
            enemies.remove(enemy)
            spawn_enemies(1)
        
        else:
            angle = math.atan2(dy, dx)
            enemy[0] += enemy_speed * math.cos(angle)
            enemy[1] += enemy_speed * math.sin(angle)
            
def pulse_enemies():
    global pulse_timer, enemy_scale
    
    pulse_timer += 0.01
    enemy_scale = 1.0 + 0.5 * math.sin(pulse_timer)
  
def find_nearest_enemy():
    distances = []
    
    for enemy in enemies:
        dx = character_position[0] - enemy[0]
        dy = character_position[1] - enemy[1]
        distance = (dx**2 + dy**2) ** 0.5
        distances.append(distance)
    
    min_distance = min(distances)
    closest_index = distances.index(min_distance)
    closest_enemy = enemies[closest_index]
    
    return closest_enemy

def get_enemy_angles():
    angles = []
    
    for enemy in enemies:
        dx = character_position[0] - enemy[0]
        dy = character_position[1] - enemy[1]
        
        angle = math.degrees(math.atan2(dy, dx)) - 90
        angle = (angle + 360) % 360
        
        angles.append(angle)
    return angles

def auto_aim_rotation():
    # Using get_enemy_angles()
    
    global character_position, character_rotation, active_projectiles, game_ended, last_shot_time, cheat_delay
    
    if not enemies:
        return
    
    enemy_angles = get_enemy_angles()
    
    character_rotation = (character_rotation + rotation_velocity / 10) % 360
    
    for angle in enemy_angles:
        angle_diff = abs((character_rotation - angle + 540) % 360 - 180)
        if angle_diff < 2: # Within 5 degrees threshold
            current_time = time.time()
            if current_time - last_shot_time > cheat_delay:
                shoot_projectile()
                last_shot_time = current_time
            break

def auto_aim_target():
    # Using find_nearest_enemy()
    global character_position, character_rotation, active_projectiles, game_ended, last_shot_time, cheat_delay
    
    if not enemies:
        return
    
    closest_enemy = find_nearest_enemy()
    
    dx = closest_enemy[0] - character_position[0]
    dy = closest_enemy[1] - character_position[1]
    
    enemy_angle = math.degrees(math.atan2(dy, dx)) + 90
    enemy_angle = (enemy_angle + 360) % 360
    current_angle = character_rotation % 360
    
    angle_diff = (enemy_angle - current_angle + 540) % 360 - 180
    
    if abs(angle_diff) > rotation_velocity:
        if angle_diff > 0:
            character_rotation += rotation_velocity / 10
        else:
            character_rotation -= rotation_velocity / 10
    else:
        character_rotation = enemy_angle

        # Fire if cooldown is over
        current_time = time.time()
        if current_time - last_shot_time > cheat_delay:
            shoot_projectile()
            last_shot_time = current_time
        
def handle_mouse_click(button, state, x_pos, y_pos):
    global game_ended, first_person_view, rotation_velocity
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_ended:
            shoot_projectile()
            print("Projectile Fired!")
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if not game_ended:
            # Toggle first-person view
            first_person_view = not first_person_view
            if first_person_view:
                rotation_velocity = 2.5
            else:
                rotation_velocity = 5

def handle_key_press(key, x_pos, y_pos):
    global character_rotation, movement_velocity, rotation_velocity, character_position, active_projectiles, failed_shots
    global game_ended, health_points, game_points, enemies, enable_cheats, xray_vision, first_person_view
    
    x = character_position[0]
    y = character_position[1]
    z = character_position[2]
    
    if not game_ended:
        if key == b'w':
            # Character moves forward
            x -= movement_velocity * math.sin(math.radians(-character_rotation))
            y -= movement_velocity * math.cos(math.radians(character_rotation))
            
            if x < -ARENA_SIZE:
                x = -ARENA_SIZE
            if x > ARENA_SIZE + 100:
                x = ARENA_SIZE + 100
            if y < -ARENA_SIZE:
                y = -ARENA_SIZE
            if y > ARENA_SIZE + 100:
                y = ARENA_SIZE + 100
        
        if key == b's':
            # Character moves backward
            x += movement_velocity * math.sin(math.radians(-character_rotation))
            y += movement_velocity * math.cos(math.radians(character_rotation))
            
            if x < -ARENA_SIZE:
                x = -ARENA_SIZE
            if x > ARENA_SIZE + 100:
                x = ARENA_SIZE + 100
            if y < -ARENA_SIZE:
                y = -ARENA_SIZE
            if y > ARENA_SIZE + 100:
                y = ARENA_SIZE + 100
        
        if key == b'a':
            # Character rotates left
            character_rotation += rotation_velocity
        
        if key == b'd':
            # Character rotates right
            character_rotation -= rotation_velocity
        
        if key == b'c':
            # Toggle cheat mode
            enable_cheats = not enable_cheats
        
        if key == b'v':
            if first_person_view and enable_cheats:
                # Toggle xray vision
                xray_vision = not xray_vision
    
    if key == b'r':
        # Restart the game
        game_ended = False
        first_person_view = False
        enable_cheats = False
        xray_vision = False
        view_position = [0, 600, 600]
        character_position = [0, 0, 0]
        character_rotation = 0
        health_points = 5
        game_points = 0
        failed_shots = 0
        active_projectiles.clear()
        enemies.clear()
        spawn_enemies()
    
    character_position = [x, y, z]
    
def handle_special_keys(key, x_pos, y_pos):
    global view_rotation, view_distance, view_elevation
    
    if key == GLUT_KEY_UP:
        view_elevation -= 10
        view_distance -= 10

    if key == GLUT_KEY_DOWN:
        view_elevation += 10
        view_distance += 10

    if key == GLUT_KEY_LEFT:
        view_rotation -= 5

    if key == GLUT_KEY_RIGHT:
        view_rotation += 5

def render_scene():
    global game_ended, health_points, game_points, failed_shots
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    configure_viewpoint()
    render_arena()
    render_character()
    
    if not game_ended:
        if enable_cheats:
            auto_aim_rotation()
            # auto_aim_target()
        
        for enemy in enemies:
            render_enemy(*enemy)
        
        for projectile in active_projectiles:
            render_projectile(projectile[0], projectile[1], projectile[2])

        display_text(10, 770, f"Health Remaining: {health_points}")
        display_text(10, 740, f"Score: {game_points}")
        display_text(10, 710, f"Missed Shots: {failed_shots}")
    else:
        display_text(10, 770, f"Game Over. Final Score: {game_points}")
        display_text(10, 740, f'Press "R" to RESTART.')    
    
    glutSwapBuffers()

def game_loop():
    if not game_ended:
        move_enemies()
        pulse_enemies()
        update_projectiles()
        check_collisions(active_projectiles, enemies)
        
    glutPostRedisplay()

def initialize_game():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(DISPLAY_WIDTH, DISPLAY_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Projectile Mayhem 3D")
    glEnable(GL_DEPTH_TEST)
    
    spawn_enemies()
    
    glutDisplayFunc(render_scene)
    glutIdleFunc(game_loop)
    glutKeyboardFunc(handle_key_press)
    glutSpecialFunc(handle_special_keys)
    glutMouseFunc(handle_mouse_click)
    
    glutMainLoop()

if __name__ == "__main__":
    initialize_game()