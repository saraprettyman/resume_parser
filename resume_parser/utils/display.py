"""
utils/display.py

Provides rich console output utilities for displaying different sections
of extracted resume data (contact info, skills, experience, education, etc.).
Uses `rich` to produce nicely formatted tables and panels.
"""
from typing import Optional
from venv import logger
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.console import Console

# Global console for printing
console = Console()


class Display:
    """
    Handles all display logic for parsed resume sections.
    Each method takes parsed data and renders it in a user-friendly format.
    """

    # ------------------------
    # Generic Section Display
    # ------------------------
    def display_section_text(self, title: str, text: str):
        """
        Displays a text block inside a titled panel.

        Args:
            title (str): Title for the panel.
            text (str): Body text. If empty, shows a "No content found" message.
        """
        panel = Panel(
            Align.left(text or "[dim]No content found[/dim]"),
            title=title,
            expand=True
        )
        console.print(panel)

    # ------------------------
    # Contact Information
    # ------------------------
    def display_contact(self, contact: dict):
        """
        Displays contact details (name, email, phone, LinkedIn, GitHub, etc.) in a table.

        Args:
            contact (dict): Dictionary of contact fields.
            full_text (str, optional): Not currently used for display but could be logged.
        """
        table = Table(
            show_header=False,
            box=None,
            expand=True,
            padding=(0, 1)
        )

        # Table columns: icon | label | value
        table.add_column("Icon", width=2, no_wrap=True)
        table.add_column("Field", style="bold cyan", width=15, no_wrap=True)
        table.add_column("Value", style="white", overflow="fold")

        def safe_value(key: str) -> str:
            """Safely retrieve and strip a field from `contact`."""
            return (contact.get(key, "") or "").strip()

        def make_link(url: Optional[str], label: Optional[str] = None, max_len: int = 40) -> str:
            """Formats clickable links for terminals supporting OSC 8 hyperlinks."""
            if not url or not url.strip():
                return ""
            display_text = label or url
            if len(display_text) > max_len:
                display_text = display_text[:max_len - 1] + "…"
            return f"\033]8;;{url}\033\\{display_text}\033]8;;\033\\"

        # Contact rows
        table.add_row("👤", "Name", safe_value("name"))

        email_val = safe_value("email")
        table.add_row("✉️", "Email",
                      make_link(f"mailto:{email_val}",
                                email_val)
                                if email_val
                                else ""
                                )

        phone_val = safe_value("phone")
        table.add_row("📞", "Phone",
                      make_link(f"tel:{phone_val}",
                                phone_val)
                                if phone_val
                                else ""
                                )

        table.add_row("🔗", "LinkedIn",
                      make_link(safe_value("linkedin"))
                      if safe_value("linkedin")
                      else ""
                      )
        table.add_row("💻", "GitHub",
                      make_link(safe_value("github"))
                      if safe_value("github")
                      else ""
                      )

        additional_urls = contact.get("additional_urls", []) or []
        if additional_urls:
            joined_links = "\n".join(make_link(u) for u in additional_urls)
            table.add_row("🌐", "Additional URLs", joined_links)

        console.print(table)

    # ------------------------
    # Skills
    # ------------------------
    def display_skills_table(self, extracted: dict, title: Optional[str] = None):
        """
        Displays skills categorized into found/missing.

        Args:
            extracted (dict): {
                "CategoryName": {"found": [...], "missing": [...]}, ...
            }
            title (str, optional): Table title.
        """
        table = Table(
            title=title,
            show_lines=True,
            expand=True,
            width=console.width
        )
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Skills", style="white")

        for category, data in extracted.items():
            found_str = ", ".join(f"[green]{s}[/green]" for s in data.get("found", [])) \
                if data.get("found") else "[dim]None[/dim]"
            missing_str = ", ".join(f"[dim]{s}[/dim]" for s in data.get("missing", [])) \
                if data.get("missing") else ""
            combined = found_str + (f"  |  {missing_str}" if missing_str else "")
            table.add_row(category, combined.strip())

        console.print(table)

    # ------------------------
    # Experience
    # ------------------------
    def display_experience(self, exp_res: dict):
        """
        Displays work experience in a table.

        Args:
            exp_res (dict or list): Either:
                {"items": [...], "section": "..."} or just a list of experience items.
        """
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

        table = Table(
            title="Experience",
            show_lines=True,
            expand=True,
            width=console.width
        )
        table.add_column("Job Title", style="bold cyan")
        table.add_column("Company", style="cyan")
        table.add_column("Start Date", style="white")
        table.add_column("End Date", style="white")
        table.add_column("Details", style="white")

        for it in items:
            if not isinstance(it, dict):
                continue

            # Merge bullets into details
            bullets = it.get("Bullets", [])
            details = "\n".join(
                b if b.strip().startswith("•") else f"• {b}"
                for b in bullets
            ) if bullets else it.get("Details", "")

            table.add_row(
                it.get("Job Title", ""),
                it.get("Company", ""),
                it.get("Start Date", ""),
                it.get("End Date", ""),
                details
            )

        console.print(table)

    # ------------------------
    # Education
    # ------------------------
    def display_education(self, education_res, show_gpa: bool = True):
        """
        Displays education details in a table, falling back to raw section text if parsing fails.

        Args:
            education_res (dict or list): Either:
                {"section": "...", "items": [ {...}, ... ] }
                or a plain list [ {...}, ... ]
            show_gpa (bool): Whether to show the GPA column.
        """
        if isinstance(education_res, dict):
            items = education_res.get("items", []) or []
            raw_section = education_res.get("section", "")
        elif isinstance(education_res, list):
            items = education_res
            raw_section = ""
        else:
            items = []
            raw_section = str(education_res)

        if not items:
            panel = Panel(
                Align.left(raw_section or "[dim]No education found[/dim]"),
                title="Education",
                expand=True
            )
            console.print(panel)
            return

        table = Table(
            title="Education",
            show_lines=True,
            expand=True,
            width=console.width
        )
        table.add_column("Institution | Location")
        table.add_column("Graduation Date", no_wrap=True)
        table.add_column("Degree & Emphasis", style="cyan")
        if show_gpa:
            table.add_column("GPA", style="blue", justify="center", no_wrap=True)
        table.add_column("Minors", style="white")
        table.add_column("Details", style="white")

        def safe_get(entry, key: str) -> str:
            """Safely extract a string value from a dict entry."""
            if isinstance(entry, dict):
                v = entry.get(key, "")
                return str(v).strip() if v is not None else ""
            return str(entry).strip()

        for edu in items:
            try:
                inst = safe_get(edu, "Institution")
                loc = safe_get(edu, "Location")
                inst_loc = f"{inst} | {loc}" if inst and loc else inst or loc or ""

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

            except (ValueError, TypeError, RuntimeError) as exc:  # noqa: B902
                logger.exception("Education panel rendering failed: %s", exc)
                panel = Panel(
                    Align.left(raw_section or "[dim]No education found[/dim]"),
                    title="Education",
                    expand=True
                )
                console.print(panel)
                return


        console.print(table)
