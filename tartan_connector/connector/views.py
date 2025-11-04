import uuid
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SourceEmployee, UnifiedEmployee, OAuthClient, AccessToken
from .permissions import IsOAuthTokenValid
from .field_mappings import ADP_TO_TARTAN_FIELD_MAP
from .permissions import IsOAuthTokenValid

import re

def get_nested_value(data, path):
    parts = re.split(r'\.(?![^\[]*\])', path)
    val = data
    for part in parts:
        match = re.match(r'(\w+)(?:\[(\d+)\])?', part)
        if not match:
            return None
        key, index = match.groups()
        val = val.get(key) if isinstance(val, dict) else None
        if val is None:
            return None
        if index is not None:
            val = val[int(index)] if len(val) > int(index) else None
        if val is None:
            return None
    return val


def set_nested_value(data, path, value):
    parts = re.split(r'\.(?![^\[]*\])', path)
    ref = data
    for i, part in enumerate(parts):
        match = re.match(r'(\w+)(?:\[(\d+)\])?', part)
        if not match:
            return
        key, index = match.groups()

        if index is not None:
            index = int(index)
            ref.setdefault(key, [])
            while len(ref[key]) <= index:
                ref[key].append({})
            if i == len(parts) - 1:
                ref[key][index] = value
            else:
                ref = ref[key][index]
        else:
            if i == len(parts) - 1:
                ref[key] = value
            else:
                ref = ref.setdefault(key, {})


class TokenView(APIView):
    def post(self, request):
        client_id = request.data.get("client_id")
        client_secret = request.data.get("client_secret")
        grant_type = request.data.get("grant_type")
        if grant_type != "client_credentials":
            return Response({"error": "unsupported_grant_type"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            client = OAuthClient.objects.get(client_id=client_id, client_secret=client_secret)
        except OAuthClient.DoesNotExist:
            return Response({"error": "invalid_client"}, status=status.HTTP_401_UNAUTHORIZED)

        token_str = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(hours=1)
        at = AccessToken.objects.create(token=token_str, client=client, expires_at=expires_at)
        return Response({
            "access_token": token_str,
            "token_type": "Bearer",
            "expires_in": int((expires_at - timezone.now()).total_seconds())
        })


class MockADPEmployeesView(APIView):
    """
    Mock API to simulate ADP employee data.
    Includes nested structures like company, salaries, deductions, and benefits.
    """

    def get(self, request):
        data = [
            {
                "id": "adp-1001",
                "employeeId": "EMP-1042",
                "firstName": "John",
                "middleInitial": "M",
                "lastName": "Doe",
                "email": "john.doe@acmecorp.com",
                "dob": "1989-04-15",
                "gender": "Male",
                "departmentName": "Engineering",
                "location": "San Francisco",
                "managerName": "Alice Johnson",
                "workPhone": "+1-415-555-0199",
                "company": {
                    "legalName": "Acme Corporation Inc.",
                    "displayName": "Acme Corp",
                    "location": "California"
                },
                "salaries": [
                    {
                        "payDate": "2025-09-30T00:00:00Z",
                        "grossPay": 9500,
                        "deductions": [{"type": "401K", "amount": 200}],
                        "contributions": [{"type": "Health Insurance", "amount": 500}]
                    }
                ],
                "benefits": [
                    {
                        "providerName": "United Healthcare",
                        "employeeContribution": 250,
                        "companyContribution": 500,
                        "planName": "Health Plan A"
                    }
                ]
            },
            {
                "id": "adp-1002",
                "employeeId": "EMP-2045",
                "firstName": "Ava",
                "lastName": "Smith",
                "email": "ava.smith@acmecorp.com",
                "dob": "1992-11-20",
                "gender": "Female",
                "departmentName": "Finance",
                "location": "New York",
                "managerName": "Robert Brown",
                "workPhone": "+1-212-555-0456",
                "company": {
                    "legalName": "Acme Corporation Inc.",
                    "displayName": "Acme Corp East",
                    "location": "New York"
                },
                "salaries": [
                    {
                        "payDate": "2025-09-30T00:00:00Z",
                        "grossPay": 8800,
                        "deductions": [{"type": "Tax", "amount": 900}],
                        "contributions": [{"type": "401K Match", "amount": 250}]
                    }
                ],
                "benefits": [
                    {
                        "providerName": "MetLife",
                        "employeeContribution": 180,
                        "companyContribution": 400,
                        "planName": "Dental Plan"
                    }
                ]
            }
        ]
        return Response(data, status=status.HTTP_200_OK)


class TransformEmployeesView(APIView):
    permission_classes = [IsOAuthTokenValid]

    def post(self, request):
        mock_data = MockADPEmployeesView().get(request).data
        mapping_dict = ADP_TO_TARTAN_FIELD_MAP
        transformed = []

        for emp in mock_data:
            tartan = {}

            for adp_key, tartan_key in mapping_dict.items():
                val = get_nested_value(emp, adp_key)
                if val is not None:
                    set_nested_value(tartan, tartan_key, val)

            transformed.append(tartan)

        return Response(transformed, status=status.HTTP_200_OK)


