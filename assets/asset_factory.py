"""
Fish Quest - Ocean Adventure Game
Procedural Asset Generator

Generates theme-consistent high-resolution underwater backgrounds, cartoon fish,
hearts, and coins without requiring external asset downloads.
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

from config.settings import IMAGES_DIR, BACKGROUNDS_DIR, SCREEN_WIDTH, SCREEN_HEIGHT


def generate_ocean_background():
    """Generates an atmospheric underwater gradient background with caustic light rays and coral floor."""
    bg_path = BACKGROUNDS_DIR / "ocean_bg.png"
    if bg_path.exists():
        return

    img = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), (10, 25, 48, 255))
    draw = ImageDraw.Draw(img)

    # Vertical gradient from deep sapphire blue to dark midnight abyss
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(18 * (1 - ratio) + 6 * ratio)
        g = int(58 * (1 - ratio) + 14 * ratio)
        b = int(112 * (1 - ratio) + 32 * ratio)
        draw.line([(0, y), (SCREEN_WIDTH, y)], fill=(r, g, b, 255))

    # Sun shafts / caustic light beams descending from top
    rays = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
    ray_draw = ImageDraw.Draw(rays)
    for i in range(7):
        top_x = 100 + i * 140
        width_top = 40
        bottom_x = top_x + 80
        width_bottom = 120
        poly = [
            (top_x - width_top // 2, 0),
            (top_x + width_top // 2, 0),
            (bottom_x + width_bottom // 2, SCREEN_HEIGHT),
            (bottom_x - width_bottom // 2, SCREEN_HEIGHT)
        ]
        alpha = int(22 + (i % 3) * 10)
        ray_draw.polygon(poly, fill=(120, 220, 255, alpha))

    rays = rays.filter(ImageFilter.GaussianBlur(radius=20))
    img = Image.alpha_composite(img, rays)

    # Coral silhouettes at the bottom floor
    coral = Image.new("RGBA", (SCREEN_WIDTH, SCREEN_HEIGHT), (0, 0, 0, 0))
    coral_draw = ImageDraw.Draw(coral)

    # Sandy floor curve
    floor_points = [(0, SCREEN_HEIGHT)]
    for x in range(0, SCREEN_WIDTH + 20, 20):
        y = SCREEN_HEIGHT - 45 + int(math.sin(x * 0.015) * 12)
        floor_points.append((x, y))
    floor_points.append((SCREEN_WIDTH, SCREEN_HEIGHT))
    coral_draw.polygon(floor_points, fill=(8, 18, 36, 230))

    # Coral branches and seaweed mounds
    for i in range(14):
        cx = 40 + i * 75
        cy = SCREEN_HEIGHT - 35
        cr = 25 + (i % 4) * 8
        color = (12 + (i * 5) % 30, 28 + (i * 8) % 40, 52 + (i * 6) % 50, 220)
        coral_draw.ellipse([cx - cr, cy - cr * 2, cx + cr, cy + cr], fill=color)

    coral = coral.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(img, coral)

    BACKGROUNDS_DIR.mkdir(parents=True, exist_ok=True)
    img.save(bg_path, "PNG")
    print(f"Generated ocean background: {bg_path}")


def generate_fish_sprite():
    """Generates a cartoon clownfish icon."""
    fish_path = IMAGES_DIR / "fish_icon.png"
    if fish_path.exists():
        return

    size = (160, 110)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Tail fin
    draw.polygon([(40, 55), (10, 25), (10, 85)], fill=(249, 115, 22, 255))
    draw.polygon([(10, 25), (5, 30), (5, 80), (10, 85)], fill=(255, 255, 255, 255))

    # Main fish body (oval)
    draw.ellipse([30, 20, 140, 90], fill=(249, 115, 22, 255))

    # White stripes
    draw.arc([55, 22, 85, 88], start=270, end=90, fill=(255, 255, 255, 255), width=10)
    draw.arc([90, 25, 120, 85], start=270, end=90, fill=(255, 255, 255, 255), width=8)

    # Dorsal fin
    draw.polygon([(65, 22), (95, 8), (115, 24)], fill=(234, 88, 12, 255))

    # Eye
    draw.ellipse([112, 38, 128, 54], fill=(255, 255, 255, 255))
    draw.ellipse([120, 42, 127, 49], fill=(15, 23, 42, 255))
    draw.ellipse([124, 43, 126, 45], fill=(255, 255, 255, 255))  # shine

    # Smiling mouth
    draw.arc([122, 60, 138, 72], start=20, end=140, fill=(15, 23, 42, 255), width=2)

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    img.save(fish_path, "PNG")
    print(f"Generated fish sprite: {fish_path}")


def generate_ui_icons():
    """Generates heart, coin, and chest icons."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Heart icon (Life)
    heart_path = IMAGES_DIR / "heart.png"
    if not heart_path.exists():
        h_img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(h_img)
        # Left lobe, right lobe, bottom triangle
        h_draw.ellipse([6, 8, 26, 28], fill=(244, 63, 94, 255))
        h_draw.ellipse([22, 8, 42, 28], fill=(244, 63, 94, 255))
        h_draw.polygon([(7, 22), (41, 22), (24, 42)], fill=(244, 63, 94, 255))
        # Highlight shine
        h_draw.ellipse([11, 12, 17, 18], fill=(255, 255, 255, 180))
        h_img.save(heart_path, "PNG")

    # 2. Coin icon (Currency)
    coin_path = IMAGES_DIR / "coin.png"
    if not coin_path.exists():
        c_img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(c_img)
        # Outer coin
        c_draw.ellipse([4, 4, 44, 44], fill=(245, 158, 11, 255))
        c_draw.ellipse([8, 8, 40, 40], fill=(251, 191, 36, 255))
        # Inner ring
        c_draw.ellipse([13, 13, 35, 35], outline=(217, 119, 6, 255), width=2)
        # Star or sparkle in center
        c_draw.polygon([(24, 16), (26, 22), (32, 24), (26, 26), (24, 32), (22, 26), (16, 24), (22, 22)], fill=(254, 240, 138, 255))
        c_img.save(coin_path, "PNG")


def generate_all_assets():
    """Generates all procedural graphics."""
    generate_ocean_background()
    generate_fish_sprite()
    generate_ui_icons()


if __name__ == "__main__":
    generate_all_assets()

