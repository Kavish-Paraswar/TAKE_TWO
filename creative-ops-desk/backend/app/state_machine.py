from .models import RunState

ALLOWED = {
    RunState.CREATED: [RunState.PLANNING],
    RunState.PLANNING: [RunState.GENERATING],
    RunState.GENERATING: [RunState.REVIEWING],
    RunState.REVIEWING: [RunState.ITERATING, RunState.AWAITING_APPROVAL],
    RunState.ITERATING: [RunState.GENERATING],
}

def can_transition(a, b):
    return b in ALLOWED.get(a, [])
