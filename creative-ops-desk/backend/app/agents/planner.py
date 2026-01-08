import re
from typing import List, Dict

def run(brief_text: str) -> List[Dict]:
    """
    Generic planner agent.
    Converts any free-form brief into structured tasks using linguistic heuristics.
    """

    text = brief_text.strip()
    text_lower = text.lower()

    tasks = []
    task_id = 0

    # 1. Split brief into logical units
    separators = r"\.|,| and | then | also | plus | with "
    chunks = [c.strip() for c in re.split(separators, text) if len(c.strip()) > 3]

    # 2. Extract modifiers (styles, tones, constraints)
    modifiers = []
    modifier_patterns = [
        r"dark|light|bright|dramatic|minimal|flat|realistic|cinematic",
        r"modern|clean|vintage|retro|futuristic",
        r"professional|casual|bold|soft",
        r"high[- ]?contrast|low[- ]?contrast",
        r"fast|slow|smooth|dynamic"
    ]

    for pat in modifier_patterns:
        for match in re.findall(pat, text_lower):
            if match not in modifiers:
                modifiers.append(match)

    if not modifiers:
        modifiers.append("default style")

    # 3. Detect actions (verbs)
    actions = []
    verb_patterns = r"\b(create|design|generate|build|produce|write|draft|make|render|compose)\b"
    actions = re.findall(verb_patterns, text_lower)
    actions = list(set(actions)) or ["create"]

    # 4. Build tasks
    for chunk in chunks:
        for action in actions:
            tasks.append({
                "task_id": task_id,
                "task": f"{action.capitalize()} {chunk}",
                "meta": {
                    "modifiers": modifiers,
                    "source_brief": text
                }
            })
            task_id += 1

    # 5. Fallback safeguard
    if not tasks:
        tasks.append({
            "task_id": 0,
            "task": f"Process brief: {text}",
            "meta": {
                "modifiers": modifiers
            }
        })

    return tasks
