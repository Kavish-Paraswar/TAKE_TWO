from . import models
from .agents import planner, generator, critic, manager
from .database import SessionLocal
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def run_creative_pipeline(run_id: int, brief_text: str,
                          variants_per_task=3, max_task_iterations=2,
                          score_threshold=7):
    """
    Runs pipeline using a new DB session (safe for background execution).
    """
    db: Session = SessionLocal()
    try:
        run = db.query(models.CreativeRun).filter_by(id=run_id).first()
        if not run:
            return

        # set running
        run.state = "RUNNING"
        run.progress = 0
        db.add(run); db.commit(); db.refresh(run)

        # Planner
        planner_run = models.AgentRun(creative_run_id=run.id, agent_name="planner", iteration=0)
        db.add(planner_run); db.commit(); db.refresh(planner_run)

        tasks = planner.run(brief_text)
        db.add(models.AgentMessage(agent_run_id=planner_run.id, role="planner",
                                   content=f"Planned {len(tasks)} tasks: {[t['task'] for t in tasks]}"))
        db.commit()

        total_tasks = len(tasks)
        completed_tasks = 0

        for task_idx, task_obj in enumerate(tasks):
            # check interrupt/approve between tasks
            run = db.query(models.CreativeRun).filter_by(id=run_id).first()
            if run.state == "INTERRUPTED":
                db.add(models.AgentMessage(agent_run_id=planner_run.id, role="manager",
                                           content=f"Run interrupted before task {task_idx}"))
                db.commit()
                return
            if run.state == "APPROVED":
                db.add(models.AgentMessage(agent_run_id=planner_run.id, role="manager",
                                           content=f"Run pre-approved; stopping further generation."))
                db.commit()
                break

            task_text = task_obj.get("task") if isinstance(task_obj, dict) else str(task_obj)
            task_iteration = 0
            best_generation = None
            best_score = -1

            while True:
                # generate variants concurrently
                with ThreadPoolExecutor(max_workers=variants_per_task) as ex:
                    futures = []
                    for v in range(variants_per_task):
                        futures.append(ex.submit(generator.run, task_text, v, task_iteration))
                    for fut in as_completed(futures):
                        try:
                            gen = fut.result()
                        except Exception as e:
                            ar = models.AgentRun(creative_run_id=run.id, agent_name="generator", iteration=task_iteration)
                            db.add(ar); db.commit(); db.refresh(ar)
                            db.add(models.AgentMessage(agent_run_id=ar.id, role="system/error",
                                                       content=f"Generator failure: {str(e)}"))
                            db.commit()
                            continue

                        g = models.Generation(creative_run_id=run.id, asset_url=gen["url"],
                                              meta={"task": task_text, "variant": gen["variant"], "iteration": gen["iteration"]})
                        db.add(g); db.commit(); db.refresh(g)

                        arc = models.AgentRun(creative_run_id=run.id, agent_name="critic", iteration=task_iteration)
                        db.add(arc); db.commit(); db.refresh(arc)
                        crit = critic.run(gen)
                        db.add(models.AgentMessage(agent_run_id=arc.id, role="critic",
                                                   content=str(crit)))
                        g.meta["score"] = crit.get("score")
                        db.add(g); db.commit(); db.refresh(g)

                        if crit.get("score", 0) > best_score:
                            best_score = crit.get("score", 0)
                            best_generation = g

                # manager decision
                should_repeat = manager.should_continue_task(best_score, task_iteration, score_threshold, max_task_iterations)
                task_iteration += 1

                arm = models.AgentRun(creative_run_id=run.id, agent_name="manager", iteration=task_iteration)
                db.add(arm); db.commit(); db.refresh(arm)
                db.add(models.AgentMessage(agent_run_id=arm.id, role="manager",
                                           content=f"Task '{task_text}' iteration {task_iteration} best_score={best_score} repeat={should_repeat}"))
                db.commit()

                # check interrupt after iteration
                run = db.query(models.CreativeRun).filter_by(id=run_id).first()
                if run.state == "INTERRUPTED":
                    db.add(models.AgentMessage(agent_run_id=arm.id, role="manager",
                                               content=f"Run interrupted during task '{task_text}'"))
                    db.commit()
                    return
                if run.state == "APPROVED":
                    db.add(models.AgentMessage(agent_run_id=arm.id, role="manager",
                                               content=f"Run approved during task '{task_text}', stopping generation."))
                    db.commit()
                    break

                if (not should_repeat) or task_iteration > max_task_iterations:
                    break

            completed_tasks += 1
            run.progress = int((completed_tasks / total_tasks) * 100)
            db.add(run); db.commit(); db.refresh(run)

        # finalize
        run.state = "COMPLETED"
        run.iteration += 1
        run.progress = 100
        db.add(run); db.commit(); db.refresh(run)

        mr = models.AgentRun(creative_run_id=run.id, agent_name="manager", iteration=run.iteration)
        db.add(mr); db.commit(); db.refresh(mr)
        db.add(models.AgentMessage(agent_run_id=mr.id, role="manager",
                                   content="Run completed."))
        db.commit()
    finally:
        db.close()
