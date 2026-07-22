from components.carbon_ui import render_feedback


def render_empty(title: str, detail: str) -> None:
    render_feedback(title, detail, key=f"empty-{title.lower().replace(' ', '-')}")


def render_provisional_note(text: str) -> None:
    render_feedback(
        "Prototype logic",
        f"{text} Pending PM/Data Engineer validation.",
        kind="warning",
        key=f"prototype-{text[:24].lower().replace(' ', '-')}",
    )
