import tkinter as tk
from tkinter import messagebox
from logic import grammar, text_to_midi2


def create_visual_grid(frame):
    """
    Displays all the symbols and their visual box representation in a horizontal layout.
    """
    # Clear the frame first
    for widget in frame.winfo_children():
        widget.destroy()

    column = 0  # Start placing sections from the first column
    for category, tokens in grammar.items():
        if isinstance(tokens, dict):  # Only process tokens that have patterns
            # Create a frame for each section
            section_frame = tk.Frame(frame)
            section_frame.grid(row=0, column=column, padx=20, pady=10)  # Place each section in a new column

            # Display the category name
            tk.Label(section_frame, text=category, font=("Arial", 14, "bold")).pack(anchor="w", pady=5)

            # Display symbols and their visual patterns
            for symbol, pattern in tokens.items():
                row_frame = tk.Frame(section_frame)
                row_frame.pack(anchor="w", pady=2)

                # Display the symbol
                tk.Label(row_frame, text=f"{symbol}:", font=("Arial", 12)).pack(side="left", padx=5)

                # Display the visual representation of the pattern
                for value in pattern:
                    color = "black" if value == 1 else "white"
                    tk.Label(row_frame, bg=color, width=2, height=1, relief="solid").pack(side="left", padx=1)

            column += 1  # Move to the next column for the next section


def log_message(message, is_error=False):
    """
    Logs a message to the console box.
    """
    console_box.config(state="normal")  # Enable editing to append
    console_box.insert(tk.END, message + "\n")
    console_box.see(tk.END)  # Auto-scroll to the latest log
    if is_error:
        console_box.tag_add("error", "end-2l", "end-1l")
        console_box.tag_config("error", foreground="red")
    console_box.config(state="disabled")  # Disable editing to prevent user input


def run_midi_conversion():
    input_text = input_field.get()
    file_name = file_name_field.get().strip()

    if not input_text:
        log_message("Error: Input field cannot be empty.", is_error=True)
        return

    if not file_name:
        log_message("Error: File name field cannot be empty.", is_error=True)
        return

    if not file_name.endswith(".mid"):
        file_name += ".mid"

    try:
        # Pass the log_message function as the logger to text_to_midi2
        text_to_midi2(input_text, output_file=file_name, logger=log_message)
    except Exception as e:
        log_message(f"An unexpected error occurred: {e}", is_error=True)


# Main Tkinter setup
root = tk.Tk()
root.title("Text to MIDI Converter with Symbol Visualizer")

# Top frame for the visual representation
visual_frame = tk.Frame(root)
visual_frame.grid(row=0, column=0, columnspan=2, pady=10)

# Create the visual grid
create_visual_grid(visual_frame)

# Console box for displaying logs
console_frame = tk.Frame(root)
console_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=10)
console_box = tk.Text(console_frame, height=10, width=80, state="disabled", wrap="word", bg="lightgrey")
console_box.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(console_frame, command=console_box.yview)
scrollbar.pack(side="right", fill="y")
console_box.config(yscrollcommand=scrollbar.set)

# Bottom frame for input fields and button
input_frame = tk.Frame(root)
input_frame.grid(row=2, column=0, columnspan=2, pady=10)

# Input for the MIDI string
tk.Label(input_frame, text="Enter your input string:").grid(row=0, column=0, padx=5, sticky="e")
input_field = tk.Entry(input_frame, width=50)
input_field.grid(row=0, column=1, padx=5)

# Input for the file name
tk.Label(input_frame, text="Enter file name:").grid(row=1, column=0, padx=5, sticky="e")
file_name_field = tk.Entry(input_frame, width=50)
file_name_field.grid(row=1, column=1, padx=5)

# Submit button
submit_button = tk.Button(input_frame, text="Convert to MIDI", command=run_midi_conversion)
submit_button.grid(row=2, column=0, columnspan=2, pady=10)

# Run the Tkinter loop
root.mainloop()