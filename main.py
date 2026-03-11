import ollama
import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Error: {e}"

def is_destructive(command):
    dangerous = ["rm", "del", "format", "rmdir", "rd", "shutdown", "taskkill"]
    return any(word in command.lower() for word in dangerous)

history = [
    {
        "role": "system",
        "content": """You are astrOS, an AI operating system assistant running on Windows 11.
When the user asks you to do something on their computer, respond with:
THOUGHT: your reasoning
COMMAND: the windows command to run

Important rules:
- Never use wmic, it is deprecated and removed in Windows 11
- Use powershell commands for system info, like: powershell "Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory, TotalVisibleMemorySize"
- For disk info use: powershell "Get-PSDrive C"
- For processes use: tasklist
- Always use commands that work on modern Windows 11
- For top processes by memory use: powershell "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 5 Name, @{Name='RAM(MB)';Expression={[math]::Round($_.WorkingSet64/1MB,1)}}"
If it's just a question, reply normally with no COMMAND.
Always be concise."""
    }
]

print("astrOS v0.1 — type 'exit' to quit")
print("=" * 40)

while True:
    user_input = input("\n> ")

    if user_input.lower() == "exit":
        print("Shutting down astrOS...")
        break

    if not user_input.strip():
        continue

    history.append({"role": "user", "content": user_input})

    print("\nthinking...")

    response = ollama.chat(model="qwen2.5-coder:7b", messages=history)
    reply = response["message"]["content"]

    history.append({"role": "assistant", "content": reply})

    if "COMMAND:" in reply:
        lines = reply.splitlines()
        for line in lines:
            if line.startswith("COMMAND:"):
                command = line.replace("COMMAND:", "").strip().strip("`")

                if is_destructive(command):
                    confirm = input(f"\n⚠️  astrOS wants to run: {command}\nAre you sure? (yes/no): ")
                    if confirm.lower() != "yes":
                        print("Cancelled.")
                        continue

                print(f"\nrunning: {command}")
                output = run_command(command)
                print(f"\n{output}")
    else:
        print(f"\nastrOS: {reply}")