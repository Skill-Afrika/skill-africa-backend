from django.test import TestCase,SimpleTestCase
from .models import Post
from .views import PostDetails,PostListCreate
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse,resolve  
 
                                                                                                     
#testing models

class PostModelTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(
            title = 'Test Post',
            content = 'This is a test post'
        )
        
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test post')
        self.assertIsInstance(self.post, Post) 

    def test_post_str(self):
        self.assertEqual(str(self.post.title), 'Test Post')     


#testing views
class PostViewTests(TestCase):
    def setUp(self):
        
        self.post = Post.objects.create()
        self.client = APIClient()
        self.post = Post.objects.create(
                title= 'test post',
                content = 'this is a test post'
    )                                                                            
        self.post_data= {
            'title': 'New post',
            'content': 'new post data'
        }                       
        self.url_list_create = reverse('post_list_create')
        self.url_details =     reverse('post_details',args=[self.post.id])
    def test_list_post(self):
        response=self.client.get(self.url_list_create)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response,self.post.title)

    def test_post_create(self):
        response=self.client.post(self.url_list_create,self.post_data,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)   
        self.assertEqual(Post.objects.get(id=response.data['id']).title, self.post_data['title'])

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

#Testing url

class TestUrl(SimpleTestCase):
    def test_post_url_is_resolved(self):
        url=reverse('post_list_create')
        self.assertEqual(resolve(url).func.view_class,PostListCreate)

    def test_post_details(self):
        url=reverse('post_details') 
        self.assertEqual(resolve(url).func.view_class, PostDetails)    
                                                 