# Imports
import math
from mido import MidiFile, MidiTrack, Message

# Grammar
grammar = {
    '0a': [0, 0, 0, 0, 0],
    '0b': [1, 0, 0, 0, 0],
    '1b': [0, 1, 0, 0, 0],
    '2b': [0, 0, 1, 0, 0],
    '3b': [0, 0, 0, 1, 0],
    '4b': [0, 0, 0, 0, 1],
    '0c': [1, 1, 0, 0, 0],
    '1c': [1, 0, 1, 0, 0],
    '2c': [1, 0, 0, 1, 0],
    '3c': [1, 0, 0, 0, 1],
    '4c': [0, 1, 1, 0, 0],
    '5c': [0, 1, 0, 1, 0],
    '6c': [0, 1, 0, 0, 1],
    '7c': [0, 0, 1, 1, 0],
    '8c': [0, 0, 1, 0, 1],
    '9c': [0, 0, 0, 1, 1],
    '0d': [1, 1, 1, 0, 0],
    '1d': [1, 1, 0, 1, 0],
    '2d': [1, 1, 0, 0, 1],
    '3d': [1, 0, 1, 1, 0],
    '4d': [1, 0, 1, 0, 1],
    '5d': [1, 0, 0, 1, 1],
    '6d': [0, 1, 1, 1, 0],
    '7d': [0, 1, 1, 0, 1],
    '8d': [0, 1, 0, 1, 1],
    '9d': [0, 0, 1, 1, 1],
    '0e': [1, 1, 1, 1, 0],
    '1e': [1, 1, 1, 0, 1],
    '2e': [1, 1, 0, 1, 1],
    '3e': [1, 0, 1, 1, 1],
    '4e': [0, 1, 1, 1, 1],
    '0f': [1, 1, 1, 1, 1],
    '0o': 'end',
}


# Main function
def text_to_midi2(text):
    # Index
    i = 0
    # Array to store all rows in the current 5 columns
    current_section = []
    # Counter to store the number of empty columns
    total_skips = 0
    # Array for all tokens
    all_tokens = []

    # If the number of character isn't even, there's no way it's correct
    if len(text) % 2 != 0:
        print("Input must have an even number of characters")
        return

    # Separate the input into tokens
    while i < len(text):
        # Current token
        token = text[i:i+2]
        # If token is valid
        if token in grammar or token == '0o':
            # Append it to the array
            all_tokens.append(token)
            print("Valid:", token)
        else:
            # Else, terminate
            print("invalid token:", token)
            return
        # Increment i by 2
        i += 2

    # Create a new MIDI file and track
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Loop through each token
    for token in all_tokens:
        # Get the token
        pattern = grammar.get(token)
        # Part below is for drawing a finished section to the midi
        if pattern == 'end':
            # To center the drawing, start at 60 (C4) and go up half the height of the section
            starting_pitch = math.ceil(60 + len(current_section) / 2)
            # Flip the arrays from x arrays of length y to y arrays of length x (rows to columns)
            flipped_section = [list(row) for row in zip(*current_section)]
            # Debugging
            print(current_section)
            print(flipped_section)
            # For each column in the flipped array
            for column in flipped_section:
                # Start at the top of the drawing
                current_pitch = starting_pitch
                # Switch 1 is for the first note on
                switch1 = True
                # Switch 2 is for the first note off
                switch2 = True
                # Switch to detect a completely empty column
                empty_switch = True
                # For each note in the column
                for note in column:
                    # If note is 1
                    if note == 1:
                        # The column is definitely not empty
                        if empty_switch:
                            empty_switch = False
                        # If first note on
                        if switch1:
                            # Draw the note 100 * total_skips from the last note
                            track.append(Message('note_on', note=current_pitch, velocity=64, time=(total_skips * 100)))
                            # Reset total_skips
                            total_skips = 0
                            # Make switch 1 false
                            switch1 = False
                        # Otherwise, append it with time 0
                        else:
                            track.append(Message('note_on', note=current_pitch, velocity=64, time=0))
                    # Go down one pitch to the next note
                    current_pitch -= 1
                current_pitch = starting_pitch
                # Pretty much the same thing, except for stopping the notes
                # Main difference is that the first note turned off is time = 100
                for note in column:
                    if note == 1:
                        if switch2:
                            track.append(Message('note_off', note=current_pitch, velocity=64, time=100))
                            switch2 = False
                        else:
                            track.append(Message('note_off', note=current_pitch, velocity=64, time=0))

                    current_pitch -= 1
                # If the entire column was empty, increment total_skips
                if empty_switch:
                    total_skips += 1
            # Reset current_section
            current_section = []
        else:
            # append pattern to current section
            current_section.append(pattern)

    # Save the generated MIDI file
    mid.save('result.mid')


text_to_midi2('0a9c9d4e4e0f0f0f0f0f0e6d6d9d9c0a0o0f0f0f5d5d0f0f0f0e0a0a9c9c0a0c0f0o0b0d0e2d2d0c0b0a0a0a0a4b9c7c4c0b0o0a0a0a0a0a0b0b0b0b0b0b0a0a0a0a0a0o')