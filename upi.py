# upi.py

import urllib.parse

def generate_upi_link(merchant_upi, name, amount):
    """
    Generate a UPI deep link for payment.
    """
    params = {
        "pa": merchant_upi,            # Payee VPA
        "pn": name,                    # Payee Name
        "mc": "",                      # Merchant code (optional)
        "tid": "",                     # Transaction ID (optional)
        "tr": "",                      # Transaction ref (optional)
        "tn": f"Payment to {name}",    # Transaction note
        "am": f"{amount}",             # Amount
        "cu": "INR"                    # Currency
    }

    upi_url = "upi://pay?" + urllib.parse.urlencode(params)
    return upi_url
