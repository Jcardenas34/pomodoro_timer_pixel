"""Overworld-style (Pokémon Gen 4-ish) trainer template, expressed as role grids.

Each frame is a list of strings, one character per pixel. Characters are
*roles*, not colors, so the same template can be recolored for any person:

    .  transparent        O  outline
    H  hair               h  hair highlight      D  hair shadow
    S  skin               s  skin shadow
    E  eye                W  eye shine           M  mouth
    T  shirt              t  shirt shadow        L  belt
    P  pants              p  pants shadow
    B  shoes              b  shoe sole

Chibi proportions: a big head (14 rows) on a short body (12 rows). Three
directions are drawn (down, up, right); the frontend mirrors "right" for left.
Each direction has a standing frame and two step frames; the walk cycle is
stand, step A, stand, step B.
"""

from __future__ import annotations

FRAME_W = 32
FRAME_H = 32
ROLES = set(".OHhDSsEWMTtLPpBb")

HEAD_Y = 5  # head occupies rows 5..18
BODY_Y = 19  # body + legs occupy rows 19..30
X0 = 8  # character is 16 px wide, centered in the 32 px frame

HEAD_DOWN = [
    "...OO.OOOO.OO...",
    "..OHHOHhhhOHHO..",
    ".OHHhhhHHHHHHHO.",
    ".OHhhHHHHHHHHDO.",
    "OHHhHHHHHHHHHHDO",
    "OHHHHHHHHHHHHHDO",
    "OHHDHHSHHHHSHDDO",
    "ODHSSSSSSSSSSSDO",
    "ODSSWSSSSSSWSSDO",
    "OsSSESSSSSSESSsO",
    "OsSSESSSSSSESSsO",
    ".OsSSSSMMSSSSsO.",
    "..OssSSSSSSssO..",
    "...OOOOOOOOOO...",
]

HEAD_UP = [
    "...OO.OOOO.OO...",
    "..OHHOHhhhOHHO..",
    ".OHHhhhHHHHHHHO.",
    ".OHhhHHHHHHHHDO.",
    "OHHhHHHHHHHHHHDO",
    "OHHHHHHHHHHHHHDO",
    "OHHHHHHHHHHHHHDO",
    "OHHHHHHHHHHHHDDO",
    "ODHHHHHHHHHHHDDO",
    "OsDHHHHHHHHHDDsO",
    "OsDDHHHHHHHDDDsO",
    ".ODDDHHHHHDDDDO.",
    "..OsDDDDDDDDsO..",
    "...OOOOOOOOOO...",
]

HEAD_RIGHT = [
    "..OO.OOOO.OO....",
    ".OHHOHhhhOHHO...",
    "OHHhhhHHHHHHHO..",
    "OHhhHHHHHHHHHHO.",
    "OHhHHHHHHHHHHHDO",
    "OHHHHHHHHHHHHHDO",
    "OHHHHHHHDHHSHHDO",
    "OHHHHHHDSSSSSSSO",
    "ODHHHHDSSSSSWSSO",
    "ODHHsSSSSSSSESSO",
    "ODDHsSSSSSSSESSO",
    ".ODDSSSSSSSSMSO.",
    "..ODssSSSSSSsO..",
    "...OOOOOOOOOO...",
]

# Front and back share a body; step B is step A mirrored.
BODY_FRONT_STAND = [
    "...OOTTTTTTOO...",
    "..OTTTTTTTTTTO..",
    ".OTTOTTTTTTOTTO.",
    ".OTtOTTTTTTOtTO.",
    ".OTtOTTTTTTOtTO.",
    ".OSsOLLLLLLOsSO.",
    "..OOOPPPPPPOOO..",
    "....OPPPPPPO....",
    "....OPpOOpPO....",
    "...OBBBOOBBBO...",
    "...ObbbOObbbO...",
    "....OOO..OOO....",
]

BODY_FRONT_STEP = [
    "...OOTTTTTTOO...",
    "..OTTTTTTTTTTO..",
    ".OTTOTTTTTTOTTO.",
    ".OTtOTTTTTTOtTO.",
    ".OSsOTTTTTTOtTO.",
    "..OOOLLLLLLOsSO.",
    "....OPPPPPPOOO..",
    "....OBBBOpPO....",
    "....ObbbOpPO....",
    ".....OOOOBBBO...",
    "........ObbbO...",
    ".........OOO....",
]

BODY_RIGHT_STAND = [
    ".....OOTTTOO....",
    "....OTTTTTTTO...",
    "....OTTtTTTTO...",
    "....OTTtOTTTO...",
    "....OTTtOTTTO...",
    "....OLLSsOLLO...",
    "....OPPPPPPPO...",
    ".....OPPpPPO....",
    ".....OPPpPPO....",
    ".....OBBBBBBO...",
    ".....ObbbbbbbO..",
    "......OOOOOOO...",
]

# Near leg forward, near arm swung back.
BODY_RIGHT_STEP_A = [
    ".....OOTTTOO....",
    "....OTTTTTTTO...",
    "...OtTTTTTTTO...",
    "..OtOTTTTTTTO...",
    "..OSsOTTTTTTO...",
    "...OOLLLLLLLO...",
    "....OPPPPPPPO...",
    "...OpPOOOPPPPO..",
    "..OpPO...OPPPO..",
    ".OBBO.....OBBBO.",
    ".ObbO.....ObbbbO",
    "..OO.......OOOO.",
]

# Far leg forward, near arm swung forward.
BODY_RIGHT_STEP_B = [
    ".....OOTTTOO....",
    "....OTTTTTTTO...",
    "....OTTTTTTtTO..",
    "....OTTTTTTOtTO.",
    "....OTTTTTTOsSO.",
    "....OLLLLLLLOO..",
    "....OPPPPPPPO...",
    "...OPPPOOOpPpO..",
    "..OPPPO...OpPO..",
    ".OBBBO.....OBBO.",
    ".ObbbO.....ObbbO",
    "..OOO.......OOO.",
]


def _mirror(rows: list[str]) -> list[str]:
    return [r[::-1] for r in rows]


def _compose(head: list[str], body: list[str]) -> list[str]:
    frame = [["."] * FRAME_W for _ in range(FRAME_H)]
    for oy, part in ((HEAD_Y, head), (BODY_Y, body)):
        for dy, row in enumerate(part):
            for dx, role in enumerate(row):
                if role != ".":
                    frame[oy + dy][X0 + dx] = role
    return ["".join(r) for r in frame]


# Frame order in the sheet.
DIRECTIONS = ("down", "up", "right")
FRAMES_PER_DIRECTION = 3  # stand, step A, step B


def build_frames() -> list[list[str]]:
    frames = []
    for head in (HEAD_DOWN, HEAD_UP):
        frames += [
            _compose(head, BODY_FRONT_STAND),
            _compose(head, BODY_FRONT_STEP),
            _compose(head, _mirror(BODY_FRONT_STEP)),
        ]
    frames += [
        _compose(HEAD_RIGHT, BODY_RIGHT_STAND),
        _compose(HEAD_RIGHT, BODY_RIGHT_STEP_A),
        _compose(HEAD_RIGHT, BODY_RIGHT_STEP_B),
    ]
    return frames


def sheet_meta() -> dict:
    """Frame sequences for the frontend: walk cycle and idle frame per direction."""
    walk, idle = {}, {}
    for i, d in enumerate(DIRECTIONS):
        stand, a, b = (i * FRAMES_PER_DIRECTION + k for k in range(3))
        walk[d] = [stand, a, stand, b]
        idle[d] = stand
    return {"frameWidth": FRAME_W, "frameHeight": FRAME_H, "fps": 6, "style": "overworld",
            "walk": walk, "idle": idle}
