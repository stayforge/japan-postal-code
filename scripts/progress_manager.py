"""Progress bar manager for stable multi-line progress display."""

import os
import sys
from typing import Optional

try:
    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeRemainingColumn,
        FileSizeColumn,
    )
    from rich.console import Console
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from rich.progress import TaskID
    else:
        TaskID = int  # Runtime type hint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    TaskID = int

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


def _is_ci_environment() -> bool:
    """Detect if running in CI environment (GitHub Actions, GitLab CI, etc.)."""
    ci_indicators = [
        'CI',  # Generic CI flag
        'GITHUB_ACTIONS',  # GitHub Actions
        'GITLAB_CI',  # GitLab CI
        'JENKINS_URL',  # Jenkins
        'TRAVIS',  # Travis CI
        'CIRCLECI',  # CircleCI
    ]
    return any(os.environ.get(key) for key in ci_indicators)


def _should_use_simple_output() -> bool:
    """Determine if we should use simple output instead of rich progress bars."""
    # Use simple output in CI environments or if not a terminal
    if _is_ci_environment():
        return True
    
    # Check if stdout is a terminal
    if not sys.stdout.isatty():
        return True
    
    return False


class ProgressManager:
    """Manages multiple progress bars in a stable multi-line display."""
    
    def __init__(self):
        self.rich_progress: Optional[Progress] = None
        self.console: Optional[Console] = None
        self.tasks: dict[str, TaskID] = {}
        self.simple_mode: bool = False
        self.task_status: dict[str, dict] = {}  # For simple mode: {name: {completed: int, total: int}}
        
        use_simple = _should_use_simple_output()
        
        if RICH_AVAILABLE and not use_simple:
            # Use rich in normal terminals
            self.console = Console(force_terminal=False)  # Let rich auto-detect
            if self.console.is_terminal:
                self.rich_progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TextColumn("({task.completed}/{task.total})"),
                    TimeRemainingColumn(),
                    console=self.console,
                    transient=False,  # Keep progress bars visible
                )
                self.rich_progress.start()
            else:
                # Terminal doesn't support rich, use simple mode
                self.simple_mode = True
        else:
            # Use simple mode in CI or if rich not available
            self.simple_mode = True
    
    def add_task(self, name: str, total: int, show_bytes: bool = False) -> Optional[TaskID]:
        """Add a new progress task.
        
        Args:
            name: Task name
            total: Total number of items/bytes
            show_bytes: If True, show file size column (for downloads)
        """
        if self.simple_mode:
            # Simple mode: just track status
            self.task_status[name] = {'completed': 0, 'total': total}
            if _is_ci_environment():
                # In CI, print initial status
                print(f"[{name}] Starting... (0/{total})")
            return None
        
        if self.rich_progress:
            task_id = self.rich_progress.add_task(
                f"[cyan]{name}[/cyan]",
                total=total
            )
            self.tasks[name] = task_id
            return task_id
        return None
    
    def update(self, name: str, advance: int = 1):
        """Update progress for a task."""
        if self.simple_mode:
            if name in self.task_status:
                self.task_status[name]['completed'] += advance
                completed = self.task_status[name]['completed']
                total = self.task_status[name]['total']
                
                # In CI, print progress every 10% or when complete
                if _is_ci_environment():
                    percentage = (completed / total * 100) if total > 0 else 0
                    # Print at milestones (0%, 10%, 20%, ..., 100%)
                    if completed == 0 or completed == total or (completed % max(1, total // 10) == 0):
                        print(f"[{name}] {percentage:.0f}% ({completed}/{total})")
                return
        
        if self.rich_progress and name in self.tasks:
            self.rich_progress.update(self.tasks[name], advance=advance)
    
    def close(self):
        """Close all progress bars."""
        if self.simple_mode:
            # In CI, print completion status
            if _is_ci_environment():
                for name, status in self.task_status.items():
                    if status['completed'] == status['total']:
                        print(f"[{name}] Completed ({status['completed']}/{status['total']})")
            return
        
        if self.rich_progress:
            self.rich_progress.stop()
            self.rich_progress = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Global progress manager instance
_global_progress_manager: Optional[ProgressManager] = None


def get_progress_manager() -> Optional[ProgressManager]:
    """Get or create the global progress manager."""
    global _global_progress_manager
    if _global_progress_manager is None:
        # Always create progress manager, even if rich is not available (will use simple mode)
        _global_progress_manager = ProgressManager()
    return _global_progress_manager


def reset_progress_manager():
    """Reset the global progress manager (useful for testing)."""
    global _global_progress_manager
    if _global_progress_manager:
        _global_progress_manager.close()
    _global_progress_manager = None

