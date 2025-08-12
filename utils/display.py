from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text
from rich import box

console = Console()

class Display:
    def display_section_text(self, title: str, text: str):
        panel = Panel(Align.left(text or "[dim]No content found[/dim]"), title=title, expand=True)
        console.print(panel)

    def display_contact(self, contact: dict, full_text: str = ""):
        table = Table(
            show_header=False,
            box=None,         # no borders
            expand=True,
            padding=(0, 1)    # vertical / horizontal padding
        )

        # Three columns: icon | label | value
        table.add_column("Icon", width=2, no_wrap=True)
        table.add_column("Field", style="bold cyan", width=15, no_wrap=True)
        table.add_column("Value", style="white", overflow="fold")

        def safe_value(key):
            return (contact.get(key, "") or "").strip()

        def make_link(url, label=None, max_len=40):
            if not url or not url.strip():
                return ""
            display_text = label or url
            if len(display_text) > max_len:
                display_text = display_text[:max_len - 1] + "…"
            return f"\033]8;;{url}\033\\{display_text}\033]8;;\033\\"

        # Contact rows
        table.add_row("👤", "Name", safe_value("name"))

        email_val = safe_value("email")
        table.add_row("✉️", "Email", make_link(f"mailto:{email_val}", email_val) if email_val else "")

        phone_val = safe_value("phone")
        table.add_row("📞", "Phone", make_link(f"tel:{phone_val}", phone_val) if phone_val else "")

        table.add_row("🔗", "LinkedIn", make_link(safe_value("linkedin")) if safe_value("linkedin") else "")
        table.add_row("💻", "GitHub", make_link(safe_value("github")) if safe_value("github") else "")

        additional_urls = contact.get("additional_urls", []) or []
        if additional_urls:
            joined_links = "\n".join(make_link(u) for u in additional_urls)
            table.add_row("🌐", "Additional URLs", joined_links)

        console.print(table)


    def display_skills_table(self, extracted: dict, title=None):
        table = Table(title=title, show_lines=True, expand=True, width=console.width)
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Skills", style="white")

        for category, data in extracted.items():
            found_str = ", ".join(f"[green]{s}[/green]" for s in data.get("found", [])) if data.get("found") else ""
            missing_str = ", ".join(f"[dim]{s}[/dim]" for s in data.get("missing", [])) if data.get("missing") else ""
            combined = (found_str + (f"  |  {missing_str}" if missing_str else "")).strip()
            table.add_row(category, combined)
        console.print(table)

    def display_experience(self, exp_res: dict):
        items = exp_res.get("items", []) if isinstance(exp_res, dict) else (exp_res or [])
        if not items:
            panel = Panel(
                Align.left(
                    exp_res.get("section", "[dim]No experience found[/dim]")
                    if isinstance(exp_res, dict)
                    else "[dim]No experience found[/dim]"
                ),
                title="Experience",
                expand=True
            )
            console.print(panel)
            return

        table = Table(title="Experience", show_lines=True, expand=True, width=console.width)
        table.add_column("Job Title", style="bold cyan")
        table.add_column("Company", style="cyan")
        table.add_column("Start Date", style="white")
        table.add_column("End Date", style="white")
        table.add_column("Details", style="white")

        for it in items:
            if not isinstance(it, dict):
                continue  # skip invalid entries

            # Merge bullets into details safely
            bullets = it.get("Bullets", [])
            if bullets:
                details = "\n".join(
                    b if b.strip().startswith("•") else f"• {b}"
                    for b in bullets
                )
            else:
                details = it.get("Details", "")

            table.add_row(
                it.get("Job Title", ""),
                it.get("Company", ""),
                it.get("Start Date", ""),
                it.get("End Date", ""),
                details
            )

        console.print(table)

    def display_education(self, education_res, show_gpa=True):
        """
        Accepts either:
        - a dict like {"section": "...", "items": [ {...}, ... ] }
        - or a plain list [ {...}, ... ]
        Displays a table with Institution | Location, Graduation Date, Degree & Emphasis, GPA, Minors, Details.
        Missing fields are left blank (no placeholder).
        """

        # normalize to items list and raw section for fallback
        if isinstance(education_res, dict):
            items = education_res.get("items", []) or []
            raw_section = education_res.get("section", "")
        elif isinstance(education_res, list):
            items = education_res
            raw_section = ""
        else:
            # unexpected shape: show it raw
            items = []
            raw_section = str(education_res)

        if not items:
            panel = Panel(Align.left(raw_section or "[dim]No education found[/dim]"), title="Education", expand=True)
            console.print(panel)
            return

        table = Table(title="Education", show_lines=True, expand=True, width=console.width)
        # Institution | Location as the first column
        table.add_column("Institution | Location")
        table.add_column("Graduation Date", no_wrap=True)
        table.add_column("Degree & Emphasis", style="cyan")
        if show_gpa:
            table.add_column("GPA", style="blue", justify="center", no_wrap=True)
        table.add_column("Minors", style="white")
        table.add_column("Details", style="white")

        def safe_get(entry, key):
            # Return a plain string (empty if missing). Accept dicts or other types gracefully.
            if isinstance(entry, dict):
                v = entry.get(key, "")
                return (str(v).strip() if v is not None else "")
            return str(entry).strip()

        # add rows; guard against mismatched shapes
        for edu in items:
            try:
                # institution + location
                inst = safe_get(edu, "Institution")
                loc = safe_get(edu, "Location")
                if inst and loc:
                    inst_loc = f"{inst} | {loc}"
                else:
                    inst_loc = inst or loc or ""

                row = [
                    inst_loc,
                    safe_get(edu, "Graduation Date"),
                    safe_get(edu, "Degree & Emphasis"),
                ]
                if show_gpa:
                    row.append(safe_get(edu, "GPA"))
                row.extend([
                    safe_get(edu, "Minors"),
                    safe_get(edu, "Details"),
                ])

                table.add_row(*row)
            except Exception:
                # defensive: if anything goes wrong for a row, print the raw section instead of failing
                panel = Panel(Align.left(raw_section or "[dim]No education found[/dim]"), title="Education", expand=True)
                console.print(panel)
                return

        console.print(table)
