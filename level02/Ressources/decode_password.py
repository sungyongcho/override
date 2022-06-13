# password memory values
password_memory = [
    "0x756e505234376848",
    "0x45414a3561733951",
    "0x377a7143574e6758",
    "0x354a35686e475873",
    "0x48336750664b394d",
]

# convert to decimal
ascii_memory = [bytearray.fromhex(memory[2:]).decode() for memory in password_memory]

# reverse those strings
reversed_ascii = [memory[::-1] for memory in ascii_memory]

# combine into a string
print("".join(reversed_ascii))
