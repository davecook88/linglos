import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="4d4q54c8pq32rc8j",
        public_key="wgmx7trhpv67qv3q",
        private_key="0c97f89699e6b5a3e83351885874d0da"
    )
)

client_token = gateway.client_token.generate({
    "customer_id": a_customer_id #Change this later to the user id
})

result = gateway.transaction.sale({
    "amount": "10.00",
    "payment_method_nonce": nonce_from_the_client,
    "options": {
      "submit_for_settlement": True
    }
})
