"""Generate platform-owned, text-only canonical repair patches."""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class CanonicalPatchError(ValueError):
    """The candidate worktree cannot be represented as an allowed text patch."""


@dataclass(frozen=True)
class CanonicalPatch:
    text: str
    changed_paths: tuple[str, ...]

    @property
    def size_bytes(self) -> int:
        return len(self.text.encode("utf-8"))


def _files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise CanonicalPatchError("patch source must be a directory")
    found: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in {".git", "__pycache__"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise CanonicalPatchError(
                f"symbolic links are not supported: {relative.as_posix()}"
            )
        if path.is_file():
            found[relative.as_posix()] = path
        elif not path.is_dir():
            raise CanonicalPatchError(
                f"unsupported filesystem entry: {relative.as_posix()}"
            )
    return found


def _decode(path: Path | None) -> list[str]:
    if path is None:
        return []
    content = path.read_bytes()
    if b"\0" in content:
        raise CanonicalPatchError(
            f"binary changes are not supported: {path.name}"
        )
    try:
        return content.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError as error:
        raise CanonicalPatchError(
            f"changed file is not UTF-8 text: {path.name}"
        ) from error


def generate_canonical_patch(
    original: Path,
    modified: Path,
    *,
    allowed_prefixes: tuple[str, ...] = ("input/",),
) -> CanonicalPatch:
    """Return the canonical diff between two Case trees.

    The platform owns this operation. Agent-provided patch files are ignored;
    only the resulting worktree is compared with the clean Case snapshot.
    """

    if not allowed_prefixes or any(
        not prefix or prefix.startswith("/") or not prefix.endswith("/")
        for prefix in allowed_prefixes
    ):
        raise CanonicalPatchError("allowed prefixes are invalid")

    original_files = _files(original)
    modified_files = _files(modified)
    paths = sorted(original_files.keys() | modified_files.keys())
    sections: list[str] = []
    changed: list[str] = []

    for relative in paths:
        old_path = original_files.get(relative)
        new_path = modified_files.get(relative)
        old_bytes = old_path.read_bytes() if old_path else b""
        new_bytes = new_path.read_bytes() if new_path else b""
        if old_bytes == new_bytes:
            continue

        normalized = PurePosixPath(relative).as_posix()
        if normalized != relative or not any(
            relative.startswith(prefix) for prefix in allowed_prefixes
        ):
            raise CanonicalPatchError(
                f"change is outside allowed paths: {relative}"
            )

        changed.append(relative)
        sections.append(f"diff --git a/{relative} b/{relative}\n")
        sections.extend(
            difflib.unified_diff(
                _decode(old_path),
                _decode(new_path),
                fromfile=f"a/{relative}" if old_path else "/dev/null",
                tofile=f"b/{relative}" if new_path else "/dev/null",
                lineterm="\n",
            )
        )

    if not changed:
        raise CanonicalPatchError("Agent made no allowed textual change")
    return CanonicalPatch("".join(sections), tuple(changed))


def write_canonical_patch(path: Path, patch: CanonicalPatch) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(patch.text)
    temporary.replace(path)
    return path
