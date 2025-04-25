import os
from easy import run_easylang

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("Welcome to EasyLang!")
    print("Type your code below. Press Ctrl+D (Unix) or Ctrl+Z (Windows) followed by Enter to run.")
    print("Or type 'exit' to quit.")
    print("\nExample code:")
    print("x = 5;")
    print("y = x + 3 * 2;")
    print("print(y);")
    print("\n" + "="*50 + "\n")

    while True:
        print("\nEnter your EasyLang code:")
        lines = []
        try:
            while True:
                line = input()
                if line.lower() == 'exit':
                    return
                lines.append(line)
        except EOFError:
            pass

        if not lines:
            continue

        code = '\n'.join(lines)
        clear_screen()
        print("Running your code...\n")
        print("Output:")
        print("-" * 50)
        run_easylang(code)
        print("-" * 50)
        print("\nPress Enter to continue...")
        input()
        clear_screen()

if __name__ == "__main__":
    main() 