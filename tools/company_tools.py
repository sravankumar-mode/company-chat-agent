"""Company information tools for agents."""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


class CompanyDataLoader:
    """Load and manage company data from JSON files."""
    
    DATA_DIR = Path(__file__).parent.parent / "data"
    
    @classmethod
    def load_holidays(cls) -> List[Dict[str, Any]]:
        """Load company holidays."""
        with open(cls.DATA_DIR / "holidays.json", "r") as f:
            data = json.load(f)
        return data.get("holidays", [])
    
    @classmethod
    def load_events(cls) -> List[Dict[str, Any]]:
        """Load company events."""
        with open(cls.DATA_DIR / "events.json", "r") as f:
            data = json.load(f)
        return data.get("events", [])
    
    @classmethod
    def load_employees(cls) -> Dict[str, Any]:
        """Load employee and department information."""
        with open(cls.DATA_DIR / "employees.json", "r") as f:
            data = json.load(f)
        return data
    
    @classmethod
    def load_hr_policies(cls) -> Dict[str, Any]:
        """Load HR policies."""
        with open(cls.DATA_DIR / "hr_policies.json", "r") as f:
            data = json.load(f)
        return data.get("policies", {})


class HolidayTools:
    """Tools for querying holiday information."""
    
    @staticmethod
    def get_upcoming_holidays(days_ahead: int = 90) -> str:
        """Get upcoming holidays within the specified number of days."""
        holidays = CompanyDataLoader.load_holidays()
        today = datetime.now().date()
        
        upcoming = [
            h for h in holidays
            if datetime.strptime(h["date"], "%Y-%m-%d").date() > today
            and (datetime.strptime(h["date"], "%Y-%m-%d").date() - today).days <= days_ahead
        ]
        
        if not upcoming:
            return "No upcoming holidays in the next 90 days."
        
        result = "Upcoming holidays:\n"
        for holiday in sorted(upcoming, key=lambda x: x["date"]):
            result += f"- {holiday['date']}: {holiday['name']} ({holiday['type']})\n"
        
        return result
    
    @staticmethod
    def is_holiday(date_str: str) -> bool:
        """Check if a specific date is a company holiday."""
        holidays = CompanyDataLoader.load_holidays()
        return any(h["date"] == date_str for h in holidays)
    
    @staticmethod
    def is_working_day(date_str: str) -> bool:
        """Check if a date is a working day (not holiday and not weekend)."""
        from datetime import datetime
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        is_weekend = date_obj.weekday() >= 5  # Saturday=5, Sunday=6
        is_holiday = HolidayTools.is_holiday(date_str)
        return not (is_weekend or is_holiday)


class HRTools:
    """Tools for HR-related queries."""
    
    @staticmethod
    def get_leave_policy() -> str:
        """Get leave policy information."""
        policies = CompanyDataLoader.load_hr_policies()
        
        result = "Company Leave Policies:\n\n"
        result += f"Working Hours: {policies['working_hours']['start']} to {policies['working_hours']['end']}\n"
        result += f"Break Time: {policies['working_hours']['break']}\n\n"
        
        result += "Leave Entitlements:\n"
        result += f"- Annual Leave: {policies['annual_leave']['days']} days\n"
        result += f"- Sick Leave: {policies['sick_leave']['days']} days\n"
        result += f"- Casual Leave: {policies['casual_leave']['days']} days\n"
        result += f"- Maternity Leave: {policies['maternity_leave']['days']} days\n"
        result += f"- Paternity Leave: {policies['paternity_leave']['days']} days\n"
        result += f"- Work from Home: {policies['work_from_home']['days_per_week']} days per week\n"
        
        return result
    
    @staticmethod
    def get_leave_balance(employee_name: str) -> str:
        """Get leave balance for an employee (mock data)."""
        # This is mock data. In production, this would query an actual database.
        leave_balances = {
            "alice johnson": {"annual": 15, "sick": 8, "casual": 3},
            "bob smith": {"annual": 18, "sick": 10, "casual": 2},
            "carol davis": {"annual": 12, "sick": 7, "casual": 5},
        }
        
        balance = leave_balances.get(employee_name.lower())
        if not balance:
            return f"No leave balance found for employee: {employee_name}"
        
        return (
            f"Leave balance for {employee_name}:\n"
            f"- Annual Leave: {balance['annual']} days remaining\n"
            f"- Sick Leave: {balance['sick']} days remaining\n"
            f"- Casual Leave: {balance['casual']} days remaining"
        )


class EventTools:
    """Tools for company events."""
    
    @staticmethod
    def get_upcoming_events(days_ahead: int = 30) -> str:
        """Get upcoming company events."""
        events = CompanyDataLoader.load_events()
        today = datetime.now().date()
        
        upcoming = [
            e for e in events
            if datetime.strptime(e["date"], "%Y-%m-%d").date() > today
            and (datetime.strptime(e["date"], "%Y-%m-%d").date() - today).days <= days_ahead
        ]
        
        if not upcoming:
            return "No upcoming events in the next 30 days."
        
        result = "Upcoming company events:\n"
        for event in sorted(upcoming, key=lambda x: x["date"]):
            result += f"\n- **{event['title']}** ({event['type'].upper()})\n"
            result += f"  Date: {event['date']} at {event['time']}\n"
            result += f"  Location: {event['location']}\n"
            result += f"  Description: {event['description']}\n"
        
        return result
    
    @staticmethod
    def get_event_by_title(title: str) -> str:
        """Get details of a specific event by title."""
        events = CompanyDataLoader.load_events()
        
        for event in events:
            if title.lower() in event["title"].lower():
                return (
                    f"Event: {event['title']}\n"
                    f"Date: {event['date']} at {event['time']}\n"
                    f"Location: {event['location']}\n"
                    f"Type: {event['type']}\n"
                    f"Description: {event['description']}"
                )
        
        return f"Event not found: {title}"


class TeamTools:
    """Tools for team and employee information."""
    
    @staticmethod
    def get_employee_info(name: str) -> str:
        """Get information about an employee."""
        data = CompanyDataLoader.load_employees()
        employees = data.get("employees", [])
        
        for emp in employees:
            if name.lower() in emp["name"].lower():
                result = f"Employee: {emp['name']}\n"
                result += f"Email: {emp['email']}\n"
                result += f"Department: {emp['department']}\n"
                result += f"Team: {emp['team']}\n"
                result += f"Role: {emp['role']}\n"
                if emp['manager']:
                    manager = next((e for e in employees if e['id'] == emp['manager']), None)
                    if manager:
                        result += f"Manager: {manager['name']}\n"
                result += f"Start Date: {emp['start_date']}\n"
                return result
        
        return f"Employee not found: {name}"
    
    @staticmethod
    def get_team_members(team_name: str) -> str:
        """Get members of a specific team."""
        data = CompanyDataLoader.load_employees()
        employees = data.get("employees", [])
        
        team_members = [e for e in employees if e["team"].lower() == team_name.lower()]
        
        if not team_members:
            return f"Team not found or no members: {team_name}"
        
        result = f"Team: {team_name}\n"
        for emp in team_members:
            result += f"- {emp['name']} ({emp['role']})\n"
        
        return result
    
    @staticmethod
    def get_department_info(department_name: str) -> str:
        """Get information about a department."""
        data = CompanyDataLoader.load_employees()
        departments = data.get("departments", [])
        employees = data.get("employees", [])
        
        for dept in departments:
            if department_name.lower() in dept["name"].lower():
                result = f"Department: {dept['name']}\n"
                result += f"Description: {dept['description']}\n"
                result += f"Teams: {', '.join(dept['teams'])}\n\n"
                
                # Get department members
                dept_members = [e for e in employees if e["department"] == dept["name"]]
                result += f"Members ({len(dept_members)}):\n"
                for emp in dept_members:
                    result += f"- {emp['name']} ({emp['role']})\n"
                
                return result
        
        return f"Department not found: {department_name}"
