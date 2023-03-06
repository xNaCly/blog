from math import gcd

p = 61
q = 97

print(f"n={p*q}")
# n=5917

phi = (p-1)*(q-1)

print(f"phi={phi}")
# phi=5760

pe = []
for i in range(2, phi):
    if gcd(i, phi) == 1:
        pe.append(i)
        # stop looping after 12 elements in array pe
        if len(pe) == 12:
            break

print(f"e={pe[-1]}")
# e=47

d = 0
for i in range(0, phi):
    if (i*pe[-1]) % phi == 1:
        d = i
        break

print(f"d={d}")
# d=1103

example_string = "hello:)"
print(f"example_string={example_string}")
# example_string=hello:)
example_string_numeric = [ord(c) for c in example_string]
print(f"example_string_numeric={example_string_numeric}")
# example_string_numeric=[104, 101, 108, 108, 111, 58, 41]

encrypted = []
for c in example_string_numeric:
    encrypted.append(c ** pe[-1] % (p*q))

print(f"encrypted={encrypted}")
# encrypted=[3381, 5214, 2575, 2575, 3000, 3303, 3809]
print(f"chiffre={' '.join([str(i) for i in encrypted])}")
# chiffre=3381 5214 2575 2575 3000 3303 3809

decrypted = []
for c in encrypted:
    decrypted.append(c ** d % (p*q))

print(f"decrypted={decrypted}")
# decrypted=[104, 101, 108, 108, 111, 58, 41]
print(f"result={''.join([chr(i) for i in decrypted])}")
# result=hello:)

def prime_factors(n):
    factors = []
    d = 2
    while n > 1:
        while n % d == 0:
            factors.append(d)
            n /= d
        d = d + 1
    return factors

factors = prime_factors(p*q);
print(f"factors={factors}")
# factors=[61, 97]
new_phi = (factors[0]-1)*(factors[1]-1)
for i in range(0, p*q):
    if (47 * i) % 5760 == 1:
        print(f"d={i}")
        break
