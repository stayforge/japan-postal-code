"""Progress manager for traditional log output."""

import time
from typing import Optional, Dict


class ProgressManager:
    """Manages progress tracking with traditional log output."""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}  # {name: {completed: int, total: int, last_print: float, start_time: float}}
    
    def add_task(self, name: str, total: int, show_bytes: bool = False) -> Optional[int]:
        """Add a new progress task.
        
        Args:
            name: Task name
            total: Total number of items/bytes
            show_bytes: If True, show file size column (for downloads) - not used in simple mode
        """
        self.tasks[name] = {
            'completed': 0,
            'total': total,
            'last_print': 0.0,
            'start_time': time.time(),
            'last_milestone': -1
        }
        print(f"[{name}] Starting... (0/{total})")
        return None
    
    def update(self, name: str, advance: int = 1):
        """Update progress for a task with throttled output."""
        if name not in self.tasks:
            return
        
        task = self.tasks[name]
        task['completed'] += advance
        completed = task['completed']
        total = task['total']
        
        # Calculate percentage
        percentage = int((completed / total * 100)) if total > 0 else 0
        
        # Print at milestones: 10%, 20%, ..., 90%, 100%
        # Or every 5 seconds, whichever comes first
        current_time = time.time()
        should_print = False
        
        # Print at percentage milestones (every 10%, but skip 0%)
        milestone_percentage = (percentage // 10) * 10
        if milestone_percentage > 0 and milestone_percentage != task.get('last_milestone', -1):
            should_print = True
            task['last_milestone'] = milestone_percentage
        
        # Or print every 5 seconds (but not at the very start)
        elif completed > 0 and current_time - task['last_print'] >= 5.0:
            should_print = True
        
        # Always print at completion
        if completed >= total:
            should_print = True
        
        if should_print:
            elapsed = current_time - task['start_time']
            if completed > 0 and elapsed > 0:
                rate = completed / elapsed
                remaining = (total - completed) / rate if rate > 0 else 0
                print(f"[{name}] {percentage}% ({completed}/{total}) - {rate:.1f}/s - ETA: {remaining:.0f}s")
            else:
                print(f"[{name}] {percentage}% ({completed}/{total})")
            task['last_print'] = current_time
    
    def close(self):
        """Close all progress tracking."""
        # Print final status for all tasks
        for name, task in self.tasks.items():
            if task['completed'] == task['total']:
                elapsed = time.time() - task['start_time']
                print(f"[{name}] Completed ({task['completed']}/{task['total']}) in {elapsed:.1f}s")
        self.tasks.clear()
    
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
        _global_progress_manager = ProgressManager()
    return _global_progress_manager


def reset_progress_manager():
    """Reset the global progress manager (useful for testing)."""
    global _global_progress_manager
    if _global_progress_manager:
        _global_progress_manager.close()
    _global_progress_manager = None

