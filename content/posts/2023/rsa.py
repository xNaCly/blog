from math import gcd

p = 61
q = 97

print(f"n={p*q}")

phi = (p-1)*(q-1)

print(f"phi={phi}")

pe = []
for i in range(2, phi):
    if gcd(i, phi) == 1:
        pe.append(i)
        if len(pe) == 12:
            break

print(f"e={pe[-1]}")

d = 0
for i in range(0, phi):
    if (i*pe[-1]) % phi == 1:
        d = i
        break

print(f"d={d}")

example_string = "hello:)"
print(f"example_string={example_string}")
example_string_numeric = [ord(c) for c in example_string]
print(f"example_string_numeric={example_string_numeric}")

encrypted = []
for c in example_string_numeric:
    print(f"e({c})={c}^{{{pe[-1]}}} mod {p*q}={c ** pe[-1] % (p*q)}")
    encrypted.append(c ** pe[-1] % (p*q))

print(f"encrypted={encrypted}")
