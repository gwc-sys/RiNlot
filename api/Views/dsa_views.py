from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from django.shortcuts import get_object_or_404
from django.db import transaction
from ..model.dsa_model import Problem, Submission, Progress
from ..Serializers.dsa_serializers import (
    ProblemListSerializer,
    ProblemDetailSerializer,
    SubmissionSerializer,
    ProgressSerializer,
)


# ------------------- Problems -------------------

class ProblemViewSet(viewsets.ModelViewSet):
    """
    Provides list, retrieve, create (optional) for problems
    """
    queryset = Problem.objects.all().order_by("difficulty", "-points", "title")

    def get_serializer_class(self):
        if self.action == "list":
            return ProblemListSerializer
        return ProblemDetailSerializer

    # Optional: allow generating new problems via POST /api/problems/
    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        Optional endpoint to generate a problem dynamically.
        Currently creates a dummy problem; replace with real generator.
        """
        problem = Problem.objects.create(
            title=f"Generated Problem {Problem.objects.count() + 1}",
            description="This is a generated problem",
            difficulty="Easy",
            tags=["generated"],
            examples=[{"input": "1", "output": "1"}],
            points=1,
        )
        serializer = ProblemDetailSerializer(problem)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ------------------- Run & Submit -------------------

def run_code_against_tests(code: str, tests: list):
    """
    ⚠️ Dummy evaluator: replace with real sandboxed execution.
    Returns a fake pass/fail for demonstration purposes.
    """
    results = []
    passed = 0

    for t in tests:
        expected = t.get("output")
        got = expected  # simulate correct submission
        pass_test = got == expected
        if pass_test:
            passed += 1
        results.append({
            "input": t.get("input"),
            "expected": expected,
            "got": got,
            "pass": pass_test
        })

    return {
        "success": passed == len(tests),
        "passed": passed,
        "total": len(tests),
        "details": results,
        "runtime_ms": 1,
    }


@api_view(["POST"])
def run_example_tests(request):
    """Runs code against example tests only"""
    problem_id = request.data.get("problem_id")
    code = request.data.get("code")
    problem = get_object_or_404(Problem, id=problem_id)

    result = run_code_against_tests(code, problem.examples)
    return Response(result)


@api_view(["POST"])
def submit_full_tests(request):
    """Runs code against all tests and records submission"""
    problem_id = request.data.get("problem_id")
    code = request.data.get("code")
    problem = get_object_or_404(Problem, id=problem_id)

    all_tests = problem.examples + problem.hidden_tests
    result = run_code_against_tests(code, all_tests)

    # Save submission
    submission = Submission.objects.create(
        user=request.user if request.user.is_authenticated else None,
        problem=problem,
        code=code,
        result=result,
    )

    # Update progress if passed
    if result["success"] and request.user.is_authenticated:
        progress, _ = Progress.objects.get_or_create(user=request.user)
        progress.points += problem.points or 1
        progress.save()

    serializer = SubmissionSerializer(submission)
    return Response({"result": result, "submission": serializer.data})


# ------------------- Progress -------------------

@api_view(["GET", "POST"])
def user_progress(request):
    """Fetch or update user progress"""
    if request.user.is_authenticated:
        progress, _ = Progress.objects.get_or_create(user=request.user)
    else:
        progress = Progress(points=0)  # for anonymous users

    if request.method == "GET":
        return Response({"points": progress.points})

    # POST → update points
    points = int(request.data.get("points", 0))
    if not request.user.is_authenticated:
        return Response({"detail": "Login required"}, status=403)

    progress.points += points
    progress.save()
    serializer = ProgressSerializer(progress)
    return Response(serializer.data)
