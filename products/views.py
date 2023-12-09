from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
# Special object used to generate search query
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    # Checks for a submitted query
    if request.GET:
        # Check if sort is in request.GET
        if 'sort' in request.GET:
            # if it is, we set it to both sort (which is None) and sortkey 
            sortkey = request.GET['sort']
            sort = sortkey
            # Sets case insensitivity sorting on name
            # field by setting name to lowercase
            if sortkey == 'name':
                # preserves original field name by renaming sortkey to
                # lower_name in the event the user is sorting by name 
                sortkey = 'lower_name'
                # Annotate current list of products with new field
                products = products.annotate(lower_name=Lower('name'))
            # Allows categorized products to be sorted by name
            if sortkey == 'category':
                sortkey = 'category__name'
            # Checks to see if direction is ascending or descending
            if 'direction' in request.GET:
                direction = request.GET['direction']
                # Reverses direction if direction is descending
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            # sorts products using order_by() method
            products = products.order_by(sortkey)

        # If a category is submitted
        if 'category' in request.GET:
            # splits categories into list at the commas
            categories = request.GET['category'].split(',')
            # Filters all products whos category name is in list 
            products = products.filter(category__name__in=categories)
            # Filter categories down to names in the list
            categories = Category.objects.filter(name__in=categories)
        
        # if 'q' is in the request, assigns variable to submitted value
        if 'q' in request.GET:
            query = request.GET['q']
            # if 'q' not in request, display error and redirect to products
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            
            # Allows queries to be filtered based on name OR description
            # "i" makes queries case insensitive
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    # Return current sorting methodology to the template
    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)