import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# Game World
GRID_LENGTH = 4000
FOV_Y = 80
buildings = []
trees = []
bushes = []
barricades = [] 
timbers = []
val = 0.0
apples_list = []
bonfire_list = []

# Player
p_x = 0
p_y = 0
p_z = 0.0
p_vz = 0.0 # for jump
p_vx = 0.0 # for jump
p_vy = 0.0 # for jump
p_angle = 90.0
cam_mode = 3
time_t1 = time.time()
dt = 0.0
p_animate_timer = 0
p_health = 100
p_wood = 0

# Zombies
zombie1_list = [
    (-3600, 3600, 0, 0, 3),
    (3600, 3600, 0, 0, 3),
    (-3600, -3600, 0, 0, 3),
    (3600, -3600, 0, 0, 3),
    (-1200, 2400, 0, 0, 3),
    (1200, 2400, 0, 0, 3)
]
zombie2_list = [
    (1900,1900,0,0, 2),
    (1900,-1900,0,0, 2),
    (0,1900,0,0, 2),
    (-1900,1900,0,0, 2),
    (-1900,-1900,0,0, 2)
]
attack_mode2 = False
damage_flash_timer = 0.0

# Weather
weather_type = 2
weather_object_list = []
for i in range(600):
    x = random.randint(-4000,4000)
    y = random.randint(-4000,4000)
    z = random.randint(0, 1000)
    weather_object_list.append((x,y,z))
fallen_puddle_list = []
fallen_snow_list = []

# Game Mechanics
last_heal_time = time.time()
is_game_over = False
GRAVITY = -700.0
last_time = 0.0
epoch_time = 0.001

# Knife
active_knife = []
knife_switch = True
knife_timer = 0
clicked_throw = False

# Bat
bat_timer = 0
bat_switch = True
clicked_hit = False

# Star
star_active = False
star_x = 0
star_y = 0
star_timer = 0.0
star_cooldown = 30
star_angle = 0.0

# Fallen object
fallen_object_list = []
dead_meat_count = 0

def init_world():
    # city generation
    for bx in range(-3600, 3601, 1200):
        for by in range(600, 3601, 1200):
            if bx == 0:
                continue # For making a straight road from building to forest
            b_height = random.randint(400, 1000)
            buildings.append({'x': bx, 'y': by, 'size': 600, 'height': b_height})
    
    # timber generation
    for _ in range(50):
        tx = random.randint(-3600, 3600)
        ty = random.randint(-3600, -200) # Only in forest
        if abs(tx) < 300: continue
        timbers.append({'x': tx, 'y': ty, 'angle': random.randint(0, 180), 'radius': 15})

    # forest generation
    # Trees
    for _ in range(50):
        tx = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
        ty = random.randint(-GRID_LENGTH + 200, -200)
        if abs(tx) < 300:
            continue # For making a straight road from building to forest

        is_big = random.choice([True, False])
        if is_big:
            scale = random.uniform(1.5, 2.5)
        else:
            scale = random.uniform(0.6, 1.2)
        trees.append({'x': tx, 'y': ty, 'size':150, 'scale': scale})

        if random.random() > 0.3: # 70% chance for a tree to have an apple
            ax = tx + random.randint(-40, 40)
            ay = ty + random.randint(-40, 40)
            apples_list.append({'x': ax, 'y': ay})

    # Bushes
    for _ in range(200):
        bx = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
        by = random.randint(-GRID_LENGTH + 200, -200)
        if abs(bx) < 200:
            continue # For making a straight road from building to forest
        bushes.append({'x': bx, 'y': by})
    
    # City Barricades
    for _ in range(40):
        bx = random.randint(-3600, 3600)
        by = random.randint(400, 3600) # Only in city
        if abs(bx) < 300: continue
        barricades.append({'x': bx, 'y': by, 'angle': random.choice([0, 90]), 'h': 40})

def draw_floor_and_walls():
    # Floor
    glBegin(GL_QUADS)
    glColor3f(0.35, 0.25, 0.15)
    glVertex3f(-4000, 0, 0)
    glVertex3f(-4000, 4000, 0)
    glVertex3f(4000, 4000, 0)
    glVertex3f(4000, 0, 0)
    glColor3f(0, 0.5, 0)
    glVertex3f(4000, 0, 0)
    glVertex3f(-4000, 0, 0)
    glVertex3f(-4000, -4000, 0)
    glVertex3f(4000, -4000, 0)
    glEnd()

    # Walls
    wall_height = 200
    glBegin(GL_QUADS)
    # Green Wall Around forest (Border)
    glColor3f(0.05, 0.35, 0.1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glColor3f(0.05, 0.35, 0.1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(-GRID_LENGTH, 0, wall_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glColor3f(0.05, 0.35, 0.1)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glVertex3f(GRID_LENGTH, 0, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)

    # Wall Arount the building (Border)
    glColor3f(0.08, 0.04, 0.04)
    glVertex3f(-GRID_LENGTH, 0, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, 0, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glColor3f(0.08, 0.04, 0.04)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glColor3f(0.08, 0.04, 0.04)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, 0, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, 0, wall_height)
    glEnd()

    # Sky color boundary above wall to show the sky
    light_height = 1500
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height+light_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height+light_height)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height+light_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height+light_height)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_height+light_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_height+light_height)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_height+light_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_height+light_height)
    glEnd()

    # Upper Sky (a sky color cover like boundary above the world)
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(-4000, -4000, wall_height + light_height)
    glVertex3f(-4000, 4000, wall_height + light_height)
    glVertex3f(4000, 4000, wall_height + light_height)
    glVertex3f(4000, -4000, wall_height + light_height)
    glEnd()

def draw_star():
    global star_active, star_x, star_y, star_angle
    
    if not star_active:
        return

    glPushMatrix()
    # Make it float up and down slightly
    bounce = math.sin(time.time() * 5) * 10
    glTranslatef(star_x, star_y, 50 + bounce)
    
    # Rotate the star constantly
    glRotatef(star_angle, 0, 0, 1)
    glRotatef(45, 1, 1, 0) # Tilt it so a cube looks like a 3D diamond
    
    # Gold Color
    glColor3f(1.0, 0.84, 0.0) 
    
    # Draw the star
    glScalef(50, 50, 50)
    glutSolidCube(1)
    
    
    glPopMatrix()

def draw_obstacles():
    # Draw City Barricades (Zebra Pattern)
    for b in barricades:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], b['h'] / 2)
        glRotatef(b['angle'], 0, 0, 1)
        
        num_stripes = 10
        stripe_width = 20  # Total width will be 200 (10 * 20)

        start_x = - (num_stripes * stripe_width) / 2.0 + (stripe_width / 2.0)

        for i in range(num_stripes):
            glPushMatrix()
            glTranslatef(start_x + i * stripe_width, 0, 0)
            
            # Alternate colors between White and Near-Black
            if i % 2 == 0:
                glColor3f(0.9, 0.9, 0.9)
            else:
                glColor3f(0.1, 0.1, 0.1)
                
            glScalef(stripe_width, 20, b['h'])
            glutSolidCube(1)
            glPopMatrix()
            
        glPopMatrix()
        
    # Draw Forest Timbers (Brown)
    glColor3f(0.3, 0.2, 0.1) 
    for t in timbers:
        glPushMatrix()
        glTranslatef(t['x'], t['y'], t['radius']) 
        glRotatef(t['angle'], 0, 0, 1)
        glRotatef(90, 0, 1, 0) 
        
        glTranslatef(0, 0, -100) 
        gluCylinder(gluNewQuadric(), t['radius'], t['radius'], 200, 10, 1) 
        glPopMatrix()

def draw_buildings():
    glColor3f(0.25, 0.25, 0.3)
    for b in buildings:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], b['height'] / 2)
        glScalef(1.0, 1.0, b['height'] / b['size'])
        glutSolidCube(b['size'])
        glPopMatrix()

def draw_trees():
    for t in trees:
        glPushMatrix()
        glTranslatef(t['x'], t['y'], 0)
        glScalef(t['scale'], t['scale'], t['scale'])
        
        # Trunk
        glColor3f(0.25, 0.15, 0.05)
        gluCylinder(gluNewQuadric(), 15, 10, 120, 10, 1)
        
        # Leaves
        glTranslatef(0, 0, 130)
        glColor3f(0.05, 0.25, 0.1)
        gluSphere(gluNewQuadric(), 65, 8, 8)
        
        # Apple
        glColor3f(0.8, 0.1, 0.1) 
        glPushMatrix()
        glTranslatef(65, 0, 10)
        gluSphere(gluNewQuadric(), 8, 8, 8)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-30, 55, -10)
        gluSphere(gluNewQuadric(), 8, 8, 8)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, -60, 20)
        gluSphere(gluNewQuadric(), 8, 8, 8); glPopMatrix()
        
        glPopMatrix()

def draw_bushes():
    for b in bushes:
        glPushMatrix()
        glTranslatef(b['x'], b['y'], 0)
        
        #Bush lower part
        glColor3f(0.3, 0.2, 0.1)
        gluCylinder(gluNewQuadric(), 8, 8, 15, 8, 1)
        
        #Bush above part
        glTranslatef(0, 0, 10)
        glColor3f(0.1, 0.35, 0.1)
        gluCylinder(gluNewQuadric(), 35, 0, 60, 8, 1)
        glPopMatrix()

def draw_zombie1():
    global p_x, p_y, dt, is_game_over, p_health, zombie1_list, damage_flash_timer, epoch_time
    
    epoch_time += 0.0001
    zombie1_target_x, zombie1_target_y = p_x,p_y
    detection_range = 2500
    for i in range(len(zombie1_list)):
        zombie_height = 300
        zombie1_speed = (dt * 65) + epoch_time
        zombie1_position_x, zombie1_position_y,animate_timer,val, zombie1_hp = zombie1_list[i]
        val += zombie1_speed
        dx = zombie1_target_x - zombie1_position_x
        dy = zombie1_target_y - zombie1_position_y
        dist = math.sqrt(dx**2 + dy**2)//1
        target_angle_rad = math.atan2(dy, dx)
        target_angle_deg = math.degrees(target_angle_rad)
        attack_mode = False
        if dist < detection_range:
            if dist > zombie_height:
                step_x = zombie1_speed * (dx / dist)
                step_y = zombie1_speed * (dy / dist)
                can_move_x = not check_collision(zombie1_position_x + step_x, zombie1_position_y, True)
                can_move_y = not check_collision(zombie1_position_x, zombie1_position_y + step_y, True)

                if can_move_x and can_move_y:
                    # Path is clear, move diagonally
                    zombie1_position_x += step_x
                    zombie1_position_y += step_y
                elif can_move_x:
                    zombie1_position_x += step_x
                elif can_move_y:
                    zombie1_position_y += step_y
            else:
                player_is_safe = False
                for bf in bonfire_list:
                    # Check if the player is within the bonfire's radius
                    if math.sqrt((p_x - bf['x'])**2 + (p_y - bf['y'])**2) < 300: 
                        player_is_safe = True
                        break
                
                # Only attack if the player is not in the safe zone
                if not player_is_safe:
                    attack_mode = True
                    p_health -= 15 * dt

                    damage_flash_timer = 0.2

                    if p_health <= 0:
                        is_game_over = True
        
        leg_rotate = 30 * math.sin(val * (4.8/zombie_height))
        if dist > detection_range:
            leg_rotate = 0
        if attack_mode == True:
            leg_rotate = 0
            animate_timer = (animate_timer+zombie1_speed) % 600
        else:
            animate_timer = 0
        glPushMatrix()
        glTranslatef(zombie1_position_x, zombie1_position_y, 0)
        glRotatef(target_angle_deg - 90, 0, 0, 1)

        glColor3f(0, 0.5, 0.5)

        glTranslatef(0, 0, 0.6 * zombie_height)


        # Leg (left)
        glPushMatrix()
        glColor3f(0.25, 0.18, 0.15)
        glTranslatef(-0.1 * zombie_height, 0, 0)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_rotate, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.03 * zombie_height, 0.03 * zombie_height, 0.6 * zombie_height, 10, 10)
        glPopMatrix()

        # Leg (right)
        glPushMatrix()
        glColor3f(0.25, 0.18, 0.15)
        glTranslatef(0.1 * zombie_height, 0, 0)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_rotate, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.03 * zombie_height, 0.03 * zombie_height, 0.6 * zombie_height, 10, 10)
        glPopMatrix()

        if attack_mode == True:
            if animate_timer <= 300:
                drop_angle = (animate_timer)*0.4
            else:
                drop_angle = (600 -animate_timer)*0.4
            glRotatef(-drop_angle, 1, 0, 0)

        # Body
        glPushMatrix()
        glColor3f(0.35, 0.25, 0.20)
        glScalef(1, 0.5, 1)
        gluCylinder(gluNewQuadric(), 0.1 * zombie_height, 0.2 * zombie_height, 0.6 * zombie_height, 10, 10)
        glPopMatrix()

        # Sirens and stick
        glPushMatrix()
        glTranslatef(0, 0, 0.6 * zombie_height)
        glColor3f(0.05, 0.05, 0.05)
        scale_value = 0
        if attack_mode == True:
            if animate_timer <= 300:
                scale_value = (animate_timer)*0.005
            else:
                scale_value = (600 -animate_timer)*0.005
            glScalef(1+scale_value, 1+scale_value,1+scale_value)
        gluCylinder(gluNewQuadric(), 0.02 * zombie_height, 0.02 * zombie_height, 0.30 * zombie_height, 10, 10)
        glTranslatef(0, 0, 0.2 * zombie_height)
        glRotatef(90, 0, 1, 0)
        glColor3f(0.15+scale_value, 0.15, 0.15)
        gluCylinder(gluNewQuadric(), 0.02 * zombie_height, 0.07 * zombie_height, 0.2 * zombie_height, 10, 10)
        glRotatef(-180, 0, 1, 0)
        glTranslatef(0.1 * zombie_height, 0, 0)
        gluCylinder(gluNewQuadric(), 0.02 * zombie_height, 0.07 * zombie_height, 0.2 * zombie_height, 10, 10)
        glPopMatrix()

        # Arms
        glPushMatrix()
        glColor3f(0.25, 0.18, 0.15)
        glTranslatef(0, 0, 0.6 * zombie_height)
        glTranslatef(-0.21 * zombie_height, 0, 0)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_rotate, 1, 0, 0)
        gluSphere(gluNewQuadric(), 0.07*zombie_height, 30, 10)  # parameters are: quadric, radius, slices, stacks
        gluCylinder(gluNewQuadric(), 0.02 * zombie_height, 0.02 * zombie_height, 0.7 * zombie_height, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.25, 0.18, 0.15)
        glTranslatef(0, 0, 0.6 * zombie_height)
        glTranslatef(0.21 * zombie_height, 0, 0)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_rotate, 1, 0, 0)
        gluSphere(gluNewQuadric(), 0.07*zombie_height, 30, 10)  # parameters are: quadric, radius, slices, stacks
        gluCylinder(gluNewQuadric(), 0.02 * zombie_height, 0.02 * zombie_height, 0.7 * zombie_height, 10, 10)
        glPopMatrix()

        glPopMatrix()

        zombie1_list[i] = (zombie1_position_x, zombie1_position_y,animate_timer,val, zombie1_hp)

def draw_zombie2():
    global val2, animate_timer2, trees, buildings, zombie2_list, dt, p_health, is_game_over
    global damage_flash_timer, attack_mode2,epoch_time

    zombie2_target_x, zombie2_target_y = p_x, p_y
    detection_range = 2500
    for i in range(len(zombie2_list)):
        zombie_height = 200
        zombie2_speed = (dt*65)  + epoch_time
        zombie2_position_x, zombie2_position_y,animate_timer2,val2, zombie2_hp = zombie2_list[i]
        val2 += zombie2_speed
        dx = zombie2_target_x - zombie2_position_x
        dy = zombie2_target_y - zombie2_position_y
        dist = math.sqrt(dx**2 + dy**2)//1
        target_angle_rad = math.atan2(dy, dx)
        target_angle_deg = math.degrees(target_angle_rad)
        attack_mode2 = False
        walk_ahead = True
        if dist < detection_range:
            if dist > zombie_height:
                step_x = zombie2_speed * (dx / dist)
                step_y = zombie2_speed * (dy / dist)
                can_move_x = not check_collision(zombie2_position_x + step_x, zombie2_position_y, True)
                can_move_y = not check_collision(zombie2_position_x, zombie2_position_y + step_y, True)

                if can_move_x and can_move_y:
                    zombie2_position_x += step_x
                    zombie2_position_y += step_y
                elif can_move_x:
                    zombie2_position_x += step_x
                elif can_move_y:
                    zombie2_position_y += step_y
            else:
                player_is_safe = False
                for bf in bonfire_list:
                    # Check if the player is within the bonfire's radius
                    if math.sqrt((p_x - bf['x'])**2 + (p_y - bf['y'])**2) < 300: 
                        player_is_safe = True
                        break
                
                # Only attack if the player is not in the safe zone
                if not player_is_safe:
                    attack_mode2 = True
                    p_health -= 10 * dt
                    damage_flash_timer = 0.2
                    if p_health <= 0:   
                        is_game_over = True

        leg_rotate = 30 * math.sin(val2 * (4.8/zombie_height))
        if dist > detection_range:
            leg_rotate = 0
        if attack_mode2 == True:
            leg_rotate = 0
            animate_timer2 = (animate_timer2+zombie2_speed) % 600
        else:
            animate_timer2 = 0

        glPushMatrix()
        glTranslatef(zombie2_position_x,zombie2_position_y,0)
        glRotatef(target_angle_deg - 90, 0, 0, 1)
        glColor3f(1, 0.5, 0.5)


        glTranslatef(0,0,zombie_height*0.4)
        glPushMatrix()

        glColor3f(0, 0.5, 0.5)
        glTranslatef(0.1*zombie_height,0.2*zombie_height,0)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_rotate, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.015 * zombie_height, 0.015 * zombie_height, 0.4 * zombie_height, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0.5, 0.5)
        glTranslatef(0.1*zombie_height,-0.2*zombie_height,0)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_rotate, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.015 * zombie_height, 0.015 * zombie_height, 0.4 * zombie_height, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0.5, 0.5)
        glTranslatef(-0.1*zombie_height,0.2*zombie_height,0)
        glRotatef(180, 1, 0, 0)
        glRotatef(-leg_rotate, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.015 * zombie_height, 0.015 * zombie_height, 0.4 * zombie_height, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, 0.5, 0.5)
        glTranslatef(-0.1*zombie_height,-0.2*zombie_height,0)
        glRotatef(180, 1, 0, 0)
        glRotatef(leg_rotate, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 0.015 * zombie_height, 0.015 * zombie_height, 0.4 * zombie_height, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0, (0.01* (val2%80)), (0.01* (val2%40)))
        glScalef(1,2.5,1)
        glutSolidCube(0.2* zombie_height)
        glPopMatrix()

        glPushMatrix()
        scale_value = 0
        if attack_mode2 == True:
            if animate_timer2 <= 300:
                scale_value = (animate_timer2)*0.005
            else:
                scale_value = (600 -animate_timer2)*0.005
            glScalef(1+scale_value, 1+scale_value,1+scale_value)
        glColor3f(0.3,0,1)
        glTranslatef(0,0.3*zombie_height,0)
        gluSphere(gluNewQuadric(), 0.12* zombie_height, 30, 10)
        glPopMatrix()

        glPopMatrix()

        zombie2_list[i] = (zombie2_position_x, zombie2_position_y,animate_timer2,val2, zombie2_hp)

def draw_bonfire():
    global bonfire_list, p_x, p_y, dt

    for i in bonfire_list:
        bonfire_size = 100
        bonfire_x,bonfire_y = i["x"] , i["y"]
        glPushMatrix()

        # Stick 1
        glTranslatef(bonfire_x,bonfire_y,0)
        glPushMatrix()
        glTranslatef(0,-bonfire_size * 0.7,0)
        glRotatef(-70, 1, 0, 0)
        glColor3f(0.5, 0.3, 0.1)
        gluCylinder(gluNewQuadric(), 5,5,bonfire_size, 15, 10)
        glColor3f(0.3, 0.2, 0.1)
        gluCylinder(gluNewQuadric(), 5.4,5.4,bonfire_size, 5,10)
        glPopMatrix()

        # Stick 2
        glRotatef(120, 0, 0, 1)
        glPushMatrix()
        glTranslatef(0,-bonfire_size * 0.7,0)
        glRotatef(-70, 1, 0, 0)
        glColor3f(0.5, 0.3, 0.1)
        gluCylinder(gluNewQuadric(), 5,5,bonfire_size, 15, 10)
        glColor3f(0.3, 0.2, 0.1)
        gluCylinder(gluNewQuadric(), 5.4,5.4,bonfire_size, 5,10)
        glPopMatrix()
        
        # Stick 3
        glRotatef(120, 0, 0, 1)
        glPushMatrix()
        glTranslatef(0,-bonfire_size * 0.7,0)
        glRotatef(-70, 1, 0, 0)
        glColor3f(0.5, 0.3, 0.1)
        gluCylinder(gluNewQuadric(), 5,5,bonfire_size, 15, 10)
        glColor3f(0.3, 0.2, 0.1)
        gluCylinder(gluNewQuadric(), 5.4,5.4,bonfire_size, 5,10)
        glPopMatrix()

        # Fire
        glPushMatrix()
        glTranslatef(0,0,bonfire_size*0.5)
        glColor3f(0.95, 0.5, 0.2)
        fireupdown = math.sin(time.time()*3)*0.1
        glScalef(fireupdown+1, 1+fireupdown, 1+fireupdown)
        glScalef(1, 1, 1+bonfire_size*0.01)
        gluSphere(gluNewQuadric(), bonfire_size*0.12, 30, 10)  # parameters are: quadric, radius, slices, stacks
        gluCylinder(gluNewQuadric(), bonfire_size*0.12,1,bonfire_size*0.2, 15, 10)
        glPopMatrix()

        # Safe Zone
        glPushMatrix()
        glColor3f(0.05, 0.9, 0.2)
        gluCylinder(gluNewQuadric(), bonfire_size*3,bonfire_size*3,bonfire_size*0.1, 15, 10)
        glTranslatef(0,0,bonfire_size*0.1)
        gluCylinder(gluNewQuadric(), bonfire_size*3,bonfire_size*3,bonfire_size*0.1, 15, 10)
        glPopMatrix()

        glPopMatrix()

def draw_weather():
    global weather_type, weather_object_list, dt, fallen_puddle_list, fallen_snow_list

    glPushMatrix()
    for point in range(len(weather_object_list)):
        x,y,z = weather_object_list[point]
        if weather_type == 0:
            # Rain
            glPushMatrix()
            glColor3f(0.3, 0.3, .90)
            glTranslatef(x, y, z)
            glScalef(1, 1, 25)
            glutSolidCube(2)
            glPopMatrix()
        
        if weather_type == 1:
            # Snow
            glPushMatrix()
            glColor3f(0.9, 0.9, .9)
            glTranslatef(x, y, z)
            gluSphere(gluNewQuadric(), 5, 8, 8)
            glPopMatrix()

        z = z- (dt*600)
        if z < 5:
            if weather_type == 0:
                fallen_puddle_list.append((x,y))
                if len(fallen_puddle_list) > 4000:
                    fallen_puddle_list.pop(1)
            if weather_type == 1:
                fallen_snow_list.append((x,y))
                if len(fallen_snow_list) > 4000:
                    fallen_snow_list.pop(1)
            z = 1000
            x = random.randint(-4000,4000)
            y = random.randint(-4000,4000)
        weather_object_list[point] = x,y,z
    if weather_type == 1:
        for i in range(len(fallen_snow_list)):
            snow_x,snow_y = fallen_snow_list[i]
            glPushMatrix()
            glColor3f(0.9, 0.9, .9)
            glTranslatef(snow_x, snow_y, 2)
            glScalef(1,1,0.3)
            gluSphere(gluNewQuadric(),10,10,10)
            glPopMatrix()
    if weather_type == 0:
        for i in range(len(fallen_puddle_list)):
            snow_x,snow_y = fallen_puddle_list[i]
            glPushMatrix()
            glColor3f(0.3, 0.3, .90)
            glTranslatef(snow_x, snow_y, 2)
            glScalef(1,1,0.3)
            gluSphere(gluNewQuadric(),15,10,10)
            glPopMatrix()
    if weather_type == 2:
        fallen_snow_list = []
        fallen_puddle_list = []
        # Sunny
        glPushMatrix()
        glColor3f(1.0, 0.8, 0.2)
        glTranslatef(3000, -2000, 1000)
        gluSphere(gluNewQuadric(), 200, 8, 8)
        glPopMatrix()

    glPopMatrix()

def draw_knife():
    global p_x, p_y, p_angle, knife_switch, clicked_throw, knife_timer, dt, fallen_object_list
    global active_knife, zombie1_list, zombie2_list

    if knife_switch == True and clicked_throw == True:
        knife_timer -= (dt*260)
        if knife_timer < -80:
            knife_switch = False
    if knife_switch == False:
        knife_timer += (dt*260)
        if knife_timer > 0:
            knife_switch = True
            clicked_throw = False

    # Loop backwards through the knives list
    for i in range(len(active_knife) - 1, -1, -1):
        knife_angle, knife_x, knife_y, knife_z , knife_vz = active_knife[i]

        knife_speed = 250 * dt
        knife_x += math.cos(math.radians(knife_angle)) * 5 * knife_speed
        knife_y += math.sin(math.radians(knife_angle)) * 5 * knife_speed

        knife_vz -= (800 * dt)
        knife_z += knife_vz * dt # Projectile movement
        
        hit_target = False
        hitbox_radius = 50
        
        # Knife collission with zombie1
        for j in range(len(zombie1_list) - 1, -1, -1):
            zx, zy, anim, val, hp = zombie1_list[j]
            if math.sqrt((knife_x - zx)**2 + (knife_y - zy)**2) < hitbox_radius:
                hp -= 1
                if hp <= 0:
                    zombie1_list.pop(j)
                    fallen_object_list.append((zx,zy))
                    if p_x < 0:
                        new_zombiex = 1900 + random.random()*300
                    else:
                        new_zombiex = -1900 + random.random()*300
                    if p_y < 0:
                        new_zombiey = 1900 + random.random()*300
                    else:
                        new_zombiey = -1900 + random.random()*300
                    zombie1_list.append((new_zombiex,new_zombiey,0,0,3))
                else:
                    zombie1_list[j] = (zx, zy, anim, val, hp)
                hit_target = True
                break
                
        # Knife collission with zombie2
        if not hit_target:
            for j in range(len(zombie2_list) - 1, -1, -1):
                zx, zy, anim, val, hp = zombie2_list[j]
                if math.sqrt((knife_x - zx)**2 + (knife_y - zy)**2) < hitbox_radius:
                    hp -= 1
                    if hp <= 0:
                        zombie2_list.pop(j)
                        fallen_object_list.append((zx,zy))
                        if p_x < 0:
                            new_zombiex = 1900 + random.random()*300
                        else:
                            new_zombiex = -1900 + random.random()*300
                        if p_y < 0:
                            new_zombiey = 1900 + random.random()*300
                        else:
                            new_zombiey = -1900 + random.random()*300
                        zombie2_list.append((new_zombiex,new_zombiey,0,0,2))
                    else:
                        zombie2_list[j] = (zx, zy, anim, val, hp)
                    hit_target = True
                    break

        if hit_target or knife_z < -19:
            active_knife.pop(i)
            continue
            
        # Draw the knife
        glPushMatrix()
        glTranslatef(knife_x, knife_y, knife_z+20)
        glRotatef(knife_angle, 0,0,1)
        glRotatef(-90, 0,0,1)
        glTranslatef(-27,0,0)
        glColor3f(1, 0.7, 0.8)
        glScalef(0.3,3,1)
        glutSolidCube(10)

        glScalef(1/0.3, 1/3, 1)
        glTranslatef(0, 15 ,0)
        glColor3f(0, 0.7, 0.8)
        glScalef(0.3, 1, 1)
        glRotatef(-90,1,0,0)
        gluCylinder(gluNewQuadric(), 6 , 1, 20, 10, 1)
        glPopMatrix()
        
        # Save the updated knife position
        active_knife[i] = (knife_angle, knife_x, knife_y, knife_z, knife_vz)

def draw_bat():
    global p_x, p_y, p_z, p_angle, bat_timer, bat_switch, clicked_hit, dt

    if bat_switch == True and clicked_hit == True:
        bat_timer -= 800 * dt
        if bat_timer < -80:
            bat_switch = False
    if bat_switch == False:
        bat_timer += 800 * dt
        if bat_timer > 0:
            bat_switch = True
            clicked_hit = False
    
    bat_size = 5
    glColor3f(0.3, 0.1, 0.3)
    glPushMatrix()
    glTranslatef(p_x,p_y,70+p_z)
    glRotatef(p_angle, 0,0,1)

    glRotatef(bat_timer, 0,1,0)
    glTranslatef(0,0,-30)
    glPushMatrix()
    glRotatef(90, 0,1,0)
    glTranslatef(0,-22,0)
    gluCylinder(gluNewQuadric(), bat_size * 0.3, bat_size *2, bat_size * 12, 10, 1)
    glTranslatef(0, 0 ,bat_size * 12)
    gluSphere(gluNewQuadric(), bat_size * 2, 8, 8)
    glPopMatrix()

    glPopMatrix()

def draw_fallen_object():
    global p_x, p_y, fallen_object_list, dead_meat_count, p_health

    for i in range(len(fallen_object_list) - 1, -1, -1):
        x, y = fallen_object_list[i]
        
        # Calculate distance from player to the meat
        dist = math.sqrt((p_x - x)**2 + (p_y - y)**2)
        
        if dist < 80: 
            fallen_object_list.pop(i)
            dead_meat_count += 1
            p_health = min(100, p_health + 2)
            continue

        glPushMatrix()
        passing_time = -math.sin(time.time()*3)*6
        glTranslatef(x,y,20 + passing_time)
        glRotatef(90,1,0,0)

        glPushMatrix()
        glColor3f(0.9,0.9,0.9)
        glScalef(3,3,15)
        gluCylinder(gluNewQuadric(), 1, 1, 5, 10, 1)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.9,0.9,0.9)
        glTranslatef(0,0,0)
        gluSphere(gluNewQuadric(), 6, 20, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.9,0.9,0.9)
        glTranslatef(0,0,80)
        gluSphere(gluNewQuadric(), 6, 20, 20)
        glPopMatrix()

        glPushMatrix()
        glColor3f(0.45, 0.25, 0.40)
        glTranslatef(0,0,10)
        glScalef(1,0.3,1)
        gluCylinder(gluNewQuadric(), 13, 13, 60, 10, 1)
        glPopMatrix()

        glPopMatrix()

def reset_game():
    global p_x, p_y, p_health, p_angle, is_game_over, p_wood
    global zombie1_list, zombie2_list, active_knife, bonfire_list, apples_list
    global clicked_throw, clicked_hit, dead_meat_count

    p_x = 0
    p_y = 0
    p_angle = 90.0
    p_health = 100
    p_wood = 0
    is_game_over = False
    dead_meat_count = 0
    
    active_knife = []
    bonfire_list = []
    apples_list = []
    clicked_throw = False
    clicked_hit = False

    # Reset Zombie1
    zombie1_list = [
        (-3600, 3600, 0, 0, 3), (3600, 3600, 0, 0, 3),
        (-3600, -3600, 0, 0, 3), (3600, -3600, 0, 0, 3),
        (-1200, 2400, 0, 0, 3), (1200, 2400, 0, 0, 3)
    ]
    # Reset Zombie2
    zombie2_list = [
        (1900, 1900, 0, 0, 2), (1900, -1900, 0, 0, 2),
        (0, 1900, 0, 0, 2), (-1900, 1900, 0, 0, 2),
        (-1900, -1900, 0, 0, 2)
    ]
    
    # Reappear apples under trees
    for t in trees:
        if random.random() > 0.3:
            ax = t['x'] + random.randint(-40, 40)
            ay = t['y'] + random.randint(-40, 40)
            apples_list.append({'x': ax, 'y': ay})

def draw_hero():
    global p_animate_timer, is_game_over, damage_flash_timer

    if damage_flash_timer > 0:
        skin_r, skin_g, skin_b = 1.0, 0.2, 0.2 # Player is being attacked
    else:
        skin_r, skin_g, skin_b = 0.95, 0.75, 0.65
        
    glColor3f(skin_r, skin_g, skin_b)

    if is_game_over:
        glPushMatrix()
        glTranslatef(p_x, p_y, 0.5)
        glColor3f(0.6, 0.0, 0.0)
        glScalef(1, 1, 0.1)
        gluSphere(gluNewQuadric(), 45, 20, 20)
        glPopMatrix()
    
    if not is_game_over:
        p_animate_timer += 1
    
    leg_rotate = 30 * math.sin(p_animate_timer * (4.8/100))
    glPushMatrix()
    glTranslatef(p_x, p_y, p_z)
    glRotatef(p_angle - 90, 0, 0, 1)
    if is_game_over:
        glTranslatef(0, 0, 10) 
        glRotatef(90, 1, 0, 0)
    leg_moving = math.sin(math.sqrt(p_x**2 + p_y**2))*3
    
    # Left Leg (Peach)
    glScalef(1.2, 1.2, 1.2)
    glPushMatrix()
    glTranslatef(0,leg_moving,0)
    glTranslatef(-7, 0, 20)
    glColor3f(skin_r, skin_g, skin_b)
    glPushMatrix()
    gluSphere(gluNewQuadric(), 6, 8, 8)
    glTranslatef(0, 0, -10)
    glScalef(6, 6, 20)
    glutSolidCube(1)
    glPopMatrix()
    
    # Left Foot (Black)
    glTranslatef(0, 2, -20)
    glColor3f(0.08, 0.08, 0.08)
    glPushMatrix()
    glScalef(10, 12, 6)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Right Leg (Peach)
    glPushMatrix()
    glTranslatef(0,-leg_moving,0)
    glTranslatef(7, 0, 20)
    glColor3f(skin_r, skin_g, skin_b)
    glPushMatrix()
    gluSphere(gluNewQuadric(), 6, 8, 8)
    glTranslatef(0, 0, -10)
    glScalef(6, 6, 20)
    glutSolidCube(1)
    glPopMatrix()
    
    # Right Foot
    glTranslatef(0, 2, -20)
    glColor3f(0.08, 0.08, 0.08)
    glPushMatrix()
    glScalef(10, 12, 6)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Pelvis (Dark Grey)
    glPushMatrix()
    glTranslatef(0, 0, 28)
    glColor3f(0, 0, 0.9)
    glPushMatrix()
    glScalef(26, 12, 16)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Waist Joint (Light Grey)
    glPushMatrix()
    glTranslatef(0, 0, 37)
    glColor3f(skin_r, skin_g, skin_b)
    glPushMatrix()
    glScalef(10, 8, 4)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Torso (Dark Grey)
    glPushMatrix()
    glTranslatef(0, 0, 54)
    glColor3f(0.15, 0.15, 0.15)
    glPushMatrix()
    glScalef(26, 14, 30)
    glutSolidCube(1)
    gluCylinder(gluNewQuadric(), 0.3, 0.7, 0.55, 10, 1)
    glPopMatrix()
    glPopMatrix()

    # Neck (Light Grey)
    glPushMatrix()
    glTranslatef(0, 0, 71)
    glColor3f(skin_r, skin_g, skin_b)
    glPushMatrix()
    glScalef(8, 8, 4)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Head (Medium Grey)
    glPushMatrix()
    glTranslatef(0, 0, 82)
    glColor3f(0.45, 0.45, 0.45)
    glutSolidCube(17)
    glPopMatrix()

    # Left Arm (Medium Grey)
    glPushMatrix()
    glTranslatef(-20, 0, 65)
    glRotatef(-2, 0, 1, 0)
    glRotatef(-knife_timer, 1, 0, 0)
    glTranslatef(0, 0, -14)
    glColor3f(skin_r, skin_g, skin_b)
    glPushMatrix()
    glScalef(6, 6, 28)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    # Right Arm (Medium Grey)
    glPushMatrix()
    glTranslatef(20, 0, 65)
    glRotatef(2, 0, 1, 0)
    glRotatef(-bat_timer, 1, 0, 0)
    glTranslatef(0, 0, -14)
    glColor3f(skin_r, skin_g, skin_b)
    glPushMatrix()
    glScalef(6, 6, 28)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()

    glPopMatrix()

def check_collision(nx, ny, is_Zombie = False):
    player_radius = 20
    zombie_radius = 25
    
    # Building Collision
    for b in buildings:
        half_size = b['size'] / 2 
        dx = abs(nx - b['x'])
        dy = abs(ny - b['y'])
        boundary = half_size + player_radius 
        if dx < boundary and dy < boundary:
            return True
    
    # Tree Collision
    for t in trees:
        tree_radius = 25 * t['scale']
        dx_t = nx - t['x']
        dy_t = ny - t['y']
        distance = math.sqrt(dx_t**2 + dy_t**2)
        if distance < (tree_radius + player_radius):
            return True
    
    # Barricade Collision
    for b in barricades:
        distance = math.sqrt((nx - b['x'])**2 + (ny - b['y'])**2)
        if distance < (45 + player_radius):
            # Block if it's a zombie, OR if the player hasn't jumped high enough
            if is_Zombie or p_z < b['h']: 
                return True

    # Timber Collision
    for t in timbers:
        distance = math.sqrt((nx - t['x'])**2 + (ny - t['y'])**2)
        if distance < (40 + player_radius):
            if is_Zombie or p_z < (t['radius'] * 2):
                return True
    
    # Zombie cannot enter the bonfire
    if is_Zombie:
        for bf in bonfire_list:
            half_bf_size = bf['size'] / 2
            dx_bf = abs(nx - bf['x'])
            dy_bf = abs(ny - bf['y'])
            bf_boundary = half_bf_size + zombie_radius 
            if dx_bf < bf_boundary and dy_bf < bf_boundary:
                return True
    return False

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV_Y, 1.25, 0.1, 8000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if cam_mode == 3:
        gluLookAt(p_x - 300 * math.cos(math.radians(p_angle)), p_y - 300 * math.sin(math.radians(p_angle)), 180 + p_z, 
                  p_x, p_y, 45 + p_z, 
                  0, 0, 1)
    elif cam_mode == 1:
        gluLookAt(p_x + 10 * math.cos(math.radians(p_angle)), p_y + 10 * math.sin(math.radians(p_angle)), 85 + p_z, 
                  p_x + 100 * math.cos(math.radians(p_angle)), p_y + 100 * math.sin(math.radians(p_angle)), 85 + p_z, 
                  0, 0, 1)
    elif cam_mode == 2:
        gluLookAt(p_x - 300 * math.cos(math.radians(p_angle+45)), p_y - 300 * math.sin(math.radians(p_angle)), 180 + p_z, 
                  p_x, p_y, 45 + p_z, 
                  0, 0, 1)

def keyboardListener(key, x, y):
    global p_x, p_y, p_angle, cam_mode, bonfire_list, weather_type, p_health, is_game_over, p_wood, trees
    global p_z, p_vz, p_vx, p_vy, zombie1_list, zombie2_list, clicked_hit

    # X button
    if key == b'x' or key == b'X':
        chop_reach = 100 
        action_taken = False # so that don't chop and gather at the exact same time
        
        # Chopping
        for i in range(len(trees)):
            t = trees[i]
            tree_radius = 25 * t['scale']
            
            # Check distance to the tree
            if math.sqrt((p_x - t['x'])**2 + (p_y - t['y'])**2) < (chop_reach + tree_radius):
                
                clicked_hit = True
                action_taken = True
                
                # drop timber (with a 70% chance)
                if random.random() < 0.70: 
                    # Spawn the timber
                    timbers.append({'x': t['x'], 'y': t['y'], 'angle': random.randint(0, 180), 'radius': 15})

                # Respawn the tree somewhere else in the forest
                tx = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
                ty = random.randint(-GRID_LENGTH + 200, -200)
                if abs(tx) < 300: tx += 400 
                trees[i]['x'] = tx
                trees[i]['y'] = ty
                
                break
        
        # Collect timber
        if not action_taken:
            for i in range(len(timbers) - 1, -1, -1):
                t = timbers[i]

                if math.sqrt((p_x - t['x'])**2 + (p_y - t['y'])**2) < (chop_reach + 100):
                    p_wood += 2
                    timbers.pop(i) 
                    break
    
    if key == b'r' or key == b'R':
        if is_game_over:
            reset_game()
            return
        
    if is_game_over:
        return
    
    # Movement step sizes per key press
    move_speed = 30.0
    turn_speed = 5.0

    # C button (camera angles)
    if key == b'c' or key == b'C':
        cam_mode += 1
        if cam_mode > 3:
            cam_mode = 1

    # E button (Eating)
    if key == b'e' or key == b'E':
        for i, apple in enumerate(apples_list):
            # Calculate distance from player to apple
            dist = math.sqrt((p_x - apple['x'])**2 + (p_y - apple['y'])**2)
            if dist < 80:
                apples_list.pop(i)
                p_health = min(100, p_health + 15)
                break

    # Rotation
    if key == b'a' or key == b'A':
        p_angle += turn_speed
    if key == b'd' or key == b'D':
        p_angle -= turn_speed
    
    # B button (Bonfire)
    if key == b'b':
        if p_wood >= 4:
            p_wood -= 4
            bonfire_list.append({"x":p_x, "y": p_y,"size": 600})
            kill_radius = 300 

            for i in range(len(zombie1_list) - 1, -1, -1):
                zx, zy, anim, val, hp = zombie1_list[i]
                if math.sqrt((p_x - zx)**2 + (p_y - zy)**2) < kill_radius:
                    zombie1_list.pop(i)
                    
            for i in range(len(zombie2_list) - 1, -1, -1):
                zx, zy, anim, val, hp = zombie2_list[i]
                if math.sqrt((p_x - zx)**2 + (p_y - zy)**2) < kill_radius:
                    zombie2_list.pop(i)

    # W button (Forward)
    if key == b'w' or key == b'W':
        next_px = p_x + move_speed * math.cos(math.radians(p_angle))
        next_py = p_y + move_speed * math.sin(math.radians(p_angle))
        if not check_collision(next_px, p_y):
            p_x = next_px
        if not check_collision(p_x, next_py):
            p_y = next_py

    # S button (Backward)
    if key == b's' or key == b'S':
        next_px = p_x - move_speed * math.cos(math.radians(p_angle))
        next_py = p_y - move_speed * math.sin(math.radians(p_angle))
        if not check_collision(next_px, p_y):
            p_x = next_px
        if not check_collision(p_x, next_py):
            p_y = next_py

    if key == b'p' or key == b'P':
        weather_type  = (weather_type + 1)%3

    # Condition for player not crossing boundary
    if p_x < -GRID_LENGTH + 20:
        p_x = -GRID_LENGTH + 20
    if p_x > GRID_LENGTH - 20:
        p_x = GRID_LENGTH - 20
    if p_y < -GRID_LENGTH + 20:
        p_y = -GRID_LENGTH + 20
    if p_y > GRID_LENGTH - 20:
        p_y = GRID_LENGTH - 20
    
    # Jump
    if key == b' ' and p_z <= 0:
        p_vz = 450.0
        p_vx = 300.0 * math.cos(math.radians(p_angle))
        p_vy = 300.0 * math.sin(math.radians(p_angle))

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    global p_x, p_y, p_z, p_angle, active_knife, clicked_hit, clicked_throw, p_wood, trees, fallen_object_list

    # # Left mouse button (knife movement)
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        initial_z_velocity = 200
        active_knife.append((p_angle,p_x//1, p_y//1, 40+p_z, initial_z_velocity))
        if clicked_throw == False:
            clicked_throw = True
    
    # Right mouse button (bat movement)
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if clicked_hit == False:
            clicked_hit = True
            bat_reach = 180
            
            for i in range(len(zombie1_list) - 1, -1, -1):
                zx, zy, anim, val, hp = zombie1_list[i]
                if math.sqrt((p_x - zx)**2 + (p_y - zy)**2) < bat_reach:
                    hp -= 1
                    if hp <= 0:
                        zombie1_list.pop(i)
                        fallen_object_list.append((zx,zy))
                        if p_x < 0:
                            new_zombiex = 1900 + random.random()*300
                        else:
                            new_zombiex = -1900 + random.random()*300
                        if p_y < 0:
                            new_zombiey = 1900 + random.random()*300
                        else:
                            new_zombiey = -1900 + random.random()*300
                        zombie1_list.append((new_zombiex,new_zombiey,0,0,3))
                    else:
                        zombie1_list[i] = (zx, zy, anim, val, hp)

            # Bat collission with zombie2
            for i in range(len(zombie2_list) - 1, -1, -1):
                zx, zy, anim, val, hp = zombie2_list[i]
                if math.sqrt((p_x - zx)**2 + (p_y - zy)**2) < bat_reach:
                    hp -= 1
                    if hp <= 0:
                        zombie2_list.pop(i)
                        fallen_object_list.append((zx,zy))
                        if p_x < 0:
                            new_zombiex = 1900 + random.random()*300
                        else:
                            new_zombiex = -1900 + random.random()*300
                        if p_y < 0:
                            new_zombiey = 1900 + random.random()*300
                        else:
                            new_zombiey = -1900 + random.random()*300
                        zombie2_list.append((new_zombiex,new_zombiey,0,0,2))
                    else:
                        zombie2_list[i] = (zx, zy, anim, val, hp)

def draw_apples():
    for apple in apples_list:
        glPushMatrix()
        glTranslatef(apple['x'], apple['y'], 8)
        glColor3f(0.8, 0.1, 0.1)
        gluSphere(gluNewQuadric(), 10, 10, 10)

        glTranslatef(0, 0, 5)
        glColor3f(0.1, 0.5, 0.1)
        gluCylinder(gluNewQuadric(), 0.5, 0.5, 4, 5, 1)
        glPopMatrix()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_health():
    global p_health,fallen_object_list,dead_meat_count
    draw_text(10, 770, f"Health: {int(p_health/2)*'|'}")
    draw_text(10, 740, f"Wood: {p_wood}")
    draw_text(10, 710, f"Score: {p_wood*2 + dead_meat_count * 5}")

    # Star promp
    if star_active:
        draw_text(300, 700, f"Eat the star to boost your health!! Time remaining = {int(star_timer)}")

    if is_game_over:
        draw_text(400, 450, "YOU DIED")
        draw_text(370, 400, "Press 'R' to Restart")
        draw_text(400, 350, f"Score : {p_wood*2 + dead_meat_count * 5}")

def idle():
    global p_health, p_x, p_y, bonfire_list, time_t1, dt, last_heal_time, p_z, p_vz, p_vx, p_vy
    global last_time, star_active, star_x, star_y, star_timer, star_cooldown, star_angle, damage_flash_timer

    time_t2 = time.time()
    dt = time_t2 - time_t1

    if time_t2 - last_heal_time > 0.5:
        for bf in bonfire_list:
            # Calculate distance from player to bonfire
            dist = math.sqrt((p_x - bf['x'])**2 + (p_y - bf['y'])**2)
            if dist < 300: 
                if p_health < 100:
                    p_health = min(100, p_health + 2)
                break
        last_heal_time = time_t2

    time_t1 = time_t2

    if damage_flash_timer > 0:
        damage_flash_timer -= dt

    # Jump
    if p_z > 0 or p_vz > 0:
            p_z += p_vz * dt
            p_vz += GRAVITY * dt
            
            next_px = p_x + p_vx * dt
            next_py = p_y + p_vy * dt

            if not check_collision(next_px, p_y):
                p_x = next_px
            if not check_collision(p_x, next_py):
                p_y = next_py
            
            if p_z <= 0:
                p_z = 0
                p_vz = 0
                p_vx = 0 
                p_vy = 0
    
    # Star
    if not star_active:
        star_cooldown -= dt
        if star_cooldown <= 0:
            # Spawn in visible range
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(600, 1200)
            star_x = p_x + math.cos(angle) * dist
            star_y = p_y + math.sin(angle) * dist

            star_x = max(-GRID_LENGTH + 100, min(GRID_LENGTH - 100, star_x))
            star_y = max(-GRID_LENGTH + 100, min(GRID_LENGTH - 100, star_y))
            
            star_active = True
            star_timer = 30
    else:
        star_timer -= dt
        star_angle += 100 * dt

        dist_to_star = math.sqrt((p_x - star_x)**2 + (p_y - star_y)**2)
        if dist_to_star < 120 and p_z < 150:
            p_health = 100
            star_active = False
            star_cooldown = random.uniform(20.0, 60.0)
            
        # Check if timer runs out
        if star_timer <= 0:
            star_active = False
            star_cooldown = random.uniform(20.0, 60.0)

    glutPostRedisplay()

def showScreen():
    global is_game_over

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0, 0, 1000, 800)
    setupCamera()

    draw_floor_and_walls()
    draw_trees()
    draw_bushes()
    draw_buildings()
    draw_obstacles()
    if not is_game_over:
        draw_zombie1()
        draw_zombie2()
        draw_knife()
        draw_apples()
        draw_bat()
    draw_bonfire()
    draw_weather()
    draw_star()
    draw_fallen_object()
    
    draw_health()
    if cam_mode == 3 or cam_mode == 2:
        draw_hero()

    glutSwapBuffers()

def main():
    init_world()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"CSE423 Project G5")
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()