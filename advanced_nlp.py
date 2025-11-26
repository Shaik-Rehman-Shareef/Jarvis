"""
Advanced Natural Language Processing for JARVIS
Handles complex commands, context understanding, and intelligent responses
"""

import re
import json
from datetime import datetime, timedelta
from logger import logger
from tts import tts

class AdvancedNLP:
    """Advanced natural language processing for complex commands"""
    
    def __init__(self):
        self.command_patterns = {
            # Multi-step commands
            'multi_step': [
                r'(.*) and (then )?(.*)',
                r'(.*), (then )?(.*)',
                r'first (.*) then (.*)',
                r'after (.*) do (.*)'
            ],
            
            # Conditional commands
            'conditional': [
                r'if (.*) then (.*)',
                r'when (.*) do (.*)',
                r'unless (.*) do (.*)'
            ],
            
            # Time-based commands
            'scheduled': [
                r'in (\d+) (minutes?|hours?) (.*)',
                r'at (\d{1,2}):?(\d{0,2}) (am|pm)? (.*)',
                r'tomorrow (.*)',
                r'next (week|month) (.*)'
            ],
            
            # Information queries
            'questions': [
                r'what is (.*)\??',
                r'how (do|can) I (.*)\??',
                r'where is (.*)\??',
                r'when (is|was|will) (.*)\??',
                r'why (.*)\??'
            ],
            
            # File operations
            'file_ops': [
                r'(find|search for|locate) (.*) file',
                r'(create|make) a (.*) file',
                r'(delete|remove) (.*) file',
                r'(copy|move) (.*) to (.*)',
                r'(show|list) (.*) files'
            ]
        }
        
        self.context_keywords = {
            'urgency': ['urgent', 'immediately', 'asap', 'quickly', 'now'],
            'politeness': ['please', 'could you', 'would you', 'if you don\'t mind'],
            'uncertainty': ['maybe', 'perhaps', 'possibly', 'might', 'could'],
            'affirmation': ['yes', 'yeah', 'sure', 'okay', 'alright', 'do it'],
            'negation': ['no', 'nope', 'don\'t', 'cancel', 'never mind', 'forget it']
        }
    
    def analyze_command(self, command):
        """Analyze command for complexity and intent"""
        analysis = {
            'original': command,
            'type': 'simple',
            'intent': None,
            'entities': [],
            'context': {},
            'urgency': 'normal',
            'politeness': False,
            'sub_commands': []
        }
        
        # Check urgency
        if any(word in command.lower() for word in self.context_keywords['urgency']):
            analysis['urgency'] = 'high'
        
        # Check politeness
        if any(phrase in command.lower() for phrase in self.context_keywords['politeness']):
            analysis['politeness'] = True
        
        # Check for multi-step commands
        for pattern in self.command_patterns['multi_step']:
            match = re.search(pattern, command.lower())
            if match:
                analysis['type'] = 'multi_step'
                analysis['sub_commands'] = [match.group(1).strip(), match.group(3).strip()]
                break
        
        # Check for conditional commands
        for pattern in self.command_patterns['conditional']:
            match = re.search(pattern, command.lower())
            if match:
                analysis['type'] = 'conditional'
                analysis['condition'] = match.group(1).strip()
                analysis['action'] = match.group(2).strip()
                break
        
        # Check for scheduled commands
        for pattern in self.command_patterns['scheduled']:
            match = re.search(pattern, command.lower())
            if match:
                analysis['type'] = 'scheduled'
                analysis['timing'] = match.groups()
                analysis['action'] = match.group(-1).strip()
                break
        
        # Check for questions
        for pattern in self.command_patterns['questions']:
            match = re.search(pattern, command.lower())
            if match:
                analysis['type'] = 'question'
                analysis['query'] = match.group(1).strip()
                break
        
        return analysis
    
    def process_complex_command(self, command, processor):
        """Process complex commands using the main command processor"""
        analysis = self.analyze_command(command)
        
        logger.log_activity(f"Command analysis: {analysis['type']} - {analysis.get('intent', 'unknown')}")
        
        if analysis['type'] == 'multi_step':
            return self._handle_multi_step(analysis, processor)
        elif analysis['type'] == 'conditional':
            return self._handle_conditional(analysis, processor)
        elif analysis['type'] == 'scheduled':
            return self._handle_scheduled(analysis, processor)
        elif analysis['type'] == 'question':
            return self._handle_question(analysis)
        else:
            # Fall back to regular processing
            return None
    
    def _handle_multi_step(self, analysis, processor):
        """Handle multi-step commands"""
        sub_commands = analysis['sub_commands']
        
        response = f"I'll do that in steps: first {sub_commands[0]}, then {sub_commands[1]}."
        tts.speak(response)
        
        # Execute first command
        try:
            processor.process_command(sub_commands[0])
            
            # Brief pause between commands
            import time
            time.sleep(1)
            
            # Execute second command
            processor.process_command(sub_commands[1])
            
            completion_response = "Both tasks completed successfully."
            tts.speak(completion_response)
            return response + " " + completion_response
            
        except Exception as e:
            logger.log_error("Error in multi-step command", e)
            error_response = "I encountered an issue while executing the multi-step command."
            tts.speak(error_response)
            return error_response
    
    def _handle_conditional(self, analysis, processor):
        """Handle conditional commands (basic implementation)"""
        condition = analysis['condition']
        action = analysis['action']
        
        # For now, just acknowledge the conditional
        response = f"I understand you want me to {action} if {condition}. However, I can't evaluate conditions yet, so I'll execute the action now."
        tts.speak(response)
        
        # Execute the action
        processor.process_command(action)
        return response
    
    def _handle_scheduled(self, analysis, processor):
        """Handle scheduled commands (basic implementation)"""
        timing = analysis['timing']
        action = analysis['action']
        
        response = f"I understand you want me to {action} at the specified time. For now, I'll execute it immediately."
        tts.speak(response)
        
        # Execute immediately (would need a scheduler for real timing)
        processor.process_command(action)
        return response
    
    def _handle_question(self, analysis):
        """Handle question-type commands"""
        query = analysis['query']
        
        # Basic question answering
        if 'time' in query:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
        elif 'date' in query:
            from datetime import datetime
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {current_date}"
        elif 'weather' in query:
            response = "I don't have access to weather data at the moment."
        elif 'your name' in query or 'who are you' in query:
            response = "I'm JARVIS, your virtual assistant."
        else:
            response = f"I'm not sure about {query}. Could you be more specific or try a different question?"
        
        tts.speak(response)
        return response

class SmartSuggestions:
    """Provide smart suggestions based on context and patterns"""
    
    def __init__(self):
        self.usage_patterns = {}
        self.common_workflows = {
            'coding_session': [
                'open visual studio code',
                'open chrome for documentation',
                'set focus mode'
            ],
            'meeting_prep': [
                'check calendar',
                'open zoom',
                'minimize distractions'
            ],
            'end_of_day': [
                'save all work',
                'close applications',
                'system summary'
            ]
        }
    
    def get_contextual_suggestions(self, recent_commands, current_time):
        """Get suggestions based on context"""
        suggestions = []
        
        # Time-based suggestions
        hour = current_time.hour
        if 9 <= hour <= 10:
            suggestions.append("Would you like me to check your morning schedule?")
        elif 17 <= hour <= 18:
            suggestions.append("End of workday approaching. Should I help you wrap up?")
        
        # Pattern-based suggestions
        if len(recent_commands) >= 2:
            last_two = [cmd.lower() for cmd in recent_commands[-2:]]
            
            if 'open' in last_two[0] and 'open' in last_two[1]:
                suggestions.append("I notice you're opening multiple apps. Would you like me to organize your workspace?")
            
            if 'file' in ' '.join(last_two):
                suggestions.append("Need help with any other file operations?")
        
        return suggestions
    
    def suggest_workflow(self, trigger_command):
        """Suggest complete workflows based on trigger command"""
        trigger = trigger_command.lower()
        
        if any(word in trigger for word in ['code', 'program', 'develop']):
            return self.common_workflows.get('coding_session')
        elif any(word in trigger for word in ['meeting', 'call', 'zoom']):
            return self.common_workflows.get('meeting_prep')
        elif any(word in trigger for word in ['done', 'finish', 'end day']):
            return self.common_workflows.get('end_of_day')
        
        return None

# Global instances
advanced_nlp = AdvancedNLP()
smart_suggestions = SmartSuggestions()
