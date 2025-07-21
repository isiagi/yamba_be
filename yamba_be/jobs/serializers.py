from rest_framework import serializers
from .models import Job, Category, Skill

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    posted_by = serializers.StringRelatedField(read_only=True)
    is_expired = serializers.ReadOnlyField()
    application_count = serializers.SerializerMethodField()
    
    # Write-only fields for creating/updating
    # company_id = serializers.IntegerField(write_only=True)
    category_id = serializers.IntegerField(write_only=True)
    skill_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('posted_by', 'created_at', 'updated_at')
    
    def get_application_count(self, obj):
        return obj.applications.count()
    
    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        job = Job.objects.create(**validated_data)
        if skill_ids:
            job.skills.set(skill_ids)
        return job
    
    def update(self, instance, validated_data):
        skill_ids = validated_data.pop('skill_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skill_ids is not None:
            instance.skills.set(skill_ids)
        
        return instance


class JobListSerializer(serializers.ModelSerializer):
    """Simplified serializer for job listings"""
    # company_name = serializers.CharField(source='company.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Job
        fields = ('id', 'title', 'category_name', 'job_type', 
                 'location', 'remote_ok', 'salary_min', 'salary_max', 'created_at')