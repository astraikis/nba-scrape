import sys
from enum import Enum

import requests
from bs4 import BeautifulSoup


class Position(Enum):
    PG = 1
    SG = 2
    SF = 3
    PF = 4
    C = 5


class Stats:
    def __init__(self, ppg: float, apg: float, rpg: float, bpg: float):
        self.ppg = ppg
        self.apg = apg
        self.rpg = rpg
        self.bpg = bpg

    def print(self):
        print("ppg: " + str(self.ppg))
        print("apg: " + str(self.apg))
        print("rpg: " + str(self.rpg))
        print("bpg: " + str(self.bpg))


class Player:
    def __init__(self, name: str, position: Position, height: tuple, url: str):
        self.name = name
        self.position = position
        self.height = height
        self.url = url

    def get_stats(self, options=None):
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "lxml")

        ppg = None
        apg = None
        rpg = None
        bpg = None

        stats_div = soup.find(id="div_per_game")
        stat_cells = stats_div.find("tfoot").find("tr").find_all("td")
        for cell in stat_cells:
            if cell.attrs["data-stat"] == "pts_per_g":
                ppg = float(cell.text)
            elif cell.attrs["data-stat"] == "ast_per_g":
                apg = float(cell.text)
            elif cell.attrs["data-stat"] == "trb_per_g":
                rpg = float(cell.text)
            elif cell.attrs["data-stat"] == "blk_per_g":
                bpg = float(cell.text)

        return Stats(
            ppg,
            apg,
            rpg,
            bpg
        )

    def print(self):
        print("name: " + self.name)
        print("position: " + str(self.position))
        print("height: " + str(self.height))
        print("url: " + self.url)


def get_url(name: list):
    index = 1
    return f"https://www.basketball-reference.com/players/{name[1][0]}/{name[1][:5]}{name[0][:2]}0{index}.html"


def get_player(url: str):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "lxml")

    info_div = list(soup.find(id="info").find(id="meta").descendants)[5]

    name = info_div.next.next.contents[1].text
    position = None
    height = None

    for p in info_div.find_all("p"):
        bold = p.find_all("strong")
        for tag in bold:
            # get position
            if tag.text.strip().startswith("Position:"):
                position_str = tag.next.next.strip()
                if position_str.startswith("Point"):
                    position = Position.PG
                elif position_str.startswith("Shooting"):
                    position = Position.SG
                elif position_str.startswith("Small"):
                    position = Position.SF
                elif position_str.startswith("Power"):
                    position = Position.PF
                else:
                    position = Position.C

            # get height
            if tag.text.strip().startswith("Shoots:"):
                height_split = tag.next.next.next.next.text.split()[0][:-1].split("-")
                height = (int(height_split[0]), int(height_split[1]))

    return Player(
        name,
        position,
        height,
        url
    )


if len(sys.argv) != 3:
    sys.exit(1)

input_name = sys.argv[1:]
url = get_url(input_name)

player = get_player(url)
player.print()

print("")

stats = player.get_stats();
stats.print()
