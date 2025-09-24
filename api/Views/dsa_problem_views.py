import subprocess
import tempfile
import os
import time
import psutil
from datetime import timedelta
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.authentication import TokenAuthentication
from django.http import Http404
from django.utils import timezone
from ..model import AdminProblem, CommunityProblem, AIProblem, Submission, UserProgress, ContentType
from ..Serializers import AdminProblemSerializer, CommunityProblemSerializer, AIProblemSerializer, UserProgressSerializer

def get_problem_by_id(problem_id, user):
    try:
        problem = AdminProblem.objects.get(id=problem_id)
        return problem, 'Admin'
    except AdminProblem.DoesNotExist:
        pass
    try:
        problem = CommunityProblem.objects.get(id=problem_id)
        return problem, 'User'
    except CommunityProblem.DoesNotExist:
        pass
    try:
        problem = AIProblem.objects.get(id=problem_id)
        if user.is_authenticated and problem.author == user:
            return problem, 'AI'
        raise Http404("AI problem not accessible")
    except AIProblem.DoesNotExist:
        pass
    raise Http404("Problem not found")

class ProblemListView(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        admin_qs = AdminProblem.objects.all().order_by('-created_at')
        community_qs = CommunityProblem.objects.all().order_by('-created_at')
        ai_qs = AIProblem.objects.filter(author=request.user).order_by('-created_at') if request.user.is_authenticated else AIProblem.objects.none()

        admin_data = AdminProblemSerializer(admin_qs, many=True, context={'request': request}).data
        community_data = CommunityProblemSerializer(community_qs, many=True, context={'request': request}).data
        ai_data = AIProblemSerializer(ai_qs, many=True, context={'request': request}).data

        all_data = admin_data + community_data + ai_data
        all_data.sort(key=lambda x: x['created_at'], reverse=True)

        return Response(all_data or [AdminProblemSerializer(
            AdminProblem.objects.create(
                title="Two Sum",
                statement="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                input_format="nums = [2,7,11,15], target = 9",
                output_format="Output: [0,1]",
                constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9", "Only one valid answer exists."],
                examples=[{"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] == 2 + 7 == 9"},
                          {"input": "nums = [3,2,4], target = 6", "output": "[1,2]", "explanation": "nums[1] + nums[2] == 2 + 4 == 6"}],
                difficulty="Easy",
                tags=["array", "hash-table"],
                author=None,
            ),
            context={'request': request}
        ).data])

class ProblemDetailView(views.APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, problem_id):
        problem, source = get_problem_by_id(problem_id, request.user)
        if source == 'Admin':
            serializer = AdminProblemSerializer(problem, context={'request': request})
        elif source == 'User':
            serializer = CommunityProblemSerializer(problem, context={'request': request})
        else:
            serializer = AIProblemSerializer(problem, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, problem_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': 'Unauthorized: Only admin users can update problems'}, status=status.HTTP_403_FORBIDDEN)
        problem, source = get_problem_by_id(problem_id, request.user)
        if source != 'Admin':
            return Response({'detail': 'Can only update Admin problems'}, status=status.HTTP_403_FORBIDDEN)
        serializer = AdminProblemSerializer(problem, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminProblemView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = AdminProblemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommunityProblemView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CommunityProblemSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def generate_ai_problem(difficulty, tags):
    if difficulty == 'Easy':
        return {
            'title': 'AI Generated: Sum of Two Numbers',
            'statement': 'Given two integers, return their sum.',
            'examples': [{'input': '1\n2', 'output': '3', 'explanation': '1 + 2 = 3'}],
            'constraints': ['-100 <= a, b <= 100'],
            'test_cases': [{'input': '1\n2', 'output': '3'}, {'input': '3\n4', 'output': '7'}],
        }
    elif difficulty == 'Medium':
        return {
            'title': 'AI Generated: Reverse String',
            'statement': 'Reverse the given string.',
            'examples': [{'input': 'hello', 'output': 'olleh', 'explanation': 'Reversed hello'}],
            'constraints': ['1 <= length <= 1000'],
            'test_cases': [{'input': 'hello', 'output': 'olleh'}, {'input': 'world', 'output': 'dlrow'}],
        }
    else:
        return {
            'title': 'AI Generated: Fibonacci Sequence',
            'statement': 'Compute the nth Fibonacci number.',
            'examples': [{'input': '5', 'output': '5', 'explanation': 'Fib(5) = 5'}],
            'constraints': ['0 <= n <= 30'],
            'test_cases': [{'input': '5', 'output': '5'}, {'input': '10', 'output': '55'}],
        }

class AIGenerateView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        difficulty = request.data.get('difficulty', 'Easy')
        tags = request.data.get('tags', [])
        generated = generate_ai_problem(difficulty, tags)
        problem = AIProblem.objects.create(
            title=generated['title'],
            statement=generated['statement'],
            difficulty=difficulty,
            tags=tags,
            examples=generated['examples'],
            constraints=generated['constraints'],
            test_cases=generated['test_cases'],
            author=request.user,  # Set author for access control
        )
        serializer = AIProblemSerializer(problem, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def execute_code(code, input_data):
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
        f.write(code.encode())
        f_name = f.name

    start_time = time.time()
    process = subprocess.Popen(
        ['python', f_name],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = process.communicate(input_data.encode(), timeout=5)
        output = stdout.decode().strip()
        error = stderr.decode().strip()
        runtime_ms = int((time.time() - start_time) * 1000)
        p = psutil.Process(process.pid)
        memory_kb = p.memory_info().rss // 1024 if p.is_running() else 0
    except subprocess.TimeoutExpired:
        process.kill()
        os.remove(f_name)
        return {'passed': False, 'message': 'Time Limit Exceeded', 'runtime_ms': None, 'memory_kb': None}
    finally:
        if process.poll() is None:
            process.kill()
        os.remove(f_name)

    if error:
        return {'passed': False, 'message': error, 'runtime_ms': runtime_ms, 'memory_kb': memory_kb}
    return {'passed': True, 'output': output, 'message': '', 'runtime_ms': runtime_ms, 'memory_kb': memory_kb}

class RunView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        problem_id = request.data.get('problem_id')
        code = request.data.get('code')
        problem, _ = get_problem_by_id(problem_id, request.user)

        test_results = []
        overall_status = 'Accepted'
        overall_runtime = 0
        overall_memory = 0

        for test in problem.examples:
            input_data = test.get('input', '')
            expected = test.get('output', '').strip()
            result = execute_code(code, input_data)
            passed = result['passed'] and result.get('output', '') == expected
            if not passed:
                overall_status = 'Wrong Answer' if result['passed'] else result['message']
            test_results.append({
                'name': 'Example',
                'passed': passed,
                'message': result['message'] if not passed else ''
            })
            if result.get('runtime_ms'):
                overall_runtime = max(overall_runtime, result['runtime_ms'])
            if result.get('memory_kb'):
                overall_memory = max(overall_memory, result['memory_kb'])

        return Response({
            'status': overall_status,
            'runtime_ms': overall_runtime,
            'memory_kb': overall_memory,
            'test_results': test_results,
        })

class SubmitView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        problem_id = request.data.get('problem_id')
        code = request.data.get('code')
        problem, _ = get_problem_by_id(problem_id, request.user)

        problem.attempts += 1
        problem.save()

        tests = problem.test_cases + problem.examples
        test_results = []
        overall_status = 'Accepted'
        overall_runtime = 0
        overall_memory = 0

        for i, test in enumerate(tests):
            input_data = test.get('input', '')
            expected = test.get('output', '').strip()
            result = execute_code(code, input_data)
            passed = result['passed'] and result.get('output', '') == expected
            if not passed:
                overall_status = 'Wrong Answer' if result['passed'] else result['message']
            test_results.append({
                'name': f'Test {i+1}',
                'passed': passed,
                'message': result['message'] if not passed else ''
            })
            if result.get('runtime_ms'):
                overall_runtime = max(overall_runtime, result['runtime_ms'])
            if result.get('memory_kb'):
                overall_memory = max(overall_memory, result['memory_kb'])

        ct = ContentType.objects.get_for_model(problem.__class__)
        submission = Submission.objects.create(
            user=request.user,
            content_type=ct,
            object_id=problem.id,
            code=code,
            status=overall_status,
            runtime_ms=overall_runtime if overall_status == 'Accepted' else None,
            memory_kb=overall_memory if overall_status == 'Accepted' else None,
        )

        if overall_status == 'Accepted':
            problem.solves += 1
            problem.save()

            progress, _ = UserProgress.objects.get_or_create(user=request.user)
            progress.solved_count += 1
            points_map = {'Easy': 10, 'Medium': 20, 'Hard': 30}
            progress.points += points_map.get(problem.difficulty, 0)

            today = timezone.now().date()
            if progress.last_solve_date:
                if today == progress.last_solve_date + timedelta(days=1):
                    progress.current_streak += 1
                elif today > progress.last_solve_date + timedelta(days=1):
                    progress.current_streak = 1
            else:
                progress.current_streak = 1
            progress.last_solve_date = today
            progress.save()

        return Response({
            'status': overall_status,
            'runtime_ms': overall_runtime,
            'memory_kb': overall_memory,
            'message': '' if overall_status == 'Accepted' else 'Failed some tests',
            'test_results': test_results,
        })

class ProgressView(views.APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = []

    def get(self, request):
        queryset = UserProgress.objects.order_by('-points')
        serializer = UserProgressSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        return Response({'message': 'Progress updated'}, status=status.HTTP_200_OK)