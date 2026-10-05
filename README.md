# override

> Binary exploitation track, part two — ten x86-64 pwn challenges with per-level walkthroughs.

## Overview

The successor to [rainfall](https://github.com/sungyongcho/rainfall): ten levels on 64-bit binaries. The bugs are stack overflows with shellcode, return-to-libc, an out-of-bounds index that reaches past the stack canary to the return address, an off-by-one into a saved return address, and password recovery from a binary's own logic. The lab VMs ran with ASLR disabled, so none of this is a mitigation bypass; the work is finding each primitive and turning it into the next user's credentials.

This repo contains my work on the ten levels (`level00`–`level09`), with the original challenge source, supplementary materials, and per-level exploit notes preserved.

This project was built as part of the 42 school cybersecurity track with a partner ([Teo Fleming](https://github.com/mokolodi1)) · Score: 125/100.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Architecture | x86_64 (64-bit ELF) |
| OS | Linux |
| Tools | GDB + PEDA, Ghidra, small Python helper scripts |
| Bug classes | Stack overflow, shellcode, return-to-libc, out-of-bounds write, off-by-one |

## Key Features

- Stack buffer overflows — return-address overwrites, with shellcode placed in the environment or the input
- Return-to-libc — returning into `system` where a shellcode could not be used
- Out-of-bounds writes — an unchecked index that skips the stack canary and lands on the return address; an off-by-one into a saved return address
- Manual reverse-engineering with GDB + PEDA and Ghidra to recover each binary's logic

## Architecture

```
override/
├── level00/
│   ├── Resources/        # supplementary materials
│   ├── source            # original challenge source
│   ├── flag              # captured credentials
│   └── walkthrough.MD    # my exploit notes
└── level01..09/
```

## What This Demonstrates

- **64-bit stack layout**: where the saved return address, the canary and the locals sit, and what one unchecked index or one extra byte can reach.
- **Reading checksec honestly**: each walkthrough records the binary's RELRO, canary, NX and PIE state and works within it; ASLR was off on the lab VMs, and nothing here claims to defeat it.
- **End-to-end exploit development**: from "what's broken about this binary?" to a working input — reverse-engineering, primitive identification and payload construction.

## Note

Solutions are published here as a record of completed coursework, post-graduation. They are not intended as walkthroughs for current students of the program.

## License

This project was built as part of the 42 school curriculum.

---

*Part of [sungyongcho](https://github.com/sungyongcho)'s project portfolio.*
