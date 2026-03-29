"""
Management command to seed the database with sample data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import Category, Tenant, Product, ProductCategory
import os
import glob


class Command(BaseCommand):
    help = 'Seeds the database with 10 tenants and 20 products each'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🌱 Seeding database...'))
        
        # Clear existing data
        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Tenant.objects.all().delete()
        Category.objects.all().delete()

        # Create Categories
        categories_data = [
            {'name': 'Masakan Indonesia', 'icon': '🍛'},
            {'name': 'Mie & Bakmi', 'icon': '🍜'},
            {'name': 'Ayam & Unggas', 'icon': '🍗'},
            {'name': 'Soto & Sup', 'icon': '🥣'},
            {'name': 'Kopi & Minuman', 'icon': '☕'},
            {'name': 'Western Food', 'icon': '🍕'},
            {'name': 'Japanese Food', 'icon': '🍱'},
            {'name': 'Juice & Sehat', 'icon': '🥤'},
            {'name': 'Bakso & Siomay', 'icon': '🥩'},
            {'name': 'Dessert & Kue', 'icon': '🍰'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat = Category.objects.create(**cat_data)
            categories[cat.name] = cat
            self.stdout.write(f'  ✓ Category: {cat.name}')

        # Tenant data with full details
        tenants_data = [
            {
                'name': 'Warung Nusantara',
                'slug': 'warung-nusantara',
                'description': 'Sajian masakan Nusantara yang otentik dengan cita rasa rumahan. Dari Sabang sampai Merauke, semua ada di sini! Menyajikan berbagai hidangan tradisional Indonesia yang kaya rempah.',
                'category': 'Masakan Indonesia',
                'rating': 4.8,
                'total_reviews': 1243,
                'min_order': 15000,
                'delivery_time': '10-20 menit',
                'location': 'Lantai 1, Stand A1',
                'color_theme': 'orange',
                'products': [
                    {'name': 'Nasi Rendang Daging', 'price': 35000, 'desc': 'Rendang daging sapi empuk dimasak dengan bumbu rempah pilihan khas Minang', 'cat': 'Nasi', 'featured': True, 'best': True, 'cal': 520, 'spicy': True},
                    {'name': 'Nasi Padang Komplit', 'price': 40000, 'desc': 'Nasi Padang lengkap dengan pilihan 5 lauk: rendang, gulai, sambal hijau, dll', 'cat': 'Nasi', 'featured': True, 'cal': 650},
                    {'name': 'Ayam Gulai Santan', 'price': 28000, 'desc': 'Ayam kampung dimasak gulai santan kental gurih dengan bumbu pilihan', 'cat': 'Lauk', 'cal': 380},
                    {'name': 'Nasi Goreng Kampung', 'price': 22000, 'desc': 'Nasi goreng khas kampung dengan telur, ayam, dan sayuran segar', 'cat': 'Nasi', 'cal': 450},
                    {'name': 'Ikan Bakar Bumbu Kuning', 'price': 32000, 'desc': 'Ikan segar dibakar dengan bumbu kuning rempah khas Nusantara', 'cat': 'Lauk', 'cal': 290},
                    {'name': 'Sayur Lodeh Santan', 'price': 15000, 'desc': 'Sayuran segar dalam kuah santan gurih ala masakan Jawa', 'cat': 'Sayur', 'veg': True, 'cal': 180},
                    {'name': 'Perkedel Kentang', 'price': 8000, 'desc': 'Perkedel kentang goreng renyah di luar lembut di dalam', 'cat': 'Pelengkap', 'cal': 120},
                    {'name': 'Tempe Orek Kecap', 'price': 10000, 'desc': 'Tempe goreng orek dengan saus kecap manis dan cabe', 'cat': 'Lauk', 'veg': True, 'cal': 150},
                    {'name': 'Sambal Goreng Ati', 'price': 20000, 'desc': 'Hati ayam dimasak sambal goreng pedas dengan petai', 'cat': 'Lauk', 'spicy': True, 'cal': 280},
                    {'name': 'Tahu Balado Pedas', 'price': 12000, 'desc': 'Tahu goreng siram sambal balado pedas manis', 'cat': 'Lauk', 'veg': True, 'spicy': True, 'cal': 160},
                    {'name': 'Pindang Iga Sapi', 'price': 45000, 'desc': 'Iga sapi segar dimasak pindang asam pedas segar', 'cat': 'Sup', 'spicy': True, 'cal': 480},
                    {'name': 'Lontong Cap Gomeh', 'price': 25000, 'desc': 'Lontong dengan opor ayam, lodeh, sambal goreng ati', 'cat': 'Nasi', 'cal': 520},
                    {'name': 'Sate Padang Komplit', 'price': 35000, 'desc': '10 tusuk sate padang dengan kuah kari pedas dan lontong', 'cat': 'Sate', 'spicy': True, 'best': True, 'cal': 420},
                    {'name': 'Dendeng Balado', 'price': 38000, 'desc': 'Dendeng sapi tipis renyah dibalut sambal balado merah', 'cat': 'Lauk', 'spicy': True, 'cal': 380},
                    {'name': 'Nasi Kuning Tumpeng', 'price': 30000, 'desc': 'Nasi kuning harum dengan berbagai lauk dan sayuran', 'cat': 'Nasi', 'cal': 580},
                    {'name': 'Opor Ayam Kuning', 'price': 28000, 'desc': 'Ayam kampung opor santan kuning ala lebaran', 'cat': 'Lauk', 'cal': 420},
                    {'name': 'Semur Daging Sapi', 'price': 35000, 'desc': 'Daging sapi empuk dalam kuah semur kecap yang manis', 'cat': 'Lauk', 'cal': 460},
                    {'name': 'Pepes Ikan Mas', 'price': 22000, 'desc': 'Ikan mas segar dimasak pepes dengan daun kemangi', 'cat': 'Lauk', 'spicy': True, 'cal': 250},
                    {'name': 'Kari Ayam Santan', 'price': 28000, 'desc': 'Ayam dalam kuah kari santan dengan kentang', 'cat': 'Lauk', 'cal': 480},
                    {'name': 'Es Teh Manis', 'price': 5000, 'desc': 'Es teh manis segar menyegarkan', 'cat': 'Minuman', 'cal': 80},
                ]
            },
            {
                'name': 'Bakmi Jago',
                'slug': 'bakmi-jago',
                'description': 'Spesialis mie dan bakmi dengan resep turun-temurun dari Pontianak. Mie dibuat fresh setiap hari menggunakan bahan pilihan berkualitas tinggi.',
                'category': 'Mie & Bakmi',
                'rating': 4.7,
                'total_reviews': 987,
                'min_order': 20000,
                'delivery_time': '10-15 menit',
                'location': 'Lantai 1, Stand A2',
                'color_theme': 'yellow',
                'products': [
                    {'name': 'Bakmi Ayam Original', 'price': 25000, 'desc': 'Bakmi fresh dengan topping ayam cincang dan bakso dalam kuah kaldu bening', 'cat': 'Bakmi', 'featured': True, 'best': True, 'cal': 380},
                    {'name': 'Bakmi Kuah Spesial', 'price': 28000, 'desc': 'Bakmi dalam kuah kaldu sapi kental dengan ayam, bakso, dan pangsit', 'cat': 'Bakmi', 'featured': True, 'cal': 450},
                    {'name': 'Mie Goreng Seafood', 'price': 32000, 'desc': 'Mie goreng dengan udang, cumi, dan bakso ikan', 'cat': 'Mie Goreng', 'cal': 520},
                    {'name': 'Kwetiau Sapi Goreng', 'price': 30000, 'desc': 'Kwetiau goreng dengan irisan daging sapi dan sayuran', 'cat': 'Kwetiau', 'cal': 490},
                    {'name': 'Bihun Goreng Ayam', 'price': 22000, 'desc': 'Bihun goreng dengan ayam, telur, dan sayuran segar', 'cat': 'Bihun', 'cal': 350},
                    {'name': 'Mie Yamin Spesial', 'price': 27000, 'desc': 'Mie yamin khas Bandung dengan topping ayam dan wonton', 'cat': 'Bakmi', 'best': True, 'cal': 420},
                    {'name': 'Bakmi Pangsit Rebus', 'price': 26000, 'desc': 'Bakmi dengan pangsit rebus isi ayam dalam kuah jernih', 'cat': 'Bakmi', 'cal': 400},
                    {'name': 'Mie Tek-Tek Goreng', 'price': 20000, 'desc': 'Mie tek-tek ala pinggir jalan dengan bumbu spesial', 'cat': 'Mie Goreng', 'cal': 380},
                    {'name': 'Capcay Kuah Spesial', 'price': 25000, 'desc': 'Capcay sayuran segar dalam kuah kental dengan seafood', 'cat': 'Capcay', 'veg': False, 'cal': 280},
                    {'name': 'Nasi Goreng Teri', 'price': 22000, 'desc': 'Nasi goreng dengan teri medan crispy dan kemangi', 'cat': 'Nasi', 'cal': 420},
                    {'name': 'Pangsit Goreng Renyah', 'price': 15000, 'desc': '8 buah pangsit goreng renyah isi ayam dan udang', 'cat': 'Cemilan', 'cal': 180},
                    {'name': 'Dimsum Ayam', 'price': 20000, 'desc': '5 buah dimsum kukus isi ayam dan jamur', 'cat': 'Dimsum', 'cal': 200},
                    {'name': 'Siomay Bandung', 'price': 18000, 'desc': 'Siomay ayam kukus dengan saus kacang pedas manis', 'cat': 'Cemilan', 'cal': 220},
                    {'name': 'Batagor Renyah', 'price': 20000, 'desc': 'Bakso tahu goreng crispy dengan bumbu kacang', 'cat': 'Cemilan', 'cal': 280},
                    {'name': 'Kwetiau Kuah Sapi', 'price': 30000, 'desc': 'Kwetiau dalam kuah kaldu sapi dengan irisan daging', 'cat': 'Kwetiau', 'cal': 420},
                    {'name': 'Mie Aceh Pedas', 'price': 32000, 'desc': 'Mie Aceh dengan kari rempah pedas khas Aceh', 'cat': 'Mie Goreng', 'spicy': True, 'cal': 490},
                    {'name': 'Bakso Urat Spesial', 'price': 28000, 'desc': 'Bakso urat sapi jumbo dalam kuah kaldu bening segar', 'cat': 'Bakso', 'cal': 380},
                    {'name': 'Mie Campur Seafood', 'price': 35000, 'desc': 'Mie dengan mix seafood: udang, cumi, kerang', 'cat': 'Mie Goreng', 'featured': True, 'cal': 480},
                    {'name': 'Lontong Sayur', 'price': 18000, 'desc': 'Lontong dengan sayur lodeh santan', 'cat': 'Nasi', 'veg': True, 'cal': 320},
                    {'name': 'Es Jeruk Segar', 'price': 8000, 'desc': 'Perasan jeruk segar dengan es dan gula', 'cat': 'Minuman', 'cal': 80},
                ]
            },
            {
                'name': 'Geprek Sultan',
                'slug': 'geprek-sultan',
                'description': 'Raja ayam geprek dengan level kepedasan yang bisa disesuaikan! Level 1-10 tersedia untuk semua jagoan pedas. Ayam crispy super renyah dengan sambal segar.',
                'category': 'Ayam & Unggas',
                'rating': 4.9,
                'total_reviews': 2156,
                'min_order': 20000,
                'delivery_time': '5-15 menit',
                'location': 'Lantai 1, Stand B1',
                'color_theme': 'red',
                'products': [
                    {'name': 'Ayam Geprek Level 5', 'price': 25000, 'desc': 'Ayam goreng crispy digeprek sambal level 5, nasi + lalapan', 'cat': 'Geprek', 'featured': True, 'best': True, 'spicy': True, 'cal': 580},
                    {'name': 'Ayam Geprek Keju', 'price': 28000, 'desc': 'Ayam geprek lumer dengan keju mozzarella dan sambal', 'cat': 'Geprek', 'featured': True, 'spicy': True, 'cal': 650},
                    {'name': 'Ayam Bakar Kecap', 'price': 28000, 'desc': 'Ayam kampung bakar dengan saus kecap manis dan lalapan', 'cat': 'Ayam Bakar', 'cal': 480},
                    {'name': 'Ayam Goreng Crispy', 'price': 22000, 'desc': 'Ayam goreng crispy renyah dengan tepung bumbu spesial', 'cat': 'Ayam Goreng', 'best': True, 'cal': 520},
                    {'name': 'Nasi Ayam Geprek Komplit', 'price': 30000, 'desc': 'Paket komplit: geprek + nasi + 2 lauk + es teh', 'cat': 'Paket', 'spicy': True, 'cal': 750},
                    {'name': 'Geprek Sambal Matah', 'price': 26000, 'desc': 'Geprek dengan sambal matah Bali segar dan aromatik', 'cat': 'Geprek', 'spicy': True, 'cal': 540},
                    {'name': 'Ayam Geprek Mozarella', 'price': 30000, 'desc': 'Geprek berbalut mozarella meleleh yang menggugah selera', 'cat': 'Geprek', 'spicy': True, 'cal': 680},
                    {'name': 'Paket Hemat Geprek', 'price': 20000, 'desc': 'Sepotong ayam geprek dengan nasi dan es teh tawar', 'cat': 'Paket', 'spicy': True, 'cal': 480},
                    {'name': 'Geprek Sambal Bawang', 'price': 24000, 'desc': 'Geprek dengan sambal bawang putih aromatik', 'cat': 'Geprek', 'spicy': True, 'cal': 560},
                    {'name': 'Ayam Kuah Kuning', 'price': 26000, 'desc': 'Ayam kampung dalam kuah kuning rempah segar', 'cat': 'Ayam Kuah', 'cal': 420},
                    {'name': 'Telur Ceplok Sambal', 'price': 12000, 'desc': 'Telur ceplok dengan sambal merah pedas manis', 'cat': 'Telur', 'spicy': True, 'cal': 180},
                    {'name': 'Tahu Tempe Balado', 'price': 12000, 'desc': 'Tahu dan tempe goreng siraman sambal balado', 'cat': 'Sayur', 'veg': True, 'spicy': True, 'cal': 200},
                    {'name': 'Nasi Putih Hangat', 'price': 5000, 'desc': 'Nasi putih pulen dan hangat', 'cat': 'Nasi', 'veg': True, 'cal': 200},
                    {'name': 'Lalap Segar', 'price': 5000, 'desc': 'Lalapan segar: timun, kol, kemangi', 'cat': 'Sayur', 'veg': True, 'cal': 30},
                    {'name': 'Kentang Goreng', 'price': 15000, 'desc': 'Kentang goreng renyah dengan saus sambal', 'cat': 'Cemilan', 'veg': True, 'cal': 280},
                    {'name': 'Es Teh Tawar', 'price': 5000, 'desc': 'Es teh tawar menyegarkan', 'cat': 'Minuman', 'cal': 10},
                    {'name': 'Es Jeruk Peras', 'price': 8000, 'desc': 'Perasan jeruk manis dengan es batu', 'cat': 'Minuman', 'cal': 80},
                    {'name': 'Geprek Double Crispy', 'price': 28000, 'desc': 'Double layer crispy coating dengan geprek super pedas', 'cat': 'Geprek', 'spicy': True, 'featured': True, 'cal': 620},
                    {'name': 'Sayur Asem', 'price': 10000, 'desc': 'Sayur asem segar dengan berbagai sayuran', 'cat': 'Sayur', 'veg': True, 'cal': 120},
                    {'name': 'Jus Mangga Segar', 'price': 12000, 'desc': 'Jus mangga harum manis', 'cat': 'Minuman', 'cal': 150},
                ]
            },
            {
                'name': 'Soto Betawi Bu Sri',
                'slug': 'soto-betawi-bu-sri',
                'description': 'Soto Betawi asli dengan kuah santan susu yang kaya rempah. Sudah berdiri 25 tahun dengan resep rahasia keluarga yang dijaga turun-temurun.',
                'category': 'Soto & Sup',
                'rating': 4.8,
                'total_reviews': 1876,
                'min_order': 15000,
                'delivery_time': '10-20 menit',
                'location': 'Lantai 1, Stand B2',
                'color_theme': 'orange',
                'products': [
                    {'name': 'Soto Betawi Asli', 'price': 28000, 'desc': 'Soto Betawi kuah santan dengan irisan daging sapi, tomat, emping', 'cat': 'Soto', 'featured': True, 'best': True, 'cal': 480},
                    {'name': 'Soto Betawi Susu', 'price': 30000, 'desc': 'Soto Betawi premium dengan kuah susu yang lebih creamy', 'cat': 'Soto', 'featured': True, 'cal': 520},
                    {'name': 'Soto Daging Sapi', 'price': 32000, 'desc': 'Soto kuah bening dengan irisan daging sapi empuk', 'cat': 'Soto', 'cal': 420},
                    {'name': 'Ketoprak Betawi', 'price': 18000, 'desc': 'Ketoprak dengan tahu, bihun, ketupat, dan saus kacang', 'cat': 'Ketoprak', 'veg': True, 'cal': 350},
                    {'name': 'Nasi Uduk Komplit', 'price': 25000, 'desc': 'Nasi uduk dengan ayam goreng, tempe, emping, dan sambal', 'cat': 'Nasi', 'best': True, 'cal': 580},
                    {'name': 'Bubur Ayam Spesial', 'price': 22000, 'desc': 'Bubur ayam dengan cakwe, kedelai goreng, dan kaldu', 'cat': 'Bubur', 'cal': 380},
                    {'name': 'Soto Ayam Kampung', 'price': 25000, 'desc': 'Soto ayam kampung bening dengan bumbu kuning', 'cat': 'Soto', 'cal': 350},
                    {'name': 'Rawon Surabaya', 'price': 30000, 'desc': 'Rawon hitam khas Surabaya dengan kluwek dan empal', 'cat': 'Sup', 'cal': 450},
                    {'name': 'Lontong Sayur Padang', 'price': 22000, 'desc': 'Lontong dengan sayur nangka dan rendang', 'cat': 'Lontong', 'cal': 480},
                    {'name': 'Nasi Rames Spesial', 'price': 28000, 'desc': 'Nasi dengan pilihan lauk: rendang, ayam, sayur', 'cat': 'Nasi', 'cal': 620},
                    {'name': 'Sup Iga Sapi', 'price': 45000, 'desc': 'Iga sapi empuk dalam kuah sup bening jernih', 'cat': 'Sup', 'cal': 520},
                    {'name': 'Empal Gentong', 'price': 35000, 'desc': 'Empal gentong khas Cirebon dengan santan gurih', 'cat': 'Sup', 'cal': 480},
                    {'name': 'Sate Padang Mini', 'price': 25000, 'desc': 'Sate padang mini 8 tusuk dengan kuah kari', 'cat': 'Sate', 'spicy': True, 'cal': 320},
                    {'name': 'Pecel Lele Goreng', 'price': 22000, 'desc': 'Lele goreng dengan sambal terasi dan lalapan', 'cat': 'Lauk', 'spicy': True, 'cal': 380},
                    {'name': 'Ayam Penyet Spesial', 'price': 25000, 'desc': 'Ayam goreng dipenyet dengan sambal terasi segar', 'cat': 'Lauk', 'spicy': True, 'cal': 480},
                    {'name': 'Es Jeruk Nipis', 'price': 8000, 'desc': 'Es jeruk nipis segar dengan gula aren', 'cat': 'Minuman', 'cal': 60},
                    {'name': 'Teh Tarik Panas', 'price': 8000, 'desc': 'Teh tarik susu kental panas', 'cat': 'Minuman', 'cal': 120},
                    {'name': 'Kerupuk Udang', 'price': 5000, 'desc': 'Kerupuk udang renyah untuk pelengkap', 'cat': 'Cemilan', 'cal': 80},
                    {'name': 'Sambal Terong', 'price': 10000, 'desc': 'Terong panggang dengan sambal tomat', 'cat': 'Sayur', 'veg': True, 'spicy': True, 'cal': 120},
                    {'name': 'Es Campur Segar', 'price': 12000, 'desc': 'Es campur dengan cincau, kolang-kaling, santan', 'cat': 'Minuman', 'cal': 200},
                ]
            },
            {
                'name': 'Kopi Kekinian',
                'slug': 'kopi-kekinian',
                'description': 'Kopi specialty lokal terbaik Indonesia dengan metode V60, Aeropress, dan Cold Brew. Biji kopi segar dari berbagai daerah Nusantara disajikan oleh barista berpengalaman.',
                'category': 'Kopi & Minuman',
                'rating': 4.7,
                'total_reviews': 3421,
                'min_order': 20000,
                'delivery_time': '5-10 menit',
                'location': 'Lantai 2, Stand C1',
                'color_theme': 'indigo',
                'products': [
                    {'name': 'Kopi Hitam Tubruk', 'price': 8000, 'desc': 'Kopi tubruk tradisional dengan biji pilihan Toraja atau Flores', 'cat': 'Kopi Panas', 'featured': True, 'cal': 5},
                    {'name': 'Cappuccino Panas', 'price': 22000, 'desc': 'Cappuccino dengan foam susu lembut dan latte art cantik', 'cat': 'Kopi Panas', 'featured': True, 'best': True, 'cal': 120},
                    {'name': 'Latte Art Susu', 'price': 24000, 'desc': 'Espresso double dengan susu steamed dan latte art', 'cat': 'Kopi Panas', 'cal': 150},
                    {'name': 'Es Kopi Susu Gula Aren', 'price': 20000, 'desc': 'Es kopi susu manis dengan gula aren khas Indonesia', 'cat': 'Kopi Dingin', 'featured': True, 'best': True, 'cal': 180},
                    {'name': 'Americano Dingin', 'price': 18000, 'desc': 'Espresso double dengan air dingin dan es batu', 'cat': 'Kopi Dingin', 'cal': 15},
                    {'name': 'Matcha Latte Panas', 'price': 22000, 'desc': 'Matcha premium dengan susu oat atau susu sapi', 'cat': 'Non Kopi', 'cal': 140},
                    {'name': 'Teh Tarik Panas', 'price': 12000, 'desc': 'Teh tarik susu kental creamy ala Malaysia', 'cat': 'Non Kopi', 'cal': 150},
                    {'name': 'Brown Sugar Boba Milk', 'price': 25000, 'desc': 'Boba milk tea dengan gula brown sugar caramel', 'cat': 'Boba', 'best': True, 'cal': 320},
                    {'name': 'Caramel Macchiato', 'price': 26000, 'desc': 'Espresso dengan susu vanilla dan karamel', 'cat': 'Kopi Panas', 'cal': 200},
                    {'name': 'Vanilla Latte', 'price': 24000, 'desc': 'Espresso latte dengan sirup vanilla premium', 'cat': 'Kopi Panas', 'cal': 180},
                    {'name': 'Milo Dinosaur', 'price': 20000, 'desc': 'Milo dingin dengan taburan bubuk Milo di atas', 'cat': 'Non Kopi', 'cal': 250},
                    {'name': 'Chocolate Frappe', 'price': 25000, 'desc': 'Frappe coklat blended dengan whipped cream', 'cat': 'Frappe', 'cal': 350},
                    {'name': 'Kopi V60 Specialty', 'price': 30000, 'desc': 'Pour over V60 dengan biji single origin pilihan', 'cat': 'Kopi Panas', 'cal': 10},
                    {'name': 'Affogato Es Krim', 'price': 22000, 'desc': 'Espresso panas dituang di atas es krim vanilla', 'cat': 'Dessert Drink', 'cal': 200},
                    {'name': 'Red Velvet Latte', 'price': 25000, 'desc': 'Latte dengan sirup red velvet creamy manis', 'cat': 'Kopi Panas', 'cal': 220},
                    {'name': 'Croissant Mentega', 'price': 20000, 'desc': 'Croissant butter fresh baked renyah dan berlapis', 'cat': 'Pastri', 'cal': 280},
                    {'name': 'Roti Bakar Coklat', 'price': 18000, 'desc': 'Roti bakar dengan selai coklat dan keju', 'cat': 'Pastri', 'cal': 320},
                    {'name': 'Pancake Susu', 'price': 22000, 'desc': '3 lembar pancake fluffly dengan madu dan butter', 'cat': 'Pastri', 'cal': 380},
                    {'name': 'Waffle Madu', 'price': 25000, 'desc': 'Waffle crispy dengan madu, butter, dan buah segar', 'cat': 'Pastri', 'cal': 420},
                    {'name': 'Cake Slice Tiramisu', 'price': 28000, 'desc': 'Sepotong tiramisu dengan mascarpone dan espresso', 'cat': 'Cake', 'cal': 380},
                ]
            },
            {
                'name': 'Pizza Bros',
                'slug': 'pizza-bros',
                'description': 'Pizza dan pasta authentic Italia dengan bahan impor premium. Adonan hand-tossed dimatangkan di oven kayu tradisional selama 90 detik untuk hasil terbaik.',
                'category': 'Western Food',
                'rating': 4.6,
                'total_reviews': 892,
                'min_order': 35000,
                'delivery_time': '15-25 menit',
                'location': 'Lantai 2, Stand C2',
                'color_theme': 'red',
                'products': [
                    {'name': 'Pizza Margherita', 'price': 55000, 'desc': 'Pizza klasik dengan sauce tomat, mozzarella, dan basil segar', 'cat': 'Pizza', 'veg': True, 'cal': 680},
                    {'name': 'Pizza Pepperoni', 'price': 65000, 'desc': 'Pizza dengan pepperoni asli import dan mozzarella premium', 'cat': 'Pizza', 'featured': True, 'best': True, 'cal': 780},
                    {'name': 'Pizza BBQ Chicken', 'price': 68000, 'desc': 'Pizza ayam BBQ dengan sauce barbeque smoky dan bawang bombay', 'cat': 'Pizza', 'featured': True, 'cal': 820},
                    {'name': 'Pizza 4 Keju', 'price': 72000, 'desc': 'Pizza 4 keju: mozzarella, cheddar, parmesan, gorgonzola', 'cat': 'Pizza', 'best': True, 'cal': 850},
                    {'name': 'Pizza Seafood Spesial', 'price': 75000, 'desc': 'Pizza dengan udang, cumi, dan crab stick pilihan', 'cat': 'Pizza', 'cal': 760},
                    {'name': 'Pizza Vegetarian', 'price': 58000, 'desc': 'Pizza dengan aneka sayuran segar dan keju mozzarella', 'cat': 'Pizza', 'veg': True, 'cal': 620},
                    {'name': 'Pizza Hawaiian', 'price': 62000, 'desc': 'Pizza dengan ham, nanas segar, dan mozzarella', 'cat': 'Pizza', 'cal': 700},
                    {'name': 'Pizza Meat Lovers', 'price': 78000, 'desc': 'Pizza dengan daging sapi, ayam, sosis, pepperoni', 'cat': 'Pizza', 'cal': 950},
                    {'name': 'Calzone Spesial', 'price': 65000, 'desc': 'Calzone isi daging sapi, mozzarella, dan ricotta', 'cat': 'Pizza', 'cal': 780},
                    {'name': 'Garlic Bread', 'price': 25000, 'desc': '4 potong garlic bread butter dengan parsley segar', 'cat': 'Starter', 'veg': True, 'cal': 280},
                    {'name': 'Bruschetta Tomat', 'price': 28000, 'desc': 'Bruschetta roti panggang dengan tomat segar dan basil', 'cat': 'Starter', 'veg': True, 'cal': 220},
                    {'name': 'Pasta Carbonara', 'price': 48000, 'desc': 'Pasta spaghetti dengan sauce carbonara creamy dan pancetta', 'cat': 'Pasta', 'featured': True, 'cal': 680},
                    {'name': 'Pasta Bolognese', 'price': 45000, 'desc': 'Pasta dengan ragù bolognese daging sapi slow-cooked', 'cat': 'Pasta', 'cal': 650},
                    {'name': 'Spaghetti Aglio Olio', 'price': 40000, 'desc': 'Spaghetti dengan olive oil, bawang putih, dan cabe', 'cat': 'Pasta', 'veg': True, 'spicy': True, 'cal': 520},
                    {'name': 'Lasagna Daging', 'price': 55000, 'desc': 'Lasagna berlapis dengan daging, bechamel, dan keju', 'cat': 'Pasta', 'cal': 780},
                    {'name': 'Chicken Wings', 'price': 38000, 'desc': '6 buah chicken wings dengan saus BBQ atau hot', 'cat': 'Starter', 'cal': 450},
                    {'name': 'Mozzarella Sticks', 'price': 32000, 'desc': '6 buah mozzarella sticks goreng dengan marinara dip', 'cat': 'Starter', 'veg': True, 'cal': 350},
                    {'name': 'Caesar Salad', 'price': 35000, 'desc': 'Salad romaine dengan dressing caesar, crouton, parmesan', 'cat': 'Salad', 'cal': 280},
                    {'name': 'Tiramisu Slice', 'price': 32000, 'desc': 'Tiramisu slice dengan mascarpone dan espresso', 'cat': 'Dessert', 'cal': 380},
                    {'name': 'Minuman Soda', 'price': 15000, 'desc': 'Minuman soda pilihan: cola, sprite, fanta', 'cat': 'Minuman', 'cal': 150},
                ]
            },
            {
                'name': 'Sushi Zen',
                'slug': 'sushi-zen',
                'description': 'Restoran Jepang authentic dengan chef berpengalaman langsung dari Tokyo. Bahan-bahan segar impor setiap hari untuk memastikan kualitas terbaik di setiap hidangan.',
                'category': 'Japanese Food',
                'rating': 4.8,
                'total_reviews': 1654,
                'min_order': 40000,
                'delivery_time': '10-20 menit',
                'location': 'Lantai 2, Stand D1',
                'color_theme': 'red',
                'products': [
                    {'name': 'Sushi Salmon Roll', 'price': 45000, 'desc': '8 pcs salmon roll dengan alpukat dan cream cheese', 'cat': 'Sushi Roll', 'featured': True, 'best': True, 'cal': 380},
                    {'name': 'Sashimi Tuna Segar', 'price': 65000, 'desc': '8 pcs sashimi tuna bluefin segar impor berkualitas', 'cat': 'Sashimi', 'featured': True, 'cal': 220},
                    {'name': 'California Roll', 'price': 38000, 'desc': '8 pcs california roll dengan crab stick, alpukat, timun', 'cat': 'Sushi Roll', 'cal': 320},
                    {'name': 'Dragon Roll Spesial', 'price': 55000, 'desc': '8 pcs dragon roll dengan udang tempura dan alpukat', 'cat': 'Sushi Roll', 'best': True, 'cal': 420},
                    {'name': 'Edamame Rebus', 'price': 18000, 'desc': 'Edamame rebus dengan garam laut fleur de sel', 'cat': 'Starter', 'veg': True, 'cal': 120},
                    {'name': 'Miso Soup', 'price': 15000, 'desc': 'Sup miso dengan tofu, rumput laut, dan daun bawang', 'cat': 'Sup', 'veg': True, 'cal': 80},
                    {'name': 'Gyoza Goreng', 'price': 32000, 'desc': '6 buah gyoza pan-fried crispy dengan saus ponzu', 'cat': 'Starter', 'cal': 280},
                    {'name': 'Takoyaki Gurita', 'price': 28000, 'desc': '8 buah takoyaki gurita dengan mayo dan okonomiyaki sauce', 'cat': 'Starter', 'cal': 320},
                    {'name': 'Ramen Tonkotsu', 'price': 55000, 'desc': 'Ramen kuah tonkotsu kental dengan chashu, telur, nori', 'cat': 'Ramen', 'featured': True, 'cal': 680},
                    {'name': 'Karaage Chicken', 'price': 35000, 'desc': 'Ayam goreng Jepang crispy dengan mayo yuzu', 'cat': 'Main Course', 'cal': 480},
                    {'name': 'Tempura Udang', 'price': 45000, 'desc': '6 pcs udang tempura renyah dengan dipping sauce', 'cat': 'Main Course', 'cal': 380},
                    {'name': 'Yakiniku Beef', 'price': 68000, 'desc': 'Daging sapi wagyu dipanggang dengan saus yakiniku', 'cat': 'Yakiniku', 'best': True, 'cal': 520},
                    {'name': 'Onigiri Tuna Mayo', 'price': 20000, 'desc': 'Onigiri segitiga dengan filling tuna mayo segar', 'cat': 'Onigiri', 'cal': 250},
                    {'name': 'Udon Kuah', 'price': 42000, 'desc': 'Udon kenyal dalam kuah dashi hangat dengan topping', 'cat': 'Udon', 'cal': 480},
                    {'name': 'Soba Dingin', 'price': 38000, 'desc': 'Soba dingin dengan saus tsuyu dan wasabi segar', 'cat': 'Soba', 'cal': 350},
                    {'name': 'Dorayaki Coklat', 'price': 18000, 'desc': 'Dorayaki pancake dengan isian coklat smooth', 'cat': 'Dessert', 'cal': 280},
                    {'name': 'Mochi Es Krim', 'price': 22000, 'desc': '3 pcs mochi es krim: matcha, stroberi, vanilla', 'cat': 'Dessert', 'cal': 220},
                    {'name': 'Green Tea Soft Serve', 'price': 18000, 'desc': 'Soft serve matcha premium dengan cone crispy', 'cat': 'Dessert', 'cal': 180},
                    {'name': 'Ramune Soda', 'price': 15000, 'desc': 'Minuman soda Jepang Ramune original', 'cat': 'Minuman', 'cal': 130},
                    {'name': 'Bento Box Set', 'price': 75000, 'desc': 'Bento lengkap: nasi, sushi, karaage, edamame, miso soup', 'cat': 'Set Menu', 'featured': True, 'cal': 850},
                ]
            },
            {
                'name': 'Juice Paradise',
                'slug': 'juice-paradise',
                'description': 'Pusat juice dan smoothie segar dari buah-buahan pilihan tanpa pengawet dan pewarna. Sehat, segar, dan lezat untuk semua kalangan!',
                'category': 'Juice & Sehat',
                'rating': 4.6,
                'total_reviews': 743,
                'min_order': 15000,
                'delivery_time': '5-10 menit',
                'location': 'Lantai 2, Stand D2',
                'color_theme': 'green',
                'products': [
                    {'name': 'Jus Mangga Segar', 'price': 18000, 'desc': 'Jus mangga harumanis murni tanpa tambahan air', 'cat': 'Jus Buah', 'featured': True, 'best': True, 'veg': True, 'cal': 150},
                    {'name': 'Jus Semangka', 'price': 15000, 'desc': 'Jus semangka merah dingin menyegarkan', 'cat': 'Jus Buah', 'veg': True, 'cal': 80},
                    {'name': 'Jus Jeruk Peras', 'price': 16000, 'desc': 'Perasan jeruk segar tanpa ampas ditambah es', 'cat': 'Jus Buah', 'veg': True, 'cal': 90},
                    {'name': 'Jus Alpukat Kental', 'price': 20000, 'desc': 'Jus alpukat mentega kental dengan susu dan coklat', 'cat': 'Jus Buah', 'veg': True, 'best': True, 'cal': 250},
                    {'name': 'Jus Strawberry', 'price': 20000, 'desc': 'Jus strawberry manis asam segar dengan susu', 'cat': 'Jus Buah', 'veg': True, 'cal': 140},
                    {'name': 'Jus Wortel Apel', 'price': 18000, 'desc': 'Kombinasi wortel dan apel hijau penuh vitamin', 'cat': 'Jus Sehat', 'veg': True, 'cal': 110},
                    {'name': 'Smoothie Green Detox', 'price': 25000, 'desc': 'Smoothie hijau: bayam, timun, apel, lemon, jahe', 'cat': 'Smoothie', 'veg': True, 'featured': True, 'cal': 120},
                    {'name': 'Jus Melon Mint', 'price': 16000, 'desc': 'Jus melon segar dengan daun mint dan es batu', 'cat': 'Jus Buah', 'veg': True, 'cal': 90},
                    {'name': 'Coconut Shake', 'price': 22000, 'desc': 'Milkshake kelapa muda dengan nata de coco', 'cat': 'Shake', 'veg': True, 'cal': 220},
                    {'name': 'Mixed Berry Smoothie', 'price': 25000, 'desc': 'Smoothie mixed berry: blueberry, stroberi, raspberi', 'cat': 'Smoothie', 'veg': True, 'cal': 180},
                    {'name': 'Jus Nanas Segar', 'price': 15000, 'desc': 'Jus nanas manis asam segar murni', 'cat': 'Jus Buah', 'veg': True, 'cal': 80},
                    {'name': 'Teh Leci Segar', 'price': 15000, 'desc': 'Teh hijau segar dengan buah leci dan es', 'cat': 'Teh', 'veg': True, 'cal': 70},
                    {'name': 'Boba Taro Milk Tea', 'price': 22000, 'desc': 'Milk tea taro ungu dengan boba kenyal', 'cat': 'Boba', 'best': True, 'cal': 280},
                    {'name': 'Matcha Boba', 'price': 22000, 'desc': 'Matcha latte dingin dengan boba dan jelly', 'cat': 'Boba', 'cal': 250},
                    {'name': 'Es Kelapa Muda', 'price': 18000, 'desc': 'Kelapa muda segar langsung dari buahnya', 'cat': 'Es Tradisional', 'veg': True, 'cal': 120},
                    {'name': 'Lemon Tea Panas', 'price': 12000, 'desc': 'Teh panas dengan perasan lemon segar', 'cat': 'Teh', 'veg': True, 'cal': 40},
                    {'name': 'Infused Water Mentimun', 'price': 12000, 'desc': 'Air infused dengan mentimun dan mint segar', 'cat': 'Air Sehat', 'veg': True, 'cal': 10},
                    {'name': 'Açaí Bowl', 'price': 38000, 'desc': 'Açaí bowl dengan granola, pisang, dan madu', 'cat': 'Bowl Sehat', 'veg': True, 'featured': True, 'cal': 380},
                    {'name': 'Fruit Salad Segar', 'price': 22000, 'desc': 'Campuran buah segar dengan yogurt dan madu', 'cat': 'Bowl Sehat', 'veg': True, 'cal': 180},
                    {'name': 'Es Cincau Pandan', 'price': 12000, 'desc': 'Es cincau hijau pandan segar dengan santan', 'cat': 'Es Tradisional', 'veg': True, 'cal': 120},
                ]
            },
            {
                'name': 'Bakso Malang Pak Kumis',
                'slug': 'bakso-malang-pak-kumis',
                'description': 'Bakso Malang asli dengan resep legendaris sejak 1985. Bakso kenyal gurih dibuat dari daging sapi segar pilihan tanpa pengawet, disajikan dalam kuah kaldu sapi yang kaya rasa.',
                'category': 'Bakso & Siomay',
                'rating': 4.7,
                'total_reviews': 2890,
                'min_order': 15000,
                'delivery_time': '5-15 menit',
                'location': 'Lantai 1, Stand E1',
                'color_theme': 'indigo',
                'products': [
                    {'name': 'Bakso Urat Spesial', 'price': 28000, 'desc': 'Bakso urat sapi besar kenyal dalam kuah kaldu bening segar', 'cat': 'Bakso', 'featured': True, 'best': True, 'cal': 380},
                    {'name': 'Bakso Goreng Renyah', 'price': 20000, 'desc': 'Bakso digoreng crispy dengan saus kacang pedas', 'cat': 'Bakso', 'cal': 320},
                    {'name': 'Bakso Keju Meleleh', 'price': 30000, 'desc': 'Bakso berisi keju mozzarella meleleh di dalam', 'cat': 'Bakso', 'featured': True, 'cal': 420},
                    {'name': 'Bakso Halus Sapi', 'price': 22000, 'desc': 'Bakso halus premium dari daging sapi segar giling', 'cat': 'Bakso', 'cal': 300},
                    {'name': 'Mie Bakso Kuah', 'price': 25000, 'desc': 'Mie dengan bakso campur dalam kuah sapi kental', 'cat': 'Mie Bakso', 'best': True, 'cal': 450},
                    {'name': 'Bakso Bakar Pedas', 'price': 22000, 'desc': 'Bakso dibakar dengan bumbu pedas kecap manis', 'cat': 'Bakso', 'spicy': True, 'cal': 350},
                    {'name': 'Tahu Bakso Goreng', 'price': 18000, 'desc': 'Tahu isi bakso digoreng crispy dengan bumbu', 'cat': 'Tahu', 'cal': 280},
                    {'name': 'Siomay Bakso', 'price': 22000, 'desc': 'Siomay isi bakso kukus dengan saus kacang', 'cat': 'Siomay', 'cal': 250},
                    {'name': 'Bakso Jumbo Komplit', 'price': 35000, 'desc': 'Paket bakso jumbo: 3 jenis bakso + mie + tahu', 'cat': 'Paket', 'cal': 580},
                    {'name': 'Mie Ayam Bakso', 'price': 25000, 'desc': 'Mie ayam dengan topping bakso dan ayam cincang', 'cat': 'Mie Bakso', 'cal': 420},
                    {'name': 'Bihun Bakso Kuah', 'price': 22000, 'desc': 'Bihun dalam kuah bakso dengan sayuran segar', 'cat': 'Mie Bakso', 'cal': 350},
                    {'name': 'Bakso Beranak', 'price': 32000, 'desc': 'Bakso besar berisi telur puyuh di dalamnya', 'cat': 'Bakso', 'cal': 420},
                    {'name': 'Pentol Goreng Crispy', 'price': 15000, 'desc': 'Pentol kecil digoreng crispy dengan saus sambal', 'cat': 'Cemilan', 'spicy': True, 'cal': 200},
                    {'name': 'Bakso Telur Puyuh', 'price': 28000, 'desc': 'Bakso dengan telur puyuh utuh di dalam', 'cat': 'Bakso', 'cal': 380},
                    {'name': 'Kwetiau Bakso', 'price': 26000, 'desc': 'Kwetiau lebar dalam kuah bakso segar', 'cat': 'Mie Bakso', 'cal': 400},
                    {'name': 'Es Teh Manis', 'price': 5000, 'desc': 'Es teh manis menyegarkan', 'cat': 'Minuman', 'cal': 80},
                    {'name': 'Es Jeruk Bakso', 'price': 8000, 'desc': 'Es jeruk segar pelengkap bakso', 'cat': 'Minuman', 'cal': 70},
                    {'name': 'Tahu Kulit Isi', 'price': 15000, 'desc': 'Tahu kulit isi bakso dan bihun', 'cat': 'Tahu', 'cal': 220},
                    {'name': 'Pangsit Goreng', 'price': 15000, 'desc': '8 buah pangsit goreng crispy isi daging', 'cat': 'Cemilan', 'cal': 180},
                    {'name': 'Jus Tomat', 'price': 10000, 'desc': 'Jus tomat segar dengan sedikit gula', 'cat': 'Minuman', 'cal': 50},
                ]
            },
            {
                'name': 'Dessert House',
                'slug': 'dessert-house',
                'description': 'Surga makanan manis dengan kue artisan dan dessert premium. Dibuat setiap hari oleh pastry chef berpengalaman dengan bahan-bahan berkualitas tinggi pilihan.',
                'category': 'Dessert & Kue',
                'rating': 4.9,
                'total_reviews': 1432,
                'min_order': 20000,
                'delivery_time': '10-15 menit',
                'location': 'Lantai 2, Stand E2',
                'color_theme': 'pink',
                'products': [
                    {'name': 'Cheesecake Blueberry', 'price': 45000, 'desc': 'Cheesecake creamy dengan topping blueberry sauce segar', 'cat': 'Cake', 'featured': True, 'best': True, 'veg': True, 'cal': 420},
                    {'name': 'Tiramisu Slice', 'price': 40000, 'desc': 'Tiramisu authentic dengan mascarpone dan espresso premium', 'cat': 'Cake', 'featured': True, 'veg': True, 'cal': 380},
                    {'name': 'Chocolate Lava Cake', 'price': 38000, 'desc': 'Lava cake hangat dengan isian coklat leleh gurih manis', 'cat': 'Cake', 'veg': True, 'cal': 450},
                    {'name': 'Red Velvet Cake', 'price': 42000, 'desc': 'Red velvet dengan cream cheese frosting tebal', 'cat': 'Cake', 'veg': True, 'cal': 420},
                    {'name': 'Mille Crepes', 'price': 45000, 'desc': 'Kue crepe berlapis 20 layer dengan cream vanilla', 'cat': 'Cake', 'featured': True, 'best': True, 'veg': True, 'cal': 480},
                    {'name': 'Croissant Almond', 'price': 25000, 'desc': 'Croissant berlapis dengan krim almond dan topping almond slice', 'cat': 'Pastri', 'veg': True, 'cal': 380},
                    {'name': 'Donut Glaze Rainbow', 'price': 18000, 'desc': 'Donut manis dengan glazed rainbow berwarna-warni', 'cat': 'Donut', 'veg': True, 'cal': 280},
                    {'name': 'Macaroon Vanilla', 'price': 22000, 'desc': '3 buah macaroon French dengan buttercream vanilla', 'cat': 'Cookies', 'veg': True, 'cal': 240},
                    {'name': 'Brownies Fudgy', 'price': 25000, 'desc': 'Brownies fudgy coklat hitam pekat dengan walnut', 'cat': 'Brownies', 'veg': True, 'cal': 380},
                    {'name': 'Banana Foster', 'price': 35000, 'desc': 'Pisang karamel panas dengan es krim vanilla', 'cat': 'Dessert Panas', 'veg': True, 'cal': 320},
                    {'name': 'Panna Cotta Strawberry', 'price': 32000, 'desc': 'Panna cotta susu lembut dengan coulis strawberry', 'cat': 'Pudding', 'veg': True, 'cal': 280},
                    {'name': 'Creme Brulee', 'price': 35000, 'desc': 'Creme brulee vanilla dengan gula karamel crispy', 'cat': 'Pudding', 'veg': True, 'best': True, 'cal': 350},
                    {'name': 'Waffle Ice Cream', 'price': 35000, 'desc': 'Waffle crispy dengan dua scoop es krim premium', 'cat': 'Waffle', 'veg': True, 'cal': 480},
                    {'name': 'Churros Coklat', 'price': 25000, 'desc': 'Churros goreng crispy dengan dipping coklat hangat', 'cat': 'Gorengan', 'veg': True, 'cal': 380},
                    {'name': 'Pudding Karamel', 'price': 22000, 'desc': 'Pudding susu lembut dengan saus karamel homemade', 'cat': 'Pudding', 'veg': True, 'cal': 280},
                    {'name': 'Klepon Coklat', 'price': 18000, 'desc': 'Klepon modern isi coklat dengan kelapa parut', 'cat': 'Tradisional', 'veg': True, 'cal': 220},
                    {'name': 'Bingsu Matcha', 'price': 38000, 'desc': 'Bingsu es serut matcha dengan red bean dan mochi', 'cat': 'Es Krim', 'veg': True, 'cal': 280},
                    {'name': 'Frappe Oreo', 'price': 28000, 'desc': 'Frappe oreo blended dengan whipped cream dan oreo crumble', 'cat': 'Minuman', 'veg': True, 'cal': 380},
                    {'name': 'Affogato Espresso', 'price': 28000, 'desc': 'Espresso double panas dituang es krim vanilla Italia', 'cat': 'Es Krim', 'veg': True, 'cal': 180},
                    {'name': 'Es Krim Gelato Mix', 'price': 32000, 'desc': '3 scoop gelato pilihan: pistachio, coklat, stroberi', 'cat': 'Es Krim', 'veg': True, 'best': True, 'cal': 320},
                ]
            },
        ]

        # Get product image files
        product_files = {}
        import glob as gmodule
        for f in gmodule.glob('media/products/*.jpg'):
            basename = os.path.basename(f)
            parts = basename.split('_', 2)
            if len(parts) >= 2:
                key = '_'.join(parts[:2])  # slug_01, slug_02 etc
                product_files[basename] = f.replace('media/', '')

        for tenant_data in tenants_data:
            cat = categories[tenant_data['category']]
            
            tenant = Tenant.objects.create(
                name=tenant_data['name'],
                slug=tenant_data['slug'],
                description=tenant_data['description'],
                category=cat,
                rating=tenant_data['rating'],
                total_reviews=tenant_data['total_reviews'],
                min_order=tenant_data['min_order'],
                delivery_time=tenant_data['delivery_time'],
                location=tenant_data['location'],
                color_theme=tenant_data['color_theme'],
                is_open=True,
            )

            # Set logo if exists
            logo_path = f"tenants/{tenant_data['slug']}_logo.png"
            if os.path.exists(f'media/{logo_path}'):
                tenant.logo = logo_path

            banner_path = f"tenants/banners/{tenant_data['slug']}_banner.jpg"
            if os.path.exists(f'media/{banner_path}'):
                tenant.banner = banner_path

            tenant.save()
            self.stdout.write(f'  ✓ Tenant: {tenant.name}')

            # Create product categories (unique cats)
            product_cats = {}
            for prod_data in tenant_data['products']:
                cat_name = prod_data['cat']
                if cat_name not in product_cats:
                    pc = ProductCategory.objects.create(name=cat_name, tenant=tenant)
                    product_cats[cat_name] = pc

            # Create products
            for idx, prod_data in enumerate(tenant_data['products'], 1):
                prod_cat = product_cats.get(prod_data['cat'])
                
                product = Product(
                    tenant=tenant,
                    category=prod_cat,
                    name=prod_data['name'],
                    description=prod_data['desc'],
                    price=prod_data['price'],
                    is_available=True,
                    is_featured=prod_data.get('featured', False),
                    is_best_seller=prod_data.get('best', False),
                    is_spicy=prod_data.get('spicy', False),
                    is_vegetarian=prod_data.get('veg', False),
                    calories=prod_data.get('cal', 0),
                )

                # Set product image
                prod_slug = tenant_data['slug']
                img_path = f"products/{prod_slug}_{idx:02d}_"
                # Find matching image file
                for fname, fpath in product_files.items():
                    if fname.startswith(f"{prod_slug}_{idx:02d}_"):
                        product.image = fpath
                        break

                product.save()

            self.stdout.write(f'    → {len(tenant_data["products"])} products created')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  • {Category.objects.count()} categories'))
        self.stdout.write(self.style.SUCCESS(f'  • {Tenant.objects.count()} tenants'))
        self.stdout.write(self.style.SUCCESS(f'  • {Product.objects.count()} products'))
