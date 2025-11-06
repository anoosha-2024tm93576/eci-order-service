import hashlib
from decimal import Decimal, ROUND_HALF_EVEN
from typing import List


def bankers_round(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)


def signature_for_order(items: List[dict], tax: Decimal, shipping: Decimal) -> str:
    text = '|'.join([f"{i['sku']}:{i['unit_price']}:{i['quantity']}" for i in items])
    text += f"|tax:{tax}|shipping:{shipping}"
    return hashlib.sha256(text.encode('utf-8')).hexdigest()