import random
import csv

# get random rows from csv
def get_passengers(filename):
    with open(filename) as f:
        reader = csv.DictReader(f)
        return random.sample(list(reader), 1)[0]
        
if __name__ == "__main__":
    print(get_passengers("test.csv"))