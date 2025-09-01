import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLabel, QPushButton, QLineEdit,
                             QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QMovie, QPixmap
from agent_1 import Agent_one
from agent_2 import Agent_two
from config import *

class ConversationThread(QThread):
    """Thread for handling agent conversations without freezing UI"""
    message_stream = pyqtSignal(str, str, int, str)  # agent_type, content, round_num, stream_type
    message_complete = pyqtSignal(str, str, int)  # agent_type, full_message, round_num
    search_notification = pyqtSignal(str, str)  # agent_type, search_query
    error_occurred = pyqtSignal(str)  # error_message
    conversation_complete = pyqtSignal()
    
    def __init__(self, agent_one, agent_two, initial_topic, prompt_one=None, prompt_two=None):
        super().__init__()
        self.agent_one = agent_one
        self.agent_two = agent_two
        self.initial_topic = initial_topic
        self.should_stop = False
        self.prompt_one = prompt_one or OPTIMISTIC_PROMPT
        self.prompt_two = prompt_two or CAUTIOUS_PROMPT
        
    def stop_conversation(self):
        """Signal the thread to stop the conversation"""
        self.should_stop = True
        
    def run(self):
        """Run conversation in background thread with streaming and search"""
        try:
            current_message = self.initial_topic
            
            for round_num in range(MAX_CONVERSATION_ROUNDS):
                if self.should_stop:
                    self.conversation_complete.emit()
                    return
                
                # Agent_one responds with streaming and search capability
                self.agent_one_response = ""
                
                def agent_one_stream_callback(chunk):
                    self.agent_one_response += chunk
                    self.message_stream.emit("agent_one", chunk, round_num + 1, "chunk")
                
                def agent_one_search_callback(search_info):
                    self.search_notification.emit("agent_one", search_info)
                
                response = self.agent_one.generate_streaming_response_with_search(
                    current_message, 
                    self.prompt_one,
                    stream_callback=agent_one_stream_callback,
                    search_callback=agent_one_search_callback
                )
                
                if response.startswith("Error:"):
                    self.error_occurred.emit(f"Agent_one: {response}")
                    return
                
                self.message_complete.emit("agent_one", response, round_num + 1)
                current_message = response
                
                if self.should_stop:
                    self.conversation_complete.emit()
                    return
                
                # Agent_two responds with streaming and search capability
                self.agent_two_response = ""
                
                def agent_two_stream_callback(chunk):
                    self.agent_two_response += chunk
                    self.message_stream.emit("agent_two", chunk, round_num + 1, "chunk")
                
                def agent_two_search_callback(search_info):
                    self.search_notification.emit("agent_two", search_info)
                
                response = self.agent_two.generate_streaming_response_with_search(
                    current_message, 
                    self.prompt_two,
                    stream_callback=agent_two_stream_callback,
                    search_callback=agent_two_search_callback
                )
                
                if response.startswith("Error:"):
                    self.error_occurred.emit(f"Agent_two: {response}")
                    return
                
                self.message_complete.emit("agent_two", response, round_num + 1)
                current_message = response
            
            self.conversation_complete.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Thread error: {str(e)}")

class ModernInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Initialize both AI agents
        try:
            self.agent_one = Agent_one()
            self.agent_two = Agent_two()
            
        except ValueError as e:
            print(f"Startup error: {e}")
            sys.exit(1)
        
        # Initialize conversation state
        self.agent_one_history = ""
        self.agent_two_history = ""
        self.agent_one_current = ""
        self.agent_two_current = ""
        self.agent_one_round = 0
        self.agent_two_round = 0
        self.conversation_thread = None
        
        # Set modern styling with background image
        if os.path.exists("versus.png"):
            self.setStyleSheet(APP_STYLE + f"""
                QMainWindow {{
                    border-image: url(versus.png) 0 0 0 0 stretch stretch;
                }}
            """)
        else:
            self.setStyleSheet(APP_STYLE)
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(LAYOUT_SPACING)
        main_layout.setContentsMargins(LAYOUT_MARGINS, LAYOUT_MARGINS, LAYOUT_MARGINS, LAYOUT_MARGINS)
        
        # Horizontal layout for two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(LAYOUT_SPACING)
        
        # Left column
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Left avatar (Blue)
        self.left_avatar_label = QLabel()
        self.left_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_avatar_label.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 10px;
            }
        """)
        
        # Try to load animated GIF, fallback to static image
        avatar_blue_gif = "avatar_blue.gif"
        avatar_blue_static = "avatar_blue_static.png"
        
        if os.path.exists(avatar_blue_gif):
            self.left_avatar_movie = QMovie(avatar_blue_gif)
            self.left_avatar_movie.setScaledSize(QSize(100, 100))
            self.left_avatar_label.setMovie(self.left_avatar_movie)
            self.left_avatar_movie.start()
        elif os.path.exists(avatar_blue_static):
            pixmap = QPixmap(avatar_blue_static)
            self.left_avatar_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.left_avatar_label.setText("🔵")
            self.left_avatar_label.setStyleSheet("""
                QLabel {
                    font-size: 60px;
                    background: transparent;
                    padding: 10px;
                }
            """)
        
        # Left customization group
        self.left_custom_group = QGroupBox("Customize Agent One")
        self.left_custom_group.setStyleSheet("""
            QGroupBox {
                color: #00aaff;
                border: 1px solid #00aaff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        left_custom_layout = QVBoxLayout()
        left_custom_layout.setSpacing(5)  # Reduce spacing between elements
        
        # Left name field
        left_name_layout = QHBoxLayout()
        left_name_label = QLabel("Name:")
        left_name_label.setMinimumWidth(60)
        self.left_name_input = QLineEdit("Agent One")
        self.left_name_input.setPlaceholderText("Enter agent name...")
        self.left_name_input.textChanged.connect(self.update_left_label)
        left_name_layout.addWidget(left_name_label)
        left_name_layout.addWidget(self.left_name_input)
        
        # Left prompt field
        left_prompt_label = QLabel("Custom Prompt:")
        self.left_prompt_input = QTextEdit()
        self.left_prompt_input.setPlaceholderText("Enter custom prompt or leave empty for default...")
        self.left_prompt_input.setMinimumHeight(120)
        self.left_prompt_input.setMaximumHeight(150)
        self.left_prompt_input.setText(OPTIMISTIC_PROMPT)
        
        left_custom_layout.addLayout(left_name_layout)
        left_custom_layout.addWidget(left_prompt_label)
        left_custom_layout.addWidget(self.left_prompt_input)
        self.left_custom_group.setLayout(left_custom_layout)
        
        # Left text window with label
        self.left_label = QLabel("Agent One (Tech Optimist 🔥)")
        self.left_label.setStyleSheet("""
            QLabel {
                color: #00aaff;
                font-family: 'Consolas';
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        self.left_text = QTextEdit()
        self.left_text.setPlaceholderText("Agent One responses will appear here...")
        self.left_text.setReadOnly(True)
        self.left_text.setStyleSheet("""
            QTextEdit {
                color: #00aaff;
                font-family: 'Consolas';
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: rgba(0, 17, 34, 0.85);
                border: 2px solid #00aaff;
                border-radius: 10px;
            }
        """)
        
        # Left search indicator
        self.left_search_label = QLabel("")
        self.left_search_label.setStyleSheet("""
            color: #00aaff;
            font-family: 'Consolas';
            font-size: 12px;
            font-style: italic;
            padding: 5px;
        """)
        self.left_search_label.setVisible(False)
        
        left_layout.addWidget(self.left_avatar_label)  # Add avatar at the top
        left_layout.addWidget(self.left_custom_group)  # Add customization group
        left_layout.addWidget(self.left_label)
        left_layout.addWidget(self.left_search_label)
        left_layout.addWidget(self.left_text)
        
        # Right column
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Right avatar (Red)
        self.right_avatar_label = QLabel()
        self.right_avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.right_avatar_label.setStyleSheet("""
            QLabel {
                background: transparent;
                padding: 10px;
            }
        """)
        
        # Try to load animated GIF, fallback to static image
        avatar_red_gif = "avatar_red.gif"
        avatar_red_static = "avatar_red_static.png"
        
        if os.path.exists(avatar_red_gif):
            self.right_avatar_movie = QMovie(avatar_red_gif)
            self.right_avatar_movie.setScaledSize(QSize(100, 100))
            self.right_avatar_label.setMovie(self.right_avatar_movie)
            self.right_avatar_movie.start()
        elif os.path.exists(avatar_red_static):
            pixmap = QPixmap(avatar_red_static)
            self.right_avatar_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.right_avatar_label.setText("🔴")
            self.right_avatar_label.setStyleSheet("""
                QLabel {
                    font-size: 60px;
                    background: transparent;
                    padding: 10px;
                }
            """)
        
        # Right customization group
        self.right_custom_group = QGroupBox("Customize Agent Two")
        self.right_custom_group.setStyleSheet("""
            QGroupBox {
                color: #ff4444;
                border: 1px solid #ff4444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        right_custom_layout = QVBoxLayout()
        right_custom_layout.setSpacing(5)  # Reduce spacing between elements
        
        # Right name field
        right_name_layout = QHBoxLayout()
        right_name_label = QLabel("Name:")
        right_name_label.setMinimumWidth(60)
        self.right_name_input = QLineEdit("Agent Two")
        self.right_name_input.setPlaceholderText("Enter agent name...")
        self.right_name_input.textChanged.connect(self.update_right_label)
        right_name_layout.addWidget(right_name_label)
        right_name_layout.addWidget(self.right_name_input)
        
        # Right prompt field
        right_prompt_label = QLabel("Custom Prompt:")
        self.right_prompt_input = QTextEdit()
        self.right_prompt_input.setPlaceholderText("Enter custom prompt or leave empty for default...")
        self.right_prompt_input.setMinimumHeight(120)
        self.right_prompt_input.setMaximumHeight(150)
        self.right_prompt_input.setText(CAUTIOUS_PROMPT)
        
        right_custom_layout.addLayout(right_name_layout)
        right_custom_layout.addWidget(right_prompt_label)
        right_custom_layout.addWidget(self.right_prompt_input)
        self.right_custom_group.setLayout(right_custom_layout)
        
        # Right text window with label
        self.right_label = QLabel("Agent Two (Tech Skeptic 💀)")
        self.right_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-family: 'Consolas';
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        self.right_text = QTextEdit()
        self.right_text.setPlaceholderText("Agent Two responses will appear here...")
        self.right_text.setReadOnly(True)
        self.right_text.setStyleSheet("""
            QTextEdit {
                color: #ff4444;
                font-family: 'Consolas';
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: rgba(0, 17, 34, 0.85);
                border: 2px solid #ff4444;
                border-radius: 10px;
            }
        """)
        
        # Right search indicator
        self.right_search_label = QLabel("")
        self.right_search_label.setStyleSheet("""
            color: #ff4444;
            font-family: 'Consolas';
            font-size: 12px;
            font-style: italic;
            padding: 5px;
        """)
        self.right_search_label.setVisible(False)
        
        right_layout.addWidget(self.right_avatar_label)  # Add avatar at the top
        right_layout.addWidget(self.right_custom_group)  # Add customization group
        right_layout.addWidget(self.right_label)
        right_layout.addWidget(self.right_search_label)
        right_layout.addWidget(self.right_text)
        
        # Add both columns to content layout
        content_layout.addWidget(left_widget)
        content_layout.addWidget(right_widget)
        
        # Create topic input section
        topic_layout = QHBoxLayout()
        topic_label = QLabel("Debate Topic:")
        topic_label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-family: 'Consolas';
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
            }
        """)
        self.topic_input = QLineEdit()
        self.topic_input.setText(DEFAULT_DEBATE_TOPIC)
        self.topic_input.setPlaceholderText("Enter debate topic...")
        self.topic_input.setStyleSheet("""
            QLineEdit {
                color: #00ffff;
                font-family: 'Consolas';
                font-size: 14px;
                padding: 8px;
                background-color: #001122;
                border: 1px solid #00ffff;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #00ffff;
            }
        """)
        topic_layout.addWidget(topic_label)
        topic_layout.addWidget(self.topic_input)
        
        # Create button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # Create toggle customization button
        self.toggle_custom_button = QPushButton("⚙️ Toggle Customization")
        self.toggle_custom_button.clicked.connect(self.toggle_customization)
        
        # Create start button
        self.start_button = QPushButton("🚀 START DEBATE")
        self.start_button.clicked.connect(self.on_start_clicked)
        
        # Create stop button
        self.stop_button = QPushButton("🛑 STOP")
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.toggle_custom_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        
        # Add content, topic input, and buttons to main layout
        main_layout.addLayout(content_layout)
        main_layout.addLayout(topic_layout)
        main_layout.addLayout(button_layout)
    
    def toggle_customization(self):
        """Toggle visibility of customization panels"""
        left_visible = self.left_custom_group.isVisible()
        self.left_custom_group.setVisible(not left_visible)
        self.right_custom_group.setVisible(not left_visible)
        
        if left_visible:
            self.toggle_custom_button.setText("⚙️ Show Customization")
        else:
            self.toggle_custom_button.setText("⚙️ Hide Customization")
    
    def update_left_label(self, text):
        """Update left agent label with custom name"""
        if text:
            self.left_label.setText(f"{text} (Tech Optimist 🔥)")
        else:
            self.left_label.setText("Agent One (Tech Optimist 🔥)")
    
    def update_right_label(self, text):
        """Update right agent label with custom name"""
        if text:
            self.right_label.setText(f"{text} (Tech Skeptic 💀)")
        else:
            self.right_label.setText("Agent Two (Tech Skeptic 💀)")
    
    def on_start_clicked(self):
        # Update button states
        self.start_button.setEnabled(False)
        self.start_button.setText("⚡ DEBATE IN PROGRESS...")
        self.stop_button.setEnabled(True)
        
        # Clear history and search indicators
        self.agent_one_history = ""
        self.agent_two_history = ""
        self.agent_one_current = ""
        self.agent_two_current = ""
        self.agent_one_round = 0
        self.agent_two_round = 0
        self.left_search_label.setVisible(False)
        self.right_search_label.setVisible(False)
        
        # Show starting message
        self.left_text.setText("🔥 Preparing arguments...")
        self.right_text.setText("💀 Loading counterarguments...")
        
        # Get custom topic and prompts
        debate_topic = self.topic_input.text().strip()
        if not debate_topic:
            debate_topic = DEFAULT_DEBATE_TOPIC
        
        custom_prompt_one = self.left_prompt_input.toPlainText().strip()
        custom_prompt_two = self.right_prompt_input.toPlainText().strip()
        
        # Start conversation in background thread with custom topic and prompts
        self.conversation_thread = ConversationThread(
            self.agent_one, self.agent_two, debate_topic,
            prompt_one=custom_prompt_one if custom_prompt_one else None,
            prompt_two=custom_prompt_two if custom_prompt_two else None
        )
        
        # Connect thread signals
        self.conversation_thread.message_stream.connect(self.on_message_stream)
        self.conversation_thread.message_complete.connect(self.on_message_complete)
        self.conversation_thread.search_notification.connect(self.on_search_notification)
        self.conversation_thread.error_occurred.connect(self.on_error_occurred)
        self.conversation_thread.conversation_complete.connect(self.on_conversation_complete)
        
        # Start the thread
        self.conversation_thread.start()
    
    def on_stop_clicked(self):
        """Stop the ongoing debate"""
        if self.conversation_thread and self.conversation_thread.isRunning():
            self.conversation_thread.stop_conversation()
            self.stop_button.setEnabled(False)
            self.stop_button.setText("⏹️ STOPPING...")
    
    def on_search_notification(self, agent_type, search_info):
        """Handle search notifications"""
        if agent_type == "agent_one":
            self.left_search_label.setText(search_info)
            self.left_search_label.setVisible(True)
            # Add search info to current message
            if self.agent_one_current:
                self.agent_one_current += f"\n{search_info}\n"
                self.left_text.setText(self.agent_one_history + self.agent_one_current)
        elif agent_type == "agent_two":
            self.right_search_label.setText(search_info)
            self.right_search_label.setVisible(True)
            # Add search info to current message
            if self.agent_two_current:
                self.agent_two_current += f"\n{search_info}\n"
                self.right_text.setText(self.agent_two_history + self.agent_two_current)
    
    def on_message_stream(self, agent_type, content, round_num, stream_type):
        """Handle streaming message chunks"""
        # Speed up avatar animation when agent is talking
        if agent_type == "agent_one" and hasattr(self, 'left_avatar_movie'):
            self.left_avatar_movie.setSpeed(200)  # Speed up animation
        elif agent_type == "agent_two" and hasattr(self, 'right_avatar_movie'):
            self.right_avatar_movie.setSpeed(200)  # Speed up animation
        
        if agent_type == "agent_one":
            if round_num > self.agent_one_round:
                # New message, clear current and add to history if there was a previous one
                if self.agent_one_current:
                    self.agent_one_history += f"\n\n"
                self.agent_one_current = f"[Round {round_num}]\n"
                self.agent_one_round = round_num
                self.left_search_label.setVisible(False)  # Hide search label for new message
            
            self.agent_one_current += content
            self.left_text.setText(self.agent_one_history + self.agent_one_current)
            # Auto-scroll to bottom
            cursor = self.left_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.left_text.setTextCursor(cursor)
            
        elif agent_type == "agent_two":
            if round_num > self.agent_two_round:
                # New message, clear current and add to history if there was a previous one
                if self.agent_two_current:
                    self.agent_two_history += f"\n\n"
                self.agent_two_current = f"[Round {round_num}]\n"
                self.agent_two_round = round_num
                self.right_search_label.setVisible(False)  # Hide search label for new message
            
            self.agent_two_current += content
            self.right_text.setText(self.agent_two_history + self.agent_two_current)
            # Auto-scroll to bottom
            cursor = self.right_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.right_text.setTextCursor(cursor)
    
    def on_message_complete(self, agent_type, full_message, round_num):
        """Handle completed messages"""
        if agent_type == "agent_one":
            # Finalize the current message in history
            self.agent_one_history += self.agent_one_current
            self.left_search_label.setVisible(False)  # Hide search label
            # Slow down avatar animation
            if hasattr(self, 'left_avatar_movie'):
                self.left_avatar_movie.setSpeed(100)  # Normal speed
            print(f"Agent_one [Round {round_num}]: {full_message[:100]}...")
        elif agent_type == "agent_two":
            # Finalize the current message in history
            self.agent_two_history += self.agent_two_current
            self.right_search_label.setVisible(False)  # Hide search label
            # Slow down avatar animation
            if hasattr(self, 'right_avatar_movie'):
                self.right_avatar_movie.setSpeed(100)  # Normal speed
            print(f"Agent_two [Round {round_num}]: {full_message[:100]}...")
    
    def on_error_occurred(self, error_message):
        """Handle errors from conversation thread"""
        print(f"Conversation error: {error_message}")
        error_text = f"\n\n❌ ERROR: {error_message}"
        self.left_text.setText(self.agent_one_history + error_text)
        self.right_text.setText(self.agent_two_history + error_text)
        self.left_search_label.setVisible(False)
        self.right_search_label.setVisible(False)
        self.reset_buttons()
    
    def on_conversation_complete(self):
        """Handle conversation completion"""
        completion_message = "\n\n" + "=" * 30 + "\n🏁 DEBATE COMPLETED!\n" + "=" * 30
        self.left_text.setText(self.agent_one_history + completion_message)
        self.right_text.setText(self.agent_two_history + completion_message)
        self.left_search_label.setVisible(False)
        self.right_search_label.setVisible(False)
        self.reset_buttons()
        print("Debate completed successfully")
    
    def reset_buttons(self):
        """Reset buttons to original state"""
        self.start_button.setEnabled(True)
        self.start_button.setText("🚀 START DEBATE")
        self.stop_button.setEnabled(False)
        self.stop_button.setText("🛑 STOP")

def main():
    app = QApplication(sys.argv)
    window = ModernInterface()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()