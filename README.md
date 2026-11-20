# llm-rtl

A Python tool that uses Claude to generate Verilog RTL from a plain-English description, checks that it compiles, and synthesizes it into logic gates.

## How it works

1. **Generate:** Claude writes a synthesizable Verilog module from your description.
2. **Check:** Icarus Verilog (`iverilog`) compiles it.
3. **Fix:** If it fails, the compiler error is sent back to Claude to fix (up to 3 tries).
4. **Synthesize:** Yosys turns the RTL into a gate-level netlist and reports the cell count.

## Sample results

| Description | Compiled on | Cells | Notes |
|---|---|---|---|
| 4-bit counter with reset | Attempt 1 | 10 | 4 flip-flops + increment logic |
| 2-to-1 multiplexer | Attempt 1 | 1 | Maps to a single MUX cell |
| 8-bit adder | Attempt 1 | 41 | Pure logic, no flip-flops |

## Setup (macOS)

```bash
brew install icarus-verilog yosys
pip3 install anthropic
export ANTHROPIC_API_KEY="your-key"
```

## Run

```bash
python3 llm_rtl.py "4-bit counter with reset"
```

## Next steps

- Add a testbench to check the logic is correct, not just that it compiles
- Run place and route to produce a layout file
- Generate many designs automatically and compare their statistics

## Author

Payal Mistry — Computer Science, Portland State University
