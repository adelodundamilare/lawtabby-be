import stripe
from decouple import config

from accounts.models import StripeCustomer, User

stripe.api_key = config('STRIPE_SECRET_KEY', default='')

def create_subscriptions(data):

    results = []

    for product_data in data:
        # Create the product
        product = stripe.Product.create(
            name=product_data["name"],
            type=product_data["type"]
        )

        prices = []
        for price_data in product_data["price"]:
            # Create the price
            price = stripe.Price.create(
                unit_amount=price_data["amount"] * 100,  # Convert to cents
                currency=price_data["currency"],
                recurring=price_data["recurring"],
                product=product.id,
            )
            prices.append(price)

        results.append({"product": product, "prices": prices})

    return results

def  create_checkout_session(user, page_url, price_id):
    checkout_session = stripe.checkout.Session.create(
        success_url=page_url + '?status=success&session_id={CHECKOUT_SESSION_ID}',
        cancel_url=page_url + '?status=canceled',
        customer_email=user.email,
        mode='subscription',
        # ui_mode="embedded",
        # automatic_tax={'enabled': True},
        line_items=[{
            'price': price_id,
            'quantity': 1
        }],
    )

    stripe_customer, created = StripeCustomer.objects.get_or_create(
            user=user,
            defaults={
                'stripe_checkout_session_id': checkout_session.id,
                'stripe_price_id': price_id,
            }
        )

    if not created:
        stripe_customer.stripe_checkout_session_id = checkout_session.id
        stripe_customer.stripe_price_id = price_id
        stripe_customer.save()

    return checkout_session.url

def  create_portal_session(user, page_url):
    checkout_record = StripeCustomer.objects.filter(user=user).last()

    if not checkout_record:
        raise ValueError("Checkout record not found")

    checkout_session = stripe.checkout.Session.retrieve(checkout_record.stripe_checkout_session_id)

    portal_session = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=page_url,
    )

    return portal_session.url

def get_products(user):
    if has_active_sub(user):
        return [], True

    products = stripe.Product.list(active=True, expand=['data.default_price'])
    products_data = []

    for product in products:
        prices = stripe.Price.list(product=product.id, active=True)

        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "active": product.active,
            "prices": [{"id": price.id, "amount": price.unit_amount} for price in prices]
        }
        products_data.append(product_data)

    return products_data, False

def has_active_sub(user):
    customer = stripe.Customer.list(email=user.email).data

    if customer:
        subscriptions = stripe.Subscription.list(customer=customer[0].id, status='active')
        if subscriptions.data:
            return True
    return False

def on_checkout_session_completed(session):
    checkout_record = StripeCustomer.objects.get(
        stripe_checkout_session_id = session.get('id')
    )
    checkout_record.stripe_customer_id = session.get('customer')
    checkout_record.has_access = True
    checkout_record.save()

    return True

def on_checkout_session_deleted(session):
    # client_reference_id = session.get('client_reference_id')
    # stripe_customer_id = session.get('customer')
    # stripe_subscription_id = session.get('subscription')

    # user = User.objects.get(id=client_reference_id)
    # if not user:
    #     raise ValueError("User not found")

    # StripeCustomer.objects.create(
    #     user=user,
    #     stripeCustomerId=stripe_customer_id,
    #     stripeSubscriptionId=stripe_subscription_id,
    # )

    # checkout_record = StripeCustomer.objects.get(
    #     stripe_customer_id=data_object['customer']
    # )
    # checkout_record.has_access = False
    # checkout_record.save()

    return True