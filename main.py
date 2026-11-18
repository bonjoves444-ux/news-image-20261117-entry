"""Deliver the front page for Tuesday 17 November 2026.

The artwork is a finished broadsheet that lives next to this file as
entry.png. This program does one small job: it puts a copy of that page
where the grading harness looks for it.

Nothing here draws, downloads, or renders anything. The image was laid
out ahead of time and is shipped in the repository, so the only work left
at run time is a plain file copy. That keeps the program runnable in a
bare container with nothing installed beyond the standard library.

The output folder is created when it is missing and left alone otherwise:
the harness owns that directory, so this program never removes it and
never clears anything inside it.
"""

import os
import shutil


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    destination = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, destination)


if __name__ == "__main__":
    main()
