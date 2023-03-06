---
title: "RSA and Python"
summary: "Understanding, implementing and cracking RSA"
date: 2023-03-06
draft: true
math: true
tags:
  - crypto
  - python
---

## Understanding RSA

{{<callout type="Info">}}
Um die folgenden Erklärungen simpel zu halten beschränken wir uns auf kleine Primzahlen. In der Praxis sollten die verwendeten Zahlen mindestens 512 Bit betragen (64 byte, [long long](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1256.pdf), p. 23).
{{</callout>}}

RSA ist ein asymmetrisches kryptographisches Verfahren das aus einem öffentlichen Schlüssel zur Verschlüsselung und einem privaten Schlüssel zur Entschlüsselung besteht.

Das bedeuted, dass man den z.B. den Ascii Wert eines Buchstaben mit dem öffentlichen Schlüssel in ein Chiffre umsetzt und mit dem privaten Schlüssel wieder in den Klartext konvertiert.

RSA bietet Sicherheit, wenn der öffentlicher Schlüssel und der private Schlüssel ausreichend lang sind (min. 64bytes).
Dies ist der Fall, da man theoretisch mit ungemeinem Aufwand für kleine Primzahlen aus dem Öffentlichen Schlüssel den privaten Schlüssel errechnen kann.

### Private and Public key

#### Choose Numbers

Der erste Schritt der Schlüsselgenerierung besteht daraus
`p` und `q` so zu wählen, dass:

$$
\begin{align}
p \not= q
\end{align}
$$

und das beide Zahlen prim sind.

Hier können wir zum Beispiel `p` und `q` wie folgt wählen:

$$
\begin{align}
p = 61 \\\
q = 97
\end{align}
$$

```python
p = 61
q = 97
```

#### Calculating the sum of p and q

Nun gilt es `n` aus der Multiplikation der beiden zuvor gewählten Zahlen zu bestimmen:

$$
\begin{align}
n &= p \cdot q \\\
  &= 61 \cdot 97 \\\
n &= \underline{5917}
\end{align}
$$

```python {hl_lines=[3,4]}
p = 61
q = 97
print(f"n={p*q}")
# n=5917
```

#### Calculating phi of n and e

Nachdem wir `p` und `q` gewählt und `n` berechnet haben, folgt jetzt die Berechnung von einer Zahl `e` die zu

$$
\begin{align}
\phi(n) &= (p-1) \cdot (q-1) \\\
&= (61-1) \cdot (97-1) \\\
&= (60) \cdot (96) \\\
\phi(n) &= \underline{5760} \\\
\end{align}
$$

```python {hl_lines=[7, 9, 10]}
p = 61
q = 97

print(f"n={p*q}")
# n=5917

phi = (p-1)*(q-1)

print(f"phi={phi}")
# phi=5760
```

relativ prim ist, d.h. es gilt:

$$
\begin{align}
\gcd(e, \phi(n)) &= 1 \\\
\gcd(e, 5760) &= 1 \\\
\gcd(\underline{47}, 5760) &= 1
\end{align}
$$

Our goal is to choose a small but not too small odd number for `e`, therefore i use the 47 for `e`.

```python {hl_lines=[1, "14-20", 22, 23]}
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
```

#### Calculating the private key

Formula for calculating the private key:

$$
\begin{align}
e \cdot d \mod \phi(n) &= 1 \\\
47 \cdot d \mod 5760 &= 1 \\\
47 \cdot \underline{1103} \mod 5760 &= 1
\end{align}
$$

```python {hl_lines=["25-29", "31-32"]}
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
```

Resulting keys:

$$
\begin{align}
\textrm{Public key: } (e,n) \rightarrow (47, 5917) \\\
\textrm{Private key: } (d,n) \rightarrow (1103, 5917) \\\
\end{align}
$$

### Encrypting

To encrypt a string, we first need to convert the characters in the string to their numeric representation:

Example string: `hello:)`

| Characters | h   | e   | l   | l   | o   | :   | )   |
| ---------- | --- | --- | --- | --- | --- | --- | --- |
| Numeric    | 104 | 101 | 108 | 108 | 111 | 58  | 41  |

```python {hl_lines=["34-39"]}
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
```

We can now encrypt each characters numeric value by applying the following formula:

$$
\begin{align}
e(m) = m^e \mod n
\end{align}
$$

where `m` is the character to encrypt and `e` and `n` are pieces of the public key:

$$
\textrm{Public key: } (e,n) \rightarrow (47, 5917) \\\
$$

$$
\begin{align}
e(104)&=104^{47} \mod 5917=3381 \\\
e(101)&=101^{47} \mod 5917=5214 \\\
e(108)&=108^{47} \mod 5917=2575 \\\
e(108)&=108^{47} \mod 5917=2575 \\\
e(111)&=111^{47} \mod 5917=3000 \\\
e(58)&=58^{47} \mod 5917=3303 \\\
e(41)&=41^{47} \mod 5917=3809 \\\
\end{align}
$$

```python {hl_lines=["41-43", 45, 46]}
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
```

| Characters | h    | e    | l    | l    | o    | :    | )    |
| ---------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- |
| Numeric    | 104  | 101  | 108  | 108  | 111  | 58   | 41   |
| Chiffre    | 3381 | 5214 | 2575 | 2575 | 3000 | 3303 | 3809 |

### Decrypting

Decrypting a chiffre encrypted with RSA is simply applying the private key to the given integer and afterwards converting the result to its character representation.

Formula for decrypting:

$$
\begin{align}
d(c) = c^d \mod n
\end{align}
$$

where c is the character to decrypt and d and n are pieces of the private key:

$$
\textrm{Private key: } (d,n) \rightarrow (1103, 5917) \\\
$$

## Cracking RSA

### Factorizing

### Decrypting
