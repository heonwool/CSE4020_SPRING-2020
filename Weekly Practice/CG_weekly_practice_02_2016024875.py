import numpy as np

# A: Create a 1d array M with values ranging from 2 to 26 and print M.
temp = []
for i in range(2, 27):
    temp.append(i)

M = np.array(temp)
print(M)

# B: Reshape M as 5x5 matrix and print M.
M = M.reshape(5, 5)
print(M)

# C: Set the first column of the matrix M to 0 and print M.
M[:, 0] = 0
print(M)

# D: Assign M^2 to the M and print M.
M = M @ M
print(M)

# E: Calculate the magnitude of the vector v(first row of the matrix M) and print it.
v = M[0, :]
result = 0

for i in v:
    result += i*i

print(np.sqrt(result))
