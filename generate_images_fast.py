"""
Fast image generator using simple PIL operations
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodcourt.settings')

from PIL import Image, ImageDraw, ImageFont
import math

def create_gradient_fast(width, height, c1, c2):
    """Fast gradient using numpy-like approach with PIL"""
    img = Image.new('RGB', (width, height))
    for y in range(height):
        ratio = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))
    return img

def make_logo(width, height, c1, c2, text, emoji_text):
    """Create logo image with gradient and text"""
    # Use horizontal gradient strips for speed
    img = Image.new('RGB', (width, height), c1)
    draw = ImageDraw.Draw(img)
    
    # Draw gradient bands
    for i in range(height):
        ratio = i / height
        r = int(c1[0] + (c2[0]-c1[0]) * ratio)
        g = int(c1[1] + (c2[1]-c1[1]) * ratio)
        b = int(c1[2] + (c2[2]-c1[2]) * ratio)
        draw.line([(0,i),(width,i)], fill=(r,g,b))
    
    # Circle background
    cx, cy = width//2, height//2
    r = min(width, height)//3
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255,255,255,180))
    
    # Draw centered text
    try:
        fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", height//5)
        fnt_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", height//8)
    except:
        fnt = ImageFont.load_default()
        fnt_small = fnt
    
    # Center text
    bb = draw.textbbox((0,0), emoji_text[:2], font=fnt)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx-tw//2, cy-th//2-5), emoji_text[:2], fill=(30,30,30), font=fnt)
    
    # Bottom name
    name = text[:12]
    bb2 = draw.textbbox((0,0), name, font=fnt_small)
    tw2 = bb2[2]-bb2[0]
    draw.rectangle([cx-tw2//2-8, height*3//4-4, cx+tw2//2+8, height*3//4+bb2[3]-bb2[1]+4], fill=(0,0,0,150))
    draw.text((cx-tw2//2, height*3//4), name, fill='white', font=fnt_small)
    
    return img

def make_product(width, height, c1, c2, name, symbol):
    """Create product image"""
    img = Image.new('RGB', (width, height), c1)
    draw = ImageDraw.Draw(img)
    
    for i in range(height):
        ratio = i/height
        r = int(c1[0]*(1-ratio) + c2[0]*ratio)
        g = int(c1[1]*(1-ratio) + c2[1]*ratio)
        b = int(c1[2]*(1-ratio) + c2[2]*ratio)
        draw.line([(0,i),(width,i)], fill=(r,g,b))
    
    # Decorative circle
    cx, cy = width//2, height//2
    rc = min(width,height)//3
    draw.ellipse([cx-rc, cy-rc, cx+rc, cy+rc], outline=(255,255,255,80), width=2)
    draw.ellipse([cx-rc//2, cy-rc//2, cx+rc//2, cy+rc//2], outline=(255,255,255,60), width=2)
    
    # Symbol in center
    try:
        fnt_lg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", height//3)
        fnt_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(12, width//18))
    except:
        fnt_lg = ImageFont.load_default()
        fnt_sm = fnt_lg
    
    # Large symbol
    sym = symbol[:1] if symbol else "F"
    bb = draw.textbbox((0,0), sym, font=fnt_lg)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    draw.text((cx-tw//2+2, cy-th//2+2), sym, fill=(0,0,0,60), font=fnt_lg)
    draw.text((cx-tw//2, cy-th//2), sym, fill=(255,255,255,220), font=fnt_lg)
    
    # Bottom overlay
    draw.rectangle([0, height-45, width, height], fill=(0,0,0,160))
    
    # Product name
    pname = name[:22]
    bb2 = draw.textbbox((0,0), pname, font=fnt_sm)
    tw2 = bb2[2]-bb2[0]
    draw.text((cx-tw2//2, height-40), pname, fill='white', font=fnt_sm)
    
    return img

def make_banner(width, height, c1, c2, name, tagline):
    """Create banner"""
    img = Image.new('RGB', (width, height), c1)
    draw = ImageDraw.Draw(img)
    
    for i in range(height):
        ratio = i/height
        r = int(c1[0]*(1-ratio) + c2[0]*ratio)
        g = int(c1[1]*(1-ratio) + c2[1]*ratio)
        b = int(c1[2]*(1-ratio) + c2[2]*ratio)
        draw.line([(0,i),(width,i)], fill=(r,g,b))
    
    # Decorative circles on right
    for rr in [height, height*2//3, height//2]:
        draw.ellipse([width-rr-20, height//2-rr, width+rr-20, height//2+rr], outline=(255,255,255,20), width=2)
    
    try:
        fnt_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", height//3)
        fnt_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", height//6)
    except:
        fnt_title = ImageFont.load_default()
        fnt_tag = fnt_title
    
    draw.text((40, height//8), name[:20], fill='white', font=fnt_title)
    draw.text((42, height//8 + height//3 + 8), tagline[:40], fill=(255,255,255,200), font=fnt_tag)
    
    return img

# Tenant configs
TENANTS = [
    ('warung-nusantara', 'Warung Nusantara', 'Masakan Nusantara Terlezat', (255,107,53), (180,37,0), 'NS'),
    ('bakmi-jago', 'Bakmi Jago', 'Mie Segar Setiap Hari', (255,195,0), (200,120,0), 'BJ'),
    ('geprek-sultan', 'Geprek Sultan', 'Ayam Geprek Juara', (220,38,38), (140,20,20), 'GS'),
    ('soto-betawi-bu-sri', 'Soto Betawi Bu Sri', 'Soto Gurih & Nikmat', (245,158,11), (180,100,0), 'SB'),
    ('kopi-kekinian', 'Kopi Kekinian', 'Kopi Lokal Terbaik', (92,64,51), (44,24,16), 'KK'),
    ('pizza-bros', 'Pizza Bros', 'Pizza Authentic Italia', (234,88,12), (140,40,10), 'PB'),
    ('sushi-zen', 'Sushi Zen', 'Japanese Food Authentic', (220,38,38), (100,20,20), 'SZ'),
    ('juice-paradise', 'Juice Paradise', 'Fresh Juice Every Day', (34,197,94), (15,110,50), 'JP'),
    ('bakso-malang-pak-kumis', 'Bakso Malang', 'Bakso Kenyal & Gurih', (99,102,241), (55,50,180), 'BM'),
    ('dessert-house', 'Dessert House', 'Sweet Treats & Cakes', (236,72,153), (140,20,80), 'DH'),
]

PRODUCT_NAMES = {
    'warung-nusantara': [
        'Nasi Rendang Daging', 'Nasi Padang Komplit', 'Ayam Gulai Santan', 'Nasi Goreng Kampung',
        'Ikan Bakar Bumbu Kuning', 'Sayur Lodeh Santan', 'Perkedel Kentang', 'Tempe Orek Kecap',
        'Sambal Goreng Ati', 'Tahu Balado Pedas', 'Pindang Iga Sapi', 'Lontong Cap Gomeh',
        'Sate Padang Komplit', 'Dendeng Balado', 'Nasi Kuning Tumpeng', 'Opor Ayam Kuning',
        'Semur Daging Sapi', 'Pepes Ikan Mas', 'Kari Ayam Santan', 'Es Teh Manis'
    ],
    'bakmi-jago': [
        'Bakmi Ayam Original', 'Bakmi Kuah Spesial', 'Mie Goreng Seafood', 'Kwetiau Sapi Goreng',
        'Bihun Goreng Ayam', 'Mie Yamin Spesial', 'Bakmi Pangsit Rebus', 'Mie Tek-Tek Goreng',
        'Capcay Kuah Spesial', 'Nasi Goreng Teri', 'Pangsit Goreng Renyah', 'Dimsum Ayam',
        'Siomay Bandung', 'Batagor Renyah', 'Kwetiau Kuah Sapi', 'Mie Aceh Pedas',
        'Bakso Urat Spesial', 'Mie Campur Seafood', 'Lontong Sayur', 'Es Jeruk Segar'
    ],
    'geprek-sultan': [
        'Ayam Geprek Level 5', 'Ayam Geprek Keju', 'Ayam Bakar Kecap', 'Ayam Goreng Crispy',
        'Nasi Ayam Geprek Komplit', 'Geprek Sambal Matah', 'Ayam Geprek Mozarella', 'Paket Hemat Geprek',
        'Geprek Sambal Bawang', 'Ayam Kuah Kuning', 'Telur Ceplok Sambal', 'Tahu Tempe Balado',
        'Nasi Putih Hangat', 'Lalap Segar', 'Kentang Goreng', 'Es Teh Tawar',
        'Es Jeruk Peras', 'Geprek Double Crispy', 'Sayur Asem', 'Jus Mangga Segar'
    ],
    'soto-betawi-bu-sri': [
        'Soto Betawi Asli', 'Soto Betawi Susu', 'Soto Daging Sapi', 'Ketoprak Betawi',
        'Nasi Uduk Komplit', 'Bubur Ayam Spesial', 'Soto Ayam Kampung', 'Rawon Surabaya',
        'Lontong Sayur Padang', 'Nasi Rames Spesial', 'Sup Iga Sapi', 'Empal Gentong',
        'Sate Padang Mini', 'Pecel Lele Goreng', 'Ayam Penyet Spesial', 'Es Jeruk Nipis',
        'Teh Tarik Panas', 'Kerupuk Udang', 'Sambal Terong', 'Es Campur Segar'
    ],
    'kopi-kekinian': [
        'Kopi Hitam Tubruk', 'Cappuccino Panas', 'Latte Art Susu', 'Es Kopi Susu Gula Aren',
        'Americano Dingin', 'Matcha Latte Panas', 'Teh Tarik Panas', 'Brown Sugar Boba Milk',
        'Caramel Macchiato', 'Vanilla Latte', 'Milo Dinosaur', 'Chocolate Frappe',
        'Kopi V60 Specialty', 'Affogato Es Krim', 'Red Velvet Latte', 'Croissant Mentega',
        'Roti Bakar Coklat', 'Pancake Susu', 'Waffle Madu', 'Cake Slice Tiramisu'
    ],
    'pizza-bros': [
        'Pizza Margherita', 'Pizza Pepperoni', 'Pizza BBQ Chicken', 'Pizza 4 Keju',
        'Pizza Seafood Spesial', 'Pizza Vegetarian', 'Pizza Hawaiian', 'Pizza Meat Lovers',
        'Calzone Spesial', 'Garlic Bread', 'Bruschetta Tomat', 'Pasta Carbonara',
        'Pasta Bolognese', 'Spaghetti Aglio Olio', 'Lasagna Daging', 'Chicken Wings',
        'Mozzarella Sticks', 'Caesar Salad', 'Tiramisu Slice', 'Minuman Soda'
    ],
    'sushi-zen': [
        'Sushi Salmon Roll', 'Sashimi Tuna Segar', 'California Roll', 'Dragon Roll Spesial',
        'Edamame Rebus', 'Miso Soup', 'Gyoza Goreng', 'Takoyaki Gurita',
        'Ramen Tonkotsu', 'Karaage Chicken', 'Tempura Udang', 'Yakiniku Beef',
        'Onigiri Tuna Mayo', 'Udon Kuah', 'Soba Dingin', 'Dorayaki Coklat',
        'Mochi Es Krim', 'Green Tea Soft Serve', 'Ramune Soda', 'Bento Box Set'
    ],
    'juice-paradise': [
        'Jus Mangga Segar', 'Jus Semangka', 'Jus Jeruk Peras', 'Jus Alpukat Kental',
        'Jus Strawberry', 'Jus Wortel Apel', 'Smoothie Green Detox', 'Jus Melon Mint',
        'Coconut Shake', 'Mixed Berry Smoothie', 'Jus Nanas Segar', 'Teh Leci Segar',
        'Boba Taro Milk Tea', 'Matcha Boba', 'Es Kelapa Muda', 'Lemon Tea Panas',
        'Infused Water Mentimun', 'Acai Bowl', 'Fruit Salad Segar', 'Es Cincau Pandan'
    ],
    'bakso-malang-pak-kumis': [
        'Bakso Urat Spesial', 'Bakso Goreng Renyah', 'Bakso Keju Meleleh', 'Bakso Halus Sapi',
        'Mie Bakso Kuah', 'Bakso Bakar Pedas', 'Tahu Bakso Goreng', 'Siomay Bakso',
        'Bakso Jumbo Komplit', 'Mie Ayam Bakso', 'Bihun Bakso Kuah', 'Bakso Beranak',
        'Pentol Goreng Crispy', 'Bakso Telur Puyuh', 'Kwetiau Bakso', 'Es Teh Manis',
        'Es Jeruk Bakso', 'Tahu Kulit Isi', 'Pangsit Goreng', 'Jus Tomat'
    ],
    'dessert-house': [
        'Cheesecake Blueberry', 'Tiramisu Slice', 'Chocolate Lava Cake', 'Red Velvet Cake',
        'Mille Crepes', 'Croissant Almond', 'Donut Glaze Rainbow', 'Macaroon Vanilla',
        'Brownies Fudgy', 'Banana Foster', 'Panna Cotta Strawberry', 'Creme Brulee',
        'Waffle Ice Cream', 'Churros Coklat', 'Pudding Karamel', 'Klepon Coklat',
        'Bingsu Matcha', 'Frappe Oreo', 'Affogato Espresso', 'Es Krim Gelato Mix'
    ]
}

SYMBOLS = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T']

def main():
    os.makedirs('media/tenants/banners', exist_ok=True)
    os.makedirs('media/products', exist_ok=True)
    
    print("Generating images...")
    
    for slug, name, tagline, c1, c2, abbr in TENANTS:
        print(f"  {name}...", end=' ', flush=True)
        
        # Logo
        logo = make_logo(400, 400, c1, c2, name, abbr)
        logo.save(f'media/tenants/{slug}_logo.png')
        
        # Banner
        banner = make_banner(800, 250, c1, c2, name, tagline)
        banner.save(f'media/tenants/banners/{slug}_banner.jpg', quality=85)
        
        # Products
        products = PRODUCT_NAMES.get(slug, [])
        for i, pname in enumerate(products):
            sym = SYMBOLS[i % len(SYMBOLS)]
            # Vary colors slightly
            hv = (i * 15) % 60 - 30
            pc1 = tuple(max(0, min(255, c + hv)) for c in c1)
            pc2 = tuple(max(0, min(255, c + hv - 20)) for c in c2)
            
            prod_img = make_product(600, 400, pc1, pc2, pname, sym)
            safe_name = pname.lower().replace(' ', '_')[:25]
            prod_img.save(f'media/products/{slug}_{i+1:02d}_{safe_name}.jpg', quality=80)
        
        print(f"OK ({len(products)} products)")
    
    print("Done!")

if __name__ == '__main__':
    main()
