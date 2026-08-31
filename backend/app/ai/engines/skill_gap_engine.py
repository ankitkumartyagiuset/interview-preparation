from typing import List, Dict, Any, Optional
from backend.app.ai.gateway import ai_gateway

LEVEL_WEIGHTS = {
    "beginner": 1,
    "intermediate": 2,
    "advanced": 3,
    "expert": 4
}

class SkillGapEngine:
    """Compares Required Skills vs Resume Claimed Skills vs Interview Demonstrated Skills."""

    @staticmethod
    def calculate_gaps(
        required_skills: List[Dict[str, Any]],
        claimed_skills: List[Dict[str, Any]],
        evaluations_by_skill: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Deterministic calculation of skill gaps combined with AI evidence synthesis."""
        claimed_map = {s.get("skill_name", "").lower(): s for s in claimed_skills if s.get("skill_name")}
        
        # Build unified list of skills to assess
        all_skills_dict = {}
        for req in required_skills:
            name = req.get("name", "")
            if name:
                all_skills_dict[name.lower()] = {
                    "skill_name": name,
                    "category": req.get("category", "technical"),
                    "required_level": req.get("level", "intermediate").lower(),
                    "is_required": True
                }

        for c_name, c_val in claimed_map.items():
            if c_name not in all_skills_dict:
                all_skills_dict[c_name] = {
                    "skill_name": c_val.get("skill_name", c_name.title()),
                    "category": c_val.get("category", "technical"),
                    "required_level": "intermediate",
                    "is_required": False
                }

        results = []
        for s_key, s_info in all_skills_dict.items():
            req_lvl = s_info["required_level"]
            req_weight = LEVEL_WEIGHTS.get(req_lvl, 2)

            # Claimed Level
            claimed_item = claimed_map.get(s_key)
            if claimed_item:
                cl_lvl = claimed_item.get("claimed_level", "intermediate").lower()
            else:
                cl_lvl = "beginner"
            cl_weight = LEVEL_WEIGHTS.get(cl_lvl, 2)

            # Demonstrated Level from interview evaluations
            skill_evals = evaluations_by_skill.get(s_key, [])
            if skill_evals:
                # Average scores for this skill
                avg_score = sum(e.get("score", 5.0) for e in skill_evals) / len(skill_evals)
                if avg_score >= 8.5:
                    demo_lvl = "expert" if cl_weight >= 3 else "advanced"
                elif avg_score >= 7.0:
                    demo_lvl = "advanced" if cl_weight >= 3 else "intermediate"
                elif avg_score >= 5.0:
                    demo_lvl = "intermediate"
                else:
                    demo_lvl = "beginner"
                
                confidence = min(0.95, 0.70 + 0.1 * len(skill_evals))
                evidence = "; ".join([e.get("feedback_summary", "") for e in skill_evals if e.get("feedback_summary")])
            else:
                # Untested in this session: extrapolate cautiously
                demo_lvl = cl_lvl if cl_weight <= 2 else "intermediate"
                confidence = 0.60
                evidence = f"Extrapolated from resume claims; not directly tested in this session."

            demo_weight = LEVEL_WEIGHTS.get(demo_lvl, 1)

            # Compute Gap between Required and Demonstrated
            gap_diff = req_weight - demo_weight
            if gap_diff >= 2:
                gap_severity = "high"
                priority = "high"
            elif gap_diff == 1:
                gap_severity = "medium"
                priority = "high" if s_info["is_required"] else "medium"
            elif gap_diff == 0:
                gap_severity = "low"
                priority = "medium" if s_info["is_required"] else "low"
            else:
                gap_severity = "none"
                priority = "low"

            results.append({
                "skill_name": s_info["skill_name"],
                "category": s_info["category"],
                "required_level": req_lvl,
                "claimed_level": cl_lvl,
                "demonstrated_level": demo_lvl,
                "gap_severity": gap_severity,
                "priority": priority,
                "confidence_score": round(confidence, 2),
                "evidence_notes": evidence or f"Assessed competency level: {demo_lvl}."
            })

        # Sort with high priority gaps first
        priority_order = {"high": 0, "medium": 1, "low": 2}
        results.sort(key=lambda x: priority_order.get(x["priority"], 3))
        return results

skill_gap_engine = SkillGapEngine()
