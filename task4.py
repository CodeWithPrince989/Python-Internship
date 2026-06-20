# rock_paper_scissors_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import random
from PIL import Image, ImageTk  # You might need to install: pip install Pillow

class RockPaperScissorsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Rock-Paper-Scissors Game")
        self.root.geometry("700x650")
        self.root.configure(bg='#2c3e50')
        
        # Game variables
        self.choices = ["rock", "paper", "scissors"]
        self.winning_combinations = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper"
        }
        self.emoji_map = {
            "rock": "🪨",
            "paper": "📄",
            "scissors": "✂️"
        }
        self.user_score = 0
        self.computer_score = 0
        self.ties = 0
        self.rounds_played = 0
        self.user_choice = None
        self.computer_choice = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with gradient-like effect
        self.main_frame = tk.Frame(self.root, bg='#2c3e50')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(self.main_frame, 
                              text="🎮 Rock-Paper-Scissors 🎮",
                              font=("Arial", 24, "bold"),
                              bg='#2c3e50',
                              fg='#ecf0f1')
        title_label.pack(pady=10)
        
        # Scoreboard Frame
        self.score_frame = tk.Frame(self.main_frame, bg='#34495e', relief=tk.RAISED, bd=2)
        self.score_frame.pack(fill=tk.X, pady=10)
        
        self.score_labels = {}
        score_data = [
            ("👤 You", "user_score", '#3498db'),
            ("🤖 Computer", "computer_score", '#e74c3c'),
            ("🤝 Ties", "ties", '#f1c40f'),
            ("📈 Rounds", "rounds_played", '#2ecc71')
        ]
        
        for i, (label_text, var_name, color) in enumerate(score_data):
            frame = tk.Frame(self.score_frame, bg='#34495e')
            frame.grid(row=0, column=i, padx=10, pady=5, sticky='nsew')
            
            tk.Label(frame, text=label_text, 
                    font=("Arial", 10),
                    bg='#34495e',
                    fg='#ecf0f1').pack()
            
            self.score_labels[var_name] = tk.Label(frame, 
                                                  text="0",
                                                  font=("Arial", 16, "bold"),
                                                  bg='#34495e',
                                                  fg=color)
            self.score_labels[var_name].pack()
        
        self.score_frame.grid_columnconfigure(0, weight=1)
        self.score_frame.grid_columnconfigure(1, weight=1)
        self.score_frame.grid_columnconfigure(2, weight=1)
        self.score_frame.grid_columnconfigure(3, weight=1)
        
        # Display Area
        self.display_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        self.display_frame.pack(pady=20)
        
        # User choice display
        self.user_display = tk.Label(self.display_frame, 
                                    text="❓",
                                    font=("Arial", 60),
                                    bg='#2c3e50')
        self.user_display.grid(row=0, column=0, padx=30)
        
        tk.Label(self.display_frame, text="VS", 
                font=("Arial", 30, "bold"),
                bg='#2c3e50',
                fg='#ecf0f1').grid(row=0, column=1, padx=30)
        
        # Computer choice display
        self.computer_display = tk.Label(self.display_frame,
                                        text="❓",
                                        font=("Arial", 60),
                                        bg='#2c3e50')
        self.computer_display.grid(row=0, column=2, padx=30)
        
        # User choice label
        tk.Label(self.display_frame, text="You", 
                font=("Arial", 12),
                bg='#2c3e50',
                fg='#3498db').grid(row=1, column=0)
        
        tk.Label(self.display_frame, text="Computer", 
                font=("Arial", 12),
                bg='#2c3e50',
                fg='#e74c3c').grid(row=1, column=2)
        
        # Result Label
        self.result_label = tk.Label(self.main_frame,
                                    text="Ready to play! Choose your move below 👇",
                                    font=("Arial", 14),
                                    bg='#2c3e50',
                                    fg='#ecf0f1')
        self.result_label.pack(pady=10)
        
        # Choice Buttons Frame
        self.choice_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        self.choice_frame.pack(pady=20)
        
        # Create choice buttons with emojis
        choices_data = [
            ("🪨 Rock", "rock", '#e67e22'),
            ("📄 Paper", "paper", '#3498db'),
            ("✂️ Scissors", "scissors", '#e74c3c')
        ]
        
        for text, choice, color in choices_data:
            btn = tk.Button(self.choice_frame,
                           text=text,
                           font=("Arial", 14, "bold"),
                           bg=color,
                           fg='white',
                           padx=20,
                           pady=10,
                           relief=tk.RAISED,
                           bd=3,
                           command=lambda c=choice: self.play_round(c))
            btn.pack(side=tk.LEFT, padx=10)
            
            # Hover effect
            def on_enter(e, btn=btn, color=color):
                btn.config(bg=self.lighten_color(color))
            
            def on_leave(e, btn=btn, color=color):
                btn.config(bg=color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Control Buttons
        control_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        control_frame.pack(pady=10)
        
        self.reset_btn = tk.Button(control_frame,
                                  text="🔄 Reset Game",
                                  font=("Arial", 12),
                                  bg='#95a5a6',
                                  fg='white',
                                  padx=15,
                                  pady=8,
                                  command=self.reset_game)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = tk.Button(control_frame,
                                 text="🚪 Quit",
                                 font=("Arial", 12),
                                 bg='#e74c3c',
                                 fg='white',
                                 padx=15,
                                 pady=8,
                                 command=self.quit_game)
        self.quit_btn.pack(side=tk.LEFT, padx=5)
        
        # Stats Frame
        self.stats_frame = tk.Frame(self.main_frame, bg='#34495e', relief=tk.SUNKEN, bd=1)
        self.stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = tk.Label(self.stats_frame,
                                   text="💡 Click a button to start playing!",
                                   font=("Arial", 10),
                                   bg='#34495e',
                                   fg='#ecf0f1')
        self.stats_label.pack(pady=5)
    
    def lighten_color(self, color):
        """Lighten a color for hover effect."""
        # Simple color lightening for demo
        light_colors = {
            '#e67e22': '#f39c12',
            '#3498db': '#5dade2',
            '#e74c3c': '#ec7063'
        }
        return light_colors.get(color, color)
    
    def play_round(self, user_choice):
        """Play a single round of the game."""
        self.user_choice = user_choice
        self.computer_choice = random.choice(self.choices)
        
        # Update displays
        self.user_display.config(text=self.emoji_map[user_choice])
        self.computer_display.config(text=self.emoji_map[self.computer_choice])
        
        # Determine winner
        winner = self.determine_winner(user_choice, self.computer_choice)
        
        # Update result
        if winner == "tie":
            result_text = "🤝 It's a tie!"
            result_color = '#f1c40f'
            self.ties += 1
        elif winner == "user":
            result_text = f"🎉 You win! {user_choice.title()} beats {self.computer_choice.title()}!"
            result_color = '#2ecc71'
            self.user_score += 1
        else:
            result_text = f"😔 Computer wins! {self.computer_choice.title()} beats {user_choice.title()}!"
            result_color = '#e74c3c'
            self.computer_score += 1
        
        self.rounds_played += 1
        
        # Update result label with animation effect
        self.result_label.config(text=result_text, fg=result_color)
        
        # Update scores
        self.update_scores()
        
        # Update stats
        self.update_stats()
    
    def determine_winner(self, user_choice: str, computer_choice: str) -> str:
        """Determine the winner of the round."""
        if user_choice == computer_choice:
            return "tie"
        elif self.winning_combinations[user_choice] == computer_choice:
            return "user"
        else:
            return "computer"
    
    def update_scores(self):
        """Update score display."""
        self.score_labels['user_score'].config(text=str(self.user_score))
        self.score_labels['computer_score'].config(text=str(self.computer_score))
        self.score_labels['ties'].config(text=str(self.ties))
        self.score_labels['rounds_played'].config(text=str(self.rounds_played))
    
    def update_stats(self):
        """Update stats display."""
        if self.rounds_played > 0:
            win_rate = (self.user_score / self.rounds_played) * 100
            stats_text = f"📊 Win Rate: {win_rate:.1f}% | "
            stats_text += f"Last Round: {self.user_choice.title()} vs {self.computer_choice.title()}"
            self.stats_label.config(text=stats_text)
    
    def reset_game(self):
        """Reset the game state."""
        if messagebox.askyesno("Reset Game", "Are you sure you want to reset all scores?"):
            self.user_score = 0
            self.computer_score = 0
            self.ties = 0
            self.rounds_played = 0
            self.user_choice = None
            self.computer_choice = None
            
            # Reset displays
            self.user_display.config(text="❓")
            self.computer_display.config(text="❓")
            self.result_label.config(text="Game reset! Choose your move 👇", fg='#ecf0f1')
            self.update_scores()
            self.stats_label.config(text="💡 Game reset! Click a button to start playing!")
    
    def quit_game(self):
        """Quit the game with confirmation."""
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit?"):
            if self.rounds_played > 0:
                final_message = f"Final Score:\nYou: {self.user_score}\nComputer: {self.computer_score}\nTies: {self.ties}"
                if self.user_score > self.computer_score:
                    final_message += "\n\n🏆 You're the overall winner! 🏆"
                elif self.computer_score > self.user_score:
                    final_message += "\n\n🤖 Computer wins overall!"
                else:
                    final_message += "\n\n🤝 It's an overall tie!"
                messagebox.showinfo("Game Over", final_message)
            self.root.quit()


def main():
    root = tk.Tk()
    app = RockPaperScissorsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()