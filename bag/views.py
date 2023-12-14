from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from products.models import Product

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

# Item id = id of product user would like to add to their bag
# Form is submitted to view
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    # Getting product for messages
    product = get_object_or_404(Product, pk=item_id)
    # Gets quantity as an integer and redirect url from form
    quantity = int(request.POST.get('quantity'))
    redirect_url = request.POST.get('redirect_url')
    size = None
    # If the product size is in the request,
    # the size variable will be set to that value
    if 'product_size' in request.POST:
        size = request.POST['product_size']

    # Stores users shopping bag contents in browser session so
    # that they can browse the site while the contents are saved.
    
    # Create a variable named bag that accesses request session trying
    # to get this variable if it already exists, and initialising it to
    # an empty dictionary if it doesnt.
    bag = request.session.get('bag', {})

    if size:
        # If the item is already in the bag, we check to see if an item with the
        # same id and size already exists, and if so, increment the quantity for
        # that size. Otherwise, set it equal to the quantity since the item already
        # exists in the bag but this is a new size for that item.
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
                messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
        # If the item is not already in the bag, it is added as a dictionary
        # with the key of items_by_size as there may be multiple items with
        # the same id but a different size. This allows us to structure the
        # bag so that we can have a single item id for each item but still
        # track multiple sizes.
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
            messages.success(request, f'Added size {size.upper()} {product.name} to your bag')
    # If there is no size, this code is run
    else:
        # If there is already an id in the bag dictionary matching the product
        # id selected by the user, the quantity value in incremented
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        # creating key of products id and set equal to quantity
        else:
            bag[item_id] = quantity
            messages.success(request, f'Added {product.name} to your bag')

    # overwriting bag variable in session
    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """ Adjust the qunatity of the specified product to the specified amount """
    
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    # The below if else operations are basically the same, they just have
    # to be handled differently due to the complex structure of the bag
    # for items that have sizes

    # If the item has a size the below code is executed
    if size:
        # If quantity is greater than 0, set quantity to specified input
        if quantity > 0:
            # Drill into items_by_size dictionary, find that specific size,
            # and set its quantity to the updated or remove it if the quantity
            # submittit is 0.
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        # Otherwise delete the item if the quantity is set to 0
        else:
            del bag[item_id]['items_by_size'][size]
            # If that item was the only size the user had it the bag,
            # this will cause the items_by_size dictionary to be empty
            # which will evaluate to false. pop() method is used to remove
            # the entire item id so we dont end up with an empty dictionary.
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
    # If the item does not have a size the following code is executed
    else:
        if quantity > 0:
            # Set quantity value to updated quantity
            bag[item_id] = quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            # Removes item entirely by using pop function
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')
        
    request.session['bag'] = bag
    return redirect(reverse('view_bag'))


def remove_from_bag(request, item_id):
    """ Remove the item from the shopping bag """
    
    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        # If the user removes an item that has a size
        if size:
            # Deletes the size key in items_by_size dictionary
            del bag[item_id]['items_by_size'][size]
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(request, f'Removed size {size.upper()} {product.name} from your bag')
        # If there is no size, we pop the item out of the bag
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')
            
        request.session['bag'] = bag
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)
