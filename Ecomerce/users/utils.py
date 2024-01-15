
import random
import string
from .models import Referral

def generate_referral_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    while Referral.objects.filter(code=code).exists():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return code
