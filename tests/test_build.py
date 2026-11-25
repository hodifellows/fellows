import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import add_fellow  # noqa: E402
import build  # noqa: E402

VALID = """\
github: test-fellow
name: Test Fellow
cohort: Cohort 1 (2027)
bio: Likes building small tools.
languages: [Python, C]
links:
  portfolio: https://example.com
consent: true
"""


def write(folder, name, text):
    path = folder / name
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_fellow_is_loaded(tmp_path):
    write(tmp_path, "test-fellow.yaml", VALID)
    [fellow] = build.load_fellows(tmp_path)
    assert fellow.name == "Test Fellow"
    assert fellow.languages == ["Python", "C"]
    assert fellow.links == {"portfolio": "https://example.com"}
    assert fellow.initials == "TF"


def test_files_starting_with_underscore_are_skipped(tmp_path):
    write(tmp_path, "_template.yaml", VALID)
    assert build.load_fellows(tmp_path) == []


def test_fellow_without_consent_is_not_shown(tmp_path):
    write(tmp_path, "test-fellow.yaml", VALID.replace("consent: true", "consent: false"))
    assert build.load_fellows(tmp_path) == []


def test_missing_required_field_is_reported(tmp_path):
    write(tmp_path, "test-fellow.yaml", VALID.replace("bio: Likes building small tools.\n", ""))
    with pytest.raises(build.FellowError, match="missing bio"):
        build.load_fellows(tmp_path)


@pytest.mark.parametrize("link", ["http://example.com", "javascript:alert(1)", "example.com"])
def test_links_must_be_https(tmp_path, link):
    write(tmp_path, "test-fellow.yaml", VALID.replace("https://example.com", link))
    with pytest.raises(build.FellowError, match="https://"):
        build.load_fellows(tmp_path)


def test_file_name_must_match_username(tmp_path):
    write(tmp_path, "someone-else.yaml", VALID)
    with pytest.raises(build.FellowError, match="test-fellow.yaml"):
        build.load_fellows(tmp_path)


def test_page_escapes_text_and_has_a_card_per_fellow(tmp_path):
    write(tmp_path, "test-fellow.yaml", VALID.replace("Likes building small tools.", "<script>x</script>"))
    html = build.render(build.load_fellows(tmp_path))
    assert "<script>x</script>" not in html
    assert 'id="card-test-fellow"' in html
    assert "first fellows join" in build.render([])


def test_build_writes_the_site(tmp_path):
    out = tmp_path / "site"
    build.build(out, [])
    assert (out / "index.html").is_file()
    assert (out / "static" / "styles.css").is_file()


def test_every_fellow_file_in_the_repo_is_valid():
    """Fails if any file in fellows/ has a mistake."""
    build.load_fellows()


def test_add_fellow_builds_an_entry_without_consent():
    entry = add_fellow.build_entry(
        {"login": "test-fellow", "name": "Test Fellow", "bio": "Hi", "blog": "https://example.com"},
        "test-fellow.jpg",
    )
    assert entry["consent"] is False
    assert entry["links"] == {"website": "https://example.com"}
