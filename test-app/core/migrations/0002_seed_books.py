from django.db import migrations


def seed_books(apps, schema_editor):
    Book = apps.get_model('core', 'Book')

    books_data = [
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A classic novel set in the Jazz Age, exploring themes of wealth, love, and the American Dream through the eyes of narrator Nick Carraway and the mysterious millionaire Jay Gatsby.",
            "cover_image": "https://covers.openlibrary.org/b/id/7222246-L.jpg",
            "price": 12.99,
            "published_year": 1925,
        },
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "description": "A profound exploration of racial injustice in the American South, told through the innocent eyes of Scout Finch as her father, Atticus, defends a Black man falsely accused of crime.",
            "cover_image": "https://covers.openlibrary.org/b/id/8228691-L.jpg",
            "price": 14.99,
            "published_year": 1960,
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "description": "A dystopian masterpiece depicting a totalitarian society where Big Brother watches everyone. Winston Smith struggles against the oppressive Party that controls every aspect of life.",
            "cover_image": "https://covers.openlibrary.org/b/id/7222336-L.jpg",
            "price": 11.99,
            "published_year": 1949,
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": "A witty romantic novel following Elizabeth Bennet as she navigates issues of manners, morality, and marriage in Georgian England, ultimately finding love with the proud Mr. Darcy.",
            "cover_image": "https://covers.openlibrary.org/b/id/8479576-L.jpg",
            "price": 10.99,
            "published_year": 1813,
        },
        {
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "description": "The story of teenage angst and alienation, following Holden Caulfield through New York City after being expelled from prep school, questioning the phoniness of the adult world.",
            "cover_image": "https://covers.openlibrary.org/b/id/8231856-L.jpg",
            "price": 13.99,
            "published_year": 1951,
        },
        {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "description": "A fantasy adventure following Bilbo Baggins, a comfortable hobbit who is whisked away on an unexpected journey with dwarves to reclaim their homeland from a dragon.",
            "cover_image": "https://covers.openlibrary.org/b/id/8406786-L.jpg",
            "price": 15.99,
            "published_year": 1937,
        },
        {
            "title": "Brave New World",
            "author": "Aldous Huxley",
            "description": "A chilling vision of a future society where humans are genetically modified and socially conditioned for a seemingly perfect but ultimately dehumanizing existence.",
            "cover_image": "https://covers.openlibrary.org/b/id/5765320-L.jpg",
            "price": 12.49,
            "published_year": 1932,
        },
        {
            "title": "The Lord of the Rings",
            "author": "J.R.R. Tolkien",
            "description": "An epic fantasy trilogy following Frodo Baggins and the Fellowship on their quest to destroy the One Ring and defeat the Dark Lord Sauron in Middle-earth.",
            "cover_image": "https://covers.openlibrary.org/b/id/8743251-L.jpg",
            "price": 24.99,
            "published_year": 1954,
        },
        {
            "title": "Crime and Punishment",
            "author": "Fyodor Dostoevsky",
            "description": "A psychological drama following Raskolnikov, a poor student who commits murder and struggles with guilt, morality, and redemption in 19th century St. Petersburg.",
            "cover_image": "https://covers.openlibrary.org/b/id/8235822-L.jpg",
            "price": 11.49,
            "published_year": 1866,
        },
        {
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "description": "The magical story of Harry Potter, an orphan who discovers he is a wizard on his eleventh birthday and begins his journey at Hogwarts School of Witchcraft and Wizardry.",
            "cover_image": "https://covers.openlibrary.org/b/id/10521270-L.jpg",
            "price": 16.99,
            "published_year": 1997,
        },
        {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "description": "A philosophical novel about Santiago, an Andalusian shepherd boy who dreams of finding a worldly treasure and embarks on a journey to discover his Personal Legend.",
            "cover_image": "https://covers.openlibrary.org/b/id/8769278-L.jpg",
            "price": 14.49,
            "published_year": 1988,
        },
        {
            "title": "One Hundred Years of Solitude",
            "author": "Gabriel Garcia Marquez",
            "description": "A landmark of magical realism, chronicling seven generations of the Buendia family in the fictional town of Macondo, Colombia, blending reality with fantasy.",
            "cover_image": "https://covers.openlibrary.org/b/id/8701489-L.jpg",
            "price": 15.49,
            "published_year": 1967,
        },
    ]

    for book_data in books_data:
        Book.objects.create(**book_data)


def remove_books(apps, schema_editor):
    Book = apps.get_model('core', 'Book')
    Book.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_books, remove_books),
    ]
