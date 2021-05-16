import sys

for line in sys.stdin:
    key, value = line.split('\t', 1)
    for word in value.strip().split():
        print('{}\t{}'.format(word, 1))