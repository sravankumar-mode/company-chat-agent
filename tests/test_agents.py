"""Tests for company assistant agents."""

import pytest
import asyncio
from pathlib import Path
from tools.company_tools import (
    HolidayTools, HRTools, EventTools, TeamTools, CompanyDataLoader
)


class TestCompanyDataLoader:
    """Test data loading functionality."""
    
    def test_load_holidays(self):
        """Test loading holiday data."""
        holidays = CompanyDataLoader.load_holidays()
        assert isinstance(holidays, list)
        assert len(holidays) > 0
        assert "date" in holidays[0]
        assert "name" in holidays[0]
    
    def test_load_events(self):
        """Test loading events data."""
        events = CompanyDataLoader.load_events()
        assert isinstance(events, list)
        assert len(events) > 0
        assert "title" in events[0]
        assert "date" in events[0]
    
    def test_load_employees(self):
        """Test loading employee data."""
        data = CompanyDataLoader.load_employees()
        assert isinstance(data, dict)
        assert "employees" in data
        assert "departments" in data
        assert len(data["employees"]) > 0
    
    def test_load_hr_policies(self):
        """Test loading HR policies."""
        policies = CompanyDataLoader.load_hr_policies()
        assert isinstance(policies, dict)
        assert "working_hours" in policies
        assert "annual_leave" in policies


class TestHolidayTools:
    """Test holiday-related tools."""
    
    def test_get_upcoming_holidays(self):
        """Test getting upcoming holidays."""
        result = HolidayTools.get_upcoming_holidays(days_ahead=365)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_is_holiday(self):
        """Test checking if a date is a holiday."""
        # Test with a known holiday
        result = HolidayTools.is_holiday("2024-01-26")
        assert isinstance(result, bool)
    
    def test_is_working_day(self):
        """Test checking if a date is a working day."""
        result = HolidayTools.is_working_day("2024-01-29")
        assert isinstance(result, bool)


class TestHRTools:
    """Test HR-related tools."""
    
    def test_get_leave_policy(self):
        """Test getting leave policy."""
        result = HRTools.get_leave_policy()
        assert isinstance(result, str)
        assert "Leave" in result or "leave" in result
        assert "days" in result.lower()
    
    def test_get_leave_balance(self):
        """Test getting leave balance."""
        result = HRTools.get_leave_balance("Alice Johnson")
        assert isinstance(result, str)
        assert len(result) > 0


class TestEventTools:
    """Test event-related tools."""
    
    def test_get_upcoming_events(self):
        """Test getting upcoming events."""
        result = EventTools.get_upcoming_events()
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_event_by_title(self):
        """Test getting event by title."""
        # Get first event name and search for it
        events = CompanyDataLoader.load_events()
        if events:
            first_event_title = events[0]["title"]
            result = EventTools.get_event_by_title(first_event_title)
            assert isinstance(result, str)
            assert first_event_title in result or "not found" in result


class TestTeamTools:
    """Test team-related tools."""
    
    def test_get_employee_info(self):
        """Test getting employee information."""
        result = TeamTools.get_employee_info("Alice")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_team_members(self):
        """Test getting team members."""
        result = TeamTools.get_team_members("Backend")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_get_department_info(self):
        """Test getting department information."""
        result = TeamTools.get_department_info("Engineering")
        assert isinstance(result, str)
        assert "Engineering" in result or "not found" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
