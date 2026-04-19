#!/usr/bin/env python3
"""
Neocat (ncat) - A simple CLI text viewer with vim-like navigation.
"""

import curses
import sys
from pathlib import Path


class NeocatViewer:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.lines = []
        self.scroll_pos = 0
        self.cursor_y = 0
        self.last_scroll_pos = -1  # Track last position to avoid unnecessary redraws
        
        self._load_file()
    
    def _load_file(self):
        """Load the file content into memory."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.lines = f.read().splitlines()
        except FileNotFoundError:
            print(f"ncat: {self.filepath}: No such file or directory")
            sys.exit(1)
        except IsADirectoryError:
            print(f"ncat: {self.filepath}: Is a directory")
            sys.exit(1)
        except PermissionError:
            print(f"ncat: {self.filepath}: Permission denied")
            sys.exit(1)
        except Exception as e:
            print(f"ncat: {self.filepath}: {e}")
            sys.exit(1)
        
        if not self.lines:
            self.lines = ["(empty file)"]
    
    def _get_visible_lines(self, height):
        """Get the lines that should be visible on screen."""
        return self.lines[self.scroll_pos:self.scroll_pos + height]
    
    def _draw_screen(self, stdscr):
        """Draw the entire screen."""
        try:
            height, width = stdscr.getmaxyx()
            
            # Only redraw if scroll position changed
            if self.last_scroll_pos == self.scroll_pos:
                return
            
            self.last_scroll_pos = self.scroll_pos
            
            stdscr.erase()  # Erase instead of clear for less flicker
            
            visible_lines = self._get_visible_lines(height - 1)
            
            for i, line in enumerate(visible_lines):
                # Truncate line to fit width
                display_line = line[:width - 1] if len(line) >= width - 1 else line
                try:
                    stdscr.addstr(i, 0, display_line, curses.color_pair(2))
                except curses.error:
                    pass
            
            # Draw status bar at the bottom
            self._draw_status_bar(stdscr, height, width)
            
            stdscr.refresh()
        except curses.error:
            pass
    
    def _draw_status_bar(self, stdscr, height, width):
        """Draw the status bar showing file info."""
        try:
            total_lines = len(self.lines)
            current_line = self.scroll_pos + self.cursor_y + 1
            percentage = int((self.scroll_pos / max(1, total_lines - 1)) * 100) if total_lines > 1 else 100
            
            status = f"{self.filepath.name} | Lines: {total_lines} | {current_line}/{total_lines} ({percentage}%)"
            
            # Truncate status to fit within width
            status = status[:width - 1]
            
            # Draw status bar with inverse colors
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(height - 1, 0, status)
            
            # Fill remaining space with spaces
            remaining_space = width - len(status) - 1
            if remaining_space > 0:
                stdscr.addstr(height - 1, len(status), " " * remaining_space)
            
            stdscr.attroff(curses.color_pair(1))
        except curses.error:
            pass
    
    def _scroll_down(self, height):
        """Scroll down one line."""
        max_scroll = max(0, len(self.lines) - (height - 1))
        if self.scroll_pos < max_scroll:
            self.scroll_pos += 1
    
    def _scroll_up(self, height):
        """Scroll up one line."""
        if self.scroll_pos > 0:
            self.scroll_pos -= 1
    
    def _page_down(self, height):
        """Scroll down by page height."""
        max_scroll = max(0, len(self.lines) - (height - 1))
        self.scroll_pos = min(self.scroll_pos + (height - 2), max_scroll)
    
    def _page_up(self, height):
        """Scroll up by page height."""
        self.scroll_pos = max(0, self.scroll_pos - (height - 2))
    
    def _go_to_start(self):
        """Go to the start of the file."""
        self.scroll_pos = 0
    
    def _go_to_end(self, height):
        """Go to the end of the file."""
        max_scroll = max(0, len(self.lines) - (height - 1))
        self.scroll_pos = max_scroll
    
    def run(self, stdscr):
        """Main event loop."""
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(100)
        
        # Setup colors - pitch black background with white text
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Status bar
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Text
        
        # Set default background to black
        stdscr.bkgd(' ', curses.color_pair(2))
        
        while True:
            try:
                height, width = stdscr.getmaxyx()
                
                # Ensure minimum terminal size
                if height < 3 or width < 20:
                    continue
                
                self._draw_screen(stdscr)
            except curses.error:
                continue
            
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                break
            
            if key == -1:  # No input
                continue
            
            # Quit commands
            if key == ord('q') or key == ord('Q'):
                break
            
            # Vim-like navigation
            elif key == ord('j') or key == curses.KEY_DOWN:
                self._scroll_down(height)
            
            elif key == ord('k') or key == curses.KEY_UP:
                self._scroll_up(height)
            
            elif key == ord('d') or key == curses.KEY_NPAGE:  # Page down
                self._page_down(height)
            
            elif key == ord('u') or key == curses.KEY_PPAGE:  # Page up
                self._page_up(height)
            
            elif key == ord('g'):
                # Check for 'gg' (go to start)
                stdscr.timeout(500)
                next_key = stdscr.getch()
                stdscr.timeout(100)
                if next_key == ord('g'):
                    self._go_to_start()
            
            elif key == ord('G'):
                self._go_to_end(height)
            
            elif key == curses.KEY_HOME:
                self._go_to_start()
            
            elif key == curses.KEY_END:
                self._go_to_end(height)
    
    def display(self):
        """Display the file using curses."""
        try:
            curses.wrapper(self.run)
        except KeyboardInterrupt:
            pass


def main():
    if len(sys.argv) < 2:
        print("Usage: ncat <filepath>")
        print("\nControls:")
        print("  j / ↓       - Scroll down")
        print("  k / ↑       - Scroll up")
        print("  d / PgDn    - Page down")
        print("  u / PgUp    - Page up")
        print("  gg          - Go to start")
        print("  G           - Go to end")
        print("  Home        - Go to start")
        print("  End         - Go to end")
        print("  q           - Quit")
        sys.exit(1)
    
    filepath = sys.argv[1]
    viewer = NeocatViewer(filepath)
    viewer.display()


if __name__ == "__main__":
    main()
