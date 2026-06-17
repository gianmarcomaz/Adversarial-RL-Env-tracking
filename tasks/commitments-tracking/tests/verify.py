import json
import os
import time
from pathlib import Path

JUDGE_MODEL = os.environ.get("OPENROUTER_JUDGE_MODEL", "openai/gpt-4o-mini").removeprefix("openrouter/")
EXPECTED_TASK_COUNT = 7


# Load the final workspace state from disk.
def load_state():
    path = Path(os.environ.get("WORKSPACE_STATE", "/workspace/state.json"))
    with open(path, encoding="utf-8") as file:
        return json.load(file)


# Return normalized task text.
def task_text(task):
    return ((task.get("title") or "") + " " + (task.get("description") or "")).lower()


# Return a normalized assignee.
def assignee(task):
    return (task.get("assignee") or "").strip().lower()


# Return whether a task is still actionable.
def status_ok(task):
    return (task.get("status") or "").strip().lower() in {"todo", "open", "in_progress"}


# Return whether task text matches every keyword group.
def task_matches(task, groups):
    return all(any(word in task_text(task) for word in group) for group in groups)


# Return tasks that contain every required keyword group.
def matching_tasks(tasks, groups):
    return [task for task in tasks if task_matches(task, groups)]


# Return whether one matching task has the right owner and status.
def commitment_ok(tasks, words, owner):
    return any(assignee(task) == owner and status_ok(task) for task in matching_tasks(tasks, words))


# Return whether no task contains the forbidden words.
def no_task_for(tasks, words):
    return len(matching_tasks(tasks, words)) == 0


# Extract the first JSON object from model text.
def parse_json_object(content):
    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1:
        return {}
    return json.loads(content[start : end + 1])


# Run the deterministic verifier checks.
def deterministic_checks(state):
    tasks = list(state.get("tasks", {}).values())
    checks = {
        "launch_checklist_ok": commitment_ok(tasks, [["launch"], ["checklist"]], "ben"),
        "onboarding_faq_ok": commitment_ok(tasks, [["onboarding"], ["faq"]], "alice"),
        "billing_monitoring_ok": commitment_ok(tasks, [["billing"], ["monitoring"]], "devon"),
        "globex_questionnaire_ok": commitment_ok(tasks, [["globex"], ["questionnaire"]], "alice"),
        "initech_renewal_ok": commitment_ok(tasks, [["initech"], ["renewal"], ["email"]], "maya"),
        "staging_key_rotation_ok": commitment_ok(tasks, [["staging"], ["key"], ["rotat"]], "priya"),
        "invoice_mismatch_ok": commitment_ok(tasks, [["april"], ["invoice"], ["mismatch"]], "nina"),
        "no_launch_checklist_duplicate": len(matching_tasks(tasks, [["launch"], ["checklist"]])) == 1,
        "no_wrong_key_rotation_owner": not any(assignee(task) == "devon" for task in matching_tasks(tasks, [["key"], ["rotat"]])),
        "no_webinar_recap_task": no_task_for(tasks, [["webinar"], ["recap"]]),
        "no_rollout_plan_task": no_task_for(tasks, [["rollout"], ["plan"]]),
        "no_qbr_deck_task": no_task_for(tasks, [["qbr"]]),
        "no_globex_logo_task": no_task_for(tasks, [["globex"], ["logo"]]),
        "no_refund_summary_task": no_task_for(tasks, [["refund"], ["summary"]]),
        "no_discount_task": no_task_for(tasks, [["discount"]]),
        "no_churnco_task": no_task_for(tasks, [["churnco"]]),
        "no_snapshot_task": no_task_for(tasks, [["snapshot"]]),
        "no_docs_typo_task": no_task_for(tasks, [["docs"], ["typo"]]),
        "expected_task_count": len(tasks) == EXPECTED_TASK_COUNT,
    }
    return checks


# Ask an LLM judge for an independent secondary score.
def llm_judge_score(state):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return {"score": -1, "available": False, "error": "OPENROUTER_API_KEY is not set", "model": JUDGE_MODEL}

    try:
        from openai import OpenAI
    except Exception as error:
        return {"score": -1, "available": False, "error": str(error), "model": JUDGE_MODEL}

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    prompt = (
        "Return JSON only with keys score and reason. Score 1 only if all genuine commitments "
        "in the Slack messages are tracked as actionable tasks with the correct final owner, "
        "the reassigned key-rotation task is owned by Priya, the existing launch-checklist task "
        "is not duplicated, and no tasks were created for decoys or completed/FYI/hypothetical work. "
        "Otherwise score 0.\n\n"
        f"State:\n{json.dumps(state, indent=2)}"
    )

    # Retry transient provider failures with short backoff.
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content or "{}"
            result = parse_json_object(content)
            return {"score": int(result.get("score", 0)), "available": True, "reason": result.get("reason", ""), "model": JUDGE_MODEL}
        except Exception as error:
            if attempt == 2:
                return {"score": -1, "available": False, "error": str(error), "model": JUDGE_MODEL}
            time.sleep(2 ** attempt)


# Write Harbor reward outputs.
def main():
    state = load_state()
    checks = deterministic_checks(state)
    deterministic_reward = int(all(checks.values()))
    judge = llm_judge_score(state)
    output = {
        "reward": deterministic_reward,
        "deterministic_reward": deterministic_reward,
        "llm_judge_score": int(judge.get("score", -1)),
        "llm_judge_available": int(judge.get("available", False)),
    }
    for name, passed in checks.items():
        output[name] = int(passed)
    details = {**output, "checks": checks, "judge": judge}

    log_dir = Path(os.environ.get("VERIFIER_LOG_DIR", "/logs/verifier"))
    log_dir.mkdir(parents=True, exist_ok=True)
    with open(log_dir / "reward.json", "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)
    with open(log_dir / "details.json", "w", encoding="utf-8") as file:
        json.dump(details, file, indent=2)
    print(json.dumps(details, indent=2))


# Run the verifier when called as a script.
if __name__ == "__main__":
    main()
