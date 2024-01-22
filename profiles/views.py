from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order

def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    # If request method is post, create a new instance
    # of the user profile form using the post data
    if request.method == 'POST':
        # instance that is being updated is the profile retrieved above
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        form = UserProfileForm(instance=profile)
    # The profile and the related name on the order model are used to
    # get the users orders and we then return those to the template.
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)

def order_history(request, order_number):
    # Get order
    order = get_object_or_404(Order, order_number=order_number)

    # Message letting user know they are looking at a past order confirmation
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    # Uses template for checkout success confirmation as layout
    # is already set up for rendering a nice order confirmation.
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        # Variable added to context to check in template
        # if the user arrived via the order history view
        'from_profile': True,
    }

    return render(request, template, context)