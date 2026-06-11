from __future__ import annotations

from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from app.application.agents.intent import Intent, classify_intent
from app.application.agents.planner import StudyPlanner
from app.application.agents.quiz import QuizGenerator
from app.application.rag.service import RagService
from app.domain.agents import Quiz, StudyPlan
from app.domain.entities import Answer


class AssistantState(TypedDict):
    course_id: str
    message: str
    intent: str
    answer: Answer | None
    quiz: Quiz | None
    plan: StudyPlan | None


class AssistantOrchestrator:
    """Graphe LangGraph routant un message libre vers le bon agent (tutor/quiz/plan)."""

    def __init__(
        self,
        rag: RagService,
        quiz: QuizGenerator,
        planner: StudyPlanner,
        quiz_questions: int = 5,
        plan_days: int = 7,
    ) -> None:
        self._rag = rag
        self._quiz = quiz
        self._planner = planner
        self._quiz_questions = quiz_questions
        self._plan_days = plan_days
        self._graph = self._build()

    def _build(self) -> Any:
        graph = StateGraph(AssistantState)
        graph.add_node("route", self._route)
        graph.add_node("tutor", self._tutor)
        graph.add_node("quiz", self._quiz_node)
        graph.add_node("plan", self._plan_node)
        graph.add_edge(START, "route")
        graph.add_conditional_edges(
            "route",
            self._select,
            {Intent.TUTOR.value: "tutor", Intent.QUIZ.value: "quiz", Intent.PLAN.value: "plan"},
        )
        graph.add_edge("tutor", END)
        graph.add_edge("quiz", END)
        graph.add_edge("plan", END)
        return graph.compile()

    async def _route(self, state: AssistantState) -> dict[str, str]:
        return {"intent": classify_intent(state["message"]).value}

    def _select(self, state: AssistantState) -> str:
        return state["intent"]

    async def _tutor(self, state: AssistantState) -> dict[str, object]:
        answer = await self._rag.answer(state["course_id"], state["message"])
        return {"answer": answer}

    async def _quiz_node(self, state: AssistantState) -> dict[str, object]:
        quiz = await self._quiz.generate(state["course_id"], state["message"], self._quiz_questions)
        return {"quiz": quiz}

    async def _plan_node(self, state: AssistantState) -> dict[str, object]:
        plan = await self._planner.generate(state["course_id"], state["message"], self._plan_days)
        return {"plan": plan}

    async def run(self, course_id: str, message: str) -> AssistantState:
        initial: AssistantState = {
            "course_id": course_id,
            "message": message,
            "intent": "",
            "answer": None,
            "quiz": None,
            "plan": None,
        }
        result = await self._graph.ainvoke(initial)
        return cast(AssistantState, result)
