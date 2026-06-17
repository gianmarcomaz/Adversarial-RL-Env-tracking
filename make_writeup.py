import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("matplotlib_cache").resolve()))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


OUTPUT_DOCX = "apollo_writeup.docx"
FIGURE_1 = "figure_1_pass_rate.png"
FIGURE_2 = "figure_2_failure_counts.png"


# Create the pass-rate figure.
def make_pass_rate_figure():
    models = ["gpt-oss-20b", "gpt-oss-120b"]
    rates = [25, 50]
    colors = ["#4F81BD", "#9BBB59"]

    plt.figure(figsize=(6.5, 3.8))
    bars = plt.bar(models, rates, color=colors)
    plt.ylim(0, 100)
    plt.ylabel("Pass rate (%)")
    plt.title("Pass rate by model (n=8)")
    plt.grid(axis="y", alpha=0.25)
    for bar, rate in zip(bars, rates):
        plt.text(bar.get_x() + bar.get_width() / 2, rate + 2, f"{rate}%", ha="center")
    plt.tight_layout()
    plt.savefig(FIGURE_1, dpi=180)
    plt.close()


# Create the failed-check breakdown figure.
def make_failure_figure():
    checks = ["globex_ok", "monitoring_ok", "no_acme_duplicate", "no_checklist_duplicate"]
    target = [5, 0, 1, 0]
    stronger = [4, 0, 0, 0]
    positions = range(len(checks))
    width = 0.36

    plt.figure(figsize=(7.4, 4.0))
    plt.bar([p - width / 2 for p in positions], target, width=width, label="gpt-oss-20b", color="#4F81BD")
    plt.bar([p + width / 2 for p in positions], stronger, width=width, label="gpt-oss-120b", color="#9BBB59")
    plt.xticks(list(positions), checks, rotation=20, ha="right")
    plt.ylim(0, 8)
    plt.ylabel("Failed runs")
    plt.title("Failures by check (out of 8)")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIGURE_2, dpi=180)
    plt.close()


# Apply a restrained business-report style.
def set_styles(document):
    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10.5)

    for style_name, size, color in [
        ("Heading 1", 16, "1F4E79"),
        ("Heading 2", 12.5, "1F4E79"),
        ("Heading 3", 11, "404040"),
    ]:
        style = styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)


# Add a paragraph with optional bold lead text.
def add_paragraph(document, text, lead=None):
    paragraph = document.add_paragraph()
    if lead:
        run = paragraph.add_run(lead)
        run.bold = True
    paragraph.add_run(text)
    paragraph.paragraph_format.space_after = Pt(7)
    paragraph.paragraph_format.line_spacing = 1.08
    return paragraph


# Add a short bullet item.
def add_bullet(document, text):
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.add_run(text)
    paragraph.paragraph_format.space_after = Pt(4)
    return paragraph


# Add an image with a compact caption.
def add_figure(document, path, caption, width=6.2):
    document.add_picture(path, width=Inches(width))
    last = document.paragraphs[-1]
    last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph = document.add_paragraph(caption)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(12)
    run = paragraph.runs[0]
    run.italic = True
    run.font.size = Pt(9)


# Build the client update section.
def add_client_update(document):
    document.add_heading("Document 1: Client Update", level=1)
    add_paragraph(
        document,
        "We built a minimal, self-contained RL environment for evaluating LLM agents on knowledge-work tasks. "
        "The environment runs locally and exposes two in-memory services as function-calling tools: a Slack-like messaging service and a task manager.",
    )
    add_paragraph(
        document,
        "The seeded workspace has three channels (#general, #incidents, #leads), four users (alice, ben, carla, devon), "
        "and two pre-existing tasks: Update launch checklist assigned to ben and Send Acme pricing assigned to carla.",
    )
    add_paragraph(
        document,
        "The task, Commitments Tracking, asks the agent to review the workspace and make sure every commitment is tracked. "
        "A correct run creates a Globex security-questionnaire task assigned to alice, creates a billing-API-monitoring follow-up assigned to devon, "
        "does not duplicate the existing Acme or launch-checklist tasks, and ignores informational chatter.",
    )

    document.add_heading("Design decisions", level=2)
    add_paragraph(
        document,
        "The verifier combines deterministic state checks with a small trajectory check. The deterministic checks confirm the two required tasks, "
        "the correct owners, actionable statuses, and no duplicates. The trajectory check confirms the agent read the workspace and checked the board.",
    )
    add_paragraph(
        document,
        "This design keeps the reward objective and reproducible while reducing the chance that an agent passes by guessing. "
        "We deliberately avoided LLM-as-judge because the success criteria are objective; a judge would add nondeterminism and another surface to game.",
    )
    add_paragraph(
        document,
        "Calibration mattered. The first version, with one commitment plus deduplication, produced about 88% pass rates for both models and was saturated. "
        "The second version, with two commitments across channels, produced 0% for both and was too hard. The final version removed an ambiguous decoy and "
        "nudged the instruction to read each channel directly and check the board before finishing.",
    )
    add_paragraph(
        document,
        "We targeted a weak open-source model because making a small local eval difficult for frontier models is resource-intensive. "
        "The comparison model is stronger but close enough to keep the study focused on task behavior rather than model family differences.",
    )

    document.add_heading("Results", level=2)
    add_paragraph(
        document,
        "In the final calibration, with n=8 per model, gpt-oss-20b passed 2 of 8 runs (25%). "
        "gpt-oss-120b passed 4 of 8 runs (50%). The eval discriminates between the two models while still leaving room for failure analysis.",
    )
    add_figure(document, FIGURE_1, "Figure 1. Pass rate by model, n=8.")

    document.add_heading("Limitations", level=2)
    add_bullet(document, "The eval covers one task in one small synthetic workspace.")
    add_bullet(document, "The two models are close in capability, so the separation is useful but modest.")
    add_bullet(document, "The verifier uses keyword matching that is adequate for this controlled task but would need hardening at scale.")


# Build the loss-analysis memo section.
def add_loss_analysis(document):
    document.add_page_break()
    document.add_heading("Document 2: Loss Analysis Memo", level=1)
    add_paragraph(document, "To: Research team")
    add_paragraph(document, "Subject: Why the Commitments Tracking eval failed and what it measures")

    document.add_heading("Task and setup", level=2)
    add_paragraph(
        document,
        "This eval probes whether an agent can infer workplace commitments from ordinary messages, attribute ownership, and update a task board without duplication. "
        "The target model is gpt-oss-20b, compared with gpt-oss-120b. Each model ran 8 trials under the same seeded workspace and hybrid verifier.",
    )
    add_paragraph(
        document,
        "The required end state is concrete: a Globex questionnaire task assigned to alice, a billing API monitoring task assigned to devon, "
        "one Acme task, and one launch-checklist task. The trajectory also has to show that the agent read the workspace and checked existing tasks.",
    )

    document.add_heading("Finding 1: explicit requests were easy; implicit commitments were not", level=2)
    add_paragraph(
        document,
        "Both models created the monitoring follow-up on all 8 runs. That item was phrased as an explicit request: "
        "create a follow-up task to set up monitoring for the billing API. The Globex item was different. It required connecting "
        "a customer request with Alice's later offer to take the questionnaire.",
    )
    add_paragraph(
        document,
        "The dominant failure was globex_ok: 5 failed checks for gpt-oss-20b and 4 for gpt-oss-120b. "
        "The gap is not basic instruction execution. It is implicit-commitment inference and attribution.",
    )

    document.add_heading("Finding 2: models declared completion before proving it", level=2)
    add_paragraph(
        document,
        "Several failing trajectories ended with confident closure such as no additional commitments identified or the board is up to date. "
        "Those statements were wrong because the Globex commitment remained untracked. The failure mode matters because it looks operationally clean "
        "while leaving work behind.",
    )

    document.add_heading("Finding 3: search behavior shaped outcomes", level=2)
    add_paragraph(
        document,
        "The weaker model often searched for literal terms such as I will or commit instead of reading channels directly. "
        "Because search only returns substring matches, it missed commitments phrased outside those queries and did not recover by reading the channel history. "
        "The stronger model read channels directly more often, which explains part of its higher pass rate.",
    )
    add_figure(document, FIGURE_2, "Figure 2. Failed verifier checks by model, out of 8 runs.")

    document.add_heading("Why this eval matters", level=2)
    add_paragraph(
        document,
        "Explicit instruction-following is already near saturation for this task family. The harder capability is recognizing that a message pair creates an obligation, "
        "assigning that obligation to the right person, and reconciling it with the existing board. This eval isolates that capability with a small, reproducible setup.",
    )


# Generate the figures and Word document.
def main():
    make_pass_rate_figure()
    make_failure_figure()

    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)
    set_styles(document)

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Apollo Knowledge-Work RL Eval Write-Up")
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(18)
    run.font.color.rgb = RGBColor(31, 78, 121)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("Client update and loss analysis memo").italic = True

    add_client_update(document)
    add_loss_analysis(document)
    document.save(OUTPUT_DOCX)


# Run the document generator when called as a script.
if __name__ == "__main__":
    main()
