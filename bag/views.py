from django.shortcuts import render, redirect

# Create your views here.

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

# Item id = id of product user would like to add to their bag
# Form is submitted to view
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """
    
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
            else:
                bag[item_id]['items_by_size'][size] = quantity
        # If the item is not already in the bag, it is added as a dictionary
        # with the key of items_by_size as there may be multiple items with
        # the same id but a different size. This allows us to structure the
        # bag so that we can have a single item id for each item but still
        # track multiple sizes.
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
    # If there is no size, this code is run
    else:
        # If there is already an id in the bag dictionary matching the product
        # id selected by the user, the quantity value in incremented
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        # creating key of products id and set equal to quantity
        else:
            bag[item_id] = quantity

    # overwriting bag variable in session
    request.session['bag'] = bag
    return redirect(redirect_url)
