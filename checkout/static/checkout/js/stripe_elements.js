/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

/*
    getting 'public key' and 'client secret' from template slicing off
    the first and last character of each removing the quotation marks
*/
var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
// Create stripe variable usinnng strip public key
var stripe = Stripe(stripePublicKey);
// Create and instance of stripe elements
var elements = stripe.elements();
// Basic styles for the card
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// Create card element
var card = elements.create('card', {style: style});
// Mount card element to div
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    // Error displayed as html in card error div
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textcontent = ''
    }
})

// Handle form submit
// Getting payment form
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    // Prevent default action of POST
    ev.preventDefault();
    // Disabling card element and submit button to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    // Triggers loading overlay
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // Getting the boolean value of the save info box by looking at its checked attribute
    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // Getting csrf token from input that Django generates on our form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // Small object created to pass above information to new view,
    // in addition to passing client_secret for the payment intent.
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    // Create variable for the new url
    var url = '/checkout/cache_checkout_data/';
    // Post the post data above to the view.
    // We want to wait for a response that the payment intent was updated
    // before calling the confirmed payment method. We can do this by
    // tacking on the .done method and executing the callback function.
    $.post(url, postData).done(function() {
    // stripe.confirmCardPayment() method sends card info securely to stripe
    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            // Add form data to payment intent
            // trim method used to remove excess white space
            billing_details: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                email: $.trim(form.email.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    state: $.trim(form.county.value),
                }
            }
        },
        shipping: {
            name: $.trim(form.full_name.value),
            phone: $.trim(form.phone_number.value),
            address: {
                line1: $.trim(form.street_address1.value),
                line2: $.trim(form.street_address2.value),
                city: $.trim(form.town_or_city.value),
                country: $.trim(form.country.value),
                postal_code: $.trim(form.postcode.value),
                state: $.trim(form.county.value),
            }
        }

    // Once card info has been sent, then, this function executes
    }).then(function(result) {
        // Checking for error and diplaying message
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            // Toggles payment form back in and loading overlay out
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            // Re-enable card element and sumbit button
            // Allows user to fix error
            card.update({ 'disabled': false});
            $('#submit-button').attr('disabled', false);
        // If there are no errors, set status to succeeded and submit form
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    });
    // Failure function if the view sends a 400 bad request response
    }).fail(function () {
        // Reloads the page, the error will be in django messages
        location.reload();
    })
});