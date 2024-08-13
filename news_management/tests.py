from django.test import TestCase
from django.urls import reverse, resolve
from news_management.views import NewsFeedCreateView,NewsFeedListView,NewsFeedDetails
from rest_framework import status
from rest_framework.test import APIClient,APITestCase
from .models import NewsFeed
from .serializers import NewsFeedSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from profile_management.models import User
from rest_framework.authtoken.models import Token
#testing urls
class NewsFeedURLTests(TestCase):
    def test_newsfeed_list_url(self):
        url=reverse('NewsFeed_list')

        self.assertEqual(resolve(url).func.view_class,NewsFeedListView)

    #def test_newsfeed_create_url(self):

       # url=reverse('NewsFeed_create')

       # self.assertEqual(resolve(reverse('NewsFeed_create')).func.view_class,NewsFeedCreateView)

    def test_newsfeed_details_url(self):
        url = reverse('NewsFeed_details', args=['123'])

        self.assertEqual(resolve(url).func.view_class, NewsFeedDetails)

#testing views

class NewsFeedListViewTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.newsfeed1 = NewsFeed.objects.create(
            title='Azadirachta indica',
            content='Azadirachta indica also known as Neem tree is a common plant in Nigeria that has many important to human'        
        )
        self.newsfeed2= NewsFeed.objects.create(
            title= 'Mangifera indica',
            content= 'Mangifera indica also known as mango is a tree that produce edible fruit called mango'
        )

    def test_list_newsfeeds(self):
        response= self.client.get(reverse('NewsFeed_list'))
        newsfeeds = NewsFeed.objects.order_by('-createdAt')
        serializer= NewsFeedSerializer(newsfeeds, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)



class NewsFeedDetailsTest(APITestCase):
    def setUp(self):
        self.user= User.objects.create_superuser(username='admin',password='12345678')
        self.client= APIClient()

        self.client.force_authenticate(user=self.user)

        self.news_feed = NewsFeed.objects.create(
            title='Cats',
            content='cats are animals',
            #author=self.user
        )
        self.valid_payload={
            'title' : 'Updated title',
            'content': 'updated content',
        }
        self.invalid_payload={
            'title': '',
            'content': '',
        }
        self.detail_url= reverse('NewsFeed_details', kwargs={'pk': self.news_feed.pk})
    def test_retrieve_news_feed(self):
        response= self.client.get(self.detail_url)
        news_feed=NewsFeed.objects.get(pk=self.news_feed.pk)
        serializer=NewsFeedSerializer(news_feed)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_update_newsfeed_valid_payload(self):
        response=self.client.put(self.detail_url, data=self.valid_payload,format='json')
        self.news_feed.refresh_from_db()

        self.assertEqual(self.news_feed.title, self.valid_payload['title'])
        self.assertEqual(self.news_feed.content, self.valid_payload['content'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_newsfeed_invalid(self):
        response= self.client.put(self.detail_url, data=self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_newsfeed(self):
        response= self.client.delete(self.detail_url)
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)
        self.assertFalse(NewsFeed.objects.filter(pk=self.news_feed.pk).exists())



class NewsFeedCreateView(APITestCase):
    def setUp(self):
        self.admin_user= User.objects.create_superuser(username='admin',email='admin@gmail.com', password='12345')
        self.normal_user= User.objects.create_user(username='user', email='user@gmail.com', password='password123')
        self.url =reverse('NewsFeed_create')
        
    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
    
        return str(refresh.token)
    

    def test_create_newsfeed_as_admin(self):
        token= Token.objects.get(user= User.username)
        self.client= APIClient()
        #self.client.force_authenticate(user=User)

        self.client.credentials(HTTP_AUTHORIZATION='Token' + token.key)
        data ={
            'title': 'New News',
            'content': 'This is a test news content'
        }
        response=self.client.post(self.url,data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['content'], data['content'])

    