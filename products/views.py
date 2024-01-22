from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
# Special object used to generate search query
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm


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


def add_product(request):
    """ Add a product to the store """
    if request.method == 'POST':
        # Instanciate a new instance of the product form
        # from request.POST including request.FILES to capture
        # the image of the product if one was created.
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Store product when calling form.save()
            product = form.save()
            messages.success(request, 'Successfully added product!')
            # Redirect to the detail page of the added
            # product by sending along the product id.
            return redirect(reverse('product_detail', args=[product.id]))
        # Display error message to check the form
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
        
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


def edit_product(request, product_id):
    """ Edit a product in the store """
    # Pre fill form by getting the product
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        # Instantiate a form using request.POST and request.FILES,
        # and tell it the specific instance we want to update is 
        # the product that is obtained above.
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            # Redirect to the product detail page using the product id
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        # Info message letting user know they are editing a product
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


def delete_product(request, product_id):
    """ Delete a product from the store """
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
