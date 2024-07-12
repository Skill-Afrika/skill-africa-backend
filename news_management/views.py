from rest_framework import generics, status
from rest_framework.response import Response
from .models import NewsFeed
from .serializers import NewsFeedSerializer
from .permission import  IsAdmin   
from drf_spectacular.utils import extend_schema




class NewsFeedListView(generics.ListAPIView):
    """
    List News feeds
    """
    queryset = NewsFeed.objects.order_by('-createdAt')
    serializer_class = NewsFeedSerializer

    @extend_schema(
        request=NewsFeedSerializer,

        responses={
            201: {
                'type': 'object',
                'properties': {

                    'title': {'type': 'string'},
                    'content': {'type': 'string'},

                },
                'Example': [
                    {
                        'summary': 'NewsFeeds listed succesfully ',
                        'value': {

                            'title': 'Cats',
                            'content': 'Cats are lovely and beautiful animals that live with human being',

                        }
                    }

                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='NewsFeeds listed',
        summary='List NewsFeed'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    

class NewsFeedDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    get,update and delete  NewsFeed
    """
    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
    permission_classes=[IsAdmin]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)
    

    # schema for Put method(update)
    @extend_schema(
        request=NewsFeedSerializer,

        responses={
            200: {
                'type': 'object',
                'properties': {

                    'title': {'type': 'string'},
                    'content': {'type': 'string'},

                },
                'examples': [
                    {
                        'summary': 'News feed update response',
                        'value': {
                            'title': 'Updated title',
                            'content': 'updated content',

                        }
                    }
                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='Reads,delete and updates NewsFeed. fields Accepts GET, PUT, PATCH and DELETE  methods',
        summary='update new News'

    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    # schema for delete method
    @extend_schema(
        responses={
            204: {
                'type': 'object',

                'examples': [
                    {
                        'summary': 'No content',
                        'description': 'Successfully deleted'
                    }
                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='Reads,delete and updates NewsFeed. fields Accepts GET, PUT, PATCH and DELETE methods',
        summary='delete NewsFeed'
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    # remaining schema for  get method
    @extend_schema(
        request=NewsFeedSerializer,

        responses={
            200: {
                'type': 'object',
                'properties': {

                    'title': {'type': 'string'},
                    'content': {'type': 'string'},

                },
                'examples': [
                    {
                        'summary': 'Retrieve News Feed response',
                        'value': {
                            'title': 'Updated title',
                            'content': 'updated content',

                        }
                    }
                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='Reads,delete and updates NewsFeed. fields Accepts GET, PUT, PATCH and DELETE  methods',
        summary='Retrieve News Feed'

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class NewsFeedCreateView(generics.CreateAPIView):
    queryset = NewsFeed.objects.all()
    serializer_class = NewsFeedSerializer
    permission_classes=[IsAdmin]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    """
      Create New News

    """
    @extend_schema(
        request=NewsFeedSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'createdAt': {'type': 'Date-time'}
                },
                'Example': [
                    {
                        'summary': 'News created successfully',
                        'value': {
                            'id': 'uuid4-2839-9282-dh83js',
                            'title': 'Cats',
                            'content': 'Cats are lovely and beautiful animals that live with human being',
                            'createdAt': 2024-6-22-1-34
                        }
                    }

                ]
            },
            400: {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        description='News Creation.Field accepts only POST method',
        summary='create new News'
    )
    def post(self, request):
        serializer = NewsFeedSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved_post = serializer.save()

        if saved_post:
            response = Response(
                status=status.HTTP_200_OK
            )
        else:
            response = Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        return response
