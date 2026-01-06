import random
def run(generation):
    # Mock critic: score 0-10 and feedback string
    # If iteration increases, slightly better chance of higher score.
    base = 6
    bump = min(3, generation.get("iteration", 0))  # small improvement per iteration
    score = min(10, base + bump + random.randint(-2, 2))
    return {"score": score, "feedback": f"score {score}, feedback for {generation.get('task')}"}
