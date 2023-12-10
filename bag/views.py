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
    # Stores users shopping bag contents in browser session so
    # that they can browse the site while the contents are saved.
    
    # Create a variable named bag that accesses request session trying
    # to get this variable if it already exists, and initialising it to
    # an empty dictionary if it doesnt.
    bag = request.session.get('bag', {})

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
    
