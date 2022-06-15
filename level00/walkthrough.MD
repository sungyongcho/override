# General introduction

Welcome to our Override walkthrough! xxx finish editing

## The team

While I am correcting this project on my own at 42 Paris, I did this project's exercises with [Sungyong (@sucho)](https://profile.intra.42.fr/users/sucho), and this GitHub repo has been a collaboration between both of us.

## Setup

### The .iso

We set up a VirtualBox with the `.iso` and created a port forwarding rule to forward port `4444` to `4242` to make it easier to work with the virtual machine.

### PEDA

In this project, we used PEDA to help understand and exploit binary files. PEDA stands for Python Exploit Development Assistance for GDB, and more information can be found [here](https://github.com/longld/peda).

Setup instructions:
```
git clone https://github.com/longld/peda.git

# password: level0
scp -P 4444 -r peda/ level0@localhost:/tmp/

# NOTE: this will come in handy in future levels!
chmod +rwx /tmp/peda/; chmod +rwx ~; echo "source /tmp/peda/peda.py" > ~/.gdbinit
```

## General process

In solving Rainfall's puzzles (including level 0), we generally relied on the following process to make progress:

1. Try running the binary with various arguments and note the results
2. Use GDB to disassemble the functions we found with `info functions` in GDB.
3. Manually reverse-engineer the assembly into something similar in C (and in some cases resorting to [Hopper](https://www.hopperapp.com/))
4. Research any vulnerable functions found in the disassembly/reverse-engineering (`printf`, `strcpy`, etc.)
5. Use GDB and PEDA while the program is running to trace functionality view stack/memory addresses.
6. Exploit any vulnerabilities found
7. Document our findings and successes (not so much our failures, of which there were many)

## Caveats

Any reverse-engineered C code in this project is not necessarily complete and has not been tested. It serves only to better understand the respective binary's functionality.

It's also possible that the exact commands in this walkthrough will not work if the setup of the computer is slightly different. That said, following this walkthrough and re-calculating the addresses/commands will work.


# Level 00

## Exploit

Once logged in, you will see a binary.

```
$ ssh localhost -p 4444 -l level00
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level00@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   /home/users/level00/level00
level00@OverRide:~$ ls
level00
level00@OverRide:~$
```

By running the program, it seems is necessary to send a right password to solve the problem.
```
level00@OverRide:~$ ./level00
***********************************
* 	     -Level00 -		  *
***********************************
Password:aaaaaaaaaaaaaaaaaaaaa

Invalid Password!
level00@OverRide:~$
```

Once disassemble main function, you will get following.
On line <main+83>, there is a comparison of `0x149c` with `eax` that compares value with the return value of  `<__isoc99_scanf@plt>` (`scanf()`).

```
Dump of assembler code for function main:
   0x08048494 <+0>:	push   ebp
   0x08048495 <+1>:	mov    ebp,esp
   0x08048497 <+3>:	and    esp,0xfffffff0
   0x0804849a <+6>:	sub    esp,0x20
   0x0804849d <+9>:	mov    DWORD PTR [esp],0x80485f0
   0x080484a4 <+16>:	call   0x8048390 <puts@plt>
   0x080484a9 <+21>:	mov    DWORD PTR [esp],0x8048614
   0x080484b0 <+28>:	call   0x8048390 <puts@plt>
   0x080484b5 <+33>:	mov    DWORD PTR [esp],0x80485f0
   0x080484bc <+40>:	call   0x8048390 <puts@plt>
   0x080484c1 <+45>:	mov    eax,0x804862c
   0x080484c6 <+50>:	mov    DWORD PTR [esp],eax
   0x080484c9 <+53>:	call   0x8048380 <printf@plt>
   0x080484ce <+58>:	mov    eax,0x8048636
   0x080484d3 <+63>:	lea    edx,[esp+0x1c]
   0x080484d7 <+67>:	mov    DWORD PTR [esp+0x4],edx
   0x080484db <+71>:	mov    DWORD PTR [esp],eax
   0x080484de <+74>:	call   0x80483d0 <__isoc99_scanf@plt>
   0x080484e3 <+79>:	mov    eax,DWORD PTR [esp+0x1c]
   0x080484e7 <+83>:	cmp    eax,0x149c
   0x080484ec <+88>:	jne    0x804850d <main+121>
   0x080484ee <+90>:	mov    DWORD PTR [esp],0x8048639
   0x080484f5 <+97>:	call   0x8048390 <puts@plt>
   0x080484fa <+102>:	mov    DWORD PTR [esp],0x8048649
   0x08048501 <+109>:	call   0x80483a0 <system@plt>
   0x08048506 <+114>:	mov    eax,0x0
   0x0804850b <+119>:	jmp    0x804851e <main+138>
   0x0804850d <+121>:	mov    DWORD PTR [esp],0x8048651
   0x08048514 <+128>:	call   0x8048390 <puts@plt>
   0x08048519 <+133>:	mov    eax,0x1
   0x0804851e <+138>:	leave
   0x0804851f <+139>:	ret
End of assembler dump.
(gdb)
```

What is `0x149c`?

```
level00@OverRide:~$ python -c 'print 0x149c'
5276
```

Let's try and see whether that's the password.

```
level00@OverRide:~$ ./level00
***********************************
* 	     -Level00 -		  *
***********************************
Password:5276

Authenticated!
$ id
uid=1000(level00) gid=1000(level00) euid=1001(level01) egid=100(users) groups=1001(level01),100(users),1000(level00)
$ cat /home/users/level01/.pass
uSq2ehEGT6c9S24zbshexZQBXUGrncxn5sD5QfGL
```

Voila!
