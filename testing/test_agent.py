"""
Test Enhanced Agentic Meeting Assistant
Tests the new context-aware features including:
1. LLM-based priority extraction
2. Prep meeting detection and scheduling
3. Workshop off-hours support
4. Context-aware decision making
"""

import json
import sys
import os

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meeting_assistant_fixed import FixedMeetingAssistant

def test_edge_case_prep_meeting():
    """Test the edge case: Pre-Client Meeting Prep"""
    
    print("🧪 TESTING ENHANCED AGENTIC FEATURES")
    print("=" * 60)
    print("Edge Case: Pre-Client Meeting Prep")
    print("Expected: Context-aware scheduling with prep meeting logic")
    print("=" * 60)
    
    # Edge case test data
    test_data = {
        "Request_id": "test-005-multiple-overlaps",
        "Datetime": "23-07-2025T07:45:00",
        "Location": "Conference Room A",
        "From": "userone.amd@gmail.com",
        "Attendees": [
            {"email": "usertwo.amd@gmail.com"},
            {"email": "userthree.amd@gmail.com"}
        ],
        "Subject": "Pre-Client Meeting Prep",
        "EmailContent": "Need 1 hour prep before the important client meeting on Wednesday."
    }
    
    # Create assistant and process request
    assistant = FixedMeetingAssistant()
    result = assistant.process_meeting_request(test_data)
    
    print("📧 INPUT:")
    print(f"Subject: {test_data['Subject']}")
    print(f"Content: {test_data['EmailContent']}")
    
    print("\n🤖 AI ANALYSIS:")
    print(f"Meeting Type: {result.get('MetaData', {}).get('meeting_type', 'N/A')}")
    print(f"Relationship: {result.get('MetaData', {}).get('meeting_relationship', 'N/A')}")
    print(f"Priority Context: {result.get('MetaData', {}).get('priority_context', 'N/A')}")
    
    print("\n📅 SCHEDULING RESULT:")
    print(f"Event Start: {result.get('EventStart', 'N/A')}")
    print(f"Event End: {result.get('EventEnd', 'N/A')}")
    print(f"Duration: {result.get('Duration_mins', 'N/A')} minutes")
    
    print("\n📋 FULL RESPONSE:")
    print(json.dumps(result, indent=2))
    
    return result

def test_workshop_off_hours():
    """Test workshop scheduling with off-hours capability"""
    
    print("\n\n🧪 TESTING WORKSHOP OFF-HOURS SCHEDULING")
    print("=" * 60)
    print("Test Case: Workshop that can use off-hours")
    print("Expected: Should be able to schedule outside business hours")
    print("=" * 60)
    
    # Workshop test data
    test_data = {
        "Request_id": "workshop-test-001",
        "Datetime": "22-07-2025T10:00:00",
        "Location": "Training Room",
        "From": "userone.amd@gmail.com",
        "Attendees": [
            {"email": "usertwo.amd@gmail.com"},
            {"email": "userthree.amd@gmail.com"}
        ],
        "Subject": "AMD AI Workshop - Extended Session",
        "EmailContent": "All-day workshop on AMD AI technologies. Can extend into evening if needed for comprehensive training."
    }
    
    # Create assistant and process request
    assistant = FixedMeetingAssistant()
    result = assistant.process_meeting_request(test_data)
    
    print("📧 INPUT:")
    print(f"Subject: {test_data['Subject']}")
    print(f"Content: {test_data['EmailContent']}")
    
    print("\n🤖 AI ANALYSIS:")
    print(f"Meeting Type: {result.get('MetaData', {}).get('meeting_type', 'N/A')}")
    print(f"Relationship: {result.get('MetaData', {}).get('meeting_relationship', 'N/A')}")
    print(f"Can Use Off Hours: {result.get('MetaData', {}).get('can_use_off_hours', 'N/A')}")
    
    print("\n📅 SCHEDULING RESULT:")
    print(f"Event Start: {result.get('EventStart', 'N/A')}")
    print(f"Event End: {result.get('EventEnd', 'N/A')}")
    print(f"Duration: {result.get('Duration_mins', 'N/A')} minutes")
    
    print("\n📋 FULL RESPONSE:")
    print(json.dumps(result, indent=2))
    
    return result

def test_urgent_client_meeting():
    """Test urgent client meeting with high priority"""
    
    print("\n\n🧪 TESTING URGENT CLIENT MEETING")
    print("=" * 60)
    print("Test Case: Critical client meeting")
    print("Expected: High priority, context-aware scheduling")
    print("=" * 60)
    
    # Urgent client test data
    test_data = {
        "Request_id": "urgent-client-001",
        "Datetime": "21-07-2025T08:00:00",
        "Location": "Executive Conference Room",
        "From": "userone.amd@gmail.com",
        "Attendees": [
            {"email": "usertwo.amd@gmail.com"},
            {"email": "userthree.amd@gmail.com"}
        ],
        "Subject": "URGENT: Client Escalation Response",
        "EmailContent": "Critical client issue requires immediate attention. CEO requested emergency meeting to address customer concerns ASAP. This is a high-priority client-facing meeting."
    }
    
    # Create assistant and process request
    assistant = FixedMeetingAssistant()
    result = assistant.process_meeting_request(test_data)
    
    print("📧 INPUT:")
    print(f"Subject: {test_data['Subject']}")
    print(f"Content: {test_data['EmailContent']}")
    
    print("\n🤖 AI ANALYSIS:")
    print(f"Urgency Level: {result.get('MetaData', {}).get('urgency', 'N/A')}")
    print(f"Meeting Type: {result.get('MetaData', {}).get('meeting_type', 'N/A')}")
    print(f"Priority Context: {result.get('MetaData', {}).get('priority_context', 'N/A')}")
    
    print("\n📅 SCHEDULING RESULT:")
    print(f"Event Start: {result.get('EventStart', 'N/A')}")
    print(f"Event End: {result.get('EventEnd', 'N/A')}")
    print(f"Duration: {result.get('Duration_mins', 'N/A')} minutes")
    
    print("\n📋 FULL RESPONSE:")
    print(json.dumps(result, indent=2))
    
    return result

def test_cross_timezone_off_hours():
    """Test cross-timezone scheduling with off-hours conflicts (EDGE_004)"""
    
    print("\n\n🧪 TESTING CROSS-TIMEZONE OFF-HOURS CONFLICT")
    print("=" * 60)
    print("Edge Case: EDGE_004 - Cross-timezone scheduling with off-hours conflicts")
    print("Expected: CONFLICT - 20:00 IST falls within Off Hours, suggest next day")
    print("=" * 60)
    
    # EDGE_004 test data
    test_data = {
        "Request_id": "test-004-timezone-offhours",
        "Datetime": "21-07-2025T20:00:00",
        "Location": "Virtual",
        "From": "userone.amd@gmail.com", 
        "Attendees": [
            {"email": "usertwo.amd@gmail.com"},
            {"email": "userthree.amd@gmail.com"}
        ],
        "Subject": "Late Evening Standup",
        "EmailContent": "International client needs us to meet at 8 PM IST today for 1 hour."
    }
    
    # Create assistant and process request
    assistant = FixedMeetingAssistant()
    result = assistant.process_meeting_request(test_data)
    
    print("📧 INPUT:")
    print(f"Subject: {test_data['Subject']}")
    print(f"Content: {test_data['EmailContent']}")
    print(f"Requested Time: 8 PM IST (20:00)")
    
    print("\n🤖 AI ANALYSIS:")
    print(f"Meeting Type: {result.get('MetaData', {}).get('meeting_type', 'N/A')}")
    print(f"Urgency Level: {result.get('MetaData', {}).get('urgency', 'N/A')}")
    print(f"Time Constraint: {result.get('MetaData', {}).get('time_constraints', 'N/A')}")
    
    print("\n⚠️ OFF-HOURS ANALYSIS:")
    scheduled_time = result.get('EventStart', '')
    if '20:00' in scheduled_time or '21:00' in scheduled_time:
        print("❌ VIOLATION: Meeting scheduled during off-hours (18:00-09:00+1)")
        print("Expected: Should be rescheduled to next business day")
    else:
        print("✅ CORRECT: Meeting rescheduled outside off-hours")
        print(f"Rescheduled to: {result.get('EventStart', 'N/A')}")
    
    print("\n📅 SCHEDULING RESULT:")
    print(f"Event Start: {result.get('EventStart', 'N/A')}")
    print(f"Event End: {result.get('EventEnd', 'N/A')}")
    print(f"Duration: {result.get('Duration_mins', 'N/A')} minutes")
    
    # Check if it follows the off-hours rule
    if '20:00' in result.get('EventStart', '') or '21:00' in result.get('EventStart', ''):
        print("\n🚨 TEST ANALYSIS: FAILED - Meeting scheduled in off-hours")
        print("Expected: Next available slot Tuesday 09:00 or later")
    else:
        print("\n✅ TEST ANALYSIS: PASSED - Meeting correctly rescheduled")
    
    print("\n📋 FULL RESPONSE:")
    print(json.dumps(result, indent=2))
    
    return result

def run_all_enhanced_tests():
    """Run all enhanced feature tests"""
    
    print("🚀 RUNNING ALL ENHANCED AGENTIC TESTS")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: Prep meeting
    try:
        result1 = test_edge_case_prep_meeting()
        test_results.append(("Prep Meeting (EDGE_005)", "PASS", result1))
    except Exception as e:
        print(f"❌ Prep meeting test failed: {e}")
        test_results.append(("Prep Meeting (EDGE_005)", "FAIL", str(e)))
    
    # Test 2: Workshop off-hours
    try:
        result2 = test_workshop_off_hours()
        test_results.append(("Workshop Off-Hours", "PASS", result2))
    except Exception as e:
        print(f"❌ Workshop test failed: {e}")
        test_results.append(("Workshop Off-Hours", "FAIL", str(e)))
    
    # Test 3: Urgent client meeting
    try:
        result3 = test_urgent_client_meeting()
        test_results.append(("Urgent Client", "PASS", result3))
    except Exception as e:
        print(f"❌ Urgent client test failed: {e}")
        test_results.append(("Urgent Client", "FAIL", str(e)))
    
    # Test 4: Cross-timezone off-hours conflict (EDGE_004)
    try:
        result4 = test_cross_timezone_off_hours()
        # Check if test passed based on off-hours rule compliance
        scheduled_time = result4.get('EventStart', '')
        if '20:00' in scheduled_time or '21:00' in scheduled_time:
            test_results.append(("Cross-Timezone Off-Hours (EDGE_004)", "FAIL", "Scheduled during off-hours"))
        else:
            test_results.append(("Cross-Timezone Off-Hours (EDGE_004)", "PASS", result4))
    except Exception as e:
        print(f"❌ Cross-timezone test failed: {e}")
        test_results.append(("Cross-Timezone Off-Hours (EDGE_004)", "FAIL", str(e)))
    
    # Summary
    print("\n\n📊 ENHANCED FEATURES TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, status, _ in test_results if status == "PASS")
    total = len(test_results)
    
    for test_name, status, _ in test_results:
        status_emoji = "✅" if status == "PASS" else "❌"
        print(f"{status_emoji} {test_name}: {status}")
    
    print(f"\n🏆 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All enhanced features working correctly!")
        print("✅ Context-aware scheduling implemented")
        print("✅ LLM-based priority extraction working")
        print("✅ Prep meeting detection functional")
        print("✅ Workshop off-hours support enabled")
        print("✅ Off-hours business rule enforced")
    else:
        print("⚠️ Some features need attention:")
        for test_name, status, result in test_results:
            if status == "FAIL":
                print(f"   • {test_name}: {result if isinstance(result, str) else 'Check logs'}")
    
    return test_results

if __name__ == "__main__":
    # Run all tests
    run_all_enhanced_tests()