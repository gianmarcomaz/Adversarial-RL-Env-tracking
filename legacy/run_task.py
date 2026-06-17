import json

from agent import MODEL, run_agent
from seed import seed_workspace
from verifier import verify


with open("instruction.md", encoding="utf-8") as f:
    INSTRUCTION = f.read()


# Run one seeded task, save the trajectory, and print the reward.
def main():
    slack, tasks = seed_workspace()
    trajectory = run_agent(INSTRUCTION, slack, tasks, MODEL)

    with open("trajectory.json", "w", encoding="utf-8") as file:
        json.dump(trajectory, file, indent=2, default=str)

    print(json.dumps(trajectory, indent=2, default=str))
    reward = verify(slack, tasks, trajectory)
    print(f"reward: {reward}")


# Allow the script to be run directly.
if __name__ == "__main__":
    main()
