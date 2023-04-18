import sys 

# Class for writing errors on stderr and exiting program
class ErrorHandler:
    # Colors of stdout/stderr
    RED = "\033[1;31m"
    RESET = "\033[0m"

    def __init__(self, msg, errCode):
        sys.stderr.write(f"{self.RED}ERROR: {msg}.{self.RESET}\n")
        sys.exit(errCode)