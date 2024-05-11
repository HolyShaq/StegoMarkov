from __future__ import annotations
import random
import huffman
import re
import markovify


class HuffMarkov:
	def __init__(self, model: markovify.Text, bitstream: str, logging: bool):
		self.model = model
		self.bitstream = bitstream

		self.entrypoints = [key for key in model.chain.model.keys() if "___BEGIN__" in key][1:]

		self.current_gram = None
		self.output = []
		self.exhausted = True
		self.finished = False

		self.logging = logging
		self.c = 1

	@property
	def output_str(self):
		return " ".join(self.output)

	def step(self):
		"""
		Generates a new word for the output
		"""
		if self.finished:
			return

		char_limit = 20
		matrix_limit = 10

		# Choose new starting point
		if self.exhausted:
			self.exhausted = False
			self.current_gram = random.choice(self.entrypoints)

			if self.logging:
				print(f"Random Entrypoint Chosen: {self.current_gram[1]}")

			# Add token to output
			self.output.append(self.current_gram[1])

		# Get next word
		else:
			# Construct Huffman tree for the transition matrix of the current gram
			trans_matrix = self.get_transition_matrix(self.current_gram)
			if len(trans_matrix) > 1:
				self.c += 1
				huffman_code = huffman.codebook([(k, v) for k, v in trans_matrix.items()])
				huffman_code = {v: k for k, v in huffman_code.items()}  # Reverse lookup table to make indexing easier
				tree_depth = max(map(lambda n: len(n), huffman_code.keys()))

				# Traverse Huffman tree using bitstream
				count = 0
				for i in range(tree_depth, 0, -1):
					if i >= len(self.bitstream):
						continue
					bits = self.bitstream[:i]
					if bits in huffman_code.keys():
						next_token = huffman_code[bits]
						count = i
						break
				else:
					next_token = f"<{self.bitstream}>"
					count = len(self.bitstream)

				removed = self.bitstream[:count]
				self.bitstream = self.bitstream[count:]

				if self.logging:
					if len(self.bitstream) > char_limit:
						remaining = f"{self.bitstream[:char_limit]}..."
					else:
						remaining = self.bitstream

					if self.logging:
						transitions = trans_matrix.keys()
						print(f"{self.current_gram}:")
						print(f"\tPossible Transitions: {self.pretty_print_list(transitions, matrix_limit)}")
						print(f"\tMatrix Length: {len(transitions)}\tTree Depth: {tree_depth}")
						print(f"\tBit Stream: [{removed}]-{remaining}")
						print(f"\tEncoded Key: {removed}\tToken: {next_token}")
						if next_token == "___END__":
							print("\t-- Exhausting --")

			else:
				next_token = list(trans_matrix.keys())[0]

				if self.logging:
					if len(self.bitstream) > char_limit:
						remaining = f"{self.bitstream[:char_limit]}..."
					else:
						remaining = self.bitstream

					if self.logging:
						transitions = trans_matrix.keys()
						print(f"{self.current_gram}:")
						print(f"\tPossible Transitions: {self.pretty_print_list(transitions, matrix_limit)}")
						print(f"\tMatrix Length: {len(transitions)}\tTree Depth: 0")
						print(f"\tBit Stream: []-{remaining}")
						print(f"\tEncoded Key: None\tToken: {next_token}")
						if next_token == "___END__":
							print("\t-- Exhausting --")

			# Construct gram
			next_gram = list(self.current_gram)
			next_gram.append(next_token)
			self.current_gram = tuple(next_gram[1:])

			# Add token to output
			if next_token != "___END__":
				self.output.append(next_token)
			else:
				self.exhausted = True
				self.current_gram = None

		if not self.bitstream:
			if self.logging:
				print(f"\nOutput: {self.output_str}")

			self.finished = True

		if self.logging:
			print()

	def get_transition_matrix(self, gram):
		trans_matrix = self.model.chain.model[gram]
		return trans_matrix

	def generate(self):
		"""
		Consumes the entire bitstream and generates the output for it
		"""
		while not self.finished:
			self.step()

	@staticmethod
	def pretty_print_list(lst, limit):
		lst = list(map(lambda s: f"'{s}'", lst))
		if not lst:
			return "None"
		elif len(lst) == 1:
			return lst[0]
		elif len(lst) == 2:
			return f"{lst[0]} and {lst[1]}"
		elif len(lst) <= limit:
			return ", ".join(lst[:-1]) + ", and " + lst[-1]
		else:
			truncated_list = lst[:limit]
			remaining_count = len(lst) - limit
			return ", ".join(truncated_list) + f", and {remaining_count} more"


class HuffMarkovDecoder:
	def __init__(self, model: markovify.Text, stega_text: str, logging: bool):
		self.model = model
		self.stega_text = stega_text.split(" ")

		self.entrypoints = [key[1] for key in model.chain.model.keys() if "___BEGIN__" in key][1:]
		self.endkey = 0
		self.current_gram = None
		self.index = 0
		self.exhausted = True
		self.finished = False
		self.logging = logging

		self.output = ""

	def step(self):
		matrix_limit = 10
		char_limit = 20

		# Finish if index is at the end of the stega text
		if self.index >= len(self.stega_text) - 1 and not self.exhausted:
			if self.logging:
				print(f"\nOutput:\t\t{self.output}")
			self.finished = True
			return

		previous = self.output if len(self.output) <= char_limit else f"...{self.output[-char_limit:]}"
		if self.exhausted:
			token = self.stega_text[self.index]

			self.current_gram = ("___BEGIN__", token)
			if self.logging:
				print(f"Entrypoint: {self.current_gram[1]}")
				print(f"\tBitstream: {previous}-[]")
				print()

			self.exhausted = False
		else:
			trans_matrix = self.get_transition_matrix(self.current_gram)
			at_end = self.index == len(self.stega_text) - 1
			next_token = "" if at_end else self.stega_text[self.index + 1]

			if len(trans_matrix) > 1:
				huffman_code = huffman.codebook([(k, v) for k, v in trans_matrix.items()])
				tree_depth = max(map(lambda n: len(n), huffman_code.keys()))

				# If the last token is punctuated and the trans_matrix has an endpoint
				if self.current_gram[1][-1] in ".?!" and "___END__" in trans_matrix.keys():
					if next_token not in trans_matrix:
						next_token = "___END__"
						self.exhausted = True

				# Hard coded catch for huffman latter bit error
				if re.match(r"<[01]+>", next_token):
					bit_string = ""
					# bit_string = next_token[1:-1]  # Correction 💢
					next_token = f"INVALID TOKEN {next_token}"
				else:
					bit_string = "" if at_end else huffman_code[next_token]

			else:
				tree_depth = "0"
				bit_string = ""

				# If the last token is punctuated and the trans_matrix has an endpoint
				if self.current_gram[1][-1] in ".?!" and "___END__" in trans_matrix.keys():
					next_token = "___END__"
					self.exhausted = True

			if self.logging:
				print(f"{self.current_gram}:")
				print(f"\tPossible Transitions: {self.pretty_print_list(trans_matrix, matrix_limit)}")
				print(f"\tMatrix Length: {len(trans_matrix)}\tTree Depth: {tree_depth}")
				print(f"\tToken: {next_token}")
				print(f"\tDecoded Value: {bit_string if bit_string else 'N/A'}")
				print(f"\tBitstream: {previous}-[{bit_string}]")
				print()

			# Construct gram
			next_gram = list(self.current_gram)
			next_gram.append(next_token)
			self.current_gram = tuple(next_gram[1:])

			self.index += 1

			# Add bit string to output
			self.output += bit_string

	def solve(self):
		while not self.finished:
			self.step()

	def get_transition_matrix(self, gram):
		trans_matrix = self.model.chain.model[gram]
		return trans_matrix

	@staticmethod
	def pretty_print_list(lst, limit):
		lst = list(map(lambda s: f"'{s}'", lst))
		if not lst:
			return "None"
		elif len(lst) == 1:
			return lst[0]
		elif len(lst) == 2:
			return f"{lst[0]} and {lst[1]}"
		elif len(lst) <= limit:
			return ", ".join(lst[:-1]) + ", and " + lst[-1]
		else:
			truncated_list = lst[:limit]
			remaining_count = len(lst) - limit
			return ", ".join(truncated_list) + f", and {remaining_count} more"
