import paypalrestsdk


def payment(capsule_id):
    approval_url = ""
    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": "AeJR6f58Yie9jAXRAosl2vAV-1ZS59SEkTJdLx4CTuMto3EoEQhuvRhH_NeGivLNR5-NmoJWCJRsmMYW",
        "client_secret": "EF_VuVcHv1zWJFQGoDtROZlmknkp-EWil0RcM1GztPPkcG2dRbkNKRpsTFgNQcg5g8el8z8vZ4biFd8C"})

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:8000/payment/execute",
            "cancel_url": "http://localhost:8000/deletecapsule/" + str(capsule_id)},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "modular capsule",
                    "sku": "item",
                    "price": "11.99",
                    "currency": "EUR",
                    "quantity": 1}]},
            "amount": {
                "total": "11.99",
                "currency": "EUR"},
            "description": "Modular capsule"}]})

    if payment.create():
        print("Payment created successfully")
    else:
        print(payment.error)

    for link in payment.links:
        if link.rel == "approval_url":
            # Convert to str to avoid Google App Engine Unicode issue
            # https://github.com/paypal/rest-api-sdk-python/pull/58
            approval_url = str(link.href)

    return approval_url


def execute(payment, payer_id):
    if payment.execute({"payer_id": payer_id}):
        print("Payment execute successfully")
    else:
        print(payment.error)  # Error Hash
