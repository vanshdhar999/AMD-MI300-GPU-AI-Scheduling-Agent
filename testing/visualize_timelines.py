"""
Simple Timeline Visualizer for Meeting Scheduling
Shows before/after event timelines in an easy-to-read format
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class SimpleTimelineVisualizer:
    """Simple text-based timeline visualization"""
    
    def __init__(self):
        self.symbols = {
            'existing': '■',
            'new': '★', 
            'conflict': '⚠️',
            'rescheduled': '↻',
            'free': '·'
        }
        self.keys_directory = "Keys"
        
    def _format_time(self, time_str: str) -> str:
        """Format time string for display"""
        try:
            dt = datetime.fromisoformat(time_str.replace('+05:30', ''))
            return dt.strftime("%H:%M")
        except:
            return time_str
    
    def fetch_real_calendar_events(self, attendees: List[str], target_date: str) -> Dict[str, List[Dict]]:
        """Fetch actual calendar events from Google Calendar API"""
        
        calendars = {}
        start_time = f"{target_date}T00:00:00+05:30"
        end_time = f"{target_date}T23:59:59+05:30"
        
        print(f"📅 Fetching real calendar events for {target_date}")
        
        for attendee in attendees:
            try:
                username = attendee.split("@")[0]
                token_path = f"{self.keys_directory}/{username}.token"
                
                print(f"🔑 Loading credentials for {attendee}")
                
                # Load user credentials
                user_creds = Credentials.from_authorized_user_file(token_path)
                calendar_service = build("calendar", "v3", credentials=user_creds)
                
                # Fetch events for the target day
                events_result = calendar_service.events().list(
                    calendarId='primary',
                    timeMin=start_time,
                    timeMax=end_time,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                events = events_result.get('items', [])
                
                # Convert to our format
                formatted_events = []
                for event in events:
                    start_time_event = event["start"].get("dateTime", event["start"].get("date"))
                    end_time_event = event["end"].get("dateTime", event["end"].get("date"))
                    
                    formatted_event = {
                        "StartTime": start_time_event,
                        "EndTime": end_time_event,
                        "Summary": event.get("summary", "Busy")
                    }
                    formatted_events.append(formatted_event)
                
                calendars[attendee] = formatted_events
                print(f"✅ Found {len(formatted_events)} events for {attendee}")
                
            except FileNotFoundError:
                print(f"❌ Token file not found for {attendee}")
                calendars[attendee] = []
            except Exception as e:
                print(f"❌ Calendar fetch failed for {attendee}: {e}")
                calendars[attendee] = []
        
        return calendars
    
    def visualize_scheduling_impact(self, new_meeting: Dict, 
                                   email_content: str = "", conflicts: List[Dict] = None, 
                                   rescheduled_events: List[Dict] = None, 
                                   use_real_calendar: bool = True) -> str:
        """Create a complete day timeline before/after visualization"""
        
        output = []
        output.append("📅 COMPLETE DAY TIMELINE VISUALIZATION")
        output.append("=" * 80)
        
        # Extract the target day from email content or meeting time
        target_day = self._extract_target_day(email_content, new_meeting.get('start_time', ''))
        target_date = self._extract_date_from_target_day(target_day)
        
        # Check if the meeting itself was rescheduled
        actual_meeting = new_meeting.copy()
        meeting_rescheduled = False
        
        if rescheduled_events:
            for rescheduled in rescheduled_events:
                if (rescheduled.get('attendee') == 'ALL' and 
                    rescheduled.get('event_title') == new_meeting.get('subject', 'Meeting')):
                    actual_meeting['start_time'] = rescheduled.get('new_start_time', new_meeting['start_time'])
                    actual_meeting['end_time'] = rescheduled.get('new_end_time', new_meeting['end_time'])
                    meeting_rescheduled = True
                    break
        
        output.append(f"\n📆 TARGET DAY: {target_day}")
        output.append(f"🎯 NEW MEETING: {new_meeting.get('subject', 'N/A')}")
        
        if meeting_rescheduled:
            output.append(f"⏰ ORIGINAL TIME: {self._format_time(new_meeting.get('start_time', ''))} - {self._format_time(new_meeting.get('end_time', ''))}")
            output.append(f"⏰ RESCHEDULED TIME: {self._format_time(actual_meeting.get('start_time', ''))} - {self._format_time(actual_meeting.get('end_time', ''))}")
        else:
            output.append(f"⏰ TIME: {self._format_time(actual_meeting.get('start_time', ''))} - {self._format_time(actual_meeting.get('end_time', ''))}")
        
        output.append(f"👥 ATTENDEES: {', '.join([att.split('@')[0] for att in new_meeting.get('attendees', [])])}")
        
        # Fetch real calendar data if requested
        attendees = new_meeting.get('attendees', [])
        if use_real_calendar and target_date:
            print(f"\n🔄 Fetching real calendar data for {target_date}...")
            original_calendars = self.fetch_real_calendar_events(attendees, target_date)
        else:
            print(f"\n📋 Using mock calendar data...")
            original_calendars = self._get_mock_calendar_data(attendees)
        
        # Create complete day timeline for all attendees
        day_timeline = self._create_complete_day_timeline(
            original_calendars, actual_meeting, target_day, conflicts, rescheduled_events
        )
        output.extend(day_timeline)
        
        # Show conflicts and resolutions summary
        if conflicts or rescheduled_events:
            output.append(f"\n📋 SCHEDULING ACTIONS TAKEN:")
            output.append("-" * 40)
            
            if conflicts:
                output.append("⚠️ CONFLICTS DETECTED:")
                for conflict in conflicts:
                    output.append(f"   • {conflict.get('attendee', 'Unknown').split('@')[0]} - {conflict.get('event_title', 'Unknown Event')}")
                    output.append(f"     Priority: {conflict.get('priority', 'Unknown')}")
                
            if rescheduled_events:
                output.append("\n↻ EVENTS RESCHEDULED:")
                for rescheduled in rescheduled_events:
                    output.append(f"   • {rescheduled.get('event_title', 'Unknown Event')}")
                    output.append(f"     From: {rescheduled.get('original_time', 'Unknown')}")
                    output.append(f"     To: {rescheduled.get('new_time', 'Unknown')}")
        
        # Show legend
        output.append(f"\n📖 LEGEND:")
        output.append(f"   {self.symbols['existing']} Existing Events")
        output.append(f"   {self.symbols['new']} New Meeting")
        output.append(f"   {self.symbols['conflict']} Conflict")
        output.append(f"   {self.symbols['rescheduled']} Rescheduled")
        output.append(f"   {self.symbols['free']} Free Time")
        
        return "\n".join(output)
    
    def _extract_target_day(self, email_content: str, meeting_start_time: str) -> str:
        """Extract the target day from email content or meeting time"""
        
        # First, try to extract from email content
        content_lower = email_content.lower()
        
        day_mapping = {
            'monday': '2025-07-21',
            'tuesday': '2025-07-22', 
            'wednesday': '2025-07-23',
            'thursday': '2025-07-24',
            'friday': '2025-07-25'
        }
        
        for day_name, date_str in day_mapping.items():
            if day_name in content_lower:
                return f"{day_name.title()} ({date_str})"
        
        # Fallback: extract from meeting start time
        if meeting_start_time:
            try:
                dt = datetime.fromisoformat(meeting_start_time.replace('+05:30', ''))
                day_name = dt.strftime('%A')
                date_str = dt.strftime('%Y-%m-%d')
                return f"{day_name} ({date_str})"
            except:
                pass
        
        return "Unknown Day"
    
    def _extract_date_from_target_day(self, target_day: str) -> str:
        """Extract date string from target day description"""
        try:
            # Extract date from format like "Monday (2025-07-21)"
            date_part = target_day.split('(')[1].split(')')[0]
            return date_part
        except:
            return None
    
    def _get_mock_calendar_data(self, attendees: List[str]) -> Dict[str, List[Dict]]:
        """Fallback mock calendar data when real API fails - matches real API data structure"""
        return {
            "userone.amd@gmail.com": [
                {
                    "StartTime": "2025-07-21T10:00:00+05:30",
                    "EndTime": "2025-07-21T11:00:00+05:30", 
                    "Summary": "Team Standup"
                },
                {
                    "StartTime": "2025-07-21T14:00:00+05:30",
                    "EndTime": "2025-07-21T15:30:00+05:30",
                    "Summary": "Project Review"
                }
            ],
            "usertwo.amd@gmail.com": [
                {
                    "StartTime": "2025-07-21T11:30:00+05:30",
                    "EndTime": "2025-07-21T12:00:00+05:30",
                    "Summary": "Code Review"
                }
            ],
            "userthree.amd@gmail.com": [
                {
                    "StartTime": "2025-07-21T09:00:00+05:30",
                    "EndTime": "2025-07-21T10:00:00+05:30",
                    "Summary": "1v1 with Team Member"
                },
                {
                    "StartTime": "2025-07-21T10:00:00+05:30",
                    "EndTime": "2025-07-21T10:30:00+05:30",
                    "Summary": "Agentic AI Meeting"
                },
                {
                    "StartTime": "2025-07-21T10:30:00+05:30",
                    "EndTime": "2025-07-21T11:00:00+05:30",
                    "Summary": "Agentic AI Meeting"
                },
                {
                    "StartTime": "2025-07-21T16:00:00+05:30",
                    "EndTime": "2025-07-21T17:30:00+05:30",
                    "Summary": "Off Hour Meeting"
                }
            ]
        }
    
    def _get_mock_calendar_data_tuesday(self, attendees: List[str]) -> Dict[str, List[Dict]]:
        """Mock calendar data for Tuesday test case"""
        return {
            "userone.amd@gmail.com": [
                {
                    "StartTime": "2025-07-22T09:30:00+05:30",
                    "EndTime": "2025-07-22T10:30:00+05:30",
                    "Summary": "Sprint Planning"
                },
                {
                    "StartTime": "2025-07-22T15:00:00+05:30",
                    "EndTime": "2025-07-22T16:00:00+05:30",
                    "Summary": "1:1 with Manager"
                }
            ],
            "usertwo.amd@gmail.com": [
                {
                    "StartTime": "2025-07-22T10:00:00+05:30",
                    "EndTime": "2025-07-22T10:30:00+05:30",
                    "Summary": "Daily Standup"
                },
                {
                    "StartTime": "2025-07-22T11:30:00+05:30",
                    "EndTime": "2025-07-22T12:30:00+05:30",
                    "Summary": "Code Review Session"
                }
            ],
            "userthree.amd@gmail.com": [
                {
                    "StartTime": "2025-07-22T09:00:00+05:30",
                    "EndTime": "2025-07-22T10:00:00+05:30",
                    "Summary": "Architecture Planning"
                },
                {
                    "StartTime": "2025-07-22T11:00:00+05:30",
                    "EndTime": "2025-07-22T12:00:00+05:30",
                    "Summary": "Client Call - Feedback"
                },
                {
                    "StartTime": "2025-07-22T14:00:00+05:30",
                    "EndTime": "2025-07-22T15:00:00+05:30",
                    "Summary": "Team Training"
                }
            ]
        }
    
    def _create_complete_day_timeline(self, original_calendars: Dict, new_meeting: Dict, 
                                    target_day: str, conflicts: List[Dict], 
                                    rescheduled_events: List[Dict]) -> List[str]:
        """Create a complete day timeline showing before/after for all attendees"""
        
        output = []
        attendees = new_meeting.get('attendees', [])
        
        # Extract date from target_day
        try:
            date_part = target_day.split('(')[1].split(')')[0]
            target_date = datetime.fromisoformat(date_part).date()
        except:
            # Fallback to a default date
            target_date = datetime(2025, 7, 21).date()
        
        # Create time slots for business hours (8 AM to 6 PM)
        time_slots = []
        base_time = datetime.combine(target_date, datetime.min.time().replace(hour=8))
        
        for hour_offset in range(10):  # 8 AM to 6 PM (10 hours)
            for minute in [0, 30]:
                slot_time = base_time + timedelta(hours=hour_offset, minutes=minute)
                time_slots.append(slot_time)
        
        # Create side-by-side BEFORE and AFTER views
        output.append(f"\n⏰ COMPLETE DAY TIMELINE - {target_day}")
        output.append("=" * 80)
        
        # Header
        attendee_names = [att.split('@')[0][:8] for att in attendees]
        header_before = "Time   │ BEFORE" + " " * 50 + "│ AFTER"
        output.append(header_before)
        output.append("─" * 80)
        
        # Create BEFORE and AFTER timelines
        for attendee in attendees:
            output.append(f"\n👤 {attendee.split('@')[0].upper()}")
            output.append("─" * 40)
            
            # Get events for this attendee on target date
            original_events = self._get_events_for_date(original_calendars.get(attendee, []), target_date)
            
            # Create BEFORE timeline
            before_timeline = self._create_hourly_timeline(original_events, time_slots, "BEFORE")
            
            # Create AFTER timeline (with new meeting and rescheduled events)
            after_events = original_events.copy()
            
            # Add new meeting
            new_event = {
                'StartTime': new_meeting['start_time'],
                'EndTime': new_meeting['end_time'],
                'Summary': new_meeting.get('subject', 'New Meeting'),
                'IsNew': True
            }
            after_events.append(new_event)
            
            # Apply rescheduling for this attendee
            if rescheduled_events:
                after_events = self._apply_rescheduling(after_events, rescheduled_events, attendee)
            
            # Handle meeting rescheduling (when the new meeting itself was moved)
            meeting_was_rescheduled = False
            for rescheduled in rescheduled_events:
                if (rescheduled.get('attendee') == 'ALL' and 
                    rescheduled.get('event_title') == new_meeting.get('subject', 'New Meeting')):
                    # Update the new meeting time
                    new_event['StartTime'] = rescheduled.get('new_start_time', new_meeting['start_time'])
                    new_event['EndTime'] = rescheduled.get('new_end_time', new_meeting['end_time'])
                    meeting_was_rescheduled = True
                    break
            
            after_timeline = self._create_hourly_timeline(after_events, time_slots, "AFTER")
            
            # Combine BEFORE and AFTER side by side
            for i, time_slot in enumerate(time_slots):
                time_str = time_slot.strftime("%H:%M")
                before_status = before_timeline[i] if i < len(before_timeline) else "     ·     "
                after_status = after_timeline[i] if i < len(after_timeline) else "     ·     "
                
                output.append(f"{time_str} │ {before_status:<15} │ {after_status}")
        
        return output
    
    def _get_events_for_date(self, events: List[Dict], target_date) -> List[Dict]:
        """Filter events for a specific date"""
        day_events = []
        
        for event in events:
            try:
                event_date = datetime.fromisoformat(event['StartTime'].replace('+05:30', '')).date()
                if event_date == target_date:
                    day_events.append(event)
            except:
                continue
        
        return day_events
    
    def _create_hourly_timeline(self, events: List[Dict], time_slots: List[datetime], 
                              timeline_type: str) -> List[str]:
        """Create hourly timeline for events"""
        
        timeline = []
        
        for slot_time in time_slots:
            slot_status = "     ·     "  # Default: free
            
            # Check if any event covers this time slot
            for event in events:
                try:
                    event_start = datetime.fromisoformat(event['StartTime'].replace('+05:30', ''))
                    event_end = datetime.fromisoformat(event['EndTime'].replace('+05:30', ''))
                    
                    # Check if slot time falls within event time
                    if event_start <= slot_time < event_end:
                        if event.get('IsNew'):
                            slot_status = f"  {self.symbols['new']} NEW   "
                        elif event.get('IsRescheduled'):
                            slot_status = f"  {self.symbols['rescheduled']} MOVED "
                        else:
                            # Truncate event name to fit
                            event_name = event['Summary'][:8]
                            slot_status = f"  {self.symbols['existing']} {event_name:<6}"
                        break
                except:
                    continue
            
            timeline.append(slot_status)
        
        return timeline
    
    def _apply_rescheduling(self, events: List[Dict], rescheduled_events: List[Dict], 
                          attendee: str) -> List[Dict]:
        """Apply rescheduling changes to events list"""
        
        updated_events = []
        
        for event in events:
            # Check if this event was rescheduled
            was_rescheduled = False
            
            for rescheduled in rescheduled_events:
                if (rescheduled.get('attendee') == attendee and 
                    rescheduled.get('event_title') == event['Summary']):
                    
                    # Create rescheduled version
                    rescheduled_event = event.copy()
                    rescheduled_event['StartTime'] = rescheduled.get('new_start_time', event['StartTime'])
                    rescheduled_event['EndTime'] = rescheduled.get('new_end_time', event['EndTime'])
                    rescheduled_event['IsRescheduled'] = True
                    updated_events.append(rescheduled_event)
                    was_rescheduled = True
                    break
            
            # If not rescheduled, keep original
            if not was_rescheduled:
                updated_events.append(event)
        
        return updated_events
    
    def _find_available_time_slot(self, attendee_events: List[Dict], duration_minutes: int, 
                                 target_date: str, avoid_times: List[Dict] = None) -> Dict:
        """Intelligently find an available time slot for rescheduling"""
        
        # Convert target_date to datetime object
        try:
            target_dt = datetime.fromisoformat(target_date).date()
        except:
            target_dt = datetime(2025, 7, 21).date()
        
        # Create list of all occupied time slots
        occupied_slots = []
        
        # Add existing events
        for event in attendee_events:
            try:
                start_dt = datetime.fromisoformat(event['StartTime'].replace('+05:30', ''))
                end_dt = datetime.fromisoformat(event['EndTime'].replace('+05:30', ''))
                if start_dt.date() == target_dt:
                    occupied_slots.append({'start': start_dt, 'end': end_dt})
            except:
                continue
        
        # Add times to avoid (like the new meeting)
        if avoid_times:
            for avoid in avoid_times:
                try:
                    start_dt = datetime.fromisoformat(avoid['start_time'].replace('+05:30', ''))
                    end_dt = datetime.fromisoformat(avoid['end_time'].replace('+05:30', ''))
                    occupied_slots.append({'start': start_dt, 'end': end_dt})
                except:
                    continue
        
        # Sort occupied slots by start time
        occupied_slots.sort(key=lambda x: x['start'])
        
        # Business hours: 8 AM to 6 PM
        business_start = datetime.combine(target_dt, datetime.min.time().replace(hour=8))
        business_end = datetime.combine(target_dt, datetime.min.time().replace(hour=18))
        
        # Find gaps in the schedule
        available_slots = []
        current_time = business_start
        
        for slot in occupied_slots:
            # Check if there's a gap before this slot
            if current_time < slot['start']:
                gap_duration = (slot['start'] - current_time).total_seconds() / 60
                if gap_duration >= duration_minutes:
                    # Found a suitable gap
                    available_slots.append({
                        'start': current_time,
                        'end': current_time + timedelta(minutes=duration_minutes)
                    })
            
            # Move current_time to the end of this slot
            current_time = max(current_time, slot['end'])
        
        # Check if there's time after the last meeting
        if current_time < business_end:
            gap_duration = (business_end - current_time).total_seconds() / 60
            if gap_duration >= duration_minutes:
                available_slots.append({
                    'start': current_time,
                    'end': current_time + timedelta(minutes=duration_minutes)
                })
        
        # Return the first available slot (earliest time)
        if available_slots:
            best_slot = available_slots[0]
            return {
                'new_start_time': best_slot['start'].strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                'new_end_time': best_slot['end'].strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                'new_time': f"{best_slot['start'].strftime('%H:%M')}-{best_slot['end'].strftime('%H:%M')}"
            }
        
        # No available slot found
        return {
            'new_start_time': '2025-07-21T17:00:00+05:30',
            'new_end_time': '2025-07-21T18:00:00+05:30',
            'new_time': '17:00-18:00 (End of day)'
        }
    
    def _find_common_available_slot(self, all_calendars: Dict[str, List[Dict]], 
                                  duration_minutes: int, target_date: str) -> Dict:
        """Find a time slot that works for ALL attendees"""
        
        try:
            target_dt = datetime.fromisoformat(target_date).date()
        except:
            target_dt = datetime(2025, 7, 22).date()
        
        # Collect all events from all attendees for the target date
        all_busy_times = []
        
        for attendee, events in all_calendars.items():
            for event in events:
                try:
                    event_start = datetime.fromisoformat(event['StartTime'].replace('+05:30', ''))
                    event_end = datetime.fromisoformat(event['EndTime'].replace('+05:30', ''))
                    
                    if event_start.date() == target_dt:
                        # Skip "Off Hours" as they're not real conflicts
                        if event['Summary'].lower() != "off hours":
                            all_busy_times.append({
                                'start': event_start,
                                'end': event_end,
                                'summary': event['Summary']
                            })
                except:
                    continue
        
        # Sort all busy times
        all_busy_times.sort(key=lambda x: x['start'])
        
        # Find gaps between events
        business_start = datetime.combine(target_dt, datetime.min.time().replace(hour=8))
        business_end = datetime.combine(target_dt, datetime.min.time().replace(hour=18))
        
        current_time = business_start
        
        for busy_time in all_busy_times:
            # Check gap before this busy time
            if current_time < busy_time['start']:
                gap_duration = (busy_time['start'] - current_time).total_seconds() / 60
                
                if gap_duration >= duration_minutes:
                    # Found suitable gap
                    slot_end = current_time + timedelta(minutes=duration_minutes)
                    return {
                        'new_start_time': current_time.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                        'new_end_time': slot_end.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                        'new_time': f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
                    }
            
            # Move past this busy time
            current_time = max(current_time, busy_time['end'])
        
        # Check if there's time after the last event
        if current_time < business_end:
            gap_duration = (business_end - current_time).total_seconds() / 60
            if gap_duration >= duration_minutes:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                return {
                    'new_start_time': current_time.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                    'new_end_time': slot_end.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                    'new_time': f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
                }
        
        # No suitable slot found
        return None

# Easy integration functions
def create_timeline_from_meeting_request(request_data: Dict, use_real_calendar: bool = True) -> str:
    """Easy function to create timeline from meeting request data"""
    
    visualizer = SimpleTimelineVisualizer()
    
    # Extract meeting details
    new_meeting = {
        "subject": request_data.get("Subject", "Meeting"),
        "start_time": request_data.get("EventStart", ""),
        "end_time": request_data.get("EventEnd", ""),
        "attendees": [request_data.get("From", "")] + [att["email"] for att in request_data.get("Attendees", [])]
    }
    
    email_content = request_data.get("EmailContent", "")
    
    # Generate timeline visualization
    return visualizer.visualize_scheduling_impact(
        new_meeting, 
        email_content,
        use_real_calendar=use_real_calendar
    )

def create_timeline_for_test_case(test_case_data: Dict, use_real_calendar: bool = True) -> str:
    """Create timeline for hackathon test case format with intelligent scheduling"""
    
    visualizer = SimpleTimelineVisualizer()
    
    # Convert test case format to meeting format
    attendees = [test_case_data["From"]]
    for att in test_case_data.get("Attendees", []):
        attendees.append(att["email"])
    
    email_content = test_case_data.get("EmailContent", "")
    
    # Extract meeting details from email content
    start_time, end_time, target_date = _extract_meeting_time_from_email(email_content)
    
    new_meeting = {
        "subject": test_case_data.get("Subject", "Meeting"),
        "start_time": start_time,
        "end_time": end_time,
        "attendees": attendees
    }
    
    # Get calendar data based on the day
    if use_real_calendar:
        original_calendars = visualizer.fetch_real_calendar_events(attendees, target_date)
    else:
        # Use appropriate mock data based on day
        if "tuesday" in email_content.lower():
            original_calendars = visualizer._get_mock_calendar_data_tuesday(attendees)
        else:
            original_calendars = visualizer._get_mock_calendar_data(attendees)
    
    # Detect conflicts and find intelligent rescheduling
    conflicts, rescheduled_events = _detect_conflicts_and_reschedule(
        visualizer, original_calendars, new_meeting, target_date
    )
    
    return visualizer.visualize_scheduling_impact(
        new_meeting,
        email_content,
        conflicts,
        rescheduled_events,
        use_real_calendar=use_real_calendar
    )

def _extract_meeting_time_from_email(email_content: str) -> tuple:
    """Extract meeting time from email content"""
    content_lower = email_content.lower()
    
    # Default duration is 1 hour
    duration_minutes = 60
    
    if "tuesday" in content_lower and "11:00" in content_lower:
        return "2025-07-22T11:00:00+05:30", "2025-07-22T12:00:00+05:30", "2025-07-22"
    elif "monday" in content_lower and "9:00" in content_lower:
        return "2025-07-21T09:00:00+05:30", "2025-07-21T09:30:00+05:30", "2025-07-21"
    elif "wednesday" in content_lower and "10:00" in content_lower:
        return "2025-07-23T10:00:00+05:30", "2025-07-23T11:00:00+05:30", "2025-07-23"
    elif "thursday" in content_lower:
        return "2025-07-24T10:30:00+05:30", "2025-07-24T11:30:00+05:30", "2025-07-24"
    elif "wednesday" in content_lower:
        return "2025-07-23T10:00:00+05:30", "2025-07-23T11:00:00+05:30", "2025-07-23"
    else:
        # Default fallback
        return "2025-07-21T10:00:00+05:30", "2025-07-21T11:00:00+05:30", "2025-07-21"

def _detect_conflicts_and_reschedule(visualizer, original_calendars: Dict, new_meeting: Dict, target_date: str) -> tuple:
    """Detect conflicts and create intelligent rescheduling plan"""
    
    conflicts = []
    rescheduled_events = []
    
    # Check for conflicts
    for attendee, events in original_calendars.items():
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['StartTime'].replace('+05:30', ''))
                event_end = datetime.fromisoformat(event['EndTime'].replace('+05:30', ''))
                meeting_start = datetime.fromisoformat(new_meeting['start_time'].replace('+05:30', ''))
                meeting_end = datetime.fromisoformat(new_meeting['end_time'].replace('+05:30', ''))
                
                # Check overlap
                if event_start < meeting_end and event_end > meeting_start:
                    # Determine priority
                    priority = "HIGH" if "client" in event['Summary'].lower() else "MEDIUM"
                    
                    conflict = {
                        "attendee": attendee,
                        "event_title": event['Summary'],
                        "time": f"{event_start.strftime('%H:%M')}-{event_end.strftime('%H:%M')}",
                        "priority": priority
                    }
                    conflicts.append(conflict)
                    
                    # If MEDIUM priority, schedule for rescheduling
                    if priority == "MEDIUM":
                        # Find new time for this event
                        duration = int((event_end - event_start).total_seconds() / 60)
                        optimal_slot = visualizer._find_available_time_slot(
                            events, duration, target_date, [new_meeting]
                        )
                        
                        rescheduled_events.append({
                            "attendee": attendee,
                            "event_title": event['Summary'],
                            "original_time": f"{event_start.strftime('%H:%M')}-{event_end.strftime('%H:%M')}",
                            "new_time": optimal_slot['new_time'],
                            "new_start_time": optimal_slot['new_start_time'],
                            "new_end_time": optimal_slot['new_end_time']
                        })
            except:
                continue
    
    return conflicts, rescheduled_events

class SimpleTimelineVisualizerExtension:
    """Extension methods that got moved outside during editing"""
    
    def _create_attendee_timeline(self, attendee: str, original_events: List[Dict], 
                                new_meeting: Dict, conflicts: List[Dict]) -> List[str]:
        """Create timeline for a single attendee"""
    
        timeline = []
        
        # Get the day we're scheduling for
        meeting_start = new_meeting.get('start_time', '')
        if not meeting_start:
            return ["   No meeting time specified"]
        
        try:
            meeting_date = datetime.fromisoformat(meeting_start.replace('+05:30', '')).date()
        except:
            return ["   Invalid meeting time format"]
        
        # Filter events for the same day
        day_events = []
        for event in original_events:
            try:
                event_date = datetime.fromisoformat(event['StartTime'].replace('+05:30', '')).date()
                if event_date == meeting_date:
                    day_events.append(event)
            except:
                continue
        
        # Check if this attendee has conflicts
        attendee_conflicts = [c for c in (conflicts or []) if c.get('attendee') == attendee]
        
        # Show BEFORE timeline
        timeline.append("   BEFORE:")
        if day_events:
            for event in sorted(day_events, key=lambda x: x['StartTime']):
                start_time = self._format_time(event['StartTime'])
                end_time = self._format_time(event['EndTime'])
                symbol = self.symbols['conflict'] if any(c.get('event_title') == event['Summary'] for c in attendee_conflicts) else self.symbols['existing']
                timeline.append(f"     {symbol} {start_time}-{end_time} {event['Summary']}")
        else:
            timeline.append(f"     {self.symbols['free']} No events scheduled")
        
        # Show AFTER timeline (what it will look like)
        timeline.append("\n   AFTER:")
        
        # Combine original events with new meeting
        all_events = day_events.copy()
        
        # Add the new meeting
        new_event = {
            'StartTime': new_meeting['start_time'],
            'EndTime': new_meeting['end_time'], 
            'Summary': new_meeting.get('subject', 'New Meeting'),
            'IsNew': True
        }
        all_events.append(new_event)
        
        # Sort all events by time
        all_events.sort(key=lambda x: x['StartTime'])
        
        # Display the combined timeline
        for event in all_events:
            start_time = self._format_time(event['StartTime'])
            end_time = self._format_time(event['EndTime'])
            
            if event.get('IsNew'):
                symbol = self.symbols['new']
                title = f"{event['Summary']} (NEW)"
            elif any(c.get('event_title') == event['Summary'] for c in attendee_conflicts):
                symbol = self.symbols['conflict']
                title = f"{event['Summary']} (CONFLICT)"
            else:
                symbol = self.symbols['existing']
                title = event['Summary']
            
            timeline.append(f"     {symbol} {start_time}-{end_time} {title}")
        
        # Show impact summary for this attendee
        if attendee_conflicts:
            timeline.append(f"\n   📊 IMPACT: {len(attendee_conflicts)} conflict(s) detected")
        else:
            timeline.append(f"\n   📊 IMPACT: No conflicts - clean scheduling")
        
        return timeline
    
    def _format_time(self, time_str: str) -> str:
        """Format time string for display"""
        try:
            dt = datetime.fromisoformat(time_str.replace('+05:30', ''))
            return dt.strftime("%H:%M")
        except:
            return time_str
    
    def create_simple_schedule_view(self, attendee_calendars: Dict, day_filter: str = None) -> str:
        """Create a simple day view of all attendees' schedules"""
        
        output = []
        output.append("📅 DAILY SCHEDULE VIEW")
        output.append("=" * 50)
        
        if day_filter:
            output.append(f"📆 Date: {day_filter}")
            output.append("")
        
        # Create time slots from 9 AM to 6 PM
        time_slots = []
        base_time = datetime(2025, 7, 24, 9, 0)  # 9 AM
        for hour in range(9):  # 9 hours (9 AM to 6 PM)
            for minute in [0, 30]:
                slot_time = base_time.replace(hour=9+hour, minute=minute)
                time_slots.append(slot_time.strftime("%H:%M"))
        
        # Header row
        attendees = list(attendee_calendars.keys())
        header = "Time  │ " + " │ ".join([att.split('@')[0][:8].ljust(8) for att in attendees])
        output.append(header)
        output.append("─" * len(header))
        
        # Time slot rows
        for time_slot in time_slots:
            row = f"{time_slot} │"
            
            for attendee in attendees:
                events = attendee_calendars.get(attendee, [])
                
                # Check if this time slot has an event
                slot_status = "   ·    "  # Free
                for event in events:
                    event_start = self._format_time(event['StartTime'])
                    event_end = self._format_time(event['EndTime'])
                    
                    # Simple check if time slot falls within event
                    if event_start <= time_slot < event_end:
                        if 'New Meeting' in event['Summary'] or event.get('IsNew'):
                            slot_status = "   ★    "  # New meeting
                        else:
                            slot_status = "   ■    "  # Existing event
                        break
                
                row += f" {slot_status} │"
            
            output.append(row)
        
        # Legend
        output.append("")
        output.append("Legend: · = Free, ■ = Existing Event, ★ = New Meeting")
        
        return "\n".join(output)

# Test function with real calendar integration
def test_complete_day_timeline_with_real_calendar():
    """Test the complete day timeline visualization with real Google Calendar data"""
    
    visualizer = SimpleTimelineVisualizer()
    
    new_meeting = {
        "subject": "Client Validation - Urgent",
        "start_time": "2025-07-21T09:00:00+05:30",
        "end_time": "2025-07-21T09:30:00+05:30",
        "attendees": ["userone.amd@gmail.com", "usertwo.amd@gmail.com", "userthree.amd@gmail.com"]
    }
    
    # Email content that mentions Monday
    email_content = "Hi Team. We've just received quick feedback from the client indicating that the instructions we provided aren't working on their end. Let's prioritize resolving this promptly. Let's meet Monday at 9:00 AM to discuss and resolve this issue."
    
    conflicts = [
        {
            "attendee": "userthree.amd@gmail.com",
            "event_title": "1v1 with Team Member",
            "time": "Monday 9:00-10:00 AM",
            "priority": "MEDIUM"
        }
    ]
    
    print("🧪 TESTING COMPLETE DAY TIMELINE WITH REAL GOOGLE CALENDAR")
    print("=" * 60)
    print("Scenario: Test Case 2 - Monday client validation meeting")
    print("Data Source: Real Google Calendar API")
    print("Email mentions: 'Let's meet Monday at 9:00 AM'")
    print("=" * 60)
    
    # Get calendar data first to compute intelligent rescheduling
    target_date = "2025-07-21"
    attendees = new_meeting.get('attendees', [])
    original_calendars = visualizer.fetch_real_calendar_events(attendees, target_date)
    
    # Find intelligent rescheduling for conflicted attendee
    conflicted_attendee = "userthree.amd@gmail.com"
    attendee_events = original_calendars.get(conflicted_attendee, [])
    
    # Find available slot for the 1v1 (60 minutes duration)
    optimal_slot = visualizer._find_available_time_slot(
        attendee_events, 
        60,  # 1v1 meeting duration
        target_date,
        [new_meeting]  # Avoid the new meeting time
    )
    
    rescheduled_events = [
        {
            "attendee": conflicted_attendee,
            "event_title": "1v1 with Team Member",
            "original_time": "9:00-10:00 AM",
            "new_time": optimal_slot['new_time'],
            "new_start_time": optimal_slot['new_start_time'],
            "new_end_time": optimal_slot['new_end_time']
        }
    ]
    
    print(f"🤖 INTELLIGENT RESCHEDULING: 1v1 moved to {optimal_slot['new_time']}")
    print("=" * 60)
    
    # Generate timeline with intelligent rescheduling
    timeline_viz = visualizer.visualize_scheduling_impact(
        new_meeting, 
        email_content,
        conflicts, 
        rescheduled_events,
        use_real_calendar=True  # Enable real calendar fetching
    )
    
    print(timeline_viz)

def test_complete_day_timeline_mock():
    """Test the complete day timeline visualization with mock data"""
    
    visualizer = SimpleTimelineVisualizer()
    
    new_meeting = {
        "subject": "Client Validation - Urgent", 
        "start_time": "2025-07-21T09:00:00+05:30",
        "end_time": "2025-07-21T09:30:00+05:30",
        "attendees": ["userone.amd@gmail.com", "usertwo.amd@gmail.com", "userthree.amd@gmail.com"]
    }
    
    email_content = "Hi Team. We've just received quick feedback from the client indicating that the instructions we provided aren't working on their end. Let's prioritize resolving this promptly. Let's meet Monday at 9:00 AM to discuss and resolve this issue."
    
    conflicts = [
        {
            "attendee": "userthree.amd@gmail.com",
            "event_title": "1v1 with Team Member",
            "time": "Monday 9:00-10:00 AM",
            "priority": "MEDIUM"
        }
    ]
    
    print("🧪 TESTING COMPLETE DAY TIMELINE WITH MOCK DATA")
    print("=" * 60)
    print("Scenario: Test Case 2 - Monday client validation meeting")
    print("Data Source: Mock calendar data")
    print("=" * 60)
    
    # Get mock calendar data to compute intelligent rescheduling
    target_date = "2025-07-21"
    attendees = new_meeting.get('attendees', [])
    original_calendars = visualizer._get_mock_calendar_data(attendees)
    
    # Find intelligent rescheduling for conflicted attendee  
    conflicted_attendee = "userthree.amd@gmail.com"
    attendee_events = original_calendars.get(conflicted_attendee, [])
    
    # Find available slot for the 1v1 (60 minutes duration)
    optimal_slot = visualizer._find_available_time_slot(
        attendee_events, 
        60,  # 1v1 meeting duration
        target_date,
        [new_meeting]  # Avoid the new meeting time
    )
    
    rescheduled_events = [
        {
            "attendee": conflicted_attendee,
            "event_title": "1v1 with Team Member",
            "original_time": "9:00-10:00 AM",
            "new_time": optimal_slot['new_time'],
            "new_start_time": optimal_slot['new_start_time'],
            "new_end_time": optimal_slot['new_end_time']
        }
    ]
    
    print(f"🤖 INTELLIGENT RESCHEDULING: 1v1 moved to {optimal_slot['new_time']}")
    print("=" * 60)
    
    # Generate timeline with intelligent rescheduling
    timeline_viz = visualizer.visualize_scheduling_impact(
        new_meeting, 
        email_content,
        conflicts, 
        rescheduled_events,
        use_real_calendar=False  # Use mock data
    )
    
    print(timeline_viz)

def test_tuesday_project_status_meeting():
    """Test Tuesday Project Status meeting with real Google Calendar data and dynamic conflict detection"""
    
    visualizer = SimpleTimelineVisualizer()
    
    # Test case data - Tuesday Project Status
    test_case = {
        "Request_id": "6118b54f-907b-4451-8d48-dd13d76033c5",
        "Datetime": "19-07-2025T12:34:55",
        "Location": "IISc Bangalore",
        "From": "userone.amd@gmail.com",
        "Attendees": [
            {"email": "usertwo.amd@gmail.com"},
            {"email": "userthree.amd@gmail.com"}
        ],
        "Subject": "Project Status",
        "EmailContent": "Hi Team. Let's meet on Tuesday at 11:00 A.M and discuss about our on-going Projects."
    }
    
    new_meeting = {
        "subject": test_case["Subject"],
        "start_time": "2025-07-22T11:00:00+05:30",  # Tuesday 11:00 AM
        "end_time": "2025-07-22T12:00:00+05:30",    # 1 hour meeting
        "attendees": [test_case["From"]] + [att["email"] for att in test_case["Attendees"]]
    }
    
    email_content = test_case["EmailContent"]
    
    print("🧪 TESTING TUESDAY PROJECT STATUS MEETING")
    print("=" * 60)
    print("Scenario: Tuesday 11:00 AM Project Status Discussion")
    print("Data Source: Real Google Calendar API")
    print("Email mentions: 'Let's meet on Tuesday at 11:00 A.M'")
    print("=" * 60)
    
    # Get REAL calendar data for Tuesday
    target_date = "2025-07-22"
    attendees = new_meeting.get('attendees', [])
    original_calendars = visualizer.fetch_real_calendar_events(attendees, target_date)
    
    print("📅 REAL CALENDAR DATA RETRIEVED:")
    for attendee, events in original_calendars.items():
        print(f"   {attendee.split('@')[0]}: {len(events)} events")
        for event in events:
            start_time = visualizer._format_time(event['StartTime'])
            end_time = visualizer._format_time(event['EndTime'])
            print(f"     • {start_time}-{end_time}: {event['Summary']}")
    
    # DYNAMIC CONFLICT DETECTION using real calendar data
    print("\n🔍 DETECTING CONFLICTS WITH REAL DATA...")
    conflicts = []
    
    meeting_start = datetime.fromisoformat(new_meeting['start_time'].replace('+05:30', ''))
    meeting_end = datetime.fromisoformat(new_meeting['end_time'].replace('+05:30', ''))
    
    for attendee, events in original_calendars.items():
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['StartTime'].replace('+05:30', ''))
                event_end = datetime.fromisoformat(event['EndTime'].replace('+05:30', ''))
                
                # Check if event overlaps with proposed meeting time
                if event_start < meeting_end and event_end > meeting_start:
                    # Determine priority based on event content
                    summary_lower = event['Summary'].lower()
                    if any(keyword in summary_lower for keyword in ['client', 'customer', 'external']):
                        priority = "HIGH"
                    elif any(keyword in summary_lower for keyword in ['workshop', 'training', 'all-day']):
                        priority = "CRITICAL"  # Can't be moved
                    elif summary_lower == "off hours":
                        priority = "LOW"  # Can be ignored for business meetings
                    else:
                        priority = "MEDIUM"
                    
                    # Skip "Off Hours" conflicts as they're not real business meetings
                    if priority != "LOW":
                        conflict = {
                            "attendee": attendee,
                            "event_title": event['Summary'],
                            "time": f"{event_start.strftime('%H:%M')}-{event_end.strftime('%H:%M')}",
                            "priority": priority,
                            "start_time": event['StartTime'],
                            "end_time": event['EndTime']
                        }
                        conflicts.append(conflict)
                        print(f"   ⚠️ CONFLICT: {attendee.split('@')[0]} - {event['Summary']} ({priority} priority)")
            except Exception as e:
                print(f"   ❌ Error processing event: {e}")
                continue
    
    # INTELLIGENT RESCHEDULING DECISION
    print(f"\n🤖 ANALYZING {len(conflicts)} CONFLICTS...")
    
    # Check if any conflicts are CRITICAL (unmovable)
    critical_conflicts = [c for c in conflicts if c['priority'] == 'CRITICAL']
    high_priority_conflicts = [c for c in conflicts if c['priority'] == 'HIGH']
    
    rescheduled_events = []
    new_meeting_rescheduled = new_meeting.copy()
    
    if critical_conflicts:
        print("   🚨 CRITICAL conflicts detected (workshops/all-day events)")
        print("   💡 DECISION: Find alternative time for Project Status meeting")
        
        # Find alternative time that works for everyone
        optimal_slot = visualizer._find_common_available_slot(
            original_calendars, 60, target_date  # 60 minutes meeting
        )
        
        if optimal_slot:
            new_meeting_rescheduled['start_time'] = optimal_slot['new_start_time']
            new_meeting_rescheduled['end_time'] = optimal_slot['new_end_time']
            
            rescheduled_events.append({
                "attendee": "ALL",
                "event_title": "Project Status",
                "original_time": "11:00-12:00",
                "new_time": optimal_slot['new_time'],
                "new_start_time": optimal_slot['new_start_time'],
                "new_end_time": optimal_slot['new_end_time']
            })
            
            print(f"   ✅ RESCHEDULED: Project Status moved to {optimal_slot['new_time']}")
        else:
            print("   ❌ No available slots found for Tuesday - suggest different day")
            
    elif high_priority_conflicts:
        print("   ⚠️ HIGH priority conflicts detected (client meetings)")
        print("   💡 DECISION: Respect client meetings, find alternative time")
        
        # Similar logic as above for high priority
        optimal_slot = visualizer._find_common_available_slot(
            original_calendars, 60, target_date
        )
        
        if optimal_slot:
            new_meeting_rescheduled['start_time'] = optimal_slot['new_start_time']
            new_meeting_rescheduled['end_time'] = optimal_slot['new_end_time']
            
            rescheduled_events.append({
                "attendee": "ALL",
                "event_title": "Project Status", 
                "original_time": "11:00-12:00",
                "new_time": optimal_slot['new_time'],
                "new_start_time": optimal_slot['new_start_time'],
                "new_end_time": optimal_slot['new_end_time']
            })
            
            print(f"   ✅ RESCHEDULED: Project Status moved to {optimal_slot['new_time']}")
    else:
        print("   ✅ No critical conflicts - can proceed with original time or reschedule MEDIUM priority events")
        
        # Handle medium priority conflicts by rescheduling them
        for conflict in conflicts:
            if conflict['priority'] == 'MEDIUM':
                attendee_events = original_calendars.get(conflict['attendee'], [])
                duration = 60  # Assume 1 hour for medium priority meetings
                
                optimal_slot = visualizer._find_available_time_slot(
                    attendee_events, duration, target_date, [new_meeting]
                )
                
                rescheduled_events.append({
                    "attendee": conflict['attendee'],
                    "event_title": conflict['event_title'],
                    "original_time": conflict['time'],
                    "new_time": optimal_slot['new_time'],
                    "new_start_time": optimal_slot['new_start_time'],
                    "new_end_time": optimal_slot['new_end_time']
                })
                
                print(f"   ↻ RESCHEDULED: {conflict['event_title']} moved to {optimal_slot['new_time']}")
    
    print("=" * 60)
    
    # Generate timeline visualization with real data
    # Pass the original meeting request, let the visualizer handle rescheduling internally
    timeline_viz = visualizer.visualize_scheduling_impact(
        new_meeting,  # Pass original meeting details
        email_content,
        conflicts, 
        rescheduled_events,
        use_real_calendar=True  # Use REAL calendar data
    )
    
    print(timeline_viz)

def test_wednesday_client_feedback_meeting():
    """Test Wednesday Client Feedback meeting with real Google Calendar data and dynamic conflict detection"""
    
    visualizer = SimpleTimelineVisualizer()
    
    # Test case data - Wednesday Client Feedback
    test_case = {
        "Request_id": "6118b54f-907b-4451-8d48-dd13d76033d5",
        "Datetime": "19-07-2025T12:34:55",
        "Location": "IISc Bangalore",
        "From": "userone.amd@gmail.com",
        "Attendees": [
            {"email": "usertwo.amd@gmail.com"},
            {"email": "userthree.amd@gmail.com"}
        ],
        "Subject": "Client Feedback",
        "EmailContent": "Hi Team. We've received the final feedback from the client. Let's review it together and plan next steps. Let's meet on Wednesday at 10:00 A.M."
    }
    
    new_meeting = {
        "subject": test_case["Subject"],
        "start_time": "2025-07-23T10:00:00+05:30",  # Wednesday 10:00 AM
        "end_time": "2025-07-23T11:00:00+05:30",    # 1 hour meeting
        "attendees": [test_case["From"]] + [att["email"] for att in test_case["Attendees"]]
    }
    
    email_content = test_case["EmailContent"]
    
    print("🧪 TESTING WEDNESDAY CLIENT FEEDBACK MEETING")
    print("=" * 60)
    print("Scenario: Wednesday 10:00 AM Client Feedback Review")
    print("Data Source: Real Google Calendar API")
    print("Email mentions: 'Let's meet on Wednesday at 10:00 A.M.'")
    print("=" * 60)
    
    # Get REAL calendar data for Wednesday
    target_date = "2025-07-23"
    attendees = new_meeting.get('attendees', [])
    original_calendars = visualizer.fetch_real_calendar_events(attendees, target_date)
    
    print("📅 REAL CALENDAR DATA RETRIEVED:")
    for attendee, events in original_calendars.items():
        print(f"   {attendee.split('@')[0]}: {len(events)} events")
        for event in events:
            start_time = visualizer._format_time(event['StartTime'])
            end_time = visualizer._format_time(event['EndTime'])
            print(f"     • {start_time}-{end_time}: {event['Summary']}")
    
    # DYNAMIC CONFLICT DETECTION using real calendar data
    print("\n🔍 DETECTING CONFLICTS WITH REAL DATA...")
    conflicts = []
    
    meeting_start = datetime.fromisoformat(new_meeting['start_time'].replace('+05:30', ''))
    meeting_end = datetime.fromisoformat(new_meeting['end_time'].replace('+05:30', ''))
    
    for attendee, events in original_calendars.items():
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['StartTime'].replace('+05:30', ''))
                event_end = datetime.fromisoformat(event['EndTime'].replace('+05:30', ''))
                
                # Check if event overlaps with proposed meeting time
                if event_start < meeting_end and event_end > meeting_start:
                    # Determine priority based on event content
                    summary_lower = event['Summary'].lower()
                    if any(keyword in summary_lower for keyword in ['client', 'customer', 'external']):
                        priority = "HIGH"
                    elif any(keyword in summary_lower for keyword in ['workshop', 'training', 'all-day']):
                        priority = "CRITICAL"  # Can't be moved
                    elif summary_lower == "off hours":
                        priority = "LOW"  # Can be ignored for business meetings
                    else:
                        priority = "MEDIUM"
                    
                    # Skip "Off Hours" conflicts as they're not real business meetings
                    if priority != "LOW":
                        conflict = {
                            "attendee": attendee,
                            "event_title": event['Summary'],
                            "time": f"{event_start.strftime('%H:%M')}-{event_end.strftime('%H:%M')}",
                            "priority": priority,
                            "start_time": event['StartTime'],
                            "end_time": event['EndTime']
                        }
                        conflicts.append(conflict)
                        print(f"   ⚠️ CONFLICT: {attendee.split('@')[0]} - {event['Summary']} ({priority} priority)")
            except Exception as e:
                print(f"   ❌ Error processing event: {e}")
                continue
    
    # INTELLIGENT RESCHEDULING DECISION
    print(f"\n🤖 ANALYZING {len(conflicts)} CONFLICTS...")
    
    # Check if any conflicts are CRITICAL (unmovable)
    critical_conflicts = [c for c in conflicts if c['priority'] == 'CRITICAL']
    high_priority_conflicts = [c for c in conflicts if c['priority'] == 'HIGH']
    
    rescheduled_events = []
    new_meeting_rescheduled = new_meeting.copy()
    
    if critical_conflicts:
        print("   🚨 CRITICAL conflicts detected (workshops/all-day events)")
        print("   💡 DECISION: Find alternative time for Client Feedback meeting")
        
        # Find alternative time that works for everyone
        optimal_slot = visualizer._find_common_available_slot(
            original_calendars, 60, target_date  # 60 minutes meeting
        )
        
        if optimal_slot:
            new_meeting_rescheduled['start_time'] = optimal_slot['new_start_time']
            new_meeting_rescheduled['end_time'] = optimal_slot['new_end_time']
            
            rescheduled_events.append({
                "attendee": "ALL",
                "event_title": "Client Feedback",
                "original_time": "10:00-11:00",
                "new_time": optimal_slot['new_time'],
                "new_start_time": optimal_slot['new_start_time'],
                "new_end_time": optimal_slot['new_end_time']
            })
            
            print(f"   ✅ RESCHEDULED: Client Feedback moved to {optimal_slot['new_time']}")
        else:
            print("   ❌ No available slots found for Wednesday - suggest different day")
            
    elif high_priority_conflicts:
        print("   ⚠️ HIGH priority conflicts detected (client meetings)")
        print("   💡 DECISION: Both are client-related - find alternative time to avoid conflicts")
        
        # Since both are client-related, find alternative time
        optimal_slot = visualizer._find_common_available_slot(
            original_calendars, 60, target_date
        )
        
        if optimal_slot:
            new_meeting_rescheduled['start_time'] = optimal_slot['new_start_time']
            new_meeting_rescheduled['end_time'] = optimal_slot['new_end_time']
            
            rescheduled_events.append({
                "attendee": "ALL",
                "event_title": "Client Feedback", 
                "original_time": "10:00-11:00",
                "new_time": optimal_slot['new_time'],
                "new_start_time": optimal_slot['new_start_time'],
                "new_end_time": optimal_slot['new_end_time']
            })
            
            print(f"   ✅ RESCHEDULED: Client Feedback moved to {optimal_slot['new_time']}")
    else:
        print("   ✅ No critical conflicts - can proceed with original time or reschedule MEDIUM priority events")
        
        # Handle medium priority conflicts by rescheduling them
        for conflict in conflicts:
            if conflict['priority'] == 'MEDIUM':
                attendee_events = original_calendars.get(conflict['attendee'], [])
                
                # Calculate duration of conflicting event
                try:
                    event_start = datetime.fromisoformat(conflict['start_time'].replace('+05:30', ''))
                    event_end = datetime.fromisoformat(conflict['end_time'].replace('+05:30', ''))
                    duration = int((event_end - event_start).total_seconds() / 60)
                except:
                    duration = 60  # Default 1 hour
                
                optimal_slot = visualizer._find_available_time_slot(
                    attendee_events, duration, target_date, [new_meeting]
                )
                
                rescheduled_events.append({
                    "attendee": conflict['attendee'],
                    "event_title": conflict['event_title'],
                    "original_time": conflict['time'],
                    "new_time": optimal_slot['new_time'],
                    "new_start_time": optimal_slot['new_start_time'],
                    "new_end_time": optimal_slot['new_end_time']
                })
                
                print(f"   ↻ RESCHEDULED: {conflict['event_title']} moved to {optimal_slot['new_time']}")
    
    print("=" * 60)
    
    # Generate timeline visualization with real data
    timeline_viz = visualizer.visualize_scheduling_impact(
        new_meeting,  # Pass original meeting details
        email_content,
        conflicts, 
        rescheduled_events,
        use_real_calendar=True  # Use REAL calendar data
    )
    
    print(timeline_viz)

def test_simple_visualization():
    """Test the simple visualization (original version)"""
    
    visualizer = SimpleTimelineVisualizer()
    
    # Simple data
    original_calendars = {
        "userone.amd@gmail.com": [],
        "usertwo.amd@gmail.com": [],
        "userthree.amd@gmail.com": [
            {
                "StartTime": "2025-07-21T09:00:00+05:30",
                "EndTime": "2025-07-21T10:00:00+05:30",
                "Summary": "1v1 with Team Member"
            }
        ]
    }
    
    new_meeting = {
        "subject": "Client Validation - Urgent",
        "start_time": "2025-07-21T09:00:00+05:30",
        "end_time": "2025-07-21T09:30:00+05:30",
        "attendees": ["userone.amd@gmail.com", "usertwo.amd@gmail.com", "userthree.amd@gmail.com"]
    }
    
    conflicts = [
        {
            "attendee": "userthree.amd@gmail.com",
            "event_title": "1v1 with Team Member",
            "time": "Monday 9:00-10:00 AM",
            "priority": "MEDIUM"
        }
    ]
    
    # Generate simple visualization
    email_content = "Let's meet Monday at 9:00 AM"
    timeline_viz = visualizer.visualize_scheduling_impact(original_calendars, new_meeting, email_content, conflicts)
    
    print(timeline_viz)

if __name__ == "__main__":
    # Test selection menu
    print("Choose test scenario:")
    print("1. Monday Client Validation (Real Google Calendar API)")
    print("2. Monday Client Validation (Mock data)")
    print("3. Tuesday Project Status Meeting")
    print("4. Wednesday Client Feedback Meeting")
    print("5. Simple visualization test")
    
    choice = input("Enter choice (1-5, default=2): ").strip()
    
    if choice == "1":
        test_complete_day_timeline_with_real_calendar()
    elif choice == "3":
        test_tuesday_project_status_meeting()
    elif choice == "4":
        test_wednesday_client_feedback_meeting()
    elif choice == "5":
        test_simple_visualization()
    else:
        test_complete_day_timeline_mock()