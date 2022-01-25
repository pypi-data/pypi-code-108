from datetime import date

from django.db import connection
from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestAssertMixin, print_response
from tests.models import Author, Book, BookType


class BasicAPITest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        with connection.cursor() as cursor:
            cursor.execute("create extension if not exists unaccent;")

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        cls.author1_book1 = Book.objects.create(
            author=cls.author1,
            name="The Hobbit",
            pub_date=date(1937, 1, 1)
        )
        cls.author1_book2 = Book.objects.create(
            author=cls.author1,
            name="The Fellowship of the Ring",
            pub_date=date(1954, 1, 1)
        )
        cls.author1_book3 = Book.objects.create(
            author=cls.author1,
            name="The Two Towers",
            pub_date=date(1954, 1, 1)
        )
        cls.author1_book4 = Book.objects.create(
            author=cls.author1,
            name="The Return of the King",
            pub_date=date(1955, 1, 1)
        )
        cls.author2 = Author.objects.create(
            first_name='Philip Kindred',
            last_name='Dick',
            science_fiction=True,
            slug='philip-k-dick')
        cls.author3 = Author.objects.create(
            first_name='Isaac',
            last_name='Asimov',
            science_fiction=True,
            slug='isaac-asimov')
        cls.author3_book1 = Book.objects.create(
            author=cls.author3,
            name="The Caves of Steel",
            pub_date=date(1954, 1, 1),
            pages=224,
            rating=4.6,
        )
        cls.author3_book2 = Book.objects.create(
            author=cls.author3,
            name="The Naked Sun",
            pub_date=date(1957, 1, 1),
        )
        cls.author3_book3 = Book.objects.create(
            author=cls.author3,
            name="The Robots of Dawn",
            pub_date=date(1983, 1, 1),
        )
        cls.author4 = Author.objects.create(
            first_name='Joanne',
            last_name='Rowling',
            science_fiction=False,
            gender='female',
            slug='j-k-rowling')

    def test_get_list(self):
        response = self.client.get('/api/authors')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_order_asc(self):
        response = self.client.get('/api/authors?order=last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Asimov', 'Dick', 'Rowling', 'Tolkien'])

    def test_get_list_order_desc(self):
        response = self.client.get('/api/authors?order=-last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Tolkien', 'Rowling', 'Dick', 'Asimov'])

    def test_get_list_order_multi(self):
        response = self.client.get('/api/authors?order=gender,last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Rowling', 'Asimov', 'Dick', 'Tolkien'])

    def test_get_list_order_multi_desc(self):
        response = self.client.get('/api/authors?order=gender,-last_name')

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Rowling', 'Tolkien', 'Dick', 'Asimov'])

    def test_search_list(self):
        response = self.client.get('/api/authors?search=isaac')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.first_name', 'Isaac')
        self.assertJE(response, 'items.@0.last_name', 'Asimov')
        self.assertJE(response, 'items.@0.gender.value', 'male')
        self.assertJE(response, 'items.@0.gender.label', 'Male')

    def test_filter_get(self):
        response = self.client.get('/api/authors/filters')
        self.assertRC(response, 200)
        print_response(response)
        self.assertJE(response, 'items.@0.name', 'book_gender')
        self.assertJE(response, 'items.@0.items.@0.name', 'science_fiction')

        response = self.client.get('/api/books/filters')
        self.assertRC(response, 200)
        print_response(response)

    def test_filter_func_bool(self):
        response = self.client.get('/api/authors?heroic_fantasy=true')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.resource_name',
                                'John Ronald Reuel Tolkien')

        response = self.client.get('/api/authors?heroic_fantasy=false')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

        response = self.client.get(
            '/api/authors?heroic_fantasy=false&heroic_fantasy=true')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_filter_func_date(self):
        response = self.client.get('/api/books?pub_date_gte=1955-01-01')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_filter_func_char_choices(self):
        response = self.client.get('/api/authors?last_name_choices=Tolkien')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)

    def test_model_filter_bool(self):
        response = self.client.get('/api/authors?science_fiction=true')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 2)

    def test_model_filter_char(self):
        response = self.client.get('/api/authors?first_name=Isaac')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.first_name', "Isaac")

    def test_model_filter_integer(self):
        response = self.client.get('/api/books?pages=224')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.name', "The Caves of Steel")

    def test_model_filter_float(self):
        response = self.client.get('/api/books?rating=4.6')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.name', "The Caves of Steel")

    def test_model_filter_date(self):
        response = self.client.get('/api/books?pub_date=1954-01-01')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_model_filter_decimal(self):
        # TODO: Wait Decimal implementation
        pass

    def test_model_filter_foreign_key(self):
        response = self.client.get(f'/api/books?author={self.author3.pk}')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        self.assertJE(response, 'items.@0.author.pk', self.author3.pk)
        self.assertJE(response, 'items.@0.author.pk', self.author3.pk)
        self.assertJE(response, 'items.@0.author.pk', self.author3.pk)

    def test_model_filter_char_choices(self):
        response = self.client.get('/api/authors?gender=male')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_model_filter_func_bool(self):
        response = self.client.get('/api/authors?last_name=true')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_without_pagination(self):
        response = self.client.get('/api/authors?meta=count')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_with_subset(self):
        for i in range(1, 11):
            Author.objects.create(
                first_name='Vladimir',
                last_name=f'Ottor {i}',
                science_fiction=True,
                slug=f'vald-ottor-{i}')

        response = self.client.get('/api/authors?meta=subset&offset=5&limit=3')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.subset.count', 14)

    def test_wrong_meta(self):
        response = self.client.get('/api/authors?meta=qwertz')

        self.assertRC(response, 400)

    def test_meta_service(self):
        response = self.client.get('/api/authors/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name.type', 'CharField')
        self.assertJE(response, 'first_name.name', 'First Name')
        self.assertJE(response, 'last_name.type', 'CharField')
        self.assertJE(response, 'last_name.name', 'Last Name')
        self.assertJE(response, 'books.type', 'ForeignKey')
        self.assertJE(response, 'books.name', 'Books')
        self.assertJE(response, 'created_at.type', 'DateField')
        self.assertJE(response, 'created_at.name', 'Created at')
        self.assertJE(response, 'name_length.type', 'IntegerField')
        self.assertJE(response, 'name_length.name', 'Name Length')

    def test_get_detail_by_id(self):
        response = self.client.get(f'/api/authors/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', self.author1.first_name)
        self.assertJE(response, 'last_name', self.author1.last_name)
        self.assertJE(response, 'name_length', 25)
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_get_detail_by_slug(self):
        response = self.client.get(f'/api/authors/slug/{self.author1.slug}')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', self.author1.first_name)
        self.assertJE(response, 'last_name', self.author1.last_name)
        self.assertJE(response, 'name_length', 25)
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_get_date_format(self):
        response = self.client.get(f'/api/books/{self.author1_book1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date', '1937-01-01')
        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}?date_format=0')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date', '1937-01-01')
        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}?date_format=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date.value', '1937-01-01')
        self.assertJE(response, 'pub_date.formatted', '01/01/1937')

    def test_get_non_existant_record(self):
        response = self.client.get('/api/authors/999999')
        self.assertRC(response, 404)

    def test_get_non_existant_record_by_slug(self):
        response = self.client.get('/api/authors/slug/not-existent')
        self.assertRC(response, 404)

    def test_create(self):
        response = self.client.post(
            '/api/authors', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'name_length': 1,
                'gender': 'male',
                'slug': 'arthur-c-clarke'})

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'Arthur Charles')
        self.assertJE(response, 'last_name', 'Clarke')
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_create_enum(self):
        response = self.client.post(
            '/api/authors', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'name_length': 1,
                'gender': {'value': 'male'},
                'slug': 'arthur-c-clarke'})

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'Arthur Charles')
        self.assertJE(response, 'last_name', 'Clarke')
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_update(self):
        response = self.client.put(
            f'/api/authors/{self.author1.pk}',
            {'pk': self.author2.pk,  # pk and id must be ignored
             'created_at': '2021-01-01',  # created_at must be ignored because
                                          # it is a readonly field.
             'first_name': 'J. R. R.',
             'name_length': 1,
             'gender': 'female',
             'slug': 'j-r-r-tolkien'})  # slug must be updated})

        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')
        self.assertEqual(self.author1.last_name, self.author1.last_name)
        self.assertEqual(self.author1.slug, 'j-r-r-tolkien')
        self.assertEqual(self.author1.gender, 'female')
        self.assertNotEqual(self.author1.created_at, '2021-01-01 11:30:00')
        self.assertEqual(self.author1.created_at, self.author1.created_at)

        response = self.client.put(
            f'/api/authors/{self.author1.pk}', {'gender': {'value': 'male'}})
        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.gender, 'male')

    def test_delete(self):
        response = self.client.delete(
            f'/api/authors/{self.author2.pk}')

        self.assertRC(response, 200)

        author = Author.objects.filter(pk=self.author2.pk)
        self.assertEqual(author.count(), 0)

    def test_delete_with_wrong_key(self):
        response = self.client.delete(
            '/api/authors/99999')
        self.assertRC(response, 404)

    def test_create_with_foreignkey(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Fellowship of the Ring')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-07-29')
        self.assertNJE(response, 'created_at', '1954-07-29')

    def test_create_with_foreignkey_resource(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring',
                'author': {
                    'pk': self.author1.pk,
                    'resource_name': "Author One"},
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author1.pk)

    def test_create_with_wrong_foreignkey(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring',
                'author': 999999,
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'author',
                      ['Author instance with id 999999 does not exist.'])

    def test_update_with_foreignkey(self):
        book1 = Book.objects.create(
            name='The Fellowship of the Ring',
            author=self.author1,
            pub_date='1954-07-29',
        )

        response = self.client.put(
            f'/api/books/{book1.pk}', {
                'name': 'The Two Towers',
                'pub_date': '1954-11-11',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Two Towers')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-11-11')

        response = self.client.put(
            f'/api/books/{book1.pk}', {
                'name': 'The Man in the High Castle',
                'author': self.author2.pk,
                'author_id': self.author3.pk,  # must be ignored
                'pub_date': '1962-10-01',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Man in the High Castle')
        self.assertJE(response, 'author.pk', self.author2.pk)
        self.assertJE(response, 'pub_date', '1962-10-01')

        response = self.client.put(
            f'/api/books/{book1.pk}', {
                'name': 'A Scanner Darkly',
                'author': {
                    'pk': self.author2.pk,
                    'resource_name': 'Philip Kindred Dick'},
                'pub_date': '1977-01-01',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'A Scanner Darkly')
        self.assertJE(response, 'author.pk', self.author2.pk)
        self.assertJE(response, 'pub_date', '1977-01-01')

    def test_update_with_wrong_key_and_foreignkey(self):
        book1 = Book.objects.create(
            name='The Fellowship of the Ring',
            author=self.author1,
            pub_date='1954-07-29')

        response = self.client.put(
            '/api/books/99999', {
                'name': 'The Two Towers',
                'pub_date': '1954-11-11'})
        self.assertRC(response, 404)

        response = self.client.put(
            f'/api/books/{book1.pk}', {
                'name': 'The Two Towers',
                'author': 999999,
                'pub_date': '1954-11-11'})
        self.assertRC(response, 422)
        self.assertJE(response, 'author',
                      ['Author instance with id 999999 does not exist.'])

    def test_delete_with_foreignkey(self):
        book = Book.objects.create(
            name='The Fellowship of the Ring',
            author=self.author1,
            pub_date='1954-07-29')

        response = self.client.delete(
            f'/api/authors/{self.author1.pk}')

        self.assertRC(response, 400)
        book.refresh_from_db()

    def test_create_validation(self):
        response = self.client.post(
            '/api/books', {
                'name': '',
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 422)
        self.assertJE(response, 'name',
                      ['This field cannot be blank.'])
        self.assertJE(response, 'author',
                      ['This field cannot be null.'])

    def test_update_validation(self):
        book1 = Book.objects.create(
            name='The Fellowship of the Ring',
            author=self.author1,
            pub_date='1954-07-29',
        )

        response = self.client.put(
            f'/api/books/{book1.pk}', {
                'name': '',
                'pub_date': '1954-11-11',
            })

        self.assertRC(response, 422)
        self.assertJE(response, 'name',
                      ['This field cannot be blank.'])

    def test_custom_repr(self):
        book_type = BookType.objects.create(
            name="Epic Fantasy",
            slug="epic-fantasy",
        )

        book = Book.objects.create(
            name='The Fellowship of the Ring',
            author=self.author1,
            type=book_type,
            pub_date='1954-07-29',
        )
        response = self.client.get(f'/api/books/{book.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'type.resource_name', book_type.name)
        self.assertJE(response, 'type.resource_slug', book_type.slug)

        response = self.client.get(f'/api/book-types/{book_type.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'resource_name', book_type.name)
        self.assertJE(response, 'resource_slug', book_type.slug)
        self.assertJE(response, 'name', book_type.name)
        self.assertJE(response, 'slug', book_type.slug)
