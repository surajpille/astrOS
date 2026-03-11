# astrOS
an ai-native operating system. talk to your computer in plain english                                              .

## What is it?
astrOS replaces the traditional OS interface with an ai (or at least it is in development to do so). instead of clicking through menus and remembering commands, you just say what you want.

## Current Features
- natural language shell — type anything, astrOS figures out the command
- runs 100% locally — no internet, no API keys, your data stays on your machine
- safety layer — asks before running anything destructive

## Roadmap
- [ ] file operations
- [ ] persistent memory
- [ ] custom tauri UI (dark/light theme, eventually)
- [ ] linux base — full desktop replacement
- [ ] screen awareness

## Run it yourself
install [Ollama](https://ollama.com) and pull the model:
```
ollama pull qwen2.5-coder:7b
pip install ollama
python main.py
```

## Vision
a lightweight, beautiful, ai-first OS. no bloat. just you and your computer, finally speaking the same language simplistically.
