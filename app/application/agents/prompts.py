from __future__ import annotations

QUIZ_SYSTEM = (
    "Tu génères des quiz pédagogiques STRICTEMENT à partir du CONTEXTE fourni. "
    "Ne réponds qu'en JSON valide, sans texte autour. "
    'Schéma: {"questions":[{"question":str,"choices":[str,...],'
    '"answer_index":int,"explanation":str}]}. '
    "answer_index est l'indice (0-based) de la bonne réponse dans choices."
)

PLAN_SYSTEM = (
    "Tu construis un plan de révision réaliste à partir du CONTEXTE fourni. "
    "Ne réponds qu'en JSON valide, sans texte autour. "
    'Schéma: {"items":[{"day":int,"topic":str,"activities":[str,...]}]}.'
)

DIAGNOSIS_SYSTEM = (
    "Tu analyses les réponses d'un étudiant pour identifier ses lacunes, "
    "en t'appuyant sur le CONTEXTE du cours. "
    "Ne réponds qu'en JSON valide, sans texte autour. "
    'Schéma: {"weak_topics":[str,...],"recommendation":str}.'
)


def quiz_prompt(context: str, topic: str, num_questions: int) -> str:
    return (
        f"CONTEXTE:\n{context}\n\n"
        f"SUJET: {topic}\n"
        f"Génère {num_questions} questions à choix multiples. JSON uniquement."
    )


def plan_prompt(context: str, topic: str, days: int) -> str:
    return (
        f"CONTEXTE:\n{context}\n\n"
        f"OBJECTIF: réviser '{topic}' en {days} jours.\n"
        "Produis un plan jour par jour. JSON uniquement."
    )


def diagnosis_prompt(context: str, answers_block: str) -> str:
    return (
        f"CONTEXTE:\n{context}\n\n"
        f"RÉPONSES DE L'ÉTUDIANT:\n{answers_block}\n\n"
        "Identifie les thèmes faibles et une recommandation. JSON uniquement."
    )
