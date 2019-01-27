import random
import decimal

print("Enter number of data points to generate:")
numVanes = input()

fout = open("dataset.txt", "wt")
for i in range(int(numVanes)):
	valueA = random.randint(2, 44)/1000
	valueB = random.randint(2, 44)/1000
	fout.write(str(i) + "," + str(valueA) + "," + str(valueB) + "\n")
fout.close()