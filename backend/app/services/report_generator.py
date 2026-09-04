import json
from typing import Dict, Any, List
from app.ai.gateway import get_ai_gateway
from app.ai.base import AIMessage


class ReportGenerator:
    """Interview report generation service"""

    def __init__(self):
        self.ai_gateway = get_ai_gateway()

    async def generate_interview_report(
        self,
        interview_data: Dict[str, Any],
        evaluations: List[Dict[str, Any]],
        skill_gaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive interview report"""

        # Calculate scores
        scores = self._calculate_scores(evaluations, interview_data.get('questions', []))

        prompt = f"""Generate a comprehensive interview assessment report.

Interview Details:
- Role: {interview_data.get('job_title')}
- Total Questions: {len(interview_data.get('questions', []))}
- Difficulty: {interview_data.get('difficulty')}

Performance Scores:
{json.dumps(scores, indent=2)}

Skill Gaps Summary:
{json.dumps(skill_gaps[:5], indent=2)}

Top Evaluations:
{json.dumps(evaluations[:5], indent=2)}

Generate a professional report with:

Return JSON:
{{
  "overall_score": float (0-10),
  "technical_score": float (0-10),
  "project_score": float (0-10),
  "problem_solving_score": float (0-10),
  "communication_score": float (0-10),
  "behavioral_score": float (0-10),
  "readiness_percentage": float (0-100),
  "strengths": ["specific strength 1", "specific strength 2", "strength 3"],
  "weaknesses": ["specific weakness 1", "specific weakness 2", "weakness 3"],
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "recommendations": [
    "actionable recommendation 1",
    "actionable recommendation 2",
    "actionable recommendation 3"
  ],
  "summary": "A 3-4 sentence professional summary of the assessment"
}}

IMPORTANT:
- Be professional and constructive
- Base findings on evidence
- Make recommendations specific and actionable
- Include disclaimer: This is an interview readiness assessment, not a hiring decision
- Return ONLY valid JSON
"""

        messages = [
            AIMessage(role="system", content="You are a professional interviewer writing assessment reports."),
            AIMessage(role="user", content=prompt)
        ]

        response = await self.ai_gateway.generate(
            messages=messages,
            temperature=0.4,
            max_tokens=1500
        )

        try:
            report = json.loads(response.content)
            # Ensure scores are present
            report['overall_score'] = scores.get('overall', report.get('overall_score', 0))
            report['technical_score'] = scores.get('technical', report.get('technical_score', 0))
            report['readiness_percentage'] = report.get('readiness_percentage', report['overall_score'] * 10)
            return report
        except json.JSONDecodeError:
            content = response.content
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                report = json.loads(content[start:end])
                return report
            raise Exception("Failed to parse interview report")

    def _calculate_scores(
        self,
        evaluations: List[Dict[str, Any]],
        questions: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate category scores from evaluations"""

        if not evaluations:
            return {
                'overall': 0,
                'technical': 0,
                'project': 0,
                'problem_solving': 0,
                'communication': 0,
                'behavioral': 0
            }

        category_scores = {
            'technical': [],
            'project': [],
            'problem_solving': [],
            'behavioral': [],
            'hr': []
        }

        for i, evaluation in enumerate(evaluations):
            if i < len(questions):
                question_type = questions[i].get('type', 'technical')
                score = evaluation.get('overall_score', 0)

                if question_type in category_scores:
                    category_scores[question_type].append(score)

        # Calculate averages
        scores = {}
        for category, score_list in category_scores.items():
            if score_list:
                scores[category] = sum(score_list) / len(score_list)
            else:
                scores[category] = 0

        # Overall score
        all_scores = [e.get('overall_score', 0) for e in evaluations]
        scores['overall'] = sum(all_scores) / len(all_scores) if all_scores else 0

        # Communication score (average of clarity scores)
        clarity_scores = [e.get('clarity_score', 0) for e in evaluations if e.get('clarity_score')]
        scores['communication'] = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0

        return scores
