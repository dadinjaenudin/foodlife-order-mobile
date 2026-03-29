"""
Generate placeholder images for tenants and products using PIL
Creates visually appealing gradient images with text
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodcourt.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import math

def create_gradient_image(width, height, color1, color2, angle=135):
    """Create a gradient background image"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        for x in range(width):
            # Calculate ratio based on angle
            ratio = (x * math.cos(math.radians(angle)) + y * math.sin(math.radians(angle))) / (
                width * abs(math.cos(math.radians(angle))) + height * abs(math.sin(math.radians(angle)))
            )
            ratio = max(0, min(1, ratio))
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.point((x, y), fill=(r, g, b))
    
    return img


def add_decorative_circles(img, color):
    """Add subtle decorative circles to background"""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Add some circles
    for _ in range(5):
        x = random.randint(-50, width + 50)
        y = random.randint(-50, height + 50)
        r = random.randint(30, 100)
        alpha_color = tuple(min(255, c + 30) for c in color[:3])
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(*alpha_color, 60))
    
    return img


def create_food_icon(draw, x, y, size, icon_type, color=(255,255,255)):
    """Draw simple food icons"""
    w = size
    if icon_type == 'bowl':
        # Bowl
        draw.ellipse([x-w//2, y, x+w//2, y+w//2], fill=color)
        draw.arc([x-w//2, y-w//4, x+w//2, y+w//4], 0, 180, fill=color, width=3)
    elif icon_type == 'cup':
        # Cup/Glass
        draw.polygon([x-w//3, y, x+w//3, y, x+w//4, y+w//2, x-w//4, y+w//2], fill=color)
        draw.arc([x-w//3, y-w//8, x+w//3, y+w//8], 0, 180, fill=color, width=2)
    elif icon_type == 'pizza':
        # Pizza slice
        draw.polygon([x, y-w//2, x+w//3, y+w//3, x-w//3, y+w//3], fill=color)
    elif icon_type == 'burger':
        # Burger bun
        draw.ellipse([x-w//2, y-w//4, x+w//2, y+w//4], fill=color)
        draw.rectangle([x-w//2, y, x+w//2, y+w//6], fill=color)
        draw.rectangle([x-w//2, y+w//5, x+w//2, y+w//3], fill=(100, 200, 100))


def create_tenant_logo(tenant_name, emoji, colors, size=(400, 400)):
    """Create a stylish tenant logo"""
    img = create_gradient_image(size[0], size[1], colors[0], colors[1], 135)
    draw = ImageDraw.Draw(img)
    
    # Add decorative circle in background
    cx, cy = size[0]//2, size[1]//2
    for r in range(size[0]//3, size[0]//6, -10):
        alpha = int(30 * (size[0]//3 - r) / (size[0]//6))
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(255,255,255,alpha), width=2)
    
    # White circle background for emoji
    circle_r = size[0]//3
    draw.ellipse([cx-circle_r, cy-circle_r, cx+circle_r, cy+circle_r], fill=(255,255,255,180))
    
    # Emoji
    try:
        font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size[0]//4)
    except:
        font_emoji = ImageFont.load_default()
    
    # Draw emoji text
    bbox = draw.textbbox((0, 0), emoji, font=font_emoji)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text((cx - text_w//2, cy - text_h//2 - 10), emoji, fill=(50,50,50), font=font_emoji)
    
    # Tenant name
    try:
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(12, size[0]//12))
    except:
        font_name = ImageFont.load_default()
    
    name_bbox = draw.textbbox((0, 0), tenant_name[:12], font=font_name)
    name_w = name_bbox[2] - name_bbox[0]
    
    # Name background
    pad = 10
    draw.rounded_rectangle(
        [cx - name_w//2 - pad, size[1]*3//4 - pad, 
         cx + name_w//2 + pad, size[1]*3//4 + name_bbox[3] - name_bbox[1] + pad],
        radius=8, fill=(0,0,0,120)
    )
    draw.text((cx - name_w//2, size[1]*3//4), tenant_name[:12], fill=(255,255,255), font=font_name)
    
    return img


def create_product_image(product_name, emoji, colors, size=(600, 400)):
    """Create an attractive product image"""
    img = create_gradient_image(size[0], size[1], colors[0], colors[1], 135)
    draw = ImageDraw.Draw(img)
    
    cx, cy = size[0]//2, size[1]//2
    
    # Decorative circles
    for i, r in enumerate([size[1]//2, size[1]//3, size[1]//4]):
        opacity = 20 + i * 15
        draw.ellipse([cx-r, cy-r*3//4, cx+r, cy+r*3//4], 
                    outline=(255,255,255), width=1)
    
    # Large emoji in center
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size[1]//3)
    except:
        font_big = ImageFont.load_default()
    
    emoji_bbox = draw.textbbox((0, 0), emoji, font=font_big)
    emoji_w = emoji_bbox[2] - emoji_bbox[0]
    emoji_h = emoji_bbox[3] - emoji_bbox[1]
    
    # Shadow
    draw.text((cx - emoji_w//2 + 4, cy - emoji_h//2 + 4), emoji, fill=(0,0,0,60), font=font_big)
    draw.text((cx - emoji_w//2, cy - emoji_h//2 - size[1]//8), emoji, fill=(255,255,255,230), font=font_big)
    
    # Product name at bottom
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(14, size[0]//20))
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(11, size[0]//28))
    except:
        font_title = ImageFont.load_default()
        font_sub = font_title
    
    # Bottom gradient overlay
    overlay = Image.new('RGBA', size, (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)
    for i in range(80):
        alpha = int(i * 2.5)
        overlay_draw.rectangle([0, size[1]-80+i, size[0], size[1]-80+i+1], fill=(0,0,0,alpha))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Product name
    display_name = product_name[:20] if len(product_name) > 20 else product_name
    name_bbox = draw.textbbox((0, 0), display_name, font=font_title)
    name_w = name_bbox[2] - name_bbox[0]
    draw.text((cx - name_w//2 + 1, size[1]-55+1), display_name, fill=(0,0,0,150), font=font_title)
    draw.text((cx - name_w//2, size[1]-55), display_name, fill=(255,255,255), font=font_title)
    
    return img


def create_banner_image(tenant_name, emoji, tagline, colors, size=(800, 300)):
    """Create a tenant banner image"""
    img = create_gradient_image(size[0], size[1], colors[0], colors[1], 135)
    draw = ImageDraw.Draw(img)
    
    # Decorative elements
    for i in range(3):
        x = random.randint(size[0]//2, size[0])
        y = random.randint(0, size[1])
        r = random.randint(50, 150)
        draw.ellipse([x-r, y-r, x+r, y+r], outline=(255,255,255,30), width=2)
    
    # Big emoji on right
    try:
        font_emoji = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size[1]//2)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size[1]//4)
        font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size[1]//6)
    except:
        font_emoji = ImageFont.load_default()
        font_title = font_emoji
        font_tag = font_emoji
    
    # Emoji on right side
    emoji_bbox = draw.textbbox((0, 0), emoji, font=font_emoji)
    emoji_w = emoji_bbox[2] - emoji_bbox[0]
    draw.text((size[0] - emoji_w - 20, size[1]//2 - emoji_bbox[3]//2), emoji, fill=(255,255,255,180), font=font_emoji)
    
    # Tenant name
    draw.text((40, size[1]//4), tenant_name, fill=(255,255,255), font=font_title)
    
    # Tagline
    draw.text((42, size[1]//4 + size[1]//4 + 5), tagline, fill=(255,255,255,200), font=font_tag)
    
    return img


# Color palettes for each tenant
TENANT_CONFIGS = [
    {
        'name': 'Warung Nusantara',
        'emoji': '🍛',
        'tagline': 'Masakan Nusantara Terlezat',
        'colors': [(255, 107, 53), (192, 37, 0)],
        'color_theme': 'orange',
        'slug': 'warung-nusantara',
    },
    {
        'name': 'Bakmi Jago',
        'emoji': '🍜',
        'tagline': 'Mie Segar Setiap Hari',
        'colors': [(255, 195, 0), (200, 120, 0)],
        'color_theme': 'yellow',
        'slug': 'bakmi-jago',
    },
    {
        'name': 'Geprek Sultan',
        'emoji': '🍗',
        'tagline': 'Ayam Geprek Juara',
        'colors': [(220, 38, 38), (153, 27, 27)],
        'color_theme': 'red',
        'slug': 'geprek-sultan',
    },
    {
        'name': 'Soto Betawi Bu Sri',
        'emoji': '🥣',
        'tagline': 'Soto Gurih & Nikmat',
        'colors': [(245, 158, 11), (180, 100, 0)],
        'color_theme': 'orange',
        'slug': 'soto-betawi-bu-sri',
    },
    {
        'name': 'Kopi Kekinian',
        'emoji': '☕',
        'tagline': 'Kopi Lokal Terbaik',
        'colors': [(92, 64, 51), (44, 24, 16)],
        'color_theme': 'indigo',
        'slug': 'kopi-kekinian',
    },
    {
        'name': 'Pizza Bros',
        'emoji': '🍕',
        'tagline': 'Pizza Authentic Italia',
        'colors': [(234, 88, 12), (154, 52, 18)],
        'color_theme': 'orange',
        'slug': 'pizza-bros',
    },
    {
        'name': 'Sushi Zen',
        'emoji': '🍱',
        'tagline': 'Japanese Food Authentic',
        'colors': [(239, 68, 68), (127, 29, 29)],
        'color_theme': 'red',
        'slug': 'sushi-zen',
    },
    {
        'name': 'Juice Paradise',
        'emoji': '🥤',
        'tagline': 'Fresh Juice Every Day',
        'colors': [(34, 197, 94), (21, 128, 61)],
        'color_theme': 'green',
        'slug': 'juice-paradise',
    },
    {
        'name': 'Bakso Malang Pak Kumis',
        'emoji': '🥩',
        'tagline': 'Bakso Kenyal & Gurih',
        'colors': [(99, 102, 241), (67, 56, 202)],
        'color_theme': 'indigo',
        'slug': 'bakso-malang-pak-kumis',
    },
    {
        'name': 'Dessert House',
        'emoji': '🍰',
        'tagline': 'Sweet Treats & Cakes',
        'colors': [(236, 72, 153), (157, 23, 77)],
        'color_theme': 'pink',
        'slug': 'dessert-house',
    },
]

PRODUCT_DATA = {
    'warung-nusantara': {
        'emojis': ['🍛', '🍚', '🍖', '🥘', '🫕', '🍲', '🥗', '🌶️', '🍱', '🍛', '🫙', '🧆', '🥙', '🧂', '🍢', '🥫', '🍜', '🫔', '🧇', '🍣'],
        'products': [
            'Nasi Rendang Daging', 'Nasi Padang Komplit', 'Ayam Gulai Santan', 'Nasi Goreng Kampung',
            'Ikan Bakar Bumbu Kuning', 'Sayur Lodeh Santan', 'Perkedel Kentang', 'Tempe Orek Kecap',
            'Sambal Goreng Ati', 'Tahu Balado Pedas', 'Pindang Iga Sapi', 'Lontong Cap Gomeh',
            'Sate Padang Komplit', 'Dendeng Balado', 'Nasi Kuning Tumpeng', 'Opor Ayam Kuning',
            'Semur Daging Sapi', 'Pepes Ikan Mas', 'Kari Ayam Santan', 'Es Teh Manis'
        ]
    },
    'bakmi-jago': {
        'emojis': ['🍜', '🥡', '🫕', '🥢', '🍲', '🌶️', '🧄', '🥩', '🍳', '🥚', '🦐', '🥬', '🧅', '🍱', '🫙', '🥗', '🫒', '🫕', '🧆', '🥘'],
        'products': [
            'Bakmi Ayam Original', 'Bakmi Kuah Spesial', 'Mie Goreng Seafood', 'Kwetiau Sapi Goreng',
            'Bihun Goreng Ayam', 'Mie Yamin Spesial', 'Bakmi Pangsit Rebus', 'Mie Tek-Tek Goreng',
            'Capcay Kuah Spesial', 'Nasi Goreng Teri', 'Pangsit Goreng Renyah', 'Dimsum Ayam',
            'Siomay Bandung', 'Batagor Renyah', 'Kwetiau Kuah Sapi', 'Mie Aceh Pedas',
            'Bakso Urat Spesial', 'Mie Campur Seafood', 'Lontong Sayur', 'Es Jeruk Segar'
        ]
    },
    'geprek-sultan': {
        'emojis': ['🍗', '🌶️', '🍚', '🧄', '🫙', '🥵', '🔥', '🍋', '🧆', '🫔', '🥗', '🧅', '🍳', '🥚', '🧇', '🫕', '🥙', '🥘', '🍱', '🥤'],
        'products': [
            'Ayam Geprek Level 5', 'Ayam Geprek Keju', 'Ayam Bakar Kecap', 'Ayam Goreng Crispy',
            'Nasi Ayam Geprek Komplit', 'Geprek Sambal Matah', 'Ayam Geprek Mozarella', 'Paket Hemat Geprek',
            'Geprek Sambal Bawang', 'Ayam Kuah Kuning', 'Telur Ceplok Sambal', 'Tahu Tempe Balado',
            'Nasi Putih Hangat', 'Lalap Segar', 'Kentang Goreng', 'Es Teh Tawar',
            'Es Jeruk Peras', 'Geprek Double Crispy', 'Sayur Asem', 'Jus Mangga Segar'
        ]
    },
    'soto-betawi-bu-sri': {
        'emojis': ['🥣', '🫕', '🍖', '🧅', '🌿', '🧄', '🥛', '🍋', '🧆', '🥚', '🥘', '🫙', '🍱', '🍚', '🧇', '🫔', '🥗', '🥩', '🍲', '🥤'],
        'products': [
            'Soto Betawi Asli', 'Soto Betawi Susu', 'Soto Daging Sapi', 'Ketoprak Betawi',
            'Nasi Uduk Komplit', 'Bubur Ayam Spesial', 'Soto Ayam Kampung', 'Rawon Surabaya',
            'Lontong Sayur Padang', 'Nasi Rames Spesial', 'Sup Iga Sapi', 'Empal Gentong',
            'Sate Padang Mini', 'Pecel Lele Goreng', 'Ayam Penyet Spesial', 'Es Jeruk Nipis',
            'Teh Tarik Panas', 'Kerupuk Udang', 'Sambal Terong', 'Es Campur Segar'
        ]
    },
    'kopi-kekinian': {
        'emojis': ['☕', '🧋', '🥛', '🫖', '🍵', '🧊', '🍫', '🫙', '🧆', '🥧', '🍰', '🧁', '🍩', '🥐', '🫔', '🧇', '🍪', '🎂', '🍮', '🥤'],
        'products': [
            'Kopi Hitam Tubruk', 'Cappuccino Panas', 'Latte Art Susu', 'Es Kopi Susu Gula Aren',
            'Americano Dingin', 'Matcha Latte Panas', 'Teh Tarik Panas', 'Brown Sugar Boba Milk',
            'Caramel Macchiato', 'Vanilla Latte', 'Milo Dinosaur', 'Chocolate Frappe',
            'Kopi V60 Specialty', 'Affogato Es Krim', 'Red Velvet Latte', 'Croissant Mentega',
            'Roti Bakar Coklat', 'Pancake Susu', 'Waffle Madu', 'Cake Slice Tiramisu'
        ]
    },
    'pizza-bros': {
        'emojis': ['🍕', '🧀', '🍖', '🌶️', '🫒', '🧅', '🍅', '🌿', '🫙', '🥩', '🧄', '🥚', '🍗', '🥗', '🫔', '🧆', '🍱', '🥘', '🫕', '🥤'],
        'products': [
            'Pizza Margherita', 'Pizza Pepperoni', 'Pizza BBQ Chicken', 'Pizza 4 Keju',
            'Pizza Seafood Spesial', 'Pizza Vegetarian', 'Pizza Hawaiian', 'Pizza Meat Lovers',
            'Calzone Spesial', 'Garlic Bread', 'Bruschetta Tomat', 'Pasta Carbonara',
            'Pasta Bolognese', 'Spaghetti Aglio Olio', 'Lasagna Daging', 'Chicken Wings',
            'Mozzarella Sticks', 'Caesar Salad', 'Tiramisu Slice', 'Minuman Soda'
        ]
    },
    'sushi-zen': {
        'emojis': ['🍱', '🍣', '🦐', '🥢', '🍙', '🫙', '🥗', '🧆', '🍜', '🫕', '🥘', '🍲', '🧅', '🌿', '🧄', '🥚', '🫔', '🍛', '🥩', '🥤'],
        'products': [
            'Sushi Salmon Roll', 'Sashimi Tuna Segar', 'California Roll', 'Dragon Roll Spesial',
            'Edamame Rebus', 'Miso Soup', 'Gyoza Goreng', 'Takoyaki Gurita',
            'Ramen Tonkotsu', 'Karaage Chicken', 'Tempura Udang', 'Yakiniku Beef',
            'Onigiri Tuna Mayo', 'Udon Kuah', 'Soba Dingin', 'Dorayaki Coklat',
            'Mochi Es Krim', 'Green Tea Soft Serve', 'Ramune Soda', 'Bento Box Set'
        ]
    },
    'juice-paradise': {
        'emojis': ['🥤', '🍹', '🍊', '🍉', '🍎', '🥭', '🍋', '🫐', '🍓', '🥝', '🍇', '🍌', '🥥', '🍑', '🫒', '🌿', '🧊', '🍫', '🥛', '🧋'],
        'products': [
            'Jus Mangga Segar', 'Jus Semangka', 'Jus Jeruk Peras', 'Jus Alpukat Kental',
            'Jus Strawberry', 'Jus Wortel Apel', 'Smoothie Green Detox', 'Jus Melon Mint',
            'Coconut Shake', 'Mixed Berry Smoothie', 'Jus Nanas Segar', 'Teh Leci Segar',
            'Boba Taro Milk Tea', 'Matcha Boba', 'Es Kelapa Muda', 'Lemon Tea Panas',
            'Infused Water Mentimun', 'Açaí Bowl', 'Fruit Salad Segar', 'Es Cincau Pandan'
        ]
    },
    'bakso-malang-pak-kumis': {
        'emojis': ['🥩', '🫕', '🍲', '🥢', '🧆', '🌶️', '🧅', '🧄', '🫙', '🍖', '🥘', '🍜', '🍱', '🥗', '🫔', '🧇', '🍳', '🥚', '🧂', '🥤'],
        'products': [
            'Bakso Urat Spesial', 'Bakso Goreng Renyah', 'Bakso Keju Meleleh', 'Bakso Halus Sapi',
            'Mie Bakso Kuah', 'Bakso Bakar Pedas', 'Tahu Bakso Goreng', 'Siomay Bakso',
            'Bakso Jumbo Komplit', 'Mie Ayam Bakso', 'Bihun Bakso Kuah', 'Bakso Beranak',
            'Pentol Goreng Crispy', 'Bakso Telur Puyuh', 'Kwetiau Bakso', 'Es Teh Manis',
            'Es Jeruk Bakso', 'Tahu Kulit Isi', 'Pangsit Goreng', 'Jus Tomat'
        ]
    },
    'dessert-house': {
        'emojis': ['🍰', '🎂', '🧁', '🍩', '🍪', '🍫', '🍮', '🥧', '🍭', '🍬', '🧆', '🥐', '🫔', '🍱', '🧇', '🥞', '🍦', '🍧', '🍨', '🥤'],
        'products': [
            'Cheesecake Blueberry', 'Tiramisu Slice', 'Chocolate Lava Cake', 'Red Velvet Cake',
            'Mille Crepes', 'Croissant Almond', 'Donut Glaze Rainbow', 'Macaroon Vanilla',
            'Brownies Fudgy', 'Banana Foster', 'Panna Cotta Strawberry', 'Creme Brulee',
            'Waffle Ice Cream', 'Churros Coklat', 'Pudding Karamel', 'Klepon Coklat',
            'Bingsu Matcha', 'Frappe Oreo', 'Affogato Espresso', 'Es Krim Gelato Mix'
        ]
    }
}


def generate_all_images():
    """Generate all tenant logos, banners, and product images"""
    
    os.makedirs('media/tenants', exist_ok=True)
    os.makedirs('media/tenants/banners', exist_ok=True)
    os.makedirs('media/products', exist_ok=True)
    
    print("🎨 Generating images for all tenants and products...")
    
    for i, tenant_config in enumerate(TENANT_CONFIGS):
        slug = tenant_config['slug']
        colors = [tuple(c) for c in tenant_config['colors']]
        
        # Darker version for second color
        colors_dark = [colors[0], tuple(max(0, c-50) for c in colors[0])]
        
        print(f"\n📸 {tenant_config['name']}...")
        
        # 1. Generate Logo
        logo_path = f'media/tenants/{slug}_logo.png'
        logo = create_tenant_logo(tenant_config['name'], tenant_config['emoji'], colors)
        logo.save(logo_path, 'PNG', quality=95)
        print(f"  ✓ Logo saved")
        
        # 2. Generate Banner
        banner_path = f'media/tenants/banners/{slug}_banner.jpg'
        banner = create_banner_image(
            tenant_config['name'], tenant_config['emoji'], 
            tenant_config['tagline'], colors, (800, 300)
        )
        banner.save(banner_path, 'JPEG', quality=90)
        print(f"  ✓ Banner saved")
        
        # 3. Generate Product Images
        if slug in PRODUCT_DATA:
            product_info = PRODUCT_DATA[slug]
            emojis = product_info['emojis']
            products = product_info['products']
            
            for j, (product_name, emoji) in enumerate(zip(products, emojis)):
                # Slightly vary colors for each product
                hue_shift = j * 10
                p_colors = [
                    tuple(min(255, max(0, c + hue_shift - 20)) for c in colors[0]),
                    tuple(min(255, max(0, c + hue_shift - 40)) for c in colors[1])
                ]
                
                product_slug = product_name.lower().replace(' ', '_').replace('/', '_')[:30]
                product_path = f'media/products/{slug}_{j+1:02d}_{product_slug}.jpg'
                
                product_img = create_product_image(product_name, emoji, p_colors)
                product_img.save(product_path, 'JPEG', quality=85)
            
            print(f"  ✓ {len(products)} product images saved")
    
    print("\n✅ All images generated successfully!")
    return True


if __name__ == '__main__':
    generate_all_images()
