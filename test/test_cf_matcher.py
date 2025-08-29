import csv
from pathlib import Path
from types import SimpleNamespace

import pytest

from news_contribution_check.cf_matcher import CFMatcher, CFMatchCandidate
from news_contribution_check.config import AppConfig


class FakeClient:
    def __init__(self, decision_json: str):
        self._decision_json = decision_json

    class _Messages:
        def __init__(self, outer):
            self._outer = outer

        def create(self, **kwargs):
            return SimpleNamespace(content=[SimpleNamespace(text=self._outer._decision_json)])

    @property
    def messages(self):
        return self._Messages(self)


def _write_company_csv(path: Path, names):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Company/Organization Name"])
        for n in names:
            writer.writerow([n])


def _write_cf_csv(path: Path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Contributor Name", "Contributor Employer"])
        for name, emp in rows:
            writer.writerow([name, emp])


@pytest.fixture()
def tmp_config(tmp_path: Path):
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "output"
    data_dir.mkdir()
    out_dir.mkdir()
    cfg = AppConfig()
    # Point config to temp dirs
    cfg.processing.data_directory = str(data_dir)
    cfg.processing.output_directory = str(out_dir)
    return cfg


def test_cf_matcher_accept_via_llm(monkeypatch, tmp_config: AppConfig, tmp_path: Path):
    company_csv = tmp_path / "company.csv"
    cf_csv = Path(tmp_config.data_directory) / "cf.csv"
    _write_company_csv(company_csv, ["Acme Widgets"])
    _write_cf_csv(cf_csv, [("Acme Widgets LLC", "Other")])

    matcher = CFMatcher(api_key="test-key", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))

    # Monkeypatch shortlist to return a candidate referencing index 0
    monkeypatch.setattr(
        matcher,
        "_shortlist_candidates",
        lambda norm, names, emps, top_k: [CFMatchCandidate(index=0, contributor_name=names[0], contributor_employer=emps[0], name_score=85, employer_score=20)],
    )
    # Force LLM decision to MATCH index 1
    matcher._client = FakeClient('{"decision":"MATCH","index":1,"reason":"Distinctive tokens align"}')

    report = matcher.compare(company_csv=company_csv, cf_csv_filename="cf.csv")
    content = report.read_text(encoding="utf-8")
    assert "ACCEPT" in content
    assert "Acme Widgets" in content


def test_cf_matcher_suppresses_llm_no_match(monkeypatch, tmp_config: AppConfig, tmp_path: Path):
    company_csv = tmp_path / "company2.csv"
    cf_csv = Path(tmp_config.data_directory) / "cf2.csv"
    _write_company_csv(company_csv, ["Global Holdings Corp"])
    _write_cf_csv(cf_csv, [("Global Holdings", "Something")])

    matcher = CFMatcher(api_key="test-key", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))

    # Gray band scores to force LLM adjudication
    monkeypatch.setattr(
        matcher,
        "_shortlist_candidates",
        lambda norm, names, emps, top_k: [CFMatchCandidate(index=0, contributor_name=names[0], contributor_employer=emps[0], name_score=70, employer_score=65)],
    )
    matcher._client = FakeClient('{"decision":"NO_MATCH","index":0,"reason":"Generic tokens only"}')

    report = matcher.compare(company_csv=company_csv, cf_csv_filename="cf2.csv")
    content = report.read_text(encoding="utf-8")
    assert "Mention: Global Holdings Corp" not in content


def test_cf_matcher_rejects_low_threshold(monkeypatch, tmp_config: AppConfig, tmp_path: Path):
    company_csv = tmp_path / "company3.csv"
    cf_csv = Path(tmp_config.data_directory) / "cf3.csv"
    _write_company_csv(company_csv, ["Random Co."])
    _write_cf_csv(cf_csv, [("Unrelated", "None")])

    matcher = CFMatcher(api_key="test-key", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))

    # No candidates above minimal thresholds
    monkeypatch.setattr(
        matcher,
        "_shortlist_candidates",
        lambda norm, names, emps, top_k: [],
    )
    # Even if called, ensure no exception
    matcher._client = FakeClient('{"decision":"NO_MATCH","index":0,"reason":"n/a"}')

    report = matcher.compare(company_csv=company_csv, cf_csv_filename="cf3.csv")
    content = report.read_text(encoding="utf-8")
    assert "Mention: Random Co." not in content


def test_cf_matcher_input_validation_non_csv(monkeypatch, tmp_config: AppConfig, tmp_path: Path):
    company_csv = tmp_path / "bad.txt"
    company_csv.write_text("x", encoding="utf-8")
    cf_csv = Path(tmp_config.data_directory) / "cf.csv"
    _write_cf_csv(cf_csv, [("A", "B")])

    matcher = CFMatcher(api_key="k", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))
    with pytest.raises(ValueError):
        matcher.compare(company_csv=company_csv, cf_csv_filename="cf.csv")


def test_cf_matcher_input_validation_missing_cf(monkeypatch, tmp_config: AppConfig, tmp_path: Path):
    company_csv = tmp_path / "ok.csv"
    _write_company_csv(company_csv, ["One"])

    matcher = CFMatcher(api_key="k", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))
    with pytest.raises(FileNotFoundError):
        matcher.compare(company_csv=company_csv, cf_csv_filename="nope.csv")


def test_shortlist_candidates_and_normalize(tmp_config: AppConfig):
    matcher = CFMatcher(api_key="k", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))
    norm = matcher._normalize("Acme, Inc.")
    assert norm == "acme"
    names = ["Acme LLC", "Other Co"]
    emps = ["Other Emp", "Acme Incorporated"]
    cands = matcher._shortlist_candidates(norm, [matcher._normalize(n) for n in names], [matcher._normalize(e) for e in emps], top_k=2)
    assert isinstance(cands, list) and all(isinstance(c, CFMatchCandidate) for c in cands)


def test_llm_error_path(monkeypatch, tmp_config: AppConfig):
    matcher = CFMatcher(api_key="k", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))

    class BadClient:
        class _Messages:
            def create(self, **kwargs):
                raise RuntimeError("boom")
        @property
        def messages(self):
            return self._Messages()

    matcher._client = BadClient()

    recs = [{"Contributor Name": "Acme LLC", "Contributor Employer": "Acme"}]
    cands = [CFMatchCandidate(index=0, contributor_name="acme", contributor_employer="acme", name_score=80, employer_score=10)]
    decision, details = matcher._llm_adjudicate("Acme LLC", "acme", cands, recs)
    assert decision.startswith("REVIEW")


def test_llm_unparseable_json(monkeypatch, tmp_config: AppConfig):
    matcher = CFMatcher(api_key="k", config=tmp_config, logger=SimpleNamespace(info=lambda *a, **k: None, error=lambda *a, **k: None))
    matcher._client = FakeClient("nonsense not json")
    recs = [{"Contributor Name": "Acme LLC", "Contributor Employer": "Acme"}]
    cands = [CFMatchCandidate(index=0, contributor_name="acme", contributor_employer="acme", name_score=80, employer_score=10)]
    decision, details = matcher._llm_adjudicate("Acme LLC", "acme", cands, recs)
    assert decision == "REVIEW (LLM)"
    assert details and "Unparseable" in details[0]
