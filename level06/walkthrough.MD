# Level 06

Once logged in, you will see a binary.

```
$ ssh level06@localhost -p 4444
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on 10.0.2.15:4242
level06@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   /home/users/level06/level06
level06@OverRide:~$ ls -l
total 8
-rwsr-s---+ 1 level07 users   7907 Sep 10  2016 level06
```

Can we figure out what it does?

```
level06@OverRide:~$ ./level06
***********************************
*		level06		  *
***********************************
-> Enter Login: test
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: test
level06@OverRide:~$ ./level06
***********************************
*		level06		  *
***********************************
-> Enter Login: test2
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: 7482
```

After decompiling with Hopper and figuring out what the program does, it seems as if it takes a username and password and computes whether the password matches a hash based on the username.

We could rewrite the hash algorithm (not overly complicated) to calculate the "password" for any given username, but instead we'll just use GDB to do the work for us. We'll put a breakpoint right as the program is doing the comparison between the user input and the calculated hash.

```
gdb-peda$ r
***********************************
*		level06		  *
***********************************
-> Enter Login: tfleming
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: 222
.---------------------------.
| !! TAMPERING DETECTED !!  |
'---------------------------'
[Inferior 1 (process 1856) exited with code 01]
Warning: not running
```

How exciting! It looks as if the program checks whether we're using `ptrace` to view the program with GDB. In order to get around the `ptrace` trap, we'll tell GDB to simply return 0 to any calls to `ptrace`.

```
gdb-peda$ catch syscall ptrace
Catchpoint 1 (syscall 'ptrace' [26])
gdb-peda$ commands 1
>set $eax=0
>continue
>end
gdb-peda$ b *auth+286                 # return (serial_number != hash)
Breakpoint 2 at 0x8048866
gdb-peda$ r
***********************************
*		level06		  *
***********************************
-> Enter Login: tfleming
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: 123456

Catchpoint 1 (returned from syscall ptrace), 0xf7fdb440 in __kernel_vsyscall ()

Breakpoint 2, 0x08048866 in auth ()

[----------------------------------registers-----------------------------------]
EAX: 0x1e240
EBX: 0xf7fceff4 --> 0x1a2d7c
ECX: 0x5f1fc4
EDX: 0x3be
ESI: 0x0
EDI: 0x0
EBP: 0xffffd6b8 --> 0xffffd718 --> 0x0
ESP: 0xffffd690 --> 0x0
EIP: 0x8048866 (<auth+286>:	cmp    eax,DWORD PTR [ebp-0x10])
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x804885e <auth+278>:	cmp    eax,DWORD PTR [ebp-0xc]
   0x8048861 <auth+281>:	jl     0x804880f <auth+199>
   0x8048863 <auth+283>:	mov    eax,DWORD PTR [ebp+0xc]
=> 0x8048866 <auth+286>:	cmp    eax,DWORD PTR [ebp-0x10]
   0x8048869 <auth+289>:	je     0x8048872 <auth+298>
   0x804886b <auth+291>:	mov    eax,0x1
   0x8048870 <auth+296>:	jmp    0x8048877 <auth+303>
   0x8048872 <auth+298>:	mov    eax,0x0
[------------------------------------stack-------------------------------------]
0000| 0xffffd690 --> 0x0
0004| 0xffffd694 --> 0x0
0008| 0xffffd698 --> 0x1
0012| 0xffffd69c --> 0x0
0016| 0xffffd6a0 --> 0xffffd718 --> 0x0
0020| 0xffffd6a4 --> 0x8
0024| 0xffffd6a8 --> 0x5f2361 ('a#_')
0028| 0xffffd6ac --> 0x8
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 2, 0x08048866 in auth ()
gdb-peda$ x/x $ebp-0x10
0xffffd6a8:	0x005f2361
```

`0x005f2361` is our serial value for `"tfleming"` (the auth we entered), which is `6234977` in decimal. Let's give that a go as our password with the same username.

```
level06@OverRide:~$ ./level06
***********************************
*		level06		  *
***********************************
-> Enter Login: tfleming
***********************************
***** NEW ACCOUNT DETECTED ********
***********************************
-> Enter Serial: 6234977
Authenticated!
$ whoami
level07
$ cat /home/users/level07/.pass
GbcPDRgsFK77LNnnuh7QyFYA2942Gp8yKj9KrWD8
```
