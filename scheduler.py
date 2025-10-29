"""
Intelligent scheduling system for social media posts.

Features:
- Avoids weekends (Saturday/Sunday)
- Avoids US federal holidays
- Time slot management (4 slots per day: 9am, 11am, 1pm, 3pm EST)
- Automatic scheduling to next available slot
"""
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
import holidays


class PostScheduler:
    """Manages scheduling of social media posts with business day and time slot logic."""
    
    # Time slots in Eastern Time (EST/EDT)
    TIME_SLOTS = [
        (9, 0),   # 9:00 AM
        (13, 0),  # 1:00 PM
        (11, 0),  # 11:00 AM
        (15, 0),  # 3:00 PM
    ]
    
    MAX_POSTS_PER_DAY = 4
    
    def __init__(self):
        """Initialize scheduler with US holidays."""
        self.us_holidays = holidays.US(years=range(2024, 2030))
        self.eastern = pytz.timezone('US/Eastern')
    
    def is_business_day(self, date: datetime) -> bool:
        """
        Check if a date is a business day (not weekend or US holiday).
        
        Args:
            date: Date to check
            
        Returns:
            True if business day, False otherwise
        """
        # Check if weekend (Saturday=5, Sunday=6)
        if date.weekday() >= 5:
            return False
        
        # Check if US federal holiday
        if date.date() in self.us_holidays:
            return False
        
        return True
    
    def get_next_business_day(self, start_date: datetime) -> datetime:
        """
        Get the next business day starting from a given date.
        
        Args:
            start_date: Starting date
            
        Returns:
            Next business day
        """
        current = start_date
        while not self.is_business_day(current):
            current += timedelta(days=1)
        return current
    
    def create_scheduled_time(self, date: datetime, slot_index: int) -> datetime:
        """
        Create a scheduled datetime for a specific time slot.
        
        Args:
            date: The date to schedule on
            slot_index: Index of time slot (0-3)
            
        Returns:
            Datetime in Eastern Time with the specified slot
        """
        if slot_index >= len(self.TIME_SLOTS):
            slot_index = len(self.TIME_SLOTS) - 1
        
        hour, minute = self.TIME_SLOTS[slot_index]
        
        # Create datetime in Eastern timezone
        scheduled = self.eastern.localize(
            datetime(date.year, date.month, date.day, hour, minute, 0)
        )
        
        return scheduled
    
    def get_available_slot(self, date: datetime, existing_posts: List[datetime]) -> Optional[int]:
        """
        Find the next available time slot for a given date.
        
        Args:
            date: Date to check
            existing_posts: List of already scheduled datetimes for this date
            
        Returns:
            Available slot index (0-3), or None if day is full
        """
        # Normalize existing posts to same date for comparison
        existing_slots = []
        for post_time in existing_posts:
            # Convert to Eastern if needed
            if post_time.tzinfo is None:
                post_time = self.eastern.localize(post_time)
            else:
                post_time = post_time.astimezone(self.eastern)
            
            # Check if it's on the same date
            if post_time.date() == date.date():
                existing_slots.append((post_time.hour, post_time.minute))
        
        # Find first available slot
        for idx, slot in enumerate(self.TIME_SLOTS):
            if slot not in existing_slots:
                return idx
        
        # Day is full
        return None
    
    def can_schedule_within_days(
        self,
        num_messages: int,
        existing_schedules: List[datetime],
        max_days: int,
        start_date: Optional[datetime] = None
    ) -> bool:
        """
        Check if all messages can be scheduled within max_days from now.
        
        Args:
            num_messages: Number of messages to schedule
            existing_schedules: List of already scheduled post times
            max_days: Maximum days ahead to schedule
            start_date: Starting date (defaults to tomorrow)
            
        Returns:
            True if all messages can fit within max_days, False otherwise
        """
        if start_date is None:
            start_date = datetime.now(self.eastern) + timedelta(days=1)
        
        # Ensure start date is timezone-aware
        if start_date.tzinfo is None:
            start_date = self.eastern.localize(start_date)
        
        # Calculate cutoff date
        cutoff_date = start_date + timedelta(days=max_days)
        
        # Normalize to start of day
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        current_date = self.get_next_business_day(current_date)
        
        scheduled_count = 0
        temp_schedules = []
        
        # Try to schedule all messages
        for _ in range(num_messages):
            # Check if we've exceeded the time limit
            if current_date >= cutoff_date:
                return False  # Can't fit all messages within max_days
            
            # Find available slot on current date
            slot_index = self.get_available_slot(current_date, existing_schedules + temp_schedules)
            
            if slot_index is not None:
                # Slot available on current date
                scheduled_time = self.create_scheduled_time(current_date, slot_index)
                temp_schedules.append(scheduled_time)
                scheduled_count += 1
            else:
                # Day is full, move to next business day
                current_date += timedelta(days=1)
                current_date = self.get_next_business_day(current_date)
                continue  # Try again on the new day
            
            # Move to next day for next message from this blog post
            current_date += timedelta(days=1)
            current_date = self.get_next_business_day(current_date)
        
        return scheduled_count == num_messages
    
    def schedule_messages(
        self,
        num_messages: int,
        existing_schedules: List[datetime],
        start_date: Optional[datetime] = None,
        max_days: Optional[int] = None
    ) -> List[datetime]:
        """
        Schedule multiple messages intelligently.
        
        IMPORTANT: Messages from the same blog post are scheduled ONE PER DAY.
        This ensures each blog post's messages are distributed over multiple days.
        
        Args:
            num_messages: Number of messages to schedule
            existing_schedules: List of already scheduled post times
            start_date: Starting date (defaults to tomorrow)
            max_days: Maximum days ahead to schedule (optional check)
            
        Returns:
            List of scheduled datetimes
            
        Raises:
            ValueError: If unable to schedule within max_days (if specified)
        """
        if start_date is None:
            start_date = datetime.now(self.eastern) + timedelta(days=1)
        
        # Ensure start date is timezone-aware
        if start_date.tzinfo is None:
            start_date = self.eastern.localize(start_date)
        
        # Check if scheduling is possible within max_days
        if max_days is not None:
            if not self.can_schedule_within_days(num_messages, existing_schedules, max_days, start_date):
                cutoff = start_date + timedelta(days=max_days)
                raise ValueError(
                    f"Cannot schedule {num_messages} messages within {max_days} days "
                    f"(by {cutoff.strftime('%Y-%m-%d')}). Schedule is full."
                )
        
        # Normalize to start of day
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Ensure it's a business day
        current_date = self.get_next_business_day(current_date)
        
        scheduled_times = []
        
        # Schedule ONE MESSAGE PER DAY for this blog post
        for _ in range(num_messages):
            # Find available slot on current date
            slot_index = self.get_available_slot(current_date, existing_schedules + scheduled_times)
            
            if slot_index is not None:
                # Slot available on current date
                scheduled_time = self.create_scheduled_time(current_date, slot_index)
                scheduled_times.append(scheduled_time)
            else:
                # Day is full (4 posts already), move to next business day
                current_date += timedelta(days=1)
                current_date = self.get_next_business_day(current_date)
                
                # Try first slot on new day
                slot_index = self.get_available_slot(current_date, existing_schedules + scheduled_times)
                if slot_index is not None:
                    scheduled_time = self.create_scheduled_time(current_date, slot_index)
                    scheduled_times.append(scheduled_time)
                else:
                    # Should never happen, but handle gracefully
                    raise ValueError(f"Unable to schedule message on {current_date}")
            
            # MOVE TO NEXT DAY for next message from this blog post
            current_date += timedelta(days=1)
            current_date = self.get_next_business_day(current_date)
        
        return scheduled_times
    
    def is_time_to_post(self, scheduled_time: datetime, current_time: Optional[datetime] = None) -> bool:
        """
        Check if it's time to post a scheduled message.
        
        Uses a time window approach: posts messages scheduled for the current time slot
        or earlier, allowing for GitHub cron variance.
        
        Args:
            scheduled_time: When the message is scheduled for
            current_time: Current time (defaults to now)
            
        Returns:
            True if should post now, False otherwise
        """
        if current_time is None:
            current_time = datetime.now(self.eastern)
        
        # Ensure both times are in Eastern timezone
        if scheduled_time.tzinfo is None:
            scheduled_time = self.eastern.localize(scheduled_time)
        else:
            scheduled_time = scheduled_time.astimezone(self.eastern)
        
        if current_time.tzinfo is None:
            current_time = self.eastern.localize(current_time)
        else:
            current_time = current_time.astimezone(self.eastern)
        
        # Get the current time slot (9am, 11am, 1pm, 3pm)
        current_slot = self._get_current_time_slot(current_time)
        scheduled_slot = self._get_current_time_slot(scheduled_time)
        
        slot_names = {0: "9am", 1: "11am", 2: "1pm", 3: "3pm", -1: "before 9am"}
        print(f"   Time slot check: current={current_slot} ({slot_names.get(current_slot, 'unknown')}), scheduled={scheduled_slot} ({slot_names.get(scheduled_slot, 'unknown')})")
        print(f"   Decision: {scheduled_slot} <= {current_slot} = {scheduled_slot <= current_slot}")
        
        # Post if scheduled for current slot or earlier
        return scheduled_slot <= current_slot
    
    def _get_current_time_slot(self, dt: datetime) -> int:
        """
        Get the time slot index for a given datetime.
        
        Returns:
            0: 9am slot
            1: 11am slot  
            2: 1pm slot
            3: 3pm slot
        """
        hour = dt.hour
        minute = dt.minute
        
        # Determine which slot this time falls into
        if hour < 9 or (hour == 9 and minute < 30):
            return 0  # 9am slot
        elif hour < 11 or (hour == 11 and minute < 30):
            return 1  # 11am slot
        elif hour < 13 or (hour == 13 and minute < 30):
            return 2  # 1pm slot
        elif hour < 15 or (hour == 15 and minute < 30):
            return 3  # 3pm slot
        else:
            return 3  # Default to 3pm slot for late times
    
    def format_schedule_summary(self, scheduled_times: List[datetime]) -> str:
        """
        Create a human-readable summary of scheduled posts.
        
        Args:
            scheduled_times: List of scheduled datetimes
            
        Returns:
            Formatted string summary
        """
        lines = ["Scheduled Posts:"]
        
        for idx, scheduled_time in enumerate(scheduled_times, 1):
            # Convert to Eastern
            et_time = scheduled_time.astimezone(self.eastern)
            day_name = et_time.strftime('%A')
            date_str = et_time.strftime('%Y-%m-%d')
            time_str = et_time.strftime('%I:%M %p')
            
            lines.append(f"  {idx}. {day_name}, {date_str} at {time_str} ET")
        
        return "\n".join(lines)

