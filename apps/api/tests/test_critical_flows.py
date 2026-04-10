from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from solution_planning_api.application.dto.requirement import RequirementRevision
from solution_planning_api.application.ports.requirement_normalization import (
    NormalizationContext,
    NormalizationResult,
)
from solution_planning_api.application.services.auth_service import AuthService
from solution_planning_api.application.services.candidate_service import CandidateService
from solution_planning_api.application.services.onboarding_service import OnboardingService
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.application.services.requirement_service import RequirementService
from solution_planning_api.config import Settings
from solution_planning_api.domain import (
    ArchitectureSelection,
    ArchitectureTemplate,
    CapabilityBlock,
    ConstraintProfile,
    OnboardingTaskProgress,
    OnboardingTaskState,
    Project,
    RequirementProfile,
    SolutionCandidate,
    TaskGraph,
    TaskGraphNode,
    User,
)
from solution_planning_api.domain.scoring import ScoringMode


@pytest.mark.asyncio
async def test_auth_register_and_login_roundtrip() -> None:
    users = InMemoryUserRepo()
    service = AuthService(
        users=users,
        password_hasher=SimpleHasher(),
        token_issuer=SimpleTokenIssuer(),
        settings=Settings(),
    )

    user = await service.register(email="phase19@example.com", password="secret123")
    token, logged_in = await service.login(email=user.email, password="secret123")

    assert token.startswith("token-")
    assert logged_in.user_id == user.user_id
    assert users.by_email[user.email].password_hash == "hashed:secret123"


@pytest.mark.asyncio
async def test_project_creation_lists_for_owner() -> None:
    owner_id = uuid4()
    projects_repo = InMemoryProjectRepo()
    service = ProjectService(projects_repo)

    created = await service.create_project(
        owner_user_id=owner_id,
        name="Critical Flow Project",
        description="phase-19",
    )
    listed = await service.list_projects(owner_user_id=owner_id)

    assert created.name == "Critical Flow Project"
    assert [p.project_id for p in listed] == [created.project_id]


@pytest.mark.asyncio
async def test_requirement_submission_uses_normalized_profile() -> None:
    owner_id = uuid4()
    project = Project(
        project_id=uuid4(),
        owner_user_id=owner_id,
        name="Req Intake",
        description=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    project_service = ProjectService(InMemoryProjectRepo(seed=[project]))
    requirement_repo = InMemoryRequirementRepo()
    constraint_repo = InMemoryConstraintRepo()
    normalizer = StubRequirementNormalizer(project.project_id)
    service = RequirementService(project_service, requirement_repo, constraint_repo, normalizer)

    result = await service.submit_raw_requirement(
        owner_user_id=owner_id,
        project_id=project.project_id,
        raw_text="Build a retrieval assistant with citations.",
    )

    assert result.normalization_method == "test-double"
    assert result.revision.version == 1
    assert result.revision.profile.business_goal == "Answer domain questions"
    assert result.constraint_profile is not None


@pytest.mark.asyncio
async def test_candidate_generation_persists_batch_candidates() -> None:
    owner_id = uuid4()
    project = Project(
        project_id=uuid4(),
        owner_user_id=owner_id,
        name="Candidate Project",
        description=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    requirement = make_requirement_revision(project.project_id, version=1)
    candidate_repo = InMemoryCandidateRepo()
    service = CandidateService(
        projects=ProjectService(InMemoryProjectRepo(seed=[project])),
        requirements=InMemoryRequirementRepo(seed=[requirement]),
        constraints=InMemoryConstraintRepo(),
        candidates=candidate_repo,
        capability_registry=StaticCapabilityRegistry(),
        template_registry=StaticTemplateRegistry(),
        engine=StaticCandidateEngine(project.project_id, requirement.requirement_id),
    )

    created = await service.generate_candidates(
        owner_user_id=owner_id,
        project_id=project.project_id,
        requirement_id=requirement.requirement_id,
        scoring_mode=ScoringMode.BEST_OVERALL,
    )

    assert len(created) == 1
    assert created[0].title == "RAG baseline"
    assert candidate_repo.last_generation_batch_id is not None


@pytest.mark.asyncio
async def test_onboarding_submission_marks_task_complete() -> None:
    owner_id = uuid4()
    project = Project(
        project_id=uuid4(),
        owner_user_id=owner_id,
        name="Onboarding Project",
        description=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    requirement = make_requirement_revision(project.project_id, version=1)
    candidate_id = uuid4()
    task_graph_id = uuid4()
    selection_repo = InMemorySelectionRepo(
        ArchitectureSelection(
            selection_id=uuid4(),
            project_id=project.project_id,
            requirement_id=requirement.requirement_id,
            solution_candidate_id=candidate_id,
            selected_at=datetime.now(UTC),
        )
    )
    task_graph_repo = InMemoryTaskGraphRepo(
        TaskGraph(
            task_graph_id=task_graph_id,
            project_id=project.project_id,
            candidate_id=candidate_id,
            nodes=[
                TaskGraphNode(
                    node_id="n1",
                    title="Template alignment",
                    description="Align with selected template",
                    task_type="template_alignment",
                )
            ],
            edges=[],
            dependencies={},
            validation_rules={},
            user_guidance_refs=[],
        )
    )
    progress_repo = InMemoryProgressRepo()
    service = OnboardingService(
        projects=ProjectService(InMemoryProjectRepo(seed=[project])),
        requirements=InMemoryRequirementRepo(seed=[requirement]),
        selections=selection_repo,
        task_graphs=task_graph_repo,
        progress=progress_repo,
    )

    item = await service.submit_task(
        owner_user_id=owner_id,
        project_id=project.project_id,
        requirement_id=requirement.requirement_id,
        node_id="n1",
        response={"notes": "This task is complete with enough details."},
    )

    assert item["state"] == OnboardingTaskState.COMPLETED.value
    assert progress_repo.by_node["n1"].state == OnboardingTaskState.COMPLETED


class InMemoryUserRepo:
    def __init__(self) -> None:
        self.by_email: dict[str, User] = {}
        self.by_id: dict[UUID, User] = {}

    async def create(self, *, email: str, password_hash: str) -> User:
        user = User(user_id=uuid4(), email=email, password_hash=password_hash, created_at=datetime.now(UTC))
        self.by_email[email] = user
        self.by_id[user.user_id] = user
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.by_id.get(user_id)

    async def get_by_email(self, email: str) -> User | None:
        return self.by_email.get(email)


class SimpleHasher:
    def hash(self, plain_password: str) -> str:
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, password_hash: str) -> bool:
        return password_hash == self.hash(plain_password)


class SimpleTokenIssuer:
    def issue(self, *, user_id: UUID, email: str) -> str:
        return f"token-{user_id}-{email}"

    def verify_and_get_user_id(self, token: str) -> UUID:
        return UUID(token.split("-")[1])


class InMemoryProjectRepo:
    def __init__(self, seed: list[Project] | None = None) -> None:
        self.projects: dict[UUID, Project] = {p.project_id: p for p in (seed or [])}

    async def create(self, *, owner_user_id: UUID, name: str, description: str | None) -> Project:
        project = Project(
            project_id=uuid4(),
            owner_user_id=owner_user_id,
            name=name,
            description=description,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.projects[project.project_id] = project
        return project

    async def get_by_id(self, project_id: UUID) -> Project | None:
        return self.projects.get(project_id)

    async def list_for_user(self, user_id: UUID) -> list[Project]:
        return [p for p in self.projects.values() if p.owner_user_id == user_id]

    async def update(self, **_: object) -> Project | None:
        return None

    async def delete(self, *, project_id: UUID, owner_user_id: UUID) -> bool:
        project = self.projects.get(project_id)
        if project is None or project.owner_user_id != owner_user_id:
            return False
        del self.projects[project_id]
        return True


class InMemoryRequirementRepo:
    def __init__(self, seed: list[RequirementRevision] | None = None) -> None:
        self.revisions: dict[UUID, RequirementRevision] = {}
        self.versions: dict[UUID, int] = {}
        for row in seed or []:
            self.revisions[row.requirement_id] = row
            self.versions[row.project_id] = max(self.versions.get(row.project_id, 0), row.version)

    async def next_version(self, project_id: UUID) -> int:
        return self.versions.get(project_id, 0) + 1

    async def create(
        self, *, project_id: UUID, version: int, profile: RequirementProfile
    ) -> RequirementRevision:
        row = RequirementRevision(
            requirement_id=profile.requirement_id,
            project_id=project_id,
            version=version,
            created_at=datetime.now(UTC),
            profile=profile,
        )
        self.revisions[row.requirement_id] = row
        self.versions[project_id] = version
        return row

    async def get_by_id(self, requirement_id: UUID) -> RequirementRevision | None:
        return self.revisions.get(requirement_id)

    async def get_latest_for_project(self, project_id: UUID) -> RequirementRevision | None:
        rows = [r for r in self.revisions.values() if r.project_id == project_id]
        if not rows:
            return None
        return max(rows, key=lambda r: r.version)

    async def list_for_project(self, project_id: UUID) -> list[RequirementRevision]:
        return [r for r in self.revisions.values() if r.project_id == project_id]


class InMemoryConstraintRepo:
    def __init__(self) -> None:
        self.by_requirement: dict[UUID, ConstraintProfile] = {}

    async def create(
        self, *, project_id: UUID, requirement_profile_id: UUID, profile: ConstraintProfile
    ) -> ConstraintProfile:
        self.by_requirement[requirement_profile_id] = profile
        return profile

    async def get_for_requirement(self, requirement_id: UUID) -> ConstraintProfile | None:
        return self.by_requirement.get(requirement_id)


class StubRequirementNormalizer:
    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id

    async def normalize(self, context: NormalizationContext) -> NormalizationResult:
        requirement_id = uuid4()
        return NormalizationResult(
            requirement_profile=RequirementProfile(
                requirement_id=requirement_id,
                project_id=self.project_id,
                raw_text=context.raw_text,
                business_goal="Answer domain questions",
                primary_task_type="rag_qa",
            ),
            constraint_profile=ConstraintProfile(
                constraint_id=uuid4(),
                project_id=self.project_id,
                requirement_id=requirement_id,
                max_latency_ms=800,
            ),
            method="test-double",
            rationale=["unit test normalization path"],
        )


class InMemoryCandidateRepo:
    def __init__(self) -> None:
        self.by_requirement: dict[UUID, list[SolutionCandidate]] = {}
        self.last_generation_batch_id: UUID | None = None

    async def create_in_batch(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        generation_batch_id: UUID,
        candidates: list[SolutionCandidate],
    ) -> list[SolutionCandidate]:
        self.last_generation_batch_id = generation_batch_id
        self.by_requirement[requirement_profile_id] = candidates
        return candidates

    async def list_latest_batch(
        self, requirement_profile_id: UUID, *, sort_mode: ScoringMode
    ) -> list[SolutionCandidate]:
        _ = sort_mode
        return self.by_requirement.get(requirement_profile_id, [])

    async def get_by_id(self, project_id: UUID, candidate_id: UUID) -> SolutionCandidate | None:
        _ = project_id
        for rows in self.by_requirement.values():
            for row in rows:
                if row.candidate_id == candidate_id:
                    return row
        return None


class StaticTemplateRegistry:
    async def list_templates(self) -> list[ArchitectureTemplate]:
        return [ArchitectureTemplate(template_id="rag", name="RAG")]

    async def get_template(self, template_id: str) -> ArchitectureTemplate | None:
        if template_id == "rag":
            return ArchitectureTemplate(template_id="rag", name="RAG")
        return None


class StaticCapabilityRegistry:
    async def list_capabilities(self) -> list[CapabilityBlock]:
        return [CapabilityBlock(capability_id="retrieval", name="Retrieval")]

    async def get_capability(self, capability_id: str) -> CapabilityBlock | None:
        if capability_id == "retrieval":
            return CapabilityBlock(capability_id="retrieval", name="Retrieval")
        return None


class StaticCandidateEngine:
    def __init__(self, project_id: UUID, requirement_id: UUID) -> None:
        self.project_id = project_id
        self.requirement_id = requirement_id

    async def synthesize_and_score(self, **_: object) -> list[SolutionCandidate]:
        return [
            SolutionCandidate(
                candidate_id=uuid4(),
                project_id=self.project_id,
                requirement_id=self.requirement_id,
                title="RAG baseline",
                summary="Simple candidate for test flow",
                suitability_score=0.8,
                score_breakdown={"composite_by_mode": {"best_overall": 0.8}},
            )
        ]


class InMemorySelectionRepo:
    def __init__(self, selection: ArchitectureSelection) -> None:
        self.selection = selection

    async def replace_for_requirement(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        solution_candidate_id: UUID,
    ) -> ArchitectureSelection:
        self.selection = ArchitectureSelection(
            selection_id=uuid4(),
            project_id=project_id,
            requirement_id=requirement_profile_id,
            solution_candidate_id=solution_candidate_id,
            selected_at=datetime.now(UTC),
        )
        return self.selection

    async def get_latest_for_requirement(
        self, requirement_profile_id: UUID
    ) -> ArchitectureSelection | None:
        if self.selection.requirement_id == requirement_profile_id:
            return self.selection
        return None


class InMemoryTaskGraphRepo:
    def __init__(self, graph: TaskGraph) -> None:
        self.graph = graph

    async def upsert_for_candidate(
        self, *, project_id: UUID, solution_candidate_id: UUID, graph: TaskGraph
    ) -> TaskGraph:
        _ = project_id, solution_candidate_id
        self.graph = graph
        return graph

    async def get_for_candidate(self, project_id: UUID, solution_candidate_id: UUID) -> TaskGraph | None:
        if self.graph.project_id == project_id and self.graph.candidate_id == solution_candidate_id:
            return self.graph
        return None


class InMemoryProgressRepo:
    def __init__(self) -> None:
        self.by_node: dict[str, OnboardingTaskProgress] = {}

    async def list_for_task_graph(self, task_graph_id: UUID) -> list[OnboardingTaskProgress]:
        return [p for p in self.by_node.values() if p.task_graph_id == task_graph_id]

    async def upsert(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        task_graph_id: UUID,
        node_id: str,
        state: OnboardingTaskState,
        response: dict[str, object] | None,
        validation_feedback: dict[str, object] | None,
    ) -> OnboardingTaskProgress:
        row = OnboardingTaskProgress(
            progress_id=uuid4(),
            project_id=project_id,
            requirement_id=requirement_profile_id,
            task_graph_id=task_graph_id,
            node_id=node_id,
            state=state,
            response=response,
            validation_feedback=validation_feedback,
            updated_at=datetime.now(UTC),
        )
        self.by_node[node_id] = row
        return row

    async def delete_for_requirement_except_graph(
        self, requirement_profile_id: UUID, keep_task_graph_id: UUID
    ) -> None:
        _ = requirement_profile_id, keep_task_graph_id


def make_requirement_revision(project_id: UUID, *, version: int) -> RequirementRevision:
    req_id = uuid4()
    return RequirementRevision(
        requirement_id=req_id,
        project_id=project_id,
        version=version,
        created_at=datetime.now(UTC),
        profile=RequirementProfile(
            requirement_id=req_id,
            project_id=project_id,
            raw_text="Requirement text",
            primary_task_type="rag_qa",
        ),
    )
