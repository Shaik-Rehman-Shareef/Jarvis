"""
Conversation context and personality module for JARVIS
Handles conversational intelligence, context memory, and personality traits
"""

import json
import time
from datetime import datetime, timedelta
from logger import logger

class ConversationContext:
    """Manages conversation context and memory"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_context = {}
        self.user_preferences = {}
        self.last_interaction_time = None
        self.session_start_time = datetime.now()
        
    def add_interaction(self, user_input, assistant_response):
        """Add interaction to conversation history"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': assistant_response,
            'context': dict(self.current_context)
        }
        
        self.conversation_history.append(interaction)
        self.last_interaction_time = datetime.now()
        
        # Keep only last 10 interactions to prevent memory bloat
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
    
    def get_recent_context(self, num_interactions=3):
        """Get recent conversation context"""
        return self.conversation_history[-num_interactions:] if self.conversation_history else []
    
    def update_context(self, key, value):
        """Update current context"""
        self.current_context[key] = value
        logger.log_activity(f"Context updated: {key} = {value}")
    
    def get_context(self, key, default=None):
        """Get context value"""
        return self.current_context.get(key, default)
    
    def is_follow_up_likely(self):
        """Check if user might want to follow up on previous command"""
        if not self.last_interaction_time:
            return False
        
        time_since_last = datetime.now() - self.last_interaction_time
        return time_since_last < timedelta(minutes=2)

class JarvisPersonality:
    """JARVIS personality and response generation"""
    
    def __init__(self):
        self.personality_traits = {
            'formal_but_friendly': True,
            'proactive': True,
            'knowledgeable': True,
            'loyal': True,
            'efficient': True
        }
        
    def get_greeting(self, time_of_day=None):
        """Get personalized greeting based on time"""
        if not time_of_day:
            hour = datetime.now().hour
            if hour < 12:
                time_of_day = "morning"
            elif hour < 17:
                time_of_day = "afternoon"
            else:
                time_of_day = "evening"
        
        greetings = {
            "morning": [
                "Good morning! How may I assist you today?",
                "Good morning, sir. Ready to tackle the day?",
                "Morning! What shall we accomplish today?"
            ],
            "afternoon": [
                "Good afternoon! How can I help you?",
                "Good afternoon, sir. What can I do for you?",
                "Afternoon! How may I be of service?"
            ],
            "evening": [
                "Good evening! How may I assist you?",
                "Good evening, sir. How can I help?",
                "Evening! What do you need assistance with?"
            ]
        }
        
        import random
        return random.choice(greetings.get(time_of_day, greetings["morning"]))
    
    def get_acknowledgment(self, context=None):
        """Get contextual acknowledgment"""
        basic_acknowledgments = [
            "Yes sir?",
            "I'm listening.",
            "How can I help you?",
            "At your service.",
            "Yes?",
            "Ready for your command.",
            "I'm here."
        ]
        
        # Add contextual acknowledgments based on recent activity
        contextual_acknowledgments = []
        
        if context and context.is_follow_up_likely():
            contextual_acknowledgments.extend([
                "Yes, anything else?",
                "What else can I do for you?",
                "How else may I assist?",
                "Continuing to assist..."
            ])
        
        # Add time-based acknowledgments
        hour = datetime.now().hour
        if hour < 8:
            contextual_acknowledgments.extend([
                "Up early today, I see. How can I help?",
                "Good morning, sir. What can I do for you?"
            ])
        elif hour > 22:
            contextual_acknowledgments.extend([
                "Working late tonight? How can I assist?",
                "Evening, sir. What do you need?"
            ])
        
        import random
        all_acknowledgments = basic_acknowledgments + contextual_acknowledgments
        return random.choice(all_acknowledgments)
    
    def get_task_completion_response(self, task_type=None):
        """Get response for completed tasks"""
        basic_responses = [
            "Task completed, sir.",
            "Done.",
            "Complete.",
            "All set.",
            "Finished."
        ]
        
        task_specific_responses = {
            "file_operation": [
                "File operation completed successfully.",
                "File handled as requested.",
                "Done with the file operation."
            ],
            "web_search": [
                "Search results ready for you.",
                "Found what you were looking for.",
                "Search completed."
            ],
            "system_operation": [
                "System operation completed.",
                "System updated as requested.",
                "Changes applied successfully."
            ]
        }
        
        import random
        responses = task_specific_responses.get(task_type, basic_responses)
        return random.choice(responses)
    
    def get_error_response(self, error_type=None):
        """Get polite error response"""
        general_errors = [
            "I apologize, but I encountered an issue.",
            "I'm sorry, something went wrong.",
            "My apologies, I couldn't complete that task.",
            "I'm afraid there was a problem."
        ]
        
        specific_errors = {
            "not_found": [
                "I couldn't locate what you're looking for.",
                "That item doesn't seem to exist.",
                "I'm unable to find that resource."
            ],
            "permission_denied": [
                "I don't have the necessary permissions for that.",
                "Access denied for that operation.",
                "I'm not authorized to perform that action."
            ],
            "network_error": [
                "I'm experiencing connectivity issues.",
                "Network connection seems to be unavailable.",
                "I can't reach the internet right now."
            ]
        }
        
        import random
        responses = specific_errors.get(error_type, general_errors)
        return random.choice(responses)
    
    def get_clarification_request(self, unclear_command):
        """Get clarification for unclear commands"""
        clarifications = [
            f"I'm not sure I understood '{unclear_command}'. Could you clarify?",
            f"Could you be more specific about '{unclear_command}'?",
            f"I need a bit more detail about what you'd like me to do with '{unclear_command}'.",
            f"I didn't quite catch that. Could you rephrase '{unclear_command}'?",
        ]
        
        import random
        return random.choice(clarifications)
    
    def get_proactive_suggestion(self, context=None):
        """Get proactive suggestions based on context"""
        suggestions = []
        
        if context:
            # Time-based suggestions
            hour = datetime.now().hour
            if hour == 9:
                suggestions.append("Would you like me to check your calendar for today?")
            elif hour == 17:
                suggestions.append("End of workday approaching. Should I summarize today's activities?")
            elif hour == 22:
                suggestions.append("It's getting late. Would you like me to set a morning alarm?")
            
            # Context-based suggestions
            recent_context = context.get_recent_context(2)
            if recent_context:
                last_command = recent_context[-1].get('user_input', '').lower()
                if 'open' in last_command:
                    suggestions.append("Would you like me to organize your open windows?")
                elif 'email' in last_command:
                    suggestions.append("Should I check for new messages?")
                elif 'file' in last_command:
                    suggestions.append("Need help with any other files?")
        
        if suggestions:
            import random
            return random.choice(suggestions)
        
        return None

# Global instances
conversation_context = ConversationContext()
jarvis_personality = JarvisPersonality()
