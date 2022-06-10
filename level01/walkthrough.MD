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

