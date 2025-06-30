import datetime
import math
import pygame
import serial
import sys
from time import sleep


# --- Configuration ---
arduino_port = 'COM5' 
baud_rate = 9600
threshold_distance = 50

WIDTH, HEIGHT = 1280, 720

angle = 0
distance = 0
button_pressed = False

COLOR_BG_SEMI_TRANSPARENT = (0, 0, 0, 5) # Black with Low Alpha for the Trail Effect
COLOR_GREEN = (0, 128, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)
COLOR_BUTTON = (200, 200, 200)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)


print()
print(f"Connecting to Arduino on {arduino_port} at {baud_rate} baud...")
arduino = serial.Serial(arduino_port, baud_rate, timeout = 1)

print("Ultrasonic Radar System Booting Up...")
sleep(2)
arduino.write(f"1,{threshold_distance}\n".encode())


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultrasonic Radar System")

fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
fade_surface.fill(COLOR_BG_SEMI_TRANSPARENT)

font_large = pygame.font.SysFont('times-new-roman', 30)
font_small = pygame.font.SysFont('times-new-roman', 20)

button_w, button_h = 200, 25
button_x, button_y = 10, 50
button_rect = pygame.Rect(button_x, button_y, button_w, button_h)

output_file = open("radar.txt", "w")

clock = pygame.time.Clock()


def draw_radar():
    radar_cx = WIDTH // 2
    radar_cy = int(HEIGHT * 0.94)
    max_radius = int(WIDTH * 0.47)

    for i in range(1, 6):
        radius = max_radius * (i / 5)
        pygame.draw.arc(screen, COLOR_GREEN, (radar_cx - radius, radar_cy - radius, 2 * radius, 2 * radius), 0, math.pi, 2)

    for i in range(7):
        angle_rad = math.radians(30 * i)
        end_x = radar_cx - max_radius * math.cos(angle_rad)
        end_y = radar_cy - max_radius * math.sin(angle_rad)
        pygame.draw.line(screen, COLOR_GREEN, (radar_cx, radar_cy), (end_x, end_y), 2)


def draw_line():
    radar_cx = WIDTH // 2
    radar_cy = int(HEIGHT * 0.94)
    max_radius = int(WIDTH * 0.47)

    angle_rad = math.radians(angle)
    end_x = radar_cx + max_radius * math.cos(angle_rad)
    end_y = radar_cy - max_radius * math.sin(angle_rad)
    pygame.draw.line(screen, COLOR_GREEN, (radar_cx, radar_cy), (end_x, end_y), 2)


def draw_object():
    if distance < threshold_distance and distance != 0:
        radar_cx = WIDTH // 2
        radar_cy = int(HEIGHT * 0.94)
        max_radius = int(WIDTH * 0.47)

        mapped_dist = distance / threshold_distance * max_radius
        
        angle_rad = math.radians(angle)
        obj_x = radar_cx + mapped_dist * math.cos(angle_rad)
        obj_y = radar_cy - mapped_dist * math.sin(angle_rad)
        
        if button_pressed:
            pygame.draw.circle(screen, COLOR_RED, (obj_x, obj_y), 5)
        else:
            end_x = radar_cx + max_radius * math.cos(angle_rad)
            end_y = radar_cy - max_radius * math.sin(angle_rad)
            pygame.draw.line(screen, COLOR_RED, (obj_x, obj_y), (end_x, end_y), 4)


def draw_text():
    radar_cy = int(HEIGHT * 0.94)
    max_radius = int(WIDTH * 0.47)
    
    pygame.draw.rect(screen, COLOR_BLACK, (0, radar_cy, WIDTH, HEIGHT - radar_cy))
    pygame.draw.rect(screen, COLOR_BLACK, (0, 0, WIDTH, int(HEIGHT * 0.06)))
    
    if distance >= threshold_distance or distance == 0:
        text_surf = font_large.render("No Object Detected", True, COLOR_YELLOW)
        screen.blit(text_surf, (20, radar_cy + 10))
    else:
        polar_text = f"Polar: ({distance}, {180 - angle}°)"
        dist_text = f"Distance: {distance} cm, Angle: {180 - angle}°"
        
        polar_surf = font_large.render(polar_text, True, COLOR_YELLOW)
        dist_surf = font_large.render(dist_text, True, COLOR_YELLOW)
        
        screen.blit(polar_surf, (20, radar_cy + 10))
        screen.blit(dist_surf, (WIDTH - dist_surf.get_width() - 20, radar_cy + 10))

    now = datetime.datetime.now()
    time_text = now.strftime("%H:%M:%S")
    time_surf = font_large.render(time_text, True, COLOR_YELLOW)
    title_surf = font_large.render("Sonic Seekers", True, COLOR_YELLOW)
    
    screen.blit(title_surf, (10, 5))
    screen.blit(time_surf, (WIDTH - time_surf.get_width() - 10, 5))

    for i in range(1, 6):
        dist_val = i * threshold_distance // 5
        text = f"{dist_val} cm"
        text_surf = font_small.render(text, True, COLOR_YELLOW)
        radius = max_radius * (i / 5)
        screen.blit(text_surf, (WIDTH // 2 + radius - text_surf.get_width() // 2 - 30, radar_cy - text_surf.get_height()))

    for i in range(7):
        angle_deg = 30 * i
        angle_rad = math.radians(angle_deg)
        text = f"{angle_deg}°"
        text_surf = font_small.render(text, True, COLOR_YELLOW)
        
        pos_x = WIDTH // 2 - (max_radius + 20) * math.cos(angle_rad)
        pos_y = radar_cy - (max_radius + 20) * math.sin(angle_rad)
        
        text_rect = text_surf.get_rect(center = (pos_x, pos_y))
        screen.blit(text_surf, text_rect)


def draw_button():
    pygame.draw.rect(screen, COLOR_BUTTON, button_rect)
    text_surf = font_small.render("Initiate Object Search", True, COLOR_BLACK)
    text_rect = text_surf.get_rect(center = button_rect.center)
    screen.blit(text_surf, text_rect)
    

running = True
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    button_pressed = not button_pressed
                    print(f"Button Toggled: {'ON' if button_pressed else 'OFF'}")


        line = arduino.readline().decode().strip()

        if (line):
            data = line.split(',')
            angle = int(data[0])
            distance = int(data[1])

        if distance < threshold_distance and distance != 0:
            now = datetime.datetime.now()
            log_entry = f"{now.strftime('%H:%M:%S')} - {distance}, {180 - angle}\n"
            print(log_entry)
            output_file.write(log_entry)
            output_file.flush()


        screen.blit(fade_surface, (0, 0))
        
        draw_text()
        draw_radar()
        draw_line()
        draw_object()
        draw_button()
        
        pygame.display.flip()

        clock.tick(60)

finally:
    print("Shutting Down...")
    output_file.close()
    arduino.write(f"0,{threshold_distance}\n".encode())
    arduino.close()
    pygame.quit()
    sys.exit()