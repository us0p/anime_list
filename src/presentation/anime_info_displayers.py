import os
from sys import stdout

from interfaces.movie_service_interface import AnimeListReturn

from ..interfaces.displayer_interface import AnimeListItem, FormatedTitleMap, AnimeDetailedInfo, IAnimeInfoListItem, IAnimeDetailedInfo, IDisplayer 
from .image_builder import ImagePixels

class TextBuilder():
    _terminal_columns: int
    _dflt_img_char_p_line = 31
    _dflt_txt_spc: int
    _curr_contet_printed_lines = 0
    _lines_printed = 0
    _terminal_columns = 0
    _printed_anime_inf: list[FormatedTitleMap]
    _anime_info_to_print: list[FormatedTitleMap]
    _image_pixels: ImagePixels

    def __init__(
        self,
        image_pixels: ImagePixels,
        anime_info_to_print: list[FormatedTitleMap]
    ):
        self._terminal_columns = os.get_terminal_size().columns
        self._dflt_txt_spc = self._terminal_columns - self._dflt_img_char_p_line
        self._printed_anime_inf = []
        self._image_pixels = image_pixels
        self._anime_info_to_print = anime_info_to_print

    def _parse_content(self, content: str) -> str:
        if type(content) == list:
            return ', '.join(content).replace('\n', " ")

        return str(content).replace('\n', " ")

    def _get_content_lines(
        self,
        title_map: FormatedTitleMap,
        content: str,
        padding: int
    ) -> list[str]:
        content = self._parse_content(content)
        inf_prefix = f"{title_map['title']}: "
        inf_prefix_len = len(inf_prefix)
        printed_char = 0
        lines = []
        while printed_char < len(content):
            offset = printed_char + padding
            line = content[printed_char:offset]
            if printed_char == 0:
                offset -= inf_prefix_len
                line = f"{inf_prefix}{content[printed_char:offset]}"
            if offset <= len(content) and line[-1] != " ":
                count = -1
                while line[count] != " ":
                    count -= 1
                offset += count + 1 # slicing is exclusive
                prefix_len = inf_prefix_len if printed_char == 0 else 0
                new_offset = offset + prefix_len - printed_char
                line = line[0:new_offset]
            lines.append(line)
            printed_char = offset

        return lines

AnimeListItemFields: list[FormatedTitleMap] = [
        {
            "title": "ID",
            "original_title": "api_id",
            "max_lines": 1
        },
        {
            "title": "Title",
            "original_title": "title",
            "max_lines": 2
        },
        {
            "title": "Overview",
            "original_title": "overview",
            "max_lines": 17
        },
        {
            "title": "Release Date",
            "original_title": "release_date",
            "max_lines": 1
        },
        {
            "title": "Genres",
            "original_title": "genres",
            "max_lines": 1
        },
    ]

AnimeDetailsFields: list[FormatedTitleMap] = [
        {
            "title": "Number of episdes",
            "original_title": "episodes_count",
            "max_lines": 1
        },
        {
            "title": "Number of seasons",
            "original_title": "seasons_count",
            "max_lines": 1
        },
        {
            "title": "Status",
            "original_title": "status",
            "max_lines": 1
        },
        {
            "title": "Trailers",
            "original_title": "trailers",
            "max_lines": 6
        }
]

class AnimeDetailedItemDisplayer(
    TextBuilder,
    IAnimeDetailedInfo,
    IDisplayer,
):
    def __init__(
        self,
        anime_inf: AnimeDetailedInfo,
        image_pixels: ImagePixels
    ):
        super().__init__(
            image_pixels,
            AnimeListItemFields + AnimeDetailsFields
        )
        self._anime_inf = anime_inf
        self._image_pixels = image_pixels

    @property
    def anime_inf(self) -> AnimeDetailedInfo:
        return self._anime_inf

    def render_info(self):
        for info in self._anime_info_to_print:
            if info["original_title"] == "trailers":
                print(f"{info['title']}:")
                trailers = self.anime_inf[info["original_title"]]
                for trailer_info in trailers:
                    print(f'{trailer_info["name"]}: {trailer_info["link"]}')
                continue

            content_lines = self._get_content_lines(
                info,
                self.anime_inf[info["original_title"]],
                self._terminal_columns
            )
            for line in content_lines:
                print(line)

        image_middle = self._image_pixels.default_width / 2
        blank_offset = int((self._terminal_columns / 2) - image_middle)
        for pixel_line in self._image_pixels:
            stdout.write(" " * blank_offset)
            for r,g,b in pixel_line:
                stdout.write(f"\033[38;2;{r};{g};{b}mo\033[0m")
            print(" " * blank_offset)



class AnimeListItemDisplayer(TextBuilder,IAnimeInfoListItem, IDisplayer):
    def __init__(
        self,
        anime_inf: AnimeListItem,
        image_pixels: ImagePixels
    ):
        super().__init__(image_pixels, AnimeListItemFields)
        self._anime_inf = anime_inf
        self._image_pixels = image_pixels

    @property
    def anime_inf(self) -> AnimeListItem:
        return self._anime_inf

    def _get_next_anime_info(self):
        printed_anime_inf = len(self._printed_anime_inf)
        if printed_anime_inf == len(self._anime_info_to_print):
            raise StopIteration

        anime_inf_to_print = self._anime_info_to_print[printed_anime_inf]
        yield anime_inf_to_print 

    def _add_elipsis(self, lines: list[str], max_lines: int):
        line_count = len(lines)
        if max_lines < line_count:
            last_visible_line = max_lines - line_count - 1
            last_line = lines[last_visible_line]
            len_line = len(last_line)

            if len_line + 3 < self._dflt_txt_spc:
                lines[last_visible_line] = f"{last_line}..."
                return

            lines[last_visible_line] = f"{last_line[0:len_line]}..."

    def _text_producer(self):
        if len(self._printed_anime_inf) == len(self._anime_info_to_print):
            yield ""

        anime_info_to_print = next(self._get_next_anime_info())
        if anime_info_to_print["original_title"] == "release_date":
            if self._lines_printed < self._image_pixels.default_height - 2:
                yield ""
        content_lines = self._get_content_lines(
            anime_info_to_print,
            self.anime_inf[anime_info_to_print["original_title"]],
            self._dflt_txt_spc
        )
        self._add_elipsis(content_lines, anime_info_to_print["max_lines"])
        line = content_lines[self._curr_contet_printed_lines]
        self._curr_contet_printed_lines += 1
        if self._curr_contet_printed_lines == len(content_lines):
            self._printed_anime_inf.append(anime_info_to_print)
            self._curr_contet_printed_lines = 0
        yield line

    def render_info(self):
        for pixel_line in self._image_pixels:
            for r,g,b in pixel_line:
                stdout.write(f"\033[38;2;{r};{g};{b}mo\033[0m")
            stdout.write('|')
            anime_info = next(self._text_producer())
            stdout.write(anime_info)
            stdout.write('\n')
            self._lines_printed += 1
        print('-' * self._terminal_columns)

class ListDisplayer(IDisplayer):
    name: str
    list_to_display: list[str]

    def __init__(self, name: str, list_to_display: list[str]):
        self.name = name
        self.list_to_display = list_to_display

    def render_info(self):
        print("Genres:")
        for item in self.list_to_display:
            print(f"- {item}")
