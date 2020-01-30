import string
import random

def func_generate_user_app_id(size = 3, chars=string.ascii_uppercase):
    res = ''.join(random.choice(chars) for _ in range(size))
    return res.upper()

def func_generate_claim_id(size = 5, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))