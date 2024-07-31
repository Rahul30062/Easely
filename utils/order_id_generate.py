import random
import string

def generate_order_id(length=16):
    characters = string.ascii_letters + string.digits
    generated = ''.join(random.choice(characters) for _ in range(length))
    return f'order_{generated}'
