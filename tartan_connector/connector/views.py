import uuid
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SourceEmployee, UnifiedEmployee, OAuthClient, AccessToken
from .permissions import IsOAuthTokenValid

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
    def get(self, request):
        data = [
            {
                "id": "adp-1001",
                "employeeId": "EMP-1042",
                "firstName": "John",
                "middleInitial": "M.",
                "lastName": "Doe",
                "preferredName": "Johnny",
                "userName": "johndoe",
                "workEmail": "john.doe@acmecorp.com",
                "personalEmail": "john.doe@gmail.com",
                "mobilePhone": "+1-415-555-0199",
                "manager": "EMP-1023",
                "payGroup": "Engineering Team",
                "ssn": "XXX-XX-4321",
                "gender": "Male",
                "ethnicity": "Caucasian",
                "maritalStatus": "Married",
                "dateOfBirth": "1989-04-15T00:00:00Z",
                "startDate": "2022-03-01T00:00:00Z",
                "remoteCreatedAt": "2022-03-01T12:45:00Z",
                "employmentStatus": "Active",
                "terminationDate": None,
                "avatarUrl": "https://cdn.acmecorp.com/avatars/john_doe.png",
                "department": "Engineering",
                "company": {
                    "legalName": "Acme Corporation Inc.",
                    "displayName": "Acme Corp",
                    "eins": ["12-3456789"]
                },
                "employments": [
                    {
                        "jobTitle": "Senior Software Engineer",
                        "payRate": "9500.0000",
                        "payPeriod": "Monthly",
                        "payFrequency": "12",
                        "payCurrency": "USD",
                        "flsaStatus": "Exempt",
                        "effectiveDate": "2023-01-01T00:00:00Z",
                        "employmentType": "Full-Time"
                    },
                    {
                        "jobTitle": "Software Engineer",
                        "payRate": "8000.0000",
                        "payPeriod": "Monthly",
                        "payFrequency": "12",
                        "payCurrency": "USD",
                        "flsaStatus": "Exempt",
                        "effectiveDate": "2022-03-01T00:00:00Z",
                        "employmentType": "Full-Time"
                    }
                ],
                "salaries": [
                    {
                        "payDate": "2025-09-30T00:00:00Z",
                        "startDate": "2025-09-01T00:00:00Z",
                        "endDate": "2025-09-30T23:59:59Z",
                        "totalHours": 160,
                        "payFrequency": "Monthly",
                        "salaryType": "Base",
                        "salaryMethod": "Direct Deposit",
                        "grossPayDetails": {"base": 9500, "bonus": 500, "overtime": 0},
                        "netPayDetails": {"amount": 7100, "currency": "USD"},
                        "taxDetails": [{"type": "Federal Tax", "amount": 900}, {"type": "State Tax", "amount": 250}],
                        "deductionDetails": [{"type": "401K", "amount": 200}],
                        "contributionDetails": [{"type": "Health Insurance", "amount": 500}]
                    }
                ],
                "benefits": [
                    {
                        "providerName": "United Healthcare",
                        "employeeContribution": "250.0000",
                        "companyContribution": "500.0000",
                        "startDate": "2024-01-01T00:00:00Z",
                        "endDate": None,
                        "employerBenefit": "Health Plan A"
                    }
                ],
                "locations": {
                    "home": {
                        "name": "John Doe Residence",
                        "phoneNumber": "+1-415-555-0197",
                        "street1": "123 Main St",
                        "street2": "Apt 4B",
                        "city": "San Francisco",
                        "state": "California",
                        "zipCode": "94105",
                        "country": "USA",
                        "locationType": "HOME"
                    },
                    "work": {
                        "name": "Acme Corp HQ",
                        "phoneNumber": "+1-415-555-0198",
                        "street1": "500 Market Street",
                        "street2": "Suite 1500",
                        "city": "San Francisco",
                        "state": "California",
                        "zipCode": "94105",
                        "country": "USA",
                        "locationType": "WORK"
                    }
                }
            }
        ]
        return Response(data)

class TransformEmployeesView(APIView):
    permission_classes = [IsOAuthTokenValid]

    def post(self, request):
        mock_view = MockADPEmployeesView()
        adp_response = mock_view.get(request).data

        transformed = []
        for emp in adp_response:
            source = SourceEmployee.objects.create(source_id=emp.get("id", uuid.uuid4().hex), raw_json=emp)
            t = {
                "employee_number": emp.get("employeeId"),
                "first_name": emp.get("firstName"),
                "middle_name": emp.get("middleInitial"),
                "last_name": emp.get("lastName"),
                "preferred_name": emp.get("preferredName"),
                "display_full_name": f"{emp.get('firstName', '')} {emp.get('middleInitial','')} {emp.get('lastName','')}".replace("  ", " ").strip(),
                "username": emp.get("userName"),
                "work_email": emp.get("workEmail"),
                "personal_email": emp.get("personalEmail"),
                "mobile_phone_number": emp.get("mobilePhone"),
                "manager_id": emp.get("manager"),
                "pay_group": emp.get("payGroup"),
                "ssn": emp.get("ssn"),
                "gender": emp.get("gender"),
                "ethnicity": emp.get("ethnicity"),
                "marital_status": emp.get("maritalStatus"),
                "date_of_birth": emp.get("dateOfBirth"),
                "start_date": emp.get("startDate"),
                "remote_created_at": emp.get("remoteCreatedAt"),
                "employment_status": emp.get("employmentStatus"),
                "termination_date": emp.get("terminationDate"),
                "avatar": emp.get("avatarUrl"),
                "department": emp.get("department"),
                "company": emp.get("company"),
                "employments": emp.get("employments", []),
                "salaries": emp.get("salaries", []),
                "benefits": emp.get("benefits", []),
                "locations": {
                    "home": emp.get("locations", {}).get("home"),
                    "work": emp.get("locations", {}).get("work"),
                }
            }

            ue = UnifiedEmployee.objects.create(employee_number=t["employee_number"] or uuid.uuid4().hex, unified_json=t)
            transformed.append(t)
        return Response(transformed, status=status.HTTP_200_OK)
