# AMD MI300-AI Scheduling Agent

An intelligent meeting scheduling system that uses AMD MI300X GPU-accelerated AI models for context-aware calendar management and conflict resolution.

## Overview

This project implements an agentic methodology for meeting scheduling that goes beyond simple calendar slot finding. The system analyzes email content, understands context and priorities, detects conflicts, and makes intelligent rescheduling decisions.

## Core Architecture

### 1. Calendar Manager (Google Calendar Integration)
- **Real-time calendar access** using Google Calendar API
- **Multi-user support** with individual token-based authentication  
- **Business hours filtering** to exclude non-work events
- **Conflict detection** across all attendees' calendars

### 2. NLP Processor (AMD GPU-Accelerated)
- **DeepSeek LLM** running on AMD MI300X via vLLM
- **Context extraction** from email subjects and content
- **Priority analysis** to identify urgent vs routine meetings
- **Meeting relationship detection** (prep meetings, workshops, client calls)
- **Fallback regex parsing** for reliability

### 3. Intelligent Scheduling Engine
- **Multi-criteria optimization** considering urgency, conflicts, and preferences
- **Automatic rescheduling** of lower-priority conflicting events
- **Context-aware decisions** (workshops can use off-hours, prep meetings scheduled before main events)
- **Business rules enforcement** (no meetings during off-hours unless specifically allowed)

## Agentic Methodology

The system implements three layers of intelligent decision-making:

### Layer 1: Context Understanding
The NLP processor extracts semantic meaning from meeting requests:

```python
# Example context extraction
{
    "urgency": "critical",           # Detected from keywords like "ASAP", "urgent"
    "meeting_type": "prep",          # Identified prep meetings vs regular meetings  
    "meeting_relationship": "client_facing",  # Client vs internal meetings
    "time_constraints": "monday",    # Specific day preferences
    "priority_context": "CEO requested emergency meeting"  # Why it's important
}
```

### Layer 2: Conflict Analysis & Prioritization
Events are automatically categorized by priority:

- **CRITICAL**: Workshops, all-day events, CEO meetings (unmovable)
- **HIGH**: Client meetings, presentations, demos  
- **MEDIUM**: Team meetings, 1-on-1s (can be rescheduled)
- **LOW**: Personal events, off-hours blocks

### Layer 3: Intelligent Rescheduling
The system makes autonomous decisions:

1. **CRITICAL conflicts** � Find alternative time for new meeting
2. **HIGH conflicts** � Evaluate importance and reschedule appropriately  
3. **MEDIUM conflicts** � Automatically reschedule conflicting events
4. **Prep meetings** � Schedule before main meeting, fallback to previous day

## Key Features

### Context-Aware Scheduling
- **Prep meeting detection**: Automatically schedules preparation meetings before main events
- **Workshop support**: Allows extended hours for training sessions
- **Urgency handling**: ASAP/critical meetings get immediate time slots
- **Client priority**: Client-facing meetings take precedence over internal ones

### Intelligent Conflict Resolution
- **Automatic rescheduling** of medium-priority conflicts
- **Gap analysis** to find optimal alternative time slots
- **Multi-attendee coordination** ensuring everyone's availability
- **Business hours compliance** with exceptions for workshops

### Real-time Calendar Integration
- **Live Google Calendar data** for accurate conflict detection
- **Token-based authentication** for multiple users
- **Event filtering** to focus on business-relevant meetings
- **Format standardization** for consistent processing

## Technical Implementation

### AMD GPU Acceleration
The system leverages AMD MI300X GPUs through vLLM for fast LLM inference:

```python
client = OpenAI(
    api_key="NULL",
    base_url="http://localhost:3000/v1",  # vLLM endpoint
    timeout=8,
    max_retries=1
)

# Model: deepseek-llm-7b-chat running on AMD MI300X
response = client.chat.completions.create(
    model="/home/user/Models/deepseek-ai/deepseek-llm-7b-chat",
    temperature=0.0,
    max_tokens=200,
    messages=[{"role": "user", "content": context_prompt}]
)
```

### Email Context Analysis
Advanced prompt engineering extracts detailed context:

```python
prompt = f"""Analyze this meeting request email and extract details.

Email Subject: {subject}
Email Content: {email_content}

Extract and return JSON with these fields:
- time_constraints: day of week or "flexible"
- urgency: "critical", "high", "medium", or "low"
- meeting_type: "prep", "workshop", "client", "planning", etc.
- meeting_relationship: relationship to other meetings
- priority_context: explain why urgent/important
"""
```

### Conflict Detection Algorithm
```python
def _detect_conflicts_and_reschedule(self, calendars, optimal_start, optimal_end, attendees):
    conflicts = []
    rescheduled_events = []
    
    for attendee, events in calendars.items():
        for event in events:
            # Check temporal overlap
            if event_start < meeting_end and event_end > meeting_start:
                # Classify priority based on content
                priority = self._classify_event_priority(event['Summary'])
                
                # Apply rescheduling logic based on priority
                if priority == "MEDIUM":
                    new_slot = self._find_available_time_slot(events, duration, target_date)
                    rescheduled_events.append(new_slot)
```

## Business Rules

### Off-Hours Policy
- **Regular meetings**: Restricted to 9 AM - 6 PM business hours
- **Workshops/training**: Can extend to 8 PM for comprehensive sessions
- **Emergency meetings**: Can override off-hours if marked critical

### Priority Hierarchy
1. **Client meetings** take precedence over internal meetings
2. **Prep meetings** are scheduled optimally before main events  
3. **Workshops** get flexibility for extended time slots
4. **Emergency meetings** get immediate available slots

### Rescheduling Logic
- **Never reschedule** CRITICAL priority events
- **Evaluate alternatives** for HIGH priority conflicts
- **Automatically reschedule** MEDIUM priority conflicts
- **Ignore** LOW priority or off-hours conflicts

## Installation

1. **Set up AMD GPU environment** with vLLM and DeepSeek model
2. **Configure Google Calendar API** with OAuth tokens
3. **Install Python dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 
   pip install google-api-python-client openai
   ```
4. **Place OAuth tokens** in `Keys/` directory

## Usage

### Starting the Agent Service
First, start the web service:

```bash
cd AMD-MI300-AI-Scheduling-Agent
python web_service.py
```

The agent will be available at `http://localhost:5000/schedule`

### Making Requests with Curl

Send meeting scheduling requests using curl:

```bash
curl -X POST http://localhost:5000/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "Request_id": "meeting-001",
    "From": "user@company.com",
    "Attendees": [{"email": "colleague@company.com"}],
    "Subject": "Project Review",
    "EmailContent": "Let'\''s meet Monday at 9 AM to review the project status.",
    "Datetime": "2025-07-21T09:00:00",
    "Location": "Conference Room A"
  }'
```

### Health Check
Check if the service is running:

```bash
curl -X GET http://localhost:5000/health
```

### Response Format
```json
{
    "EventStart": "2025-07-21T09:00:00+05:30",
    "EventEnd": "2025-07-21T10:00:00+05:30", 
    "Duration_mins": "60",
    "Attendees": [
        {
            "email": "user@company.com",
            "events": [...] 
        }
    ],
    "MetaData": {
        "urgency": "medium",
        "meeting_type": "planning",
        "context_aware_scheduling": true,
        "amd_gpu_processing": true
    }
}
```

## Performance

- **GPU acceleration** reduces LLM inference time to <2 seconds
- **Real-time calendar access** with <1 second API response
- **Context analysis** processes complex email content in <3 seconds total
- **Conflict resolution** handles 10+ attendees with multiple conflicts efficiently

## Files

- `agent.py` - Main scheduling agent with all components
- `Submission.ipynb` - Jupyter notebook for hackathon submission
- `testing/` - Test cases and visualization tools
- `Keys/` - Google Calendar OAuth tokens

The system represents a significant advancement in calendar management by combining GPU-accelerated AI with intelligent business logic for truly autonomous meeting scheduling.
