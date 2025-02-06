from rest_framework import filters


# Custom filters
class CustomSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get("name"):
            return ["name"]

        if request.query_params.get("location"):
            return ["location"]

        if request.query_params.get("datetime"):
            return ["datetime"]

        return super().get_search_fields(view, request)


class CustomOrderingFilter(filters.OrderingFilter):
    def get_ordering(self, request, queryset, view):
        if request.query_params.get("name"):
            return ["name"]

        if request.query_params.get("location"):
            return ["location"]

        if request.query_params.get("datetime"):
            return ["datetime"]

        return super().get_ordering(request, queryset, view)
