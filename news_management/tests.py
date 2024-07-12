from django.test import TestCase
from .models import NewsFeed
from .views import NewsFeedDetails,NewsFeedCreateView
from .serializers import NewsFeedSerializer
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse,resolve  
import uuid 
                                                                                                     
#testing models

class PostModelTest(TestCase):
    def setUp(self):
        self.post = NewsFeed.objects.create(
            title = 'Test Post',
            content = 'This is a test post'
        )
        
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post')
        self.assertIsInstance(self.post, NewsFeed) 

    def test_post_str(self):
        self.assertEqual(str(self.post.title), 'Test Post')     


#testing views
class PostViewTests(TestCase):
    def setUp(self):
        
        self.client = APIClient()
        self.post = NewsFeed.objects.create(
                title= 'test post',
                content = 'this is a test post'
    )                                                                            
        self.post_data= {
            'id': 23,
            'title': 'New post',
            'content': 'new post data',
            'createdAt': 2023-7-27
        }  
        self.url_list=reverse('NewsFeed_list')                     
        self.url_create = reverse('NewsFeed_create')
        self.url_details = reverse('NewsFeed_details',args=self.post_data['id'])
    def test_newsfeed_list(self):
        response=self.client.get(self.url_list)
        self.assertEqual(response.status_code,status.HTTP_200_OK)  

    #def test_newsfeed_details(self):
     #   response=self.client.get(reverse('NewsFeed_details'))
      #  newsfeed1=NewsFeed.objects.get(id=newsfeed1.id)
       # serializer=NewsFeedSerializer(newsfeed1)

        #self.assertEqual(response.status_code, status.HTTP_200_OK)
        #self.assertEqual(response.data,serializer.data)

    def test_post_create(self):
        newsfeed_data={
             'title':'newfeed3',
             'content':'this is new news'
         }
        response=self.client.post(self.url_create,newsfeed_data,format='json')
        
        self.assertEqual(response.status_code,status.HTTP_200_OK)   
             
        self.assertEqual(NewsFeed.objects.last().title, 'newfeed3')

    def test_update_post(self):
        updated_post={                        
            'title': 'updated post',
            'content': 'updated content for the post'
        }     
        response=self.client.put(self.url_details, updated_post, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, updated_post['title'])

    def test_delete_post(self):
        response=self.client.delete(self.url_details)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    def test_get_post(self):
        response = self.client.get(self.url_details)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], self.post.content)  

    def test_invalid_method(self):
        response=self.client.post(self.url_list, {'title':'Invalid', 'content':'invalid'})
        self.assertEqual(response.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)    

#Testing url

class TestUrl(TestCase):
    def setUp(self):
        self.News=NewsFeed.objects.create(
            title= 'test detail post',
            content = 'this is a test detail post'
            )
        
    def test_post_url_is_resolved(self):
        url=reverse('NewsFeed_create')
        self.assertEqual(resolve(url).func.view_class,NewsFeedCreateView )

    def test_post_details(self):    
        url=reverse('NewsFeed_details',args=[self.News.id]) 
        self.assertEqual(resolve(url).func.view_class, NewsFeedDetails)        

                                                                        