import sys
import time

from agent import MODEL, run_agent
from run_task import INSTRUCTION
from seed import seed_workspace
from verifier import verify, verify_details


# Run the full task n times and print the pass rate.
def run_rollouts(n=8, model=MODEL):
    passes = 0
    fails = 0
    errors = 0
    failed_checks = {
        "globex_ok": 0,
        "monitoring_ok": 0,
        "no_acme_duplicate": 0,
        "no_checklist_duplicate": 0,
        "read_workspace": 0,
        "checked_board": 0,
    }

    for _ in range(n):
        try:
            slack, tasks = seed_workspace()
            trajectory = run_agent(INSTRUCTION, slack, tasks, model)
            details = verify_details(slack, tasks, trajectory)
            reward = verify(slack, tasks, trajectory)
            if reward:
                passes += 1
            else:
                fails += 1
                for name, passed in details.items():
                    if not passed:
                        failed_checks[name] += 1
        except Exception:
            errors += 1
        time.sleep(3)

    total = passes + fails + errors
    percent = round((passes / n) * 100) if n else 0
    breakdown = ", ".join(f"{name} {count}" for name, count in failed_checks.items() if count)
    if not breakdown:
        breakdown = "none"
    print(f"model={model}  {passes}/{n} passed = {percent}%  (errors: {errors})")
    print(f"passes={passes} fails={fails} errors={errors} total={total}")
    print(f"failed checks across {n} runs: {breakdown}")


# Read the optional model slug and run count from the command line.
def read_args():
    model = sys.argv[1] if len(sys.argv) > 1 else MODEL
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    return model, n


# Run a small default rollout batch when called as a script.
if __name__ == "__main__":
    chosen_model, run_count = read_args()
    run_rollouts(run_count, chosen_model)
