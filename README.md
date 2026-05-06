# override

> Advanced binary exploitation — ten levels of heap-focused pwn challenges and modern mitigation bypasses.

## Overview

The successor to [rainfall](https://github.com/sungyongcho/rainfall): ten levels that move beyond stack-based exploits into heap exploitation and bypassing modern mitigations. Each binary is more constrained than the last — fewer obvious primitives, fewer leaks, more chaining required.

This repo contains my work on the ten levels (`level00`–`level09`), with the original challenge source, supplementary materials, and per-level exploit notes preserved.

This project was built as part of the 42 school cybersecurity track with a partner ([Teo Fleming](https://github.com/mokolodi1)) · Score: 125/100.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Architecture | x86_64 (64-bit ELF) |
| OS | Linux |
| Tools | GDB + PEDA, Ghidra, pwntools-style scripting |
| Bug classes | Heap exploitation, ASLR / NX / canary bypass, multi-step chains |

## Key Features

- Heap exploitation — use-after-free, double-free, fastbin attacks
- Mitigation bypasses — ASLR, NX, stack canaries, partial-RELRO interactions
- Multi-step exploit chains where a single primitive isn't enough
- Manual reverse-engineering with Ghidra to recover decompiled C from stripped binaries

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

- **Heap internals**: understanding how glibc's malloc allocator manages chunks, bins, and freelists — and how to corrupt them into useful primitives.
- **Defense-in-depth bypasses**: combining infoleaks, ROP gadgets, and timing tricks to defeat ASLR, NX, and stack canaries on the same binary.
- **End-to-end exploit development**: from "what's broken about this binary?" to a reproducible exploit script — including reverse-engineering, primitive identification, and chain construction.

## Note

Solutions are published here as a record of completed coursework, post-graduation. They are not intended as walkthroughs for current students of the program.

## License

This project was built as part of the 42 school curriculum.

---

*Part of [sungyongcho](https://github.com/sungyongcho)'s project portfolio.*
