def run(task, variant_index=0, iteration=0):
    safe_text = task.replace(" ", "+")
    url = f"https://via.placeholder.com/600x400?text={safe_text}+v{variant_index}+it{iteration}"
    return {"task": task, "variant": variant_index, "iteration": iteration, "url": url}
