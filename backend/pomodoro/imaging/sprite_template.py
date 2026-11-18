"""Overworld-style (Pokémon Gen 4-ish) trainer template, expressed as role grids.

Each frame is a list of strings, one character per pixel. Characters are
*roles*, not colors, so the same template can be recolored for any person:

    .  transparent        O  outline
    H  hair               h  hair highlight      D  hair shadow
    S  skin               s  skin shadow
    E  eye                W  eye shine           M  mouth
    U  facial hair (mustache; map it to the skin color for none)
    T  shirt              t  shirt shadow        L  belt
    P  pants              p  pants shadow
    B  shoes              b  shoe sole

Chibi proportions: a big head (13-16 rows, by hairstyle) on a short body (12 rows). Three
directions are drawn (down, up, right); the frontend mirrors "right" for left.
Each direction has a standing frame and two step frames; the walk cycle is
stand, step A, stand, step B.
"""

from __future__ import annotations

FRAME_W = 32
FRAME_H = 32
ROLES = set(".OHhDSsEWMUTtLPpBb")

HEAD_Y = 3  # 16-row head grids occupy rows 3..18 (the top rows hold hair volume)
BODY_Y = 19  # body + legs occupy rows 19..30
X0 = 8  # character is 16 px wide, centered in the 32 px frame

# Heads are 16x16 per hairstyle and direction. The face sits in the lower rows
# and is the same across styles except where hair frames it; `U` is facial hair
# (a mustache), which a palette can set to the skin color to remove it.
HAIRSTYLES: dict[str, dict[str, list[str]]] = {
    # The original Juan from before hairstyles: wavy tufts, no mustache. Kept
    # pixel-for-pixel (two blank rows on top put the head back at row 5).
    "original": {
        "down": [
            "................",
            "................",
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
        ],
        "up": [
            "................",
            "................",
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
        ],
        "right": [
            "................",
            "................",
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
        ],
    },
    # Short: close-cropped crew cut, flat top, straight hairline, ears showing.
    "crew": {
        "down": [
            "................",
            "................",
            "................",
            "...OOOOOOOOOO...",
            "..OHhHhHhHHHHO..",
            ".OHhHhHHHHHHHDO.",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHHHHHDO",
            "ODHHHHHHHHHHHDDO",
            "ODSSSSSSSSSSSSDO",
            "OsSSWSSSSSSWSSsO",
            "OsSSESSSSSSESSsO",
            "OsSSESSSSSSESSsO",
            ".OsSSUUUUUUSSsO.",
            "..OssUSMMSUssO..",
            "...OOOOOOOOOO...",
        ],
        "up": [
            "................",
            "................",
            "................",
            "...OOOOOOOOOO...",
            "..OHhHhHhHHHHO..",
            ".OHhHhHHHHHHHDO.",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHHHHDDO",
            "ODHHHHHHHHHHHDDO",
            "OsDHHHHHHHHHDDsO",
            "OsSDDHHHHHDDDSsO",
            ".OsSDDDDDDDDSsO.",
            ".OsSSSSSSSSSSsO.",
            "..OssSSSSSSssO..",
            "...OOOOOOOOOO...",
        ],
        "right": [
            "................",
            "................",
            "................",
            "..OOOOOOOOOO....",
            ".OHhHhHhHHHHO...",
            "OHhHhHHHHHHHHO..",
            "OHHHHHHHHHHHHHO.",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHDSSSSSO",
            "ODHHHHHDSSSSSSSO",
            "ODHHsSSSSSSSWSSO",
            "OsDHsSSSSSSSESSO",
            "OsSSSSSSSSSSESSO",
            ".OsSSSSSSSSUUUO.",
            "..OssSSSSSSMsO..",
            "...OOOOOOOOOO...",
        ],
    },
    # Short-medium: side part with a swoop across the forehead.
    "sidepart": {
        "down": [
            "................",
            "................",
            "....OOOOOOOOO...",
            "..OOHDhhhhhHHO..",
            ".OHHDHhhHHHHHHO.",
            ".OHDHHHHHhhHHHDO",
            "OHHDHHHHHHHhhHDO",
            "OHDSHHHHHHHHhHDO",
            "ODSSSDhHHHHHHDDO",
            "ODSSSSSSSDhHHSDO",
            "OsSSWSSSSSSWSSsO",
            "OsSSESSSSSSESSsO",
            "OsSSESSSSSSESSsO",
            ".OsSSUUUUUUSSsO.",
            "..OssUSMMSUssO..",
            "...OOOOOOOOOO...",
        ],
        "up": [
            "................",
            "................",
            "...OOOOOOOOO....",
            "..OHHhhhhhDHOO..",
            ".OHHHHhhHHHDHHO.",
            ".OHHHHHHHHHHDHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHHHHDDO",
            "ODHHHHHHHHHHHDDO",
            "OsDHHHHHHHHHDDsO",
            "OsDDHHHHHHHDDDsO",
            ".ODDDHHHHHDDDDO.",
            ".OsDDDDDDDDDDsO.",
            "..OssSSSSSSssO..",
            "...OOOOOOOOOO...",
        ],
        "right": [
            "................",
            "................",
            "...OOOOOOOO.....",
            ".OOHHhhhhHHOO...",
            "OHHHHHhhhHHHHO..",
            "OHHHHHHHHHHHHHO.",
            "OHHHHHHHhhhhHHHO",
            "OHHHHHHHHHHhhDDO",
            "OHHHHHHHHDHhDSSO",
            "ODHHHHHDSSSSSSSO",
            "ODHHsSSSSSSSWSSO",
            "OsDHsSSSSSSSESSO",
            "OsSSSSSSSSSSESSO",
            ".OsSSSSSSSSUUUO.",
            "..OssSSSSSSMsO..",
            "...OOOOOOOOOO...",
        ],
    },
    # Medium: wavy, with volume on top, over the ears and down to the nape.
    "wavy": {
        "down": [
            "....OO..OO......",
            "...OHHOOHHOOO...",
            "..OHhhHHhhHHHO..",
            ".OHhhhHHhHHHHHO.",
            "OHHhHHHHHHHHHHHO",
            "OHHHHhHHHHhHHHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHDHHHDHHHHDHDO",
            "OHDSSHDSSSHDSHDO",
            "OHDSSSSSSSSSSDHO",
            "OHSSWSSSSSSWSSHO",
            "OHSSESSSSSSESSHO",
            "OHsSESSSSSSESsHO",
            "ODOsSUUUUUUSsODO",
            ".OOssUSMMSUssOO.",
            "...OOOOOOOOOO...",
        ],
        "up": [
            "....OO..OO......",
            "...OHHOOHHOOO...",
            "..OHhhHHhhHHHO..",
            ".OHhhhHHhHHHHHO.",
            "OHHhHHHHHHHHHHHO",
            "OHHHHhHHHHhHHHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHHHhHHHHhHHDDO",
            "ODHHHHHHHHHHHDDO",
            "ODHHHHHHHHHHHDDO",
            "ODDHHHHHHHHHDDDO",
            "ODHDHHDHHDHHDHDO",
            ".ODODDODDODDODO.",
            "..OsSSSSSSSSsO..",
            "...OOOOOOOOOO...",
        ],
        "right": [
            "...OO..OO.......",
            "..OHHOOHHOOO....",
            ".OHhhHHhhHHHO...",
            "OHhhhHHhHHHHHO..",
            "OHhHHHHHHHHHHHO.",
            "OHHHHhHHHHhHHHDO",
            "OHHHHHHHHHHHHHDO",
            "OHHHHHHHHHDHHDDO",
            "OHHHHHHHHDSHDSSO",
            "OHHHHHHDSSSSSSSO",
            "ODHHHHHSSSSSWSSO",
            "ODHHHHDSSSSSESSO",
            "ODHDHDSSSSSSESSO",
            ".ODODOSSSSSUUUO.",
            "..O.OOssSSSMsO..",
            "......OOOOOOO...",
        ],
    },
}
HAIRSTYLE_NAMES = {"original": "Original", "crew": "Crew cut", "sidepart": "Side part", "wavy": "Wavy"}
DEFAULT_HAIRSTYLE = "sidepart"

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


def build_frames(hairstyle: str = DEFAULT_HAIRSTYLE) -> list[list[str]]:
    heads = HAIRSTYLES[hairstyle]
    frames = []
    for head in (heads["down"], heads["up"]):
        frames += [
            _compose(head, BODY_FRONT_STAND),
            _compose(head, BODY_FRONT_STEP),
            _compose(head, _mirror(BODY_FRONT_STEP)),
        ]
    frames += [
        _compose(heads["right"], BODY_RIGHT_STAND),
        _compose(heads["right"], BODY_RIGHT_STEP_A),
        _compose(heads["right"], BODY_RIGHT_STEP_B),
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
