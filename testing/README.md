# Testing Framework for AMD MI300-AI Scheduling Agent

This directory contains comprehensive testing tools for validating the intelligent scheduling agent's agentic capabilities and visualization tools for analyzing scheduling decisions.

## Test Files

### `test_agent.py` - Enhanced Agent Feature Testing
Tests the advanced agentic features of the meeting scheduler:

- **Context-aware scheduling** with LLM-based priority extraction
- **Prep meeting detection** and intelligent timing
- **Workshop off-hours support** 
- **Critical/urgent meeting handling**
- **Cross-timezone conflict resolution**

### `visualize_timelines.py` - Schedule Visualization Tool
Creates visual timelines showing before/after meeting schedules:

- **Real-time Google Calendar integration**
- **Conflict detection visualization**
- **Rescheduling impact analysis**
- **Multi-attendee timeline comparison**

## Running Tests

### 1. Enhanced Feature Tests

Test the agentic capabilities with different meeting scenarios:

```bash
cd testing/
python test_agent.py
```

**Test Cases Included:**

1. **Prep Meeting Detection** - Tests detection of preparation meetings and scheduling before main events
2. **Workshop Off-Hours** - Validates that workshops can use extended hours
3. **Urgent Client Meeting** - Tests priority handling for critical/emergency meetings  
4. **Cross-Timezone Off-Hours** - Validates off-hours business rules enforcement

**Expected Output:**
```
🧪 TESTING ENHANCED AGENTIC FEATURES
📧 INPUT: Pre-Client Meeting Prep
🤖 AI ANALYSIS: meeting_type=prep, urgency=high
📅 SCHEDULING RESULT: Scheduled before main meeting
✅ TEST ANALYSIS: PASSED
```

### 2. Timeline Visualization

Generate visual timelines to analyze scheduling decisions:

```bash
cd testing/
python visualize_timelines.py
```

**Interactive Test Menu:**
```
Choose test scenario:
1. Monday Client Validation (Real Google Calendar API)
2. Monday Client Validation (Mock data)  
3. Tuesday Project Status Meeting
4. Wednesday Client Feedback Meeting
5. Simple visualization test
```

## Test Scenarios

### Scenario 1: Monday Client Validation
**Purpose**: Test urgent client meeting with conflict resolution

**Email Content**: "Hi Team. We've just received quick feedback from the client indicating that the instructions we provided aren't working on their end. Let's meet Monday at 9:00 AM to discuss and resolve this issue."

**Expected Behavior**:
- Detect urgency from "quick feedback" and "resolve this issue"
- Identify client-facing nature
- Handle conflicts with lower-priority meetings
- Schedule at requested Monday 9:00 AM time

### Scenario 2: Tuesday Project Status  
**Purpose**: Test regular team meeting scheduling

**Email Content**: "Hi Team. Let's meet on Tuesday at 11:00 A.M and discuss about our on-going Projects."

**Expected Behavior**:
- Parse specific day/time preference
- Handle medium-priority conflicts through rescheduling
- Coordinate multiple attendees' calendars
- Generate comprehensive schedule updates

### Scenario 3: Wednesday Client Feedback
**Purpose**: Test client meeting prioritization

**Email Content**: "Hi Team. We've received the final feedback from the client. Let's review it together and plan next steps. Let's meet on Wednesday at 10:00 A.M."

**Expected Behavior**:
- Recognize client-facing importance
- Handle conflicts with existing client meetings intelligently
- Prioritize based on business impact

### Scenario 4: Cross-Timezone Off-Hours
**Purpose**: Test business hours enforcement

**Email Content**: "International client needs us to meet at 8 PM IST today for 1 hour."

**Expected Behavior**:
- Detect off-hours request (8 PM)
- Apply business rules (no regular meetings after 6 PM)
- Suggest alternative time within business hours
- Handle timezone considerations

### Scenario 5: Prep Meeting Detection
**Purpose**: Test preparation meeting scheduling logic

**Email Content**: "Need 1 hour prep before the important client meeting on Wednesday."

**Expected Behavior**:
- Identify as preparation meeting
- Schedule before main meeting time
- Handle conflicts with early morning scheduling
- Fallback to previous day if needed

## Visualization Features

### Timeline Comparison
Shows before/after view of attendee schedules:

```
⏰ COMPLETE DAY TIMELINE - Monday (2025-07-21)
════════════════════════════════════════════════════════════════════════════════
👤 USERONE
Time   │ BEFORE          │ AFTER
09:00  │     ·           │  ★ NEW CLIENT MEETING
10:00  │  ■ Team Standup │  ■ Team Standup  
11:00  │     ·           │     ·
```

### Conflict Analysis
Highlights scheduling conflicts and resolutions:

```
📋 SCHEDULING ACTIONS TAKEN:
⚠️ CONFLICTS DETECTED:
   • userthree - 1v1 with Team Member (Priority: MEDIUM)
↻ EVENTS RESCHEDULED:
   • 1v1 with Team Member: From 09:00-10:00 → To 14:00-15:00
```

### Real Calendar Integration
Connects to actual Google Calendar data:

```
📅 Fetching real calendar events for 2025-07-21
🔑 Loading credentials for userone.amd@gmail.com
✅ Found 2 events for userone.amd@gmail.com
🤖 INTELLIGENT RESCHEDULING: 1v1 moved to 14:00-15:00
```

## Advanced Testing

### Custom Test Cases
Add your own test scenarios by modifying the test data structure:

```python
test_data = {
    "Request_id": "custom-test-001",
    "From": "your.email@company.com",
    "Attendees": [{"email": "colleague@company.com"}],
    "Subject": "Your Meeting Subject",
    "EmailContent": "Your meeting request email content here...",
    "Datetime": "2025-07-21T10:00:00"
}
```

### Real Calendar Testing
To test with your actual Google Calendar:

1. **Set up OAuth tokens** in the `Keys/` directory
2. **Update email addresses** in test files to match your calendar users
3. **Run with real calendar flag**: `use_real_calendar=True`

```python
timeline_viz = visualizer.visualize_scheduling_impact(
    new_meeting, 
    email_content,
    conflicts, 
    rescheduled_events,
    use_real_calendar=True  # Use real Google Calendar data
)
```

### Performance Testing
Monitor agent performance with multiple scenarios:

```python
# Time multiple test runs
import time
start = time.time()
result = your_meeting_assistant(test_data)
processing_time = time.time() - start
print(f"Processing time: {processing_time:.2f} seconds")
```

## Validation Criteria

### Agent Intelligence
- ✅ **Context extraction** accuracy (urgency, meeting type, relationships)
- ✅ **Priority classification** of conflicting events
- ✅ **Business rules compliance** (off-hours, client priority)
- ✅ **Autonomous decision making** for rescheduling

### Technical Performance  
- ✅ **Response time** <5 seconds for complex scenarios
- ✅ **Calendar API integration** reliability
- ✅ **LLM inference** accuracy and speed
- ✅ **Error handling** and fallback mechanisms

### User Experience
- ✅ **Clear scheduling rationale** in metadata
- ✅ **Comprehensive conflict resolution**
- ✅ **Intuitive visualization** of changes
- ✅ **Minimal user intervention** required

## Troubleshooting

### Common Issues

**Google Calendar API errors**:
- Verify OAuth tokens are in `Keys/` directory
- Check token expiration and refresh if needed
- Ensure calendar API is enabled in Google Cloud Console

**LLM inference failures**:
- Confirm vLLM server is running on `localhost:3000`
- Verify DeepSeek model is loaded correctly
- Check AMD GPU availability and memory

**Test failures**:
- Review email content for clear context indicators
- Verify expected vs actual scheduling decisions
- Check timezone handling and business hours logic

### Debug Mode
Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

The testing framework provides comprehensive validation of the agent's intelligent scheduling capabilities, ensuring reliable performance across diverse meeting scenarios.
