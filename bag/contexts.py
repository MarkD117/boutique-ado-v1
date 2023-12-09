from decimal import Decimal
from django.conf import settings

def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0

    # Calculates delivery under threshold by multiplying
    # standard delivery percentage by total price
    if total < settings.FREE_DELIVERY_THRESHOLD:
        # total is calulated using Decimal() method as it is more accurate
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # Variable calculates how much more user has to spend for free delivery
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    # Sets delivery to 0 if total is over threshold
    else:
        delivery = 0
        free_delivery_delta = 0
    
    grand_total = delivery + total
    
    # Add all items to context for use in templates across the site
    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context