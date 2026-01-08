import random
def run(generation):
    base = 6
    bump = min(3, generation.get("iteration", 0))  
    score = min(10, base + bump + random.randint(-2, 2))
    return {"score": score, "feedback": f"score {score}, feedback for {generation.get('task')}"}
