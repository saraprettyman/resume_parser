# utils/display.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

console = Console()

class Display:
    def display_section_text(self, title: str, text: str):
        panel = Panel(Align.left(text or "[dim]No content found[/dim]"), title=title, expand=True)
        console.print(panel)

    def display_contact(self, contact: dict):
        table = Table(title="Contact")
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white", overflow="fold")
        table.add_row("Email", contact.get("email", ""))
        table.add_row("Phone", contact.get("phone", ""))
        table.add_row("LinkedIn", contact.get("linkedin", ""))
        table.add_row("GitHub", contact.get("github", ""))
        console.print(table)

    def display_skills_table(self, extracted: dict, title=None, score=None):
        table = Table(title=title, show_lines=True, expand=True)
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Skills", style="white")
        for category, data in extracted.items():
            found_str = ", ".join(f"[green]{s}[/green]" for s in data["found"]) if data["found"] else "[dim]None[/dim]"
            missing_str = ", ".join(f"[dim]{s}[/dim]" for s in data["missing"]) if data["missing"] else ""
            combined = found_str + (f"  |  {missing_str}" if missing_str else "")
            table.add_row(category, combined)
        console.print(table)
        if score is not None:
            console.print(f"[bold]ATS Compatibility Score:[/bold] {score}%")

    def display_experience(self, exp_res: dict):
        items = exp_res.get("items", [])
        if not items:
            panel = Panel(Align.left(exp_res.get("section","[dim]No experience found[/dim]")), title="Experience", expand=True)
            console.print(panel)
            return
        table = Table(title="Experience", show_lines=True, expand=True)
        table.add_column("Job Title", style="bold cyan")
        table.add_column("Company", style="cyan")
        table.add_column("Start Date", style="white")
        table.add_column("End Date", style="white")
        table.add_column("Details", style="white")
        for it in items:
            details = ""
            if it.get("Bullets"):
                details = "\n".join(f"• {b}" for b in it["Bullets"])
            else:
                details = it.get("Details", "")
            table.add_row(it.get("Job Title",""), it.get("Company",""), it.get("Start Date",""), it.get("End Date",""), details)
        console.print(table)

    def display_education(self, edu_res: dict, show_gpa=False, show_degree=False):
        items = edu_res.get("items", [])
        if not items:
            panel = Panel(Align.left(edu_res.get("section","[dim]No education found[/dim]")), title="Education", expand=True)
            console.print(panel)
            return
        table = Table(title="Education", show_lines=True, expand=True)
        table.add_column("Institution", style="bold cyan")
        table.add_column("Graduation Date", style="white")
        if show_degree:
            table.add_column("Degree", style="cyan")
        if show_gpa:
            table.add_column("GPA", style="white")
        table.add_column("Details", style="white")
        for it in items:
            row = [it.get("Institution",""), it.get("Graduation Date","")]
            if show_degree:
                row.append(it.get("Degree",""))
            if show_gpa:
                row.append(it.get("GPA",""))
            details = "\n".join(f"• {b}" for b in it.get("Bullets",[])) if it.get("Bullets") else it.get("Details","")
            row.append(details)
            table.add_row(*row)
        console.print(table)
