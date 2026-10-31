"""Package import smoke tests."""

import ingredients as pkg


def test_import_package():
    assert pkg.__title__ == "ingredients"


def test_version_is_semver_like():
    assert pkg.__version__
    assert pkg.__version__.count(".") >= 2
    assert pkg.VERSION == pkg.__version_info__
