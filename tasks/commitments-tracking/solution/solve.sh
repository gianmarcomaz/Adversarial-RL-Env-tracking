#!/bin/bash
set -e

slack list_channels
slack get_channel_messages general
slack get_channel_messages incidents
slack get_channel_messages leads
slack get_channel_messages customer-success
slack get_channel_messages ops
tasks list_tasks

tasks create_task "Update onboarding FAQ" "Update the onboarding FAQ with the new SSO steps." "alice" "todo"
tasks create_task "Set up billing API monitoring" "Create monitoring for the billing API after the 500s incident." "devon" "todo"
tasks create_task "Complete Globex security questionnaire" "Complete the security questionnaire requested by Globex this week." "alice" "todo"
tasks create_task "Draft Initech renewal email" "Draft the Initech renewal email by Friday." "maya" "todo"
tasks create_task "Rotate staging API key" "Own the staging API key rotation after the thread reassignment." "priya" "todo"
tasks create_task "Reconcile April invoice mismatch" "Reconcile the April invoice mismatch." "nina" "todo"
