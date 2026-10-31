"""Unit metadata contracts for django-ingredients template (U1–U2, T1)."""

from __future__ import annotations

import ingredients as pkg


def test_title_placeholder_preserved():
    assert pkg.__title__ == "ingredients"


def test_version_contract():
    assert pkg.__version__
    assert pkg.__version__.count(".") >= 2
    assert pkg.__version_info__ == pkg.VERSION
    parts = pkg.__version__.split(".")
    assert len(pkg.VERSION) == len(parts)
    for raw, parsed in zip(parts, pkg.VERSION, strict=True):
        if raw.isdigit():
            assert parsed == int(raw)


def test_license_author_copyright():
    assert pkg.__license__ == "MIT"
    assert pkg.__author__ == "DLRSP"
    assert "DLRSP" in pkg.__copyright__


def test_http_and_iso_constants():
    """U2: clone-facing constants stay stable."""
    assert pkg.HTTP_HEADER_ENCODING == "iso-8859-1"
    assert pkg.ISO_8601 == "iso-8601"
