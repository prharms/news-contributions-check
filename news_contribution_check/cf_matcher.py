"""Campaign finance comparison (hybrid fuzzy gate → Haiku adjudication)."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import anthropic
from rapidfuzz import fuzz, process

from .config import AppConfig, get_timestamped_filename


@dataclass
class CFMatchCandidate:
    index: int
    contributor_name: str
    contributor_employer: str
    name_score: int
    employer_score: int


class CFMatcher:
    """Finds likely matches between company_mentions.csv and a campaign finance CSV."""

    def __init__(self, api_key: str, config: AppConfig, logger) -> None:
        self._config = config
        self._logger = logger
        self._client = anthropic.Anthropic(api_key=api_key)

    def compare(self, company_csv: Path, cf_csv_filename: str) -> Path:
        """Run comparison and produce a .txt report in the output directory.

        Args:
            company_csv: Path to the generated company mentions CSV
            cf_csv_filename: Filename of CF CSV in data directory

        Returns:
            Path to generated .txt report
        """
        data_dir = Path(self._config.data_directory)
        output_dir = Path(self._config.output_directory)
        cf_path = data_dir / cf_csv_filename

        # Validate inputs
        if not cf_path.exists():
            raise FileNotFoundError(f"CF CSV not found: {cf_path}")
        if company_csv.suffix.lower() != ".csv":
            raise ValueError(f"Company CSV must be .csv: {company_csv}")

        self._logger.info("Starting CF comparison pipeline")

        # Load company mentions
        mentions = self._load_company_mentions(company_csv)
        # Load CF records (only required fields)
        cf_records = self._load_cf_records(cf_path)

        # Build search spaces
        cf_names = [self._normalize(r["Contributor Name"]) for r in cf_records]
        cf_employers = [self._normalize(r["Contributor Employer"]) for r in cf_records]

        report_path = output_dir / get_timestamped_filename("company_mentions_MATCHES", "txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("Matches Report\n")
            f.write("=" * 40 + "\n\n")

            for mention in mentions:
                original = mention
                normalized = self._normalize(mention)

                # Fuzzy gate
                cand = self._shortlist_candidates(
                    normalized, cf_names, cf_employers, top_k=self._config.compare.top_k
                )

                # Decide using thresholds
                best = max(cand, key=lambda c: max(c.name_score, c.employer_score)) if cand else None
                details: List[str] = []

                if not cand:
                    # Nothing to write when fully rejected
                    continue
                else:
                    hi = self._config.compare.high_threshold
                    lo = self._config.compare.low_threshold
                    best_score = max(best.name_score, best.employer_score) if best else 0

                    if best_score <= lo:
                        # Suppress rejected entries
                        continue

                    # For gray band and high band, use Haiku to confirm to avoid generic-token matches
                    decision, details = self._llm_adjudicate(
                        original, normalized, cand, cf_records
                    )
                    if decision.startswith("NO_MATCH"):
                        # Suppress LLM no-match entries
                        continue
                    if decision.startswith("ACCEPT") or decision.startswith("REVIEW"):
                        f.write(f"Mention: {original}\n")
                        f.write(f"Decision: {decision}\n")
                        if details:
                            for d in details:
                                f.write(f" - {d}\n")
                        f.write("\n")

        self._logger.info(f"CF comparison completed. Report: {report_path}")
        return report_path

    def _load_company_mentions(self, company_csv: Path) -> List[str]:
        mentions: List[str] = []
        with open(company_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "Company/Organization Name" not in reader.fieldnames:
                raise ValueError("Company CSV missing 'Company/Organization Name' column")
            for row in reader:
                name = (row.get("Company/Organization Name") or "").strip()
                if name:
                    mentions.append(name)
        return mentions

    def _load_cf_records(self, cf_path: Path) -> List[Dict[str, str]]:
        with open(cf_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for col in ("Contributor Name", "Contributor Employer"):
                if col not in reader.fieldnames:
                    raise ValueError(f"CF CSV missing required column: {col}")
            return [
                {
                    "Contributor Name": (row.get("Contributor Name") or "").strip(),
                    "Contributor Employer": (row.get("Contributor Employer") or "").strip(),
                }
                for row in reader
            ]

    def _normalize(self, s: str) -> str:
        s = (s or "").lower()
        # Remove corporate suffixes
        s = re.sub(r"\b(incorporated|inc|llc|l\.l\.c\.|ltd|co|corp|corporation|plc)\b", "", s)
        # Remove punctuation
        s = re.sub(r"[^\w\s]", " ", s)
        # Collapse whitespace
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def _shortlist_candidates(
        self,
        norm_mention: str,
        cf_names: List[str],
        cf_employers: List[str],
        top_k: int,
    ) -> List[CFMatchCandidate]:
        # Use process.extract to get top matches from each field
        top_names = process.extract(
            norm_mention, cf_names, scorer=fuzz.token_set_ratio, limit=top_k
        )
        top_emps = process.extract(
            norm_mention, cf_employers, scorer=fuzz.token_set_ratio, limit=top_k
        )

        by_index: Dict[int, CFMatchCandidate] = {}
        for cand, score, idx in top_names:
            entry = by_index.get(idx)
            if entry:
                entry.name_score = max(entry.name_score, int(score))
            else:
                by_index[idx] = CFMatchCandidate(
                    index=idx,
                    contributor_name=cf_names[idx],
                    contributor_employer=cf_employers[idx],
                    name_score=int(score),
                    employer_score=0,
                )
        for cand, score, idx in top_emps:
            entry = by_index.get(idx)
            if entry:
                entry.employer_score = max(entry.employer_score, int(score))
            else:
                by_index[idx] = CFMatchCandidate(
                    index=idx,
                    contributor_name=cf_names[idx],
                    contributor_employer=cf_employers[idx],
                    name_score=0,
                    employer_score=int(score),
                )

        return sorted(
            by_index.values(), key=lambda e: max(e.name_score, e.employer_score), reverse=True
        )

    def _format_accept(self, cand: CFMatchCandidate, cf_records: List[Dict[str, str]]) -> str:
        rec = cf_records[cand.index]
        field = "Name" if cand.name_score >= cand.employer_score else "Employer"
        score = max(cand.name_score, cand.employer_score)
        return (
            f"ACCEPT ({field} score={score}) -> "
            f"Contributor Name='{rec['Contributor Name']}', "
            f"Contributor Employer='{rec['Contributor Employer']}'"
        )

    def _llm_adjudicate(
        self,
        mention_original: str,
        mention_normalized: str,
        candidates: List[CFMatchCandidate],
        cf_records: List[Dict[str, str]],
    ) -> Tuple[str, List[str]]:
        # Build compact prompt with strict policy and schema
        lines = []
        lines.append("You are a forensic document analyst. Temperature=0. Return JSON only.")
        # Explicit task aligned to domain purpose
        lines.append(
            "Task: Determine whether the company/organization mentioned in news coverage is the SAME ENTITY as a campaign contribution source — either as the contributor name or the contributor's employer."
        )
        # Decision policy
        lines.append(
            "Decision policy: Return MATCH if the mention clearly refers to the same legal entity as one candidate's contributor name OR employer. Return NO_MATCH if overlap is only generic tokens or semantics differ. Return REVIEW if uncertain."
        )
        # Hard exclusions
        lines.append(
            "NEVER match media organizations, government entities, political parties/committees, or copyright holders."
        )
        # Guidance against generic tokens and weak overlaps
        lines.append(
            "Do not rely on generic words alone (e.g., 'American', 'International', 'National', 'Global', 'Group', 'Fund', 'Holding', 'Company', 'LLC', 'Inc', 'Corp'). Require distinctive overlap beyond these."
        )
        lines.append(
            "Allow for legal suffix variations, common abbreviations, and known trade/parent-subsidiary relationships only if distinctive tokens align."
        )
        # Example guidance
        lines.append("Example: 'American Ireland Fund' vs 'American Cab' => NO_MATCH (only 'American' overlaps).")
        lines.append("Example: 'American Ireland Fund' vs 'The Ireland Funds' => NO_MATCH (distinct entities despite token similarity).")
        # Mention context
        lines.append("Company mention (original): " + mention_original)
        lines.append("Company mention (normalized): " + mention_normalized)
        # Candidates with original and normalized fields
        lines.append("Candidates:")
        for i, c in enumerate(candidates, 1):
            rec = cf_records[c.index]
            name_orig = rec['Contributor Name']
            emp_orig = rec['Contributor Employer']
            name_norm = self._normalize(name_orig)
            emp_norm = self._normalize(emp_orig)
            lines.append(
                f"{i}. name='" + name_orig.replace("'", "\'") + "' (norm='" + name_norm + "'), "
                f"employer='" + emp_orig.replace("'", "\'") + "' (norm='" + emp_norm + "'), "
                f"name_score={c.name_score}, employer_score={c.employer_score}"
            )
        lines.append(
            "Return JSON: {\"decision\": \"MATCH|NO_MATCH|REVIEW\", \"index\": <1-based index or 0 if none>, \"reason\": \"...\"}"
        )
        prompt = "\n".join(lines)

        try:
            message = self._client.messages.create(
                model=self._config.compare.cf_model,
                max_tokens=300,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text if message.content else "{}"
        except Exception as e:
            self._logger.error(f"Haiku adjudication failed: {e}")
            return ("REVIEW (LLM error)", [str(e)])

        # Parse simple JSON
        import json

        try:
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start < 0 or json_end <= json_start:
                raise ValueError("No JSON object found")
            data = json.loads(text[json_start:json_end])
            decision = str(data.get("decision", "REVIEW")).upper()
            idx = int(data.get("index", 0))
            reason = str(data.get("reason", ""))
        except Exception:
            decision, idx, reason = "REVIEW", 0, "Unparseable LLM response"

        if decision == "MATCH" and 1 <= idx <= len(candidates):
            cand = candidates[idx - 1]
            return (self._format_accept(cand, cf_records), [reason])
        elif decision == "NO_MATCH":
            return ("NO_MATCH (LLM)", [reason])
        else:
            return ("REVIEW (LLM)", [reason])


