from colorama import init, Fore, Style
import os
import subprocess
import threading
import socketserver
import http.server
import re
import shutil

init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

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
BRIGHT_BLUE = Fore.BLUE + Style.BRIGHT
BRIGHT_GREEN = Fore.GREEN + Style.BRIGHT
BRIGHT_RED = Fore.RED + Style.BRIGHT
RESET = Style.RESET_ALL

print(BRIGHT_BLUE + ascii_art)
print(BRIGHT_RED + "[~~~]        Social Engineering toolkit           [~~~]")
print(BRIGHT_RED + "[___]    Creators: Saksham, Rajeshwar, Nishant    [___]\n")

class SingleFileHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP handler that responds with the specified file for ANY GET request.
    """
    def __init__(self, *args, target_file=None, **kwargs):
        self.target_file = target_file
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.path = '/' + os.path.basename(self.target_file)
        return super().do_GET()

    def list_directory(self, path):
        # Disable directory listing entirely
        self.send_error(403, "Directory listing not allowed")
        return None

class SocialEngineeringToolkitMenu:
    def __init__(self):
        self.menu_options = {
            '1': self.stored_xss_script,
            '2': self.phishing_template,
            '3': self.use_template_and_expose_singlefile,
        }
        self.template_filename = None

    def display_menu(self):
        print(f"{BRIGHT_GREEN}Select from the menu:{RESET}")
        print(f"{BRIGHT_GREEN}1. Stored XSS script{RESET}")
        print(f"{BRIGHT_GREEN}2. Phishing template{RESET}")
        print(f"{BRIGHT_GREEN}3. Use single-file template & expose public URL{RESET}")
        print(f"{BRIGHT_GREEN}0. Exit{RESET}")

    def run(self):
        while True:
            clear_console()
            print(BRIGHT_BLUE + ascii_art)
            print(BRIGHT_RED + "[~~~]        Social Engineering toolkit           [~~~]")
            print(BRIGHT_RED + "[___]    Creators: Saksham, Rajeshwar, Nishant    [___]\n")
            self.display_menu()
            choice = input(f"{BRIGHT_GREEN}Enter your choice (or 0 to quit): {RESET}").strip()
            if choice == '0':
                print(f"{BRIGHT_GREEN}Exiting...{RESET}")
                break
            func = self.menu_options.get(choice, self.invalid_choice)
            func()
            input(f"\n{BRIGHT_GREEN}Press Enter to continue...{RESET}")

    def stored_xss_script(self):
        print(f"{BRIGHT_GREEN}Stored XSS script selected... (To be implemented){RESET}")

    def phishing_template(self):
        print(f"{BRIGHT_GREEN}Phishing template selected... (To be implemented){RESET}")

    def invalid_choice(self):
        print(f"{Fore.RED}Invalid choice. Please select a valid option.{RESET}")

    def use_existing_template(self):
        filename = input(f"{BRIGHT_GREEN}Enter HTML template filename (must be in current directory): {RESET}").strip()
        if not filename.lower().endswith(".html"):
            print(f"{Fore.RED}Please specify an HTML file with '.html' extension.{RESET}")
            return None
        if not os.path.isfile(filename):
            print(f"{Fore.RED}File '{filename}' does not exist in the current directory.{RESET}")
            return None
        print(f"{BRIGHT_GREEN}Template '{filename}' will be served exclusively.{RESET}")
        self.template_filename = filename
        return filename

    def start_python_server_singlefile(self, port=8080):
        """
        Serve ONLY the specified file, regardless of requested path.
        """
        handler_class = lambda *args, **kwargs: SingleFileHandler(*args, target_file=self.template_filename, directory=os.getcwd(), **kwargs)
        httpd = socketserver.TCPServer(("", port), handler_class)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        print(f"{BRIGHT_GREEN}Python HTTP server started on port {port}, exclusively serving: {self.template_filename}{RESET}")
        return httpd

    def start_cloudflare_tunnel(self, port=8080):
        if not shutil.which("cloudflared"):
            print(f"{Fore.RED}cloudflared is not installed or not in PATH. Please install it first.{RESET}")
            return None, None

        print(f"{BRIGHT_GREEN}Starting Cloudflare Tunnel for localhost:{port} ...{RESET}")
        proc = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        public_url = None
        while True:
            line = proc.stdout.readline()
            if line == '' and proc.poll() is not None:
                break
            if line:
                print(line.rstrip())
                match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                if match:
                    public_url = match.group(0)
                    print(f"\n{BRIGHT_GREEN}Public URL: {public_url}{RESET}\n")
                    break
        return proc, public_url

    def use_template_and_expose_singlefile(self):
        """
        Prompts user for template, starts single-file HTTP server, opens Cloudflare Tunnel.
        """
        filename = self.use_existing_template()
        if not filename:
            return
        try:
            port_str = input(f"{BRIGHT_GREEN}Enter port to serve template [default 8080]: {RESET}").strip()
            port = int(port_str) if port_str else 8080
        except ValueError:
            print(f"{Fore.RED}Invalid port number. Using default 8080.{RESET}")
            port = 8080

        httpd = self.start_python_server_singlefile(port)
        proc, public_url = self.start_cloudflare_tunnel(port)

        if public_url:
            print(f"{BRIGHT_GREEN}Share this URL to access your template publicly.{RESET}")
            print(f"{BRIGHT_GREEN}Only the specified file will be served for ALL requests.{RESET}")
            print(f"{BRIGHT_GREEN}Note: The server and tunnel will remain active as long as this tool runs.{RESET}")
            try:
                while True:
                    pass  # Keep running for server/tunnel
            except KeyboardInterrupt:
                print(f"\n{BRIGHT_RED}Shutting down server and tunnel...{RESET}")
                httpd.shutdown()
                proc.terminate()
        else:
            print(f"{Fore.RED}Failed to start Cloudflare tunnel.{RESET}")
            httpd.shutdown()
            if proc:
                proc.terminate()

if __name__ == "__main__":
    menu = SocialEngineeringToolkitMenu()
    menu.run()

