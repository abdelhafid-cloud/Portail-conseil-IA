from __future__ import annotations

from typing import Any


def generate_lead_insights(profile: dict[str, Any]) -> dict[str, Any]:
    challenge_text = f"{profile.get('challenges', '')} {profile.get('business_goals', '')}".lower()
    services = []
    if any(keyword in challenge_text for keyword in ('support', 'tickets', 'ops', 'manual', 'workflow')):
        services.append('Business Automation')
    if any(keyword in challenge_text for keyword in ('knowledge', 'docs', 'search', 'support')):
        services.append('RAG Platform')
    if any(keyword in challenge_text for keyword in ('assistant', 'agents', 'copilot')):
        services.append('AI Agents')
    if not services:
        services = ['AI Strategy Workshop', 'Automation Discovery']

    score = 40
    score += 10 if profile.get('company_name') else 0
    score += 10 if profile.get('budget') else 0
    score += 10 if profile.get('decision_maker_status') in {'decision maker', 'founder', 'c-level'} else 0
    score += 10 if profile.get('employee_count') else 0
    score += 20 if profile.get('budget') and any(token in str(profile.get('budget')).lower() for token in ('20', '30', '50', '100')) else 0
    score = max(0, min(score, 100))

    probability = round(score / 100, 2)
    priority = 'high' if score >= 75 else 'medium' if score >= 50 else 'low'

    return {
        'lead_score': score,
        'conversion_probability': probability,
        'priority_level': priority,
        'recommended_services': services,
        'estimated_project_value': '$20,000 - $50,000' if score >= 75 else '$10,000 - $20,000' if score >= 50 else '$5,000 - $10,000',
    }


def build_consultation_reply(message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    lower_message = message.lower()

    if any(word in lower_message for word in ('logistics', 'logistique', 'logist')):
        reply = 'How many employees do you currently have, and what operational bottlenecks are limiting throughput or service quality?'
    elif any(word in lower_message for word in ('support', 'tickets', 'customer service')):
        reply = 'How many tickets does your team handle per day, and where is the biggest delay in the process?'
    elif any(word in lower_message for word in ('automate', 'automation', 'workflow')):
        reply = 'Which processes are still manual today, and which of them have the highest cost or error rate?'
    else:
        reply = 'Tell me about your company size, your main objective, and the business process you want to improve first.'

    follow_up = ['company_size', 'budget', 'decision_maker']
    if context.get('industry'):
        follow_up.insert(0, 'industry_specific_pain_point')

    return {
        'reply': reply,
        'follow_up_questions': follow_up,
        'suggested_services': generate_lead_insights(context).get('recommended_services', []),
    }


def generate_meeting_brief(lead: dict[str, Any]) -> dict[str, Any]:
    return {
        'executive_summary': f"{lead.get('company_name', 'The prospect')} is being evaluated for an AI transformation roadmap.",
        'company_analysis': f"Focus on {lead.get('industry', 'their industry')} and the impact of current manual operations.",
        'pain_points': lead.get('challenges') or 'To be qualified during the session.',
        'recommended_solutions': lead.get('recommended_services') or ['AI Strategy Workshop', 'RAG Platform'],
        'potential_opportunities': ['Automate high-volume workflows', 'Deploy an internal knowledge assistant', 'Build AI-qualified inbound pipeline'],
    }


def generate_proposal(lead: dict[str, Any]) -> dict[str, Any]:
    services = lead.get('recommended_services') or ['AI Strategy Workshop']
    return {
        'title': f"AI Consulting Proposal for {lead.get('company_name', 'Prospect')}",
        'scope': 'Discovery, solution design, implementation, and enablement for an enterprise AI program.',
        'timeline': '8-12 weeks',
        'budget': lead.get('estimated_project_value', '$20,000 - $50,000'),
        'commercial_sections': [
            'Discovery and executive workshop',
            'Architecture and implementation plan',
            'Knowledge base and AI assistant deployment',
            'Governance, analytics, and adoption support',
        ],
        'technical_sections': services,
    }
