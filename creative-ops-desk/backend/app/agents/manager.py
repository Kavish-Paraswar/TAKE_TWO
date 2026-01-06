def should_continue_task(best_score, iteration, score_threshold, max_task_iterations):
    # Return True if we should attempt another generation for the same task
    if best_score >= score_threshold:
        return False
    return iteration < max_task_iterations
