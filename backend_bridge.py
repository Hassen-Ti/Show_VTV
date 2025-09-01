"""
Backend Bridge for QML Interface
Connects the existing Python agents to QML UI with Moderator
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from agent_1 import Agent_one
from agent_2 import Agent_two
from agent_moderator import AgentModerator
from config import *
import json

class AgentWorker(QThread):
    """Worker thread for moderated debate"""
    messageStream = pyqtSignal(str, str, int)  # agent_type, content, round_num
    messageComplete = pyqtSignal(str, str, int)  # agent_type, full_message, round_num
    searchNotification = pyqtSignal(str, str)  # agent_type, search_info
    errorOccurred = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, agent_one, agent_two, moderator, topic, prompt_one, prompt_two, use_moderator=True):
        super().__init__()
        self.agent_one = agent_one
        self.agent_two = agent_two
        self.moderator = moderator
        self.topic = topic
        self.prompt_one = prompt_one or OPTIMISTIC_PROMPT
        self.prompt_two = prompt_two or CAUTIOUS_PROMPT
        self.use_moderator = use_moderator
        self.should_stop = False
        
    def stop(self):
        self.should_stop = True
        
    def stream_moderator_message(self, message, round_num=0):
        """Stream moderator messages character by character"""
        for char in message:
            if self.should_stop:
                break
            self.messageStream.emit("moderator", char, round_num)
        self.messageComplete.emit("moderator", message, round_num)
        
    def run(self):
        try:
            # If moderator is enabled, start with introduction
            if self.use_moderator:
                # Moderator introduces the debate
                intro = self.moderator.introduce_debate(self.topic)
                self.stream_moderator_message(intro, 0)
                
                if self.should_stop:
                    return
            
            current_message = self.topic
            agent_one_last_response = ""
            agent_two_last_response = ""
            
            for round_num in range(MAX_CONVERSATION_ROUNDS):
                if self.should_stop:
                    break
                
                # Moderator gives floor to Agent One
                if self.use_moderator:
                    floor_message = self.moderator.give_floor_to_agent(
                        "Agent One 🔥", 
                        is_first=(round_num == 0),
                        previous_argument=agent_two_last_response if agent_two_last_response else None
                    )
                    self.stream_moderator_message(floor_message, round_num + 1)
                    
                    if self.should_stop:
                        break
                
                # Agent One responds
                agent_one_response = ""
                
                def stream_callback_one(chunk):
                    nonlocal agent_one_response
                    agent_one_response += chunk
                    self.messageStream.emit("agent_one", chunk, round_num + 1)
                
                def search_callback_one(search_info):
                    self.searchNotification.emit("agent_one", search_info)
                
                response = self.agent_one.generate_streaming_response_with_search(
                    current_message,
                    self.prompt_one,
                    stream_callback=stream_callback_one,
                    search_callback=search_callback_one
                )
                
                if response.startswith("Error:"):
                    self.errorOccurred.emit(f"Agent One: {response}")
                    return
                    
                self.messageComplete.emit("agent_one", response, round_num + 1)
                agent_one_last_response = response
                current_message = response
                
                if self.should_stop:
                    break
                
                # Moderator gives floor to Agent Two
                if self.use_moderator:
                    floor_message = self.moderator.give_floor_to_agent(
                        "Agent Two 💀",
                        is_first=False,
                        previous_argument=agent_one_last_response
                    )
                    self.stream_moderator_message(floor_message, round_num + 1)
                    
                    if self.should_stop:
                        break
                
                # Agent Two responds
                agent_two_response = ""
                
                def stream_callback_two(chunk):
                    nonlocal agent_two_response
                    agent_two_response += chunk
                    self.messageStream.emit("agent_two", chunk, round_num + 1)
                
                def search_callback_two(search_info):
                    self.searchNotification.emit("agent_two", search_info)
                
                response = self.agent_two.generate_streaming_response_with_search(
                    current_message,
                    self.prompt_two,
                    stream_callback=stream_callback_two,
                    search_callback=search_callback_two
                )
                
                if response.startswith("Error:"):
                    self.errorOccurred.emit(f"Agent Two: {response}")
                    return
                    
                self.messageComplete.emit("agent_two", response, round_num + 1)
                agent_two_last_response = response
                current_message = response
                
                # Moderator interjects every 2 rounds
                if self.use_moderator and (round_num + 1) % 2 == 0 and round_num < MAX_CONVERSATION_ROUNDS - 1:
                    if self.should_stop:
                        break
                        
                    interjection = self.moderator.interject_or_summarize(
                        agent_one_last_response,
                        agent_two_last_response,
                        round_num + 1
                    )
                    self.stream_moderator_message(interjection, round_num + 1)
            
            # Moderator concludes the debate
            if self.use_moderator and not self.should_stop:
                conclusion = self.moderator.conclude_debate(
                    f"Débat sur: {self.topic}"
                )
                self.stream_moderator_message(conclusion, MAX_CONVERSATION_ROUNDS + 1)
            
            self.finished.emit()
            
        except Exception as e:
            self.errorOccurred.emit(str(e))


class BackendBridge(QObject):
    """Bridge between Python backend and QML frontend with Moderator support"""
    
    # Signals to QML
    messageStreamReceived = pyqtSignal(str, str, int)  # agent_type, content, round_num
    messageCompleted = pyqtSignal(str, str, int)  # agent_type, full_message, round_num
    searchStarted = pyqtSignal(str, str)  # agent_type, search_query
    errorOccurred = pyqtSignal(str)  # error_message
    debateFinished = pyqtSignal()
    debateStatusChanged = pyqtSignal(bool)  # is_running
    themeGenerated = pyqtSignal(str)  # generated theme
    
    def __init__(self):
        super().__init__()
        
        # Initialize agents
        try:
            self.agent_one = Agent_one()
            self.agent_two = Agent_two()
            self.moderator = AgentModerator()
        except ValueError as e:
            print(f"Failed to initialize agents: {e}")
            raise
            
        self.worker = None
        self.is_running = False
        self.use_moderator = True  # Toggle for moderator
    
    @pyqtSlot(str)
    def generateTheme(self, user_topic):
        """Generate a debate theme from user input"""
        if not user_topic:
            user_topic = DEFAULT_USER_TOPIC
            
        try:
            theme = self.moderator.generate_debate_theme(user_topic)
            self.themeGenerated.emit(theme)
        except Exception as e:
            self.errorOccurred.emit(f"Theme generation error: {str(e)}")
    
    @pyqtSlot(str, str, str, bool)
    def startDebate(self, topic, prompt_one="", prompt_two="", use_moderator=True):
        """Start the debate with given topic and optional custom prompts"""
        if self.is_running:
            return
            
        # Use defaults if empty
        if not topic:
            topic = DEFAULT_DEBATE_TOPIC
        if not prompt_one:
            prompt_one = OPTIMISTIC_PROMPT
        if not prompt_two:
            prompt_two = CAUTIOUS_PROMPT
            
        self.use_moderator = use_moderator
            
        # Create and configure worker thread
        self.worker = AgentWorker(
            self.agent_one, 
            self.agent_two,
            self.moderator,
            topic,
            prompt_one,
            prompt_two,
            use_moderator
        )
        
        # Connect worker signals
        self.worker.messageStream.connect(self.messageStreamReceived)
        self.worker.messageComplete.connect(self.messageCompleted)
        self.worker.searchNotification.connect(self.searchStarted)
        self.worker.errorOccurred.connect(self.errorOccurred)
        self.worker.finished.connect(self.onDebateFinished)
        
        # Start debate
        self.worker.start()
        self.is_running = True
        self.debateStatusChanged.emit(True)
    
    @pyqtSlot()
    def stopDebate(self):
        """Stop the ongoing debate"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.is_running = False
            self.debateStatusChanged.emit(False)
    
    def onDebateFinished(self):
        """Handle debate completion"""
        self.is_running = False
        self.debateStatusChanged.emit(False)
        self.debateFinished.emit()
    
    @pyqtSlot(result=str)
    def getDefaultTopic(self):
        """Get the default debate topic"""
        return DEFAULT_DEBATE_TOPIC
    
    @pyqtSlot(result=str)
    def getDefaultUserTopic(self):
        """Get the default user topic for theme generation"""
        return DEFAULT_USER_TOPIC
    
    @pyqtSlot(result=str)
    def getOptimisticPrompt(self):
        """Get the default optimistic prompt"""
        return OPTIMISTIC_PROMPT
    
    @pyqtSlot(result=str)
    def getCautiousPrompt(self):
        """Get the default cautious prompt"""
        return CAUTIOUS_PROMPT
    
    @pyqtSlot(result=str)
    def getModeratorPrompt(self):
        """Get the default moderator prompt"""
        return MODERATOR_PROMPT