

with open('dog.jpg', 'rb') as f:
    bytes_ = f.read(1020)

    n = 5
    q = 99
    a = '{:032b}'.format(n)
    b = '{:04b}'.format(q)

    print(a)
    print(int(a))
