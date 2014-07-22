from django.core.urlresolvers import resolve
from django.test import TestCase
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.views import home_page
from lists.models import Item, List

class ListViewTest(TestCase):
        
    def test_uses_list_template(self):
        # Create a new List object
        list_ = List.objects.create()
        # Use Django's test client to simulate requesting the resource at '/lists/<list_id>'
        response = self.client.get('/lists/%d/' % (list_.id,))
        # Assert that the response serves 'list.html' as template
        self.assertTemplateUsed(response, 'list.html')
    
    def test_displays_only_items_for_that_list(self):
        # Create a new List object
        correct_list = List.objects.create()
        # Create two Item objects that belong to the recent List object
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)

        # Create another (user's) List object
        other_list = List.objects.create()
        # Create two other Item objects that belong to this other list
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        # Use Django test client to request the page at '/lists/<first_list_id>/'
        response = self.client.get('/lists/%d/' % (correct_list.id,))

        # Assert that we will find both 'itemey 1' and 'itemey 2' on the page
        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_passes_correct_list_to_template(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get('/lists/%d/' % (correct_list.id,))
        self.assertEqual(response.context['list'], correct_list)

class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_returns_correct_html(self):
        # Create a new request
        request = HttpRequest()
        # with method POST
        request.method = 'POST'
        # and send a dictionary {'item_text': 'A new list item'} with it
        request.POST['item_text'] = 'A new list item'
        # Call the home_page view
        response = home_page(request)
        
        # Assert that the response serves 'list.html' as template
        self.assertTemplateUsed(response, 'home.html')

        """
        self.assertIn('A new list item', response.content.decode())
        expected_html = render_to_string(
            'home.html',
            {'new_item_text': 'A new list item'}
        )
        self.assertEqual(response.content.decode(), expected_html)
        """

class ListAndItemModelTest(TestCase):
    
    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()
        
        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()
        
        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)

class NewListTest(TestCase):

    def test_saving_a_POST_request(self):
        # Use Django test client to simulate posting
        self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'}
        )
        # After posting, one new Item object must be found...
        self.assertEqual(Item.objects.count(), 1)
        # at the first row.
        new_item = Item.objects.first()
        # That item's text must equals to 'A new list item'
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        # Use Django test client to simulate posting
        response = self.client.post(
            '/lists/new',
            data={'item_text': 'A new list item'}
        )
        # After posting, one new List object must be found...
        self.assertEqual(List.objects.count(), 1)
        # at the first row.
        new_list = List.objects.first()
        # Asserting that the response redirects to '/lists/<id>/'
        self.assertRedirects(response, '/lists/%d/' % (new_list.id,))

class NewItemTest(TestCase):

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        # Use Django test client to simulate posting
        self.client.post(
            '/lists/%d/add_item' % (correct_list.id,),
            data={'item_text': 'A new item for an existing list'}
        )
        # After posting, that list must contains 1 Item object...
        self.assertEqual(Item.objects.count(), 1)
        # at the first row.
        new_item = Item.objects.first()
        # Assert that Item object's text is 'A new item ...'
        self.assertEqual(new_item.text, 'A new item for an existing list')
        # Assert that that Item object belongs to the correct list
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        # Use Django test client to simulate posting
        response = self.client.post(
            '/lists/%d/add_item' % (correct_list.id,),
            data={'item_text': 'A new item for an existing list'}
        )
        # Assert that the response redirects to '/lists/<id>/'
        self.assertRedirects(response, '/lists/%d/' % (correct_list.id,))
