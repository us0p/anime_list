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

        list_parser = subparsers.add_parser(
            "list",
            help="Display the animes in your list with relevant information."
        )
        list_parser.add_argument(
            "-id",
            type=int,
            help="Fetches anime by id"
        )
        list_parser.add_argument(
            "-n",
            "--name",
            type=str,
            help="Filter animes which have NAME in the title"
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
        add_parser.add_argument(
            "-ws",
            "--watching-season",
            type=int,
            help="Define the current season of the anime"
        )
        add_parser.add_argument(
            "-lwe",
            "--last-watched-episode",
            type=int,
            help="Set the last episode watched of the current season"
        )
        add_parser.add_argument(
            "-lwa",
            "--last-watched-at",
            type=str,
            help="A date string in the format YYYY-MM-DD. Defines the last time the anime was watched"
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
            also upates the last time watched column with the current date."""
        )
        update_parser.add_argument(
            "-ut",
            "--update-tag",
            type=int,
            help="Update the tag of the anime"
        )

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
            if options.update_seasons == None and options.update_episodes == None and options.update_tag == None:
                try: 
                    self._parser.parse_args(["update", "-h"])
                except SystemExit:
                    print(
                        "Anime List update: error: must provide update_seasons, update_episodes or update_tag",
                        file=sys.stderr
                    )
                    raise


        return options
