from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
# Special object used to generate search query
from django.db.models import Q
from .models import Product

# Create your views here.

def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None

    # Checks for a submitted query
    if request.GET:
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

    context = {
        'products': products,
        'search_term': query,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)