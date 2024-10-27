from .models import RecycledItem

def recycled_item_list(request):
    return {
        'recent_items': RecycledItem.objects.all()
    }
