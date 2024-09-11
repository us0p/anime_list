from argparse import ArgumentParser
import sys

class DefaultArgumentParser():
    def __init__(self):
        self._parser = self._init_parser()

    def _init_parser(self):
        parser = ArgumentParser(
            prog="Anime List",
            description="CLI application to manage anime lists."
        )

        subparsers = parser.add_subparsers()

        search_parser = subparsers.add_parser(
            "search",
            help="Fetches anime list from API applying filters."
        )
        search_parser.add_argument(
            "-id",
            type=int,
            help="Fetches anime details by id",
        )
        search_parser.add_argument(
            "-p",
            "--page",
            type=int,
            default=1,
            help="Defines which page of the list to show, defaults to 1."
        )
        search_parser.add_argument(
            "-g",
            "--genres",
            default="",
            help="Receive a comma separated list of genres. For a list of available genres see 'genres -h'."
        )
        search_parser.add_argument(
            "-n",
            "--name",
            default="",
            help="Filter animes wich have NAME in the title."
        )

        subparsers.add_parser(
            "list",
            help="Display the animes in your list with relevant information."
        )

        add_parser = subparsers.add_parser(
            "add",
            help="Add the specified anime_id to your list with relevant information."
        )
        add_parser.add_argument(
            "anime_id",
            type=int
        )
        add_parser.add_argument(
            "-tid",
            "--tag-id",
            type=int,
            default=1,
            help="Provide tag_id for the new anime, defaults to 1. For a list of available tags see 'tags -h'."
        )

        remove_parser = subparsers.add_parser(
            "remove",
            help="Remove the specified anime_id from your list."
        )
        remove_parser.add_argument(
            "anime_id",
            type=int
        )

        update_parser = subparsers.add_parser(
            "update",
            help="Updates the specified anime_id information."
        )
        update_parser.add_argument(
                "anime_id",
                type=int
        )
        update_parser.add_argument(
            "-us",
            "--update-seasons",
            type=int,
            help="Update the number of watched seasons."
        )
        update_parser.add_argument(
            "-ue",
            "--update-episodes",
            type=int,
            help="""Update the number of watched episodes,
            also upates the last time watched column with the current date.""")

        subparsers.add_parser(
            "genres",
            help="List available genres"
        )

        subparsers.add_parser(
            'tags',
            help='List available tags'
        )

        return parser

    def parse(self, args: list[str] | None = None):
        if not args:
            args = sys.argv[1:]

        if not args:
            self._parser.parse_args(["-h"])

        options = self._parser.parse_args(args)
        options.command = args[0]
        
        if options.command == "update":
            if options.update_seasons == None and options.update_episodes == None:
                try: 
                    self._parser.parse_args(["update", "-h"])
                except SystemExit:
                    print(
                        "Anime List update: error: must provide update_seasons or update_episodes",
                        file=sys.stderr
                    )
                    raise


        return options
