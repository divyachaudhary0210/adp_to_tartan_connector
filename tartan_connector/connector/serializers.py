from rest_framework import serializers
from .models import SourceEmployee, UnifiedEmployee

class SourceEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceEmployee
        fields = ["source_id", "raw_json", "fetched_at"]

class UnifiedEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnifiedEmployee
        fields = ["employee_number", "unified_json", "transformed_at"]
