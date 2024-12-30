import threading
from colorama import Fore

class PrintHandler:
    COLOUR_MAP = {
        'black': Fore.LIGHTBLACK_EX,
        'red': Fore.LIGHTRED_EX,
        'green': Fore.LIGHTGREEN_EX,
        'yellow': Fore.LIGHTYELLOW_EX,
        'blue': Fore.LIGHTBLUE_EX,
        'magenta': Fore.LIGHTMAGENTA_EX,
        'cyan': Fore.LIGHTCYAN_EX,
        'white': Fore.LIGHTWHITE_EX,
        'reset': Fore.RESET
    }

    print_lock = threading.Lock()

    @staticmethod
    def _colour_message(message, colour):
        """
        Surrounds the text with the appropriate colour codes.

        Parameters:
            message (str): Message to be coloured.
            colour (str): Colour to be used.

        Returns:
            str: String that will print with the desired colour.
        """
        return PrintHandler.COLOUR_MAP[colour] + message + PrintHandler.COLOUR_MAP["reset"]

    @staticmethod
    def print_message(message, sub_message=None, sub_message_colour="reset"):
        """
        Prints a message in the specified colour and following format:

        "[sub_message] message"

        Parameters:
            message (str): Message to be printed.
            sub_message (str): Sub Message to be printed.
            sub_message_colour (str): Colour to print the sub_message in.
        """
        with PrintHandler.print_lock:
            output_message = ""
            if sub_message:
                output_message += "[" + PrintHandler._colour_message(f"{sub_message}", sub_message_colour) + "] "
            output_message += message
            print(output_message)
