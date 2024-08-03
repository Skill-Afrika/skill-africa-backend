from rest_framework import filters


# Custom filters
class CustomSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        if request.query_params.get("username"):
            return ["user__username"]

        if request.query_params.get("niche"):
            return ["niche__name"]

        if request.query_params.get("name"):
            return ["first_name", "last_name"]

        return super().get_search_fields(view, request)


class CustomOrderingFilter(filters.OrderingFilter):
    def get_ordering(self, request, queryset, view):
        if request.query_params.get("username"):
            return ["user__username"]

        if request.query_params.get("lastname"):
            return ["last_name"]

        if request.query_params.get("firstname"):
            return ["first_name"]

        return super().get_ordering(request, queryset, view)
