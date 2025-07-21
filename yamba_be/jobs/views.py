from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Skill, Job
from .serializers import JobListSerializer,JobSerializer, CategorySerializer, SkillSerializer
from rest_framework.decorators import action
from rest_framework.response import Response



class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company__name', 'location']
    filterset_fields = ['job_type', 'experience_level', 'category', 'remote_ok']
    ordering_fields = ['created_at', 'salary_min', 'salary_max']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer

    
    def perform_create(self, serializer):
        # Additional check to ensure only employers can post jobs
        if self.request.user.user_type != 'employer':
            raise PermissionError("Only employers can post jobs")
        serializer.save(posted_by=self.request.user)
    
    # @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    # def apply(self, request, pk=None):
    #     job = self.get_object()
        
    #     # Check if user already applied
    #     if Application.objects.filter(job=job, applicant=request.user).exists():
    #         return Response({'error': 'Already applied to this job'}, 
    #                       status=status.HTTP_400_BAD_REQUEST)
        
    #     # Check if job is expired
    #     if job.is_expired:
    #         return Response({'error': 'Job application deadline has passed'}, 
    #                       status=status.HTTP_400_BAD_REQUEST)
        
    #     serializer = ApplicationSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save(job=job, applicant=request.user)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)