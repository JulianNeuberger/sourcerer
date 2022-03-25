import argparse

import analyze
import process

if __name__ == '__main__':
    def main():
        commands = {
            'process': process.process,
            'analyze': analyze.analyze
        }

        parser = argparse.ArgumentParser()
        parser.add_argument('command', choices=commands.keys())
        args, remaining_args = parser.parse_known_args()

        command = commands[args.command]
        command(remaining_args)


    main()
