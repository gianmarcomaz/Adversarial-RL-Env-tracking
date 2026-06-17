from services.slack import SlackService
from services.state import reset_state
from services.tasks import TaskManagerService


# Post one seeded Slack message as a named user.
def post_as(slack, channel, user, text, thread_id=None):
    message = slack.post_message(channel["id"], text, thread_id=thread_id)
    message["user"] = user
    return message


# Build a fresh commitments-tracking workspace.
def seed_workspace():
    reset_state()
    slack = SlackService()
    tasks = TaskManagerService()

    # Seed a small but varied user list.
    slack.users[:] = ["alice", "ben", "carla", "devon", "maya", "nina", "priya"]

    general = slack.create_channel("general")
    incidents = slack.create_channel("incidents")
    leads = slack.create_channel("leads")
    customer_success = slack.create_channel("customer-success")
    ops = slack.create_channel("ops")

    # Ground truth:
    # Real commitments: m2 launch checklist -> ben (already tracked as t1);
    # m5 onboarding FAQ -> alice; m11/m12 billing API monitoring -> devon;
    # m15/m16 Globex questionnaire -> alice; m23/m24 Initech renewal email -> maya;
    # m29-m32 staging API key rotation -> priya after reassignment; m34/m35 April invoice mismatch -> nina.
    # Decoys: m3 completed webinar recap; m4/m36 docs typo chatter; m6 hypothetical rollout plan;
    # m18 declined QBR deck; m20 completed logo request; m25 completed refund summary;
    # m27 hypothetical discount; m28 declined ChurnCo follow-up; m33 FYI staging snapshot.

    # Seed #general with one tracked commitment and several decoys.
    post_as(slack, general, "alice", "Morning everyone! The demo recap doc is in the drive.")
    post_as(slack, general, "ben", "I will refresh the launch checklist before tomorrow's launch review.")
    post_as(slack, general, "carla", "I finished the customer webinar recap this morning.")
    post_as(slack, general, "devon", "Should we really create a task for every tiny docs typo?")
    post_as(slack, general, "alice", "I will update the onboarding FAQ with the new SSO steps.")
    post_as(slack, general, "priya", "If the pilot slips, we might need a new rollout plan.")
    post_as(slack, general, "nina", "Coffee machine is fixed again.")

    # Seed #incidents with an explicit ask directed at Devon.
    incident = post_as(slack, incidents, "devon", "Spike in 500s on the billing API started at 09:42.")
    post_as(slack, incidents, "alice", "The deploy diff looked clean when I checked it.", thread_id=incident["id"])
    post_as(slack, incidents, "devon", "Rollback finished and errors are back to baseline.", thread_id=incident["id"])
    post_as(slack, incidents, "ben", "Devon, can you create a follow-up task to set up monitoring for the billing API?")
    post_as(slack, incidents, "devon", "Yes, I'll set up billing API monitoring this week.")
    post_as(slack, incidents, "carla", "FYI, the status page already showed green by 10:10.")
    post_as(slack, incidents, "alice", "Let's discuss alert thresholds in the retro.")

    # Seed #leads with a volunteer commitment and a declined ask.
    post_as(slack, leads, "ben", "Globex wants a security questionnaire completed this week.")
    post_as(slack, leads, "alice", "I can take the Globex questionnaire after lunch.")
    post_as(slack, leads, "carla", "Maya, can you handle the QBR deck for Globex too?")
    post_as(slack, leads, "maya", "I can't take the QBR deck this week.")
    post_as(slack, leads, "devon", "New lead from Umbrella looks early stage.")
    post_as(slack, leads, "ben", "No task needed for the old Globex logo request; it was closed last month.")
    post_as(slack, leads, "nina", "Can someone remind me where the SOC2 template lives?")

    # Seed #customer-success with an ask where the owner is not the speaker.
    post_as(slack, customer_success, "carla", "Initech renewal call went well.")
    post_as(slack, customer_success, "carla", "Maya, please draft the Initech renewal email by Friday.")
    post_as(slack, customer_success, "maya", "Got it, I'll draft the renewal email.")
    post_as(slack, customer_success, "nina", "The customer already received the refund summary yesterday.")
    post_as(slack, customer_success, "ben", "FYI, the new support macros are live.")
    post_as(slack, customer_success, "alice", "Could we maybe offer a discount if usage drops?")
    post_as(slack, customer_success, "devon", "I will not own the ChurnCo follow-up because sales is handling it.")

    # Seed #ops with a threaded reassignment and an invoice ask.
    rotation = post_as(slack, ops, "devon", "I'll rotate the staging API key after lunch.")
    post_as(slack, ops, "ben", "Please include the deploy notes when you do the key rotation.", thread_id=rotation["id"])
    post_as(slack, ops, "devon", "I'm tied up with the audit and can't own the key rotation after all.", thread_id=rotation["id"])
    post_as(slack, ops, "priya", "I can take the staging API key rotation and finish it today.", thread_id=rotation["id"])
    post_as(slack, ops, "nina", "FYI, the staging database snapshot completed overnight.")
    post_as(slack, ops, "alice", "Nina, can you reconcile the April invoice mismatch?")
    post_as(slack, ops, "nina", "Yes, I will reconcile the April invoice mismatch tomorrow.")
    post_as(slack, ops, "maya", "Docs typo cleanup can wait until next sprint.")
    slack._save()

    tasks.create_task(
        "Prepare launch readiness checklist",
        "Refresh the checklist for tomorrow's launch review.",
        "ben",
        "todo",
    )

    return slack, tasks


# Seed the workspace when this file is run directly.
if __name__ == "__main__":
    seed_workspace()
