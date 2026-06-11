class SherpaError(Exception):
    """Erreur métier de base. Levée dans le domaine, catchée en présentation."""


class CourseNotFoundError(SherpaError):
    def __init__(self, course_id: str) -> None:
        super().__init__(f"Cours introuvable: {course_id}")
        self.course_id = course_id


class NoRelevantContextError(SherpaError):
    def __init__(self, question: str) -> None:
        super().__init__("Aucun contexte pertinent trouvé dans le corpus du cours.")
        self.question = question


class AgentOutputError(SherpaError):
    def __init__(self, detail: str) -> None:
        super().__init__(f"Sortie d'agent invalide: {detail}")
        self.detail = detail


class BudgetExceededError(SherpaError):
    def __init__(self, requested: int, budget: int) -> None:
        super().__init__(f"Budget tokens dépassé: {requested} > {budget}")
        self.requested = requested
        self.budget = budget
