class FormatCodes:
    HEADER = '\033[95m'

    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'

    YELLOW = '\033[93m'

    RED = '\033[91m'

    END_CHAR = '\033[0m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_warn(msg: str):
    print(f'{FormatCodes.YELLOW}{msg}{FormatCodes.END_CHAR}')


def print_error(msg: str):
    print(f'{FormatCodes.RED}{msg}{FormatCodes.END_CHAR}')


def print_success(msg: str):
    print(f'{FormatCodes.GREEN}{msg}{FormatCodes.END_CHAR}')
