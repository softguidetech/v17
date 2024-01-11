# -*- coding: utf-8 -*-

import random
import string

# You can import it with:
# from ...thiqah_base.models.tools import get_random_string
def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
