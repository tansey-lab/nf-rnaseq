import ast

import numpy as np


def literal_eval_list(str_in):
    """Convert string to list using ast.literal_eval."""
    try:
        return ast.literal_eval(str_in.strip())
    except ValueError:
        return [np.nan]
