from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product

def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for item_id, item_data in bag.items():
        # Only execute this code if the item has no sizes
        # Checks to see if item data is an integer, if it
        # is, we are dealing with the quantity only.
        if isinstance(item_data, int):
            # Gets product and id
            product = get_object_or_404(Product, pk=item_id)
            # Adds quantity multiplied by price to total
            total += item_data * product.price
            # Increment product count by quantity
            product_count += item_data
            # Adding dictionary to list of bag items
            # Product object is added to give access to other product fields such as product.image etc
            bag_items.append({
                'item_id': item_id,
                'quantity': item_data,
                'product': product,
            })
        # If item has a size, we need to iterate through a dictionary
        else:
            product = get_object_or_404(Product, pk=item_id)
            # Iterate through inner dictionary of items_by_size
            for size, quantity in item_data['items_by_size'].items():
                # incrementing product and total count accordingly
                total += quantity * product.price
                product_count += quantity
                # Add size the bag_items returned to the template
                bag_items.append({
                    'item_id': item_id,
                    'quantity': quantity,
                    'product': product,
                    'size': size,
            })

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