import sys
from VMaker import main


def argv_parser(args: list[str]):
    args.pop(0)
    if len(args) >= 1:
        _args = [i.strip().split(" ")
                 for i in " ".join(args).split("-") if i != ""]
        print(_args)


if __name__ == "__main__":
    main.__name__ = '__main__'
    main.run()
