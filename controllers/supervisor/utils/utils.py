from utils.config import *

def encode_type(type_name):
    return TYPE_ENCODING[type_name]

def decode_type(type_id):
    for k, v in TYPE_ENCODING.items():
        if v == type_id:
            return k
    return None