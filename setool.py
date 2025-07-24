from colorama import init, Fore

init(autoreset=True)

ascii_art = r'''
                                    _H_
                                   /___\
                                   \srn/
~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~^~U~^~^~^~^~^~^~^
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

print(Fore.RED + "[~~~]        Social Engineering toolkit           [~~~]")
print(Fore.RED + "[___]    Creators: Saksham, Rajeshwar, Nishant    [___]\n")


class SocialEngineeringToolkitMenu:
    BRIGHT_GREEN = '\033[92m'
    RESET = '\033[0m'
    
    def __init__(self):
        self.menu_options = {
            '1': self.stored_xss_script,
            '2': self.phishing_template,
            # Add more options here 
        }
    
    def display_menu(self):
        print(f"{self.BRIGHT_GREEN}Select from the menu:{self.RESET}")
        print(f"{self.BRIGHT_GREEN}1. Stored XSS script{self.RESET}")
        print(f"{self.BRIGHT_GREEN}2. Phishing template{self.RESET}")
        print(f"{self.BRIGHT_GREEN}Coming soon{self.RESET}")
    
    def run(self):
        self.display_menu()
        choice = input(f"{self.BRIGHT_GREEN}Enter your choice: {self.RESET}").strip()
        func = self.menu_options.get(choice, self.invalid_choice)
        func()
    
    def stored_xss_script(self):
        # Placeholder for Stored XSS script function
        print(f"{self.BRIGHT_GREEN}Stored XSS script selected... (To be implemented){self.RESET}")
    
    def phishing_template(self):
        # Placeholder for Phishing template function
        print(f"{self.BRIGHT_GREEN}Phishing template selected... (To be implemented){self.RESET}")
    
    def invalid_choice(self):
        print(f"{self.BRIGHT_GREEN}Invalid choice. Please select a valid option.{self.RESET}")


if __name__ == "__main__":
    menu = SocialEngineeringToolkitMenu()
    menu.run()

