#!/usr/bin/env python3
"""Style 6 sheet contract, routing and unchanged-specialist regression; not a provider quality score."""
from copy import deepcopy
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/directing-stickman-videos"
REFS = SKILL / "references"
REF = (REFS / "modern-anime.md").read_text()

# The anime drawing anchor is frozen verbatim; a sheet change must not rewrite it.
blocks = re.findall(r"```text\n(.*?)\n```", REF, re.S)
anchor = blocks[0]
for token in (
    "Modern cinematic 2D anime animation",
    "clean dark ink outlines",
    "Exactly two arms and two legs, five fingers on each hand",
    "Painterly atmospheric backgrounds",
):
    assert token in anchor, token
for token in (
    "front, side and back turnarounds", "four-state expression set",
    "Young Passenger", "Station Master", "Night Railway",
    "Midnight blue, lantern amber, weathered leather brown, steam grey, moonlight silver",
    "repeat its **full description** in every prompt",
    "no provider-generated Style 6 footage has been evaluated yet",
    "voice-continuity.md", "Do not inherit Style 1", "Modern Anime / 现代动漫风",
    "NO VISIBLE TEXT", "NO 3D CGI", "NO CHIBI",
):
    assert token in REF, token

for filename in (
    "SKILL.md", "references/style-catalog.md",
    "references/storyboard-template.md", "references/omni-flash-prompt-contract.md",
):
    assert "modern-anime.md" in (SKILL / filename).read_text(), filename
entry = (SKILL / "SKILL.md").read_text()
assert "`Style 6 (Modern Anime / 现代动漫风)`" in entry
assert len(entry.encode()) <= 14000, "Keep the new style detail in references"
assert "## 6. Style 6: Modern Anime" in (REFS / "style-catalog.md").read_text()

# Existing specialist contracts must not be rewritten for this addition.
baseline = {
    "prehistoric-dark-comedy.md": "1a3a58a22b392cc087a0aa645b3f8478a3136e7e7f35d086ddb588ac091df860",
    "cozy-storytelling.md": "a0b3f5890857582bb1e7bfa819cefcc7ffd55af72ab8997e1b286b7ad27f1419",
    "historical-cartoon.md": "360f374c7b521353f5fbb9cb546b6f9f70a098973b99281c28d04ce28e77b01d",
}
for filename, fingerprint in baseline.items():
    assert hashlib.sha256((REFS / filename).read_bytes()).hexdigest() == fingerprint, filename
voice = (REFS / "voice-continuity.md").read_bytes()
heading = b"# Shared voice continuity \xe2\x80\x94 all visual styles\n\n"
notice = (
    b"Scope: **A \xc2\xb7 Director text-to-video prompts only**. B \xc2\xb7 Autopilot uses named TTS voices under `autopilot.md`; "
    b"do not copy this document's descriptive voice profiles into any B-style TTS request.\n\n"
)
assert voice.startswith(heading + notice), "Missing exact A-only voice scope"
assert hashlib.sha256(heading + voice[len(heading + notice):]).hexdigest() == \
    "24014bc599e237644c743f033a0b62c556ba4ed8689d382d08b1bcdce1967de2"

SHEET_FIELDS = ("identity", "face", "hair", "wardrobe", "prop", "silhouette", "expressions", "turnaround")


def validate(plan):
    """Reject identity drift, expression drift, prop resets and text/code leakage."""
    assert plan["style"] == "Style 6"
    sheet = plan["sheet"]
    for field in SHEET_FIELDS:
        assert sheet.get(field), "Incomplete sheet field: " + field
    assert len(sheet["expressions"]) == 4, "A sheet needs four approved expression states"
    for clip in plan["clips"]:
        assert clip["sheet"] == sheet, "Full character sheet must repeat in every clip"
        assert clip["expression"] in sheet["expressions"], "Unapproved expression state"
        assert clip["props"] == plan["props"], "Prop count/ownership drifted"
        assert "no visible text" in clip["negatives"].lower(), "Missing visible-text ban"
        assert not re.search(r"#[0-9a-fA-F]{3,6}|rgb\(", clip["palette"]), "Technical color notation"
    assert len({clip["expression"] for clip in plan["clips"]}) >= 2, "One reused expression throughout"


sheet = {
    "identity": "Young Passenger, 22–25, lean, olive-brown jacket, one suitcase",
    "face": "warm brown eyes, dark brows, calm mouth",
    "hair": "messy black hair, loose forehead strands",
    "wardrobe": "olive-brown field jacket, white shirt, dark trousers, scuffed sneakers",
    "prop": "one worn brown leather suitcase with brass corner caps",
    "silhouette": "slim open jacket, suitcase at one side",
    "expressions": ["neutral", "curious", "shocked", "calm"],
    "turnaround": "jacket back seam, suitcase strap on the right side, nape hairline",
}
plan = {
    "style": "Style 6",
    "sheet": sheet,
    "props": {"suitcase": 1, "lantern": 0},
    "clips": [
        {"sheet": sheet, "expression": "neutral", "props": {"suitcase": 1, "lantern": 0},
         "palette": "midnight blue, lantern amber", "negatives": "No visible text."}
        for _ in range(3)
    ],
}
plan["clips"][1]["expression"] = "curious"
plan["clips"][2]["expression"] = "calm"
validate(plan)

bad_cases = []
drift = deepcopy(plan)
drift["clips"][1]["sheet"] = dict(sheet, hair="short blond hair")
bad_cases.append(drift)
unapproved = deepcopy(plan)
unapproved["clips"][1]["expression"] = "smirking"
bad_cases.append(unapproved)
prop_reset = deepcopy(plan)
prop_reset["clips"][2]["props"] = {"suitcase": 2, "lantern": 0}
bad_cases.append(prop_reset)
text_leak = deepcopy(plan)
text_leak["clips"][0]["negatives"] = "No 3D."
bad_cases.append(text_leak)
hex_code = deepcopy(plan)
hex_code["clips"][0]["palette"] = "midnight blue #101a2e"
bad_cases.append(hex_code)
same_face = deepcopy(plan)
for clip in same_face["clips"]:
    clip["expression"] = "neutral"
bad_cases.append(same_face)
missing_field = deepcopy(plan)
missing_field["sheet"].pop("turnaround")
bad_cases.append(missing_field)
for bad in bad_cases:
    try:
        validate(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError("Expected invalid Style 6 fixture was accepted")

print("Style 6 anchor, sheet fields, routing, negatives and unchanged specialist contracts passed.")
print("One valid and seven invalid planning fixtures passed; no generated-video or audio score claimed.")
