"""
Comprehensive Field Report Generator.

Fuses outputs from all AI engines (Plant Vision, Pest Detection, Severity,
Weather, and Pesticides) into a single actionable diagnostic dossier:
- Structured JSON export for mobile & cloud sync
- Rich Markdown reports formatted for farmers and agronomists
- Expert human triage flagging for high-consequence or ambiguous cases.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ai.engines.decision_support.context_analyzer import ContextAssessment, FarmContext
from ai.shared.model_interfaces.base_engine import EnginePrediction

logger = logging.getLogger(__name__)


@dataclass
class TreatmentRecommendation:
    category: str  # 'Chemical', 'Biological', 'Cultural/Agronomic'
    title_ar: str
    title_en: str
    description_ar: str
    description_en: str
    safety_period_days: Optional[int] = None


@dataclass
class ComprehensiveFieldReport:
    """Full integrated report combining all AI engine outputs."""
    report_id: str
    created_at: str
    crop: str
    diagnosis: str
    severity: str
    confidence: float
    requires_expert_review: bool
    expert_review_reasons: List[str]
    alternatives: List[Dict[str, Any]]
    pest_summary: Optional[Dict[str, Any]] = None
    weather_risks: List[str] = field(default_factory=list)
    treatments: List[TreatmentRecommendation] = field(default_factory=list)
    context_notes: List[str] = field(default_factory=list)


class AnalysisReportGenerator:
    """
    Synthesizes multi-engine outputs into a comprehensive farm advisory dossier.
    """

    def generate_report(
        self,
        report_id: str,
        plant_prediction: EnginePrediction,
        severity_prediction: Optional[EnginePrediction] = None,
        crop_prediction: Optional[EnginePrediction] = None,
        pest_prediction: Optional[EnginePrediction] = None,
        context_assessment: Optional[ContextAssessment] = None,
        treatments: Optional[List[TreatmentRecommendation]] = None,
    ) -> ComprehensiveFieldReport:
        """
        Builds full structured report from individual engine predictions.
        """
        crop_name = crop_prediction.primary_label if crop_prediction else "Unknown Crop"
        diagnosis = plant_prediction.primary_label
        severity = severity_prediction.primary_label if severity_prediction else "Unknown Severity"

        conf = plant_prediction.confidence
        if context_assessment:
            conf = context_assessment.context_adjusted_confidence

        requires_review = plant_prediction.requires_expert_review
        review_reasons: List[str] = []

        if conf < 0.70:
            requires_review = True
            review_reasons.append("Model confidence is below definitive threshold (< 70%).")

        if diagnosis != "healthy" and not plant_prediction.is_confident:
            requires_review = True
            review_reasons.append("Ambiguous symptom patterns detected across top candidates.")

        if pest_prediction and pest_prediction.primary_label == "desert_locust":
            requires_review = True
            review_reasons.append("Quarantine or swarm threat alert: Desert Locust detection requires official verification.")

        alternatives = [asdict(alt) for alt in plant_prediction.alternatives]

        pest_summary = None
        if pest_prediction:
            pest_summary = {
                "dominant_pest": pest_prediction.primary_label,
                "confidence": pest_prediction.confidence,
                "counts": pest_prediction.details.get("counts_by_pest", {}),
                "total": pest_prediction.details.get("total_pest_count", 0),
            }

        weather_risks = context_assessment.environmental_risks if context_assessment else []
        notes = context_assessment.notes if context_assessment else []

        return ComprehensiveFieldReport(
            report_id=report_id,
            created_at=datetime.utcnow().isoformat(),
            crop=crop_name,
            diagnosis=diagnosis,
            severity=severity,
            confidence=round(conf, 4),
            requires_expert_review=requires_review,
            expert_review_reasons=review_reasons,
            alternatives=alternatives,
            pest_summary=pest_summary,
            weather_risks=weather_risks,
            treatments=treatments or [],
            context_notes=notes,
        )

    def export_markdown(self, report: ComprehensiveFieldReport, output_file: Union[str, Path]) -> Path:
        """Renders bilingual formatted Markdown report to disk."""
        out = Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)

        status_flag = "⚠️ **تتطلب مراجعة خبير زراعي (Requires Expert Review)**" if report.requires_expert_review else "✅ **تشخيص مؤكد (Confident Diagnosis)**"

        lines = [
            f"# AgriVision Field Diagnostic Report — {report.report_id}",
            f"**تاريخ الفحص (Inspection Date):** {report.created_at}",
            "",
            "## 1. ملخص التشخيص (Diagnostic Summary)",
            f"- **المحصول (Crop):** {report.crop}",
            f"- **التشخيص الأساسي (Primary Diagnosis):** `{report.diagnosis}`",
            f"- **شدة الإصابة (Severity Level):** `{report.severity}`",
            f"- **درجة الثقة (Confidence):** {report.confidence * 100:.1f}%",
            f"- **حالة الاعتماد:** {status_flag}",
            "",
        ]

        if report.expert_review_reasons:
            lines.append("### أسباب طلب مراجعة الخبير (Reasons for Review):")
            for r in report.expert_review_reasons:
                lines.append(f"- {r}")
            lines.append("")

        if report.alternatives:
            lines.append("### الاحتمالات والتشخيصات البديلة (Alternative Candidates):")
            for alt in report.alternatives:
                lines.append(f"- **{alt['label']}**: {alt['confidence'] * 100:.1f}%")
            lines.append("")

        if report.pest_summary and report.pest_summary.get("total", 0) > 0:
            lines.extend([
                "## 2. كشف الآفات الحشرية (Pest Detection)",
                f"- **الآفة الرئيسية السائدة:** {report.pest_summary['dominant_pest']}",
                f"- **إجمالي العدد المكتشف:** {report.pest_summary['total']}",
                "",
            ])

        if report.weather_risks:
            lines.append("## 3. المخاطر الجوية والبيئية (Micro-Climate Drivers):")
            for w in report.weather_risks:
                lines.append(f"- {w}")
            lines.append("")

        if report.treatments:
            lines.append("## 4. خطة العلاج والإدارة المتكاملة (Integrated Management Plan):")
            for idx, t in enumerate(report.treatments, start=1):
                phi_str = f" | فترة الأمان (PHI): {t.safety_period_days} يوم" if t.safety_period_days else ""
                lines.extend([
                    f"### {idx}. [{t.category}] {t.title_ar} / {t.title_en}{phi_str}",
                    f"- {t.description_ar}",
                    f"- *{t.description_en}*",
                    "",
                ])

        with open(out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return out

    def export_json(self, report: ComprehensiveFieldReport, output_file: Union[str, Path]) -> Path:
        out = Path(output_file)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)
        return out
