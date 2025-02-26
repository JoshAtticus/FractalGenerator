import pygame
import numpy as np

# Window settings
WIDTH, HEIGHT = 800, 800
MAX_ITER = 100
FPS = 30
ZOOM_SPEED = 0.1  # Smaller value = smoother zoom

# Initial view settings
zoom = 1.0
target_zoom = 1.0
offset_x, offset_y = 0.0, 0.0

def mandelbrot_vectorized(h, w, max_iter, zoom, offset_x, offset_y):
    """Vectorized Mandelbrot computation using NumPy"""
    y, x = np.ogrid[-1.4:1.4:h*1j, -2:0.8:w*1j]
    x = x/zoom - offset_x
    y = y/zoom - offset_y
    c = x + y*1j
    z = c
    divtime = max_iter + np.zeros(z.shape, dtype=int)

    for i in range(max_iter):
        z = z**2 + c
        diverge = z*np.conj(z) > 2**2
        div_now = diverge & (divtime == max_iter)
        divtime[div_now] = i
        z[diverge] = 2

    return divtime

def generate_fractal(surface, zoom, offset_x, offset_y, quality_level=1, reveal_progress=1.0):
    """Generates and draws the Mandelbrot fractal with animation effects"""
    w, h = surface.get_size()
    
    scale = 2 ** (4 - quality_level)
    w_scaled = w // scale
    h_scaled = h // scale
    
    divtime = mandelbrot_vectorized(h_scaled, w_scaled, MAX_ITER, zoom, offset_x, offset_y)
    
    # Create colorful output with sweep effect
    pixels = np.zeros((h_scaled, w_scaled, 3), dtype=np.uint8)
    sweep_line = int(h_scaled * reveal_progress)
    
    # Only render up to the sweep line
    if sweep_line > 0:
        pixels[:sweep_line, :, 0] = divtime[:sweep_line, :] % 8 * 32
        pixels[:sweep_line, :, 1] = divtime[:sweep_line, :] % 16 * 16
        pixels[:sweep_line, :, 2] = divtime[:sweep_line, :] % 32 * 8

    if scale > 1:
        pixels = pixels.repeat(scale, axis=0).repeat(scale, axis=1)
    
    pygame.surfarray.blit_array(surface, pixels)

def main():
    global zoom, target_zoom, offset_x, offset_y
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mandelbrot Fractal Viewer")
    clock = pygame.time.Clock()
    running = True
    moving = False
    render_quality = 1
    reveal_progress = 0.0  # New animation progress variable
    
    while running:
        screen.fill((0, 0, 0))
        
        # Smooth zoom
        if abs(zoom - target_zoom) > 0.01:
            zoom += (target_zoom - zoom) * ZOOM_SPEED
            moving = True
        else:
            zoom = target_zoom
        
        # Progressive rendering when not moving
        if not moving:
            if reveal_progress < 1.0:
                reveal_progress += 0.02  # Sweeping animation speed
            elif render_quality < 4:
                render_quality += 1
                reveal_progress = 0.0  # Reset sweep for next quality level
        else:
            render_quality = 1
            reveal_progress = 1.0  # Show full image while moving
            
        generate_fractal(screen, zoom, offset_x, offset_y, render_quality, reveal_progress)
        pygame.display.flip()
        
        moving = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                target_zoom *= 1.1 if event.y > 0 else 0.9
                moving = True
                render_quality = 1  # Reset quality when zooming
            
        keys = pygame.key.get_pressed()
        move_speed = 0.1 / zoom
        if any([keys[k] for k in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]]):
            moving = True
            render_quality = 1  # Reset quality when moving
            
        if keys[pygame.K_UP]: offset_y -= move_speed
        if keys[pygame.K_DOWN]: offset_y += move_speed
        if keys[pygame.K_LEFT]: offset_x -= move_speed
        if keys[pygame.K_RIGHT]: offset_x += move_speed
        
        clock.tick(FPS)
        
        # Slow down the animation
        if not moving and reveal_progress < 1.0:
            pygame.time.wait(20)  # Adjust this value to change animation speed

    pygame.quit()

if __name__ == "__main__":
    main()