import re
import subprocess
import sys

import anthropic

MODEL = "claude-sonnet-5-5"
MAX_TRIES = 3
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY


def generate_rtl(description, error=None):
    """Ask Claude for a Verilog module. If there was an error, ask it to fix it."""
    prompt = (
        f"Write a synthesizable Verilog-2005 module for: {description}. "
        "Name the module top. Return only the code in one ```verilog block."
    )
    if error:
        prompt += f"\n\nYour last version failed to compile with this error:\n{error}\nFix it."

    reply = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = reply.content[0].text
    match = re.search(r"```(?:verilog)?\n(.*?)```", text, re.S)
    return match.group(1) if match else text


def compiles(path):
    """Check the Verilog with Icarus. Returns (ok, error message)."""
    result = subprocess.run(["iverilog", path], capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def synthesize(path):
    """Run Yosys synthesis and return the statistics report."""
    result = subprocess.run(
        ["yosys", "-p", f"read_verilog {path}; synth -top top; stat"],
        capture_output=True,
        text=True,
    )
    start = result.stdout.rfind("Printing statistics")
    return result.stdout[start:] if start != -1 else result.stderr


def main():
    description = " ".join(sys.argv[1:]) or "4-bit counter with reset"
    path = "design.v"
    error = None

    for attempt in range(1, MAX_TRIES + 1):
        print(f"Attempt {attempt}: asking Claude for RTL...")
        with open(path, "w") as f:
            f.write(generate_rtl(description, error))

        ok, error = compiles(path)
        if ok:
            print("Compiled. Running synthesis...\n")
            print(synthesize(path))
            return
        print(f"Compile failed:\n{error}")

    print("Gave up after 3 tries.")


if __name__ == "__main__":
    main()
