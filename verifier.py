# Return the individual verifier checks for debugging rollouts.
def verify_details(slack, tasks, trajectory):
    all_tasks = tasks.list_tasks()
    def text(t): return ((t.get("title") or "") + " " + (t.get("description") or "")).lower()
    def assignee(t): return (t.get("assignee") or "").strip().lower()
    def status_ok(t): return (t.get("status") or "").strip().lower() in {"todo", "open"}

    # Globex questionnaire tracked, assigned alice, actionable.
    globex_ok = any("globex" in text(t) and assignee(t) == "alice" and status_ok(t) for t in all_tasks)
    # Billing API monitoring follow-up tracked, assigned devon, actionable.
    monitoring_ok = any(("monitoring" in text(t) or "billing" in text(t)) and assignee(t) == "devon" and status_ok(t) for t in all_tasks)
    # Dedup held: no duplicate Acme or launch-checklist task.
    acme_count = sum(1 for t in all_tasks if "acme" in (t.get("title") or "").lower())
    checklist_count = sum(1 for t in all_tasks if "checklist" in (t.get("title") or "").lower())
    no_acme_duplicate = acme_count == 1
    no_checklist_duplicate = checklist_count == 1

    # Trajectory: read the workspace and checked the board.
    tool_names = [tc.get("name", "") for step in trajectory for tc in step.get("tool_calls", [])]
    read_workspace = any(("get_channel_messages" in n) or ("search_messages" in n) for n in tool_names)
    checked_board = any("list_tasks" in n for n in tool_names)

    return {
        "globex_ok": globex_ok,
        "monitoring_ok": monitoring_ok,
        "no_acme_duplicate": no_acme_duplicate,
        "no_checklist_duplicate": no_checklist_duplicate,
        "read_workspace": read_workspace,
        "checked_board": checked_board,
    }


# Check whether the agent satisfied the task.
def verify(slack, tasks, trajectory):
    details = verify_details(slack, tasks, trajectory)

    return int(all(details.values()))
