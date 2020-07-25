import random, string
import os


def generate_opt_out_code():

    # Set the length
    code_length = 8

    # Set of values to pull characters from
    population = string.ascii_lowercase + string.ascii_uppercase + string.digits

    # Create code
    code = ''.join(random.choices(population, k=code_length))

    return code
