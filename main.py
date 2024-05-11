import markovify
import random
import matplotlib.pyplot as plt
import numpy as np
import timeit
from stegomarkov import StegoMarkov, StegoMarkovDecoder
from huffmarkov import HuffMarkov, HuffMarkovDecoder

with open("models/pos.json", "r") as f:
	print("Loading markov model...\n")
	model = markovify.Text.from_json(f.read())

# bitstream_len = 10_000
# repeats = 100
# vals = []
# c = 1
#
# for i in range(repeats):
# 	bitstream = ''.join(str(random.randint(0, 1)) for _ in range(bitstream_len))
# 	stego_markov = HuffMarkov(model, bitstream)
# 	stego_markov.logging = False
# 	stego_markov.generate()
#
# 	num_bits = len(''.join(format(ord(char), '08b') for char in stego_markov.output))
# 	rate = bitstream_len / num_bits
# 	vals.append(rate)
#
# 	with open("test_data.txt", "w") as f:
# 		f.write("")
#
# 	with open("test_data.txt", "a") as f:
# 		f.write(f"{bitstream[:58]}...\t{rate*100:0.2f}%\n")
#
# 	print(f"Stego #{c}: {rate * 100:.2f}%")
# 	c += 1
#
# average = np.mean(vals)
# plt.scatter(range(repeats), vals)
# plt.axhline(y=average, color='r', linestyle='--', label=f"Average: {average * 100:.2f}%")
# plt.ylim(.01, .1)
# plt.ylabel("Embedding Rate")
# plt.legend()
# plt.show()

# bitstream_lens = [10, 50, 100, 500, 1000, 5000, 10_000]
# bit_vals = []
# huff_vals = []
# c = 1
# for bitstream_len in bitstream_lens:
# 	bitstream = ''.join(str(random.randint(0, 1)) for _ in range(bitstream_len))
# 	stego_markov = StegoMarkov(model, bitstream, False)
# 	huff_markov = HuffMarkov(model, bitstream, False)
#
# 	stego_markov.generate()
# 	huff_markov.generate()
#
# 	stego_markov_decoder = StegoMarkovDecoder(model, stego_markov.output_str, False)
# 	huff_markov_decoder = HuffMarkovDecoder(model, huff_markov.output_str, False)
#
# 	bit_time = timeit.timeit(lambda: stego_markov_decoder.solve())
# 	huff_time = timeit.timeit(lambda: huff_markov_decoder.solve())
#
# 	bit_vals.append(bit_time)
# 	huff_vals.append(huff_time)
#
# 	with open("test_data.txt", "a") as f:
# 		bitstring = bitstream if bitstream_len <= 40 else f"{bitstream[:40]}..."
# 		f.write(f"{bitstream_len}\t{bitstring}\t{huff_time:.2f}s\t{bit_time:.2f}s\n")
#
# 	print(f"Stego #{c}: Bit - {bit_time:.2f}, Huff - {huff_time:.2f}")
# 	c += 1
#
# groups = list(map(str, bitstream_lens))
# x_axis = np.arange(len(groups))
# plt.bar(x_axis - 0.2, huff_vals, 0.4, label="Existing")
# plt.bar(x_axis + 0.2, bit_vals, 0.4, label="Enhanced")
#
# plt.xticks(x_axis, groups)
# plt.xlabel("Bit Stream Length")
# plt.ylabel("Decoding Time (in seconds)")
# plt.ylim(0, 8)
# plt.legend()
# plt.show()

while True:
	bitstream_len = 50
	# bitstream = ''.join(str(random.randint(0, 1)) for _ in range(bitstream_len))
	bitstream = ''.join(str(random.randint(0, 1)) for _ in range(bitstream_len))
	stego_markov = StegoMarkov(model, bitstream, True)

	print(f"Bit Stream: {bitstream}")
	while not stego_markov.finished:
		stego_markov.step()
		# input()

	stego_markov_decoder = StegoMarkovDecoder(model, stego_markov.output_str, True)

	print(f"\nSteganographic Text: {stego_markov.output_str}")
	while not stego_markov_decoder.finished:
		stego_markov_decoder.step()
		input()

	print(f"Original:\t{bitstream}")
	input()

# while True:
# 	bitstream_len = 10
# 	bitstream = ''.join(str(random.randint(0, 1)) for _ in range(bitstream_len))
# 	print(bitstream)
# 	huff_markov = HuffMarkov(model, bitstream, True)
#
# 	print("Generating steganographic text...\n")
# 	while not huff_markov.finished:
# 		huff_markov.step()
#
# 	huff_markov_decoder = HuffMarkovDecoder(model, huff_markov.output_str, True)
# 	while not huff_markov_decoder.finished:
# 		huff_markov_decoder.step()
# 		input()
#
# 	input()
