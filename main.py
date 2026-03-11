import ollama
import subprocess
import json

MODEL = "qwen2.5-coder:7b"

def run_shell(command: str) -> str:
    dangerous = ["format", "shutdown", "rd /s", "rmdir /s", "del /f", "remove-item -recurse"]
    if any(d in command.lower() for d in dangerous):
        confirm = input(f"\n  ⚠️  astrOS wants to run: {command}\n  are you sure? (yes/no): ").strip().lower()
        if confirm != "yes":
            return "user cancelled the operation."
    try:
        result = subprocess.run(f'powershell -Command "{command}"', shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout + result.stderr
        return output.strip() if output.strip() else "(no output)"
    except subprocess.TimeoutExpired:
        return "command timed out."
    except Exception as e:
        return f"error: {e}"

def get_top_processes(sort_by: str = "cpu", count: int = 5) -> str:
    if sort_by.lower() == "cpu":
        cmd = f'powershell -Command "Get-Process | Sort-Object CPU -Descending | Select-Object -First {count} Name, @{{Name=\'CPU(s)\';Expression={{[math]::Round($_.CPU,1)}}}}, Id | Format-Table -AutoSize"'
    else:
        cmd = f'powershell -Command "Get-Process | Sort-Object WS -Descending | Select-Object -First {count} Name, @{{Name=\'RAM(GB)\';Expression={{[math]::Round($_.WS/1GB,2)}}}}, Id | Format-Table -AutoSize"'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        return f"error: {e}"

def get_disk_usage() -> str:
    try:
        result = subprocess.run(
            'powershell -Command "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name=\'Used(GB)\';Expression={[math]::Round($_.Used/1GB,2)}}, @{Name=\'Free(GB)\';Expression={[math]::Round($_.Free/1GB,2)}}, @{Name=\'Total(GB)\';Expression={[math]::Round(($_.Used+$_.Free)/1GB,2)}} | Format-Table -AutoSize"',
            shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        return f"error: {e}"

def get_ram_usage() -> str:
    try:
        result = subprocess.run(
            'powershell -Command "$os = Get-CimInstance Win32_OperatingSystem; [PSCustomObject]@{\'Total(GB)\'=[math]::Round($os.TotalVisibleMemorySize/1MB,2);\'Free(GB)\'=[math]::Round($os.FreePhysicalMemory/1MB,2);\'Used(GB)\'=[math]::Round(($os.TotalVisibleMemorySize-$os.FreePhysicalMemory)/1MB,2)} | Format-Table -AutoSize"',
            shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        return f"error: {e}"

def get_network_info() -> str:
    try:
        result = subprocess.run(
            'powershell -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne \'127.0.0.1\'} | Select-Object InterfaceAlias, IPAddress, PrefixLength | Format-Table -AutoSize"',
            shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        return f"error: {e}"

def list_directory(path: str = ".") -> str:
    try:
        result = subprocess.run(
            f'powershell -Command "Get-ChildItem \'{path}\' | Select-Object Mode, LastWriteTime, @{{Name=\'Size(KB)\';Expression={{[math]::Round($_.Length/1KB,1)}}}}, Name | Format-Table -AutoSize"',
            shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except Exception as e:
        return f"error: {e}"

def create_folder(path: str) -> str:
    try:
        result = subprocess.run(f'powershell -Command "New-Item -ItemType Directory -Path \'{path}\' -Force"', shell=True, capture_output=True, text=True, timeout=15)
        return f"folder created: {path}" if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"error: {e}"

def create_file(path: str, content: str = "") -> str:
    try:
        result = subprocess.run(f'powershell -Command "Set-Content -Path \'{path}\' -Value \'{content}\'"', shell=True, capture_output=True, text=True, timeout=15)
        return f"file created: {path}" if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"error: {e}"

def delete_item(path: str) -> str:
    confirm = input(f"\n  ⚠️  astrOS wants to delete: {path}\n  are you sure? (yes/no): ").strip().lower()
    if confirm != "yes":
        return "user cancelled deletion."
    try:
        result = subprocess.run(f'powershell -Command "Remove-Item \'{path}\' -Recurse -Force"', shell=True, capture_output=True, text=True, timeout=15)
        return f"deleted: {path}" if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"error: {e}"

def kill_process(name: str) -> str:
    confirm = input(f"\n  ⚠️  astrOS wants to kill process: {name}\n  are you sure? (yes/no): ").strip().lower()
    if confirm != "yes":
        return "user cancelled."
    try:
        result = subprocess.run(f'powershell -Command "Stop-Process -Name \'{name}\' -Force"', shell=True, capture_output=True, text=True, timeout=15)
        return f"killed process: {name}" if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"error: {e}"

TOOLS = [
    {"type": "function", "function": {"name": "run_shell", "description": "Run any PowerShell command on the Windows system", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "get_top_processes", "description": "Get top processes by CPU or RAM usage", "parameters": {"type": "object", "properties": {"sort_by": {"type": "string", "enum": ["cpu", "ram"]}, "count": {"type": "integer"}}, "required": ["sort_by"]}}},
    {"type": "function", "function": {"name": "get_disk_usage", "description": "Get disk space for all drives", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_ram_usage", "description": "Get current RAM usage in GB", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "get_network_info", "description": "Get network and IP info", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "list_directory", "description": "List files in a directory", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {"name": "create_folder", "description": "Create a new folder", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "create_file", "description": "Create a new file with optional content", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "delete_item", "description": "Delete a file or folder", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "kill_process", "description": "Kill a running process by name", "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
]

TOOL_MAP = {
    "run_shell": run_shell,
    "get_top_processes": get_top_processes,
    "get_disk_usage": get_disk_usage,
    "get_ram_usage": get_ram_usage,
    "get_network_info": get_network_info,
    "list_directory": list_directory,
    "create_folder": create_folder,
    "create_file": create_file,
    "delete_item": delete_item,
    "kill_process": kill_process,
}

def call_tool(name, args):
    fn = TOOL_MAP.get(name)
    if fn:
        return fn(**args)
    return f"unknown tool: {name}"

def extract_tool_call(content):
    """Try to parse a tool call from plain text content."""
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "name" in parsed and "arguments" in parsed:
            return parsed["name"], parsed["arguments"]
    except Exception:
        pass
    return None, None

import os
HOME = os.path.expanduser("~")
SYSTEM_PROMPT =  f"""You are astrOS, an AI-native operating system assistant running on Windows 11.
You have tools to interact with the real filesystem, processes, and system.
Always use the most specific tool available rather than run_shell when possible.
Be concise. Don't over-explain. The current user's home directory is {HOME}. Always use this exact path for user directories like Downloads, Desktop, Documents etc. """

def handle_user_input(user_input, history):
    """Process one user input — call AI, execute tools, return final response."""
    history.append({"role": "user", "content": user_input})

    response = ollama.chat(model=MODEL, messages=history, tools=TOOLS)
    message = response["message"]
    history.append(message)

    tool_calls = message.get("tool_calls")
    content = message.get("content", "").strip()

    # Case 1: proper structured tool calls
    if tool_calls:
        for tool_call in tool_calls:
            if isinstance(tool_call, dict):
                name = tool_call["function"]["name"]
                args = tool_call["function"]["arguments"]
            else:
                name = tool_call.function.name
                args = tool_call.function.arguments
            if isinstance(args, str):
                args = json.loads(args)
            print(f"  → {name}({', '.join(f'{k}={v}' for k,v in args.items())})")
            result = call_tool(name, args)
            print(f"\n{result}\n")
        return

    # Case 2: qwen returned tool call as plain text JSON — execute it once, don't loop
    name, args = extract_tool_call(content)
    if name:
        if isinstance(args, str):
            args = json.loads(args)
        print(f"  → {name}({', '.join(f'{k}={v}' for k,v in args.items())})")
        result = call_tool(name, args)
        print(f"\n{result}\n")
        return

    # Case 3: plain text response
    if content:
        print(f"  astrOS: {content}\n")

def main():
    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    print("\n  astrOS v0.3")
    print("  " + "─" * 36)
    print("  type 'exit' to quit\n")

    while True:
        try:
            user_input = input("  > ").strip()
        except KeyboardInterrupt:
            print("\n\n  shutting down astrOS...")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("\n  shutting down astrOS...")
            break

        print()
        handle_user_input(user_input, history)

if __name__ == "__main__":
    main()