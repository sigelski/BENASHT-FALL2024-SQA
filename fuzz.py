### COMP-5710 Final Project ###
### 5b - Create a fuzz.py file that will automatically fuzz 5 Python methods of your choice. 
### Report any bugs you discovered by the fuzz.py file. fuzz.py will be automatically executed from GitHub actions. (20%)

import random
import string
import os
import sys
from datetime import datetime, timedelta

from MLForensics.mining.mining import (
    deleteRepo,
    dumpContentIntoFile,
    makeChunks,
    days_between,
    getPythonFileCount
)

def random_string(length=10):
    """Generate a random string of fixed length."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_path():
    """Generate a random file path."""
    return os.path.join(random_string(5), random_string(5) + ".txt")

def random_list():
    """Generate a random list with random elements."""
    return [random.randint(-1000, 1000) for _ in range(random.randint(0, 100))]

def random_date():
    """Generate a random datetime object."""
    start_date = datetime(2000, 1, 1)
    end_date = datetime.now()
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def fuzz_deleteRepo():
    print("Fuzzing deleteRepo...")
    dirName = random_path()
    type_ = random_string(5)
    try:
        deleteRepo(dirName, type_)
    except Exception as e:
        print(f"deleteRepo raised an exception with dirName='{dirName}' and type_='{type_}': {e}")

def fuzz_dumpContentIntoFile():
    print("Fuzzing dumpContentIntoFile...")
    strP = random_string(50)
    fileP = random_path()
    try:
        dumpContentIntoFile(strP, fileP)
    except Exception as e:
        print(f"dumpContentIntoFile raised an exception with strP='{strP}' and fileP='{fileP}': {e}")

def fuzz_makeChunks():
    print("Fuzzing makeChunks...")
    the_list = random_list()
    size_ = random.randint(-10, 100)
    try:
        chunks = makeChunks(the_list, size_)
        for chunk in chunks:
            pass
    except Exception as e:
        print(f"makeChunks raised an exception with the_list='{the_list}' and size_='{size_}': {e}")

def fuzz_days_between():
    print("Fuzzing days_between...")
    d1_ = random_date()
    d2_ = random_date()
    try:
        days_between(d1_, d2_)
    except Exception as e:
        print(f"days_between raised an exception with d1_='{d1_}' and d2_='{d2_}': {e}")

def fuzz_getPythonFileCount():
    print("Fuzzing getPythonFileCount...")
    path2dir = random_path()
    try:
        getPythonFileCount(path2dir)
    except Exception as e:
        print(f"getPythonFileCount raised an exception with path2dir='{path2dir}': {e}")

def main():
    print("Starting fuzz testing...\n")
    fuzz_functions = [
        fuzz_deleteRepo,
        fuzz_dumpContentIntoFile,
        fuzz_makeChunks,
        fuzz_days_between,
        fuzz_getPythonFileCount
    ]

    # Change this to determine number of times each method should be fuzzed.
    iterations = 10

    for i in range(iterations):
        print(f"\n--- Iteration {i+1} ---")
        for fuzz_func in fuzz_functions:
            fuzz_func()

    print("\nFuzzing has been completed!")

if __name__ == '__main__':
    main()