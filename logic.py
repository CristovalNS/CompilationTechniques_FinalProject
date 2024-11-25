import math
from mido import MidiFile, MidiTrack, Message

grammar = {
    'Start': ['Sequence'],  # Start
    'Sequence': [
        'Pattern',  # A single pattern
        'Pattern', 'Sequence',  # Pattern followed by another Sequence
        'Pattern', 'NewLine', 'Sequence',  # Pattern followed by NewLine and more Sequence
    ],
    'Pattern': ['SingleNote', 'DoubleNote', 'TripleNote', 'QuadNote', 'QuintNote'],  # Valid Patterns

    'SingleNote': {
        '0a': [0, 0, 0, 0, 0],
        '0b': [1, 0, 0, 0, 0],
        '1b': [0, 1, 0, 0, 0],
        '2b': [0, 0, 1, 0, 0],
        '3b': [0, 0, 0, 1, 0],
        '4b': [0, 0, 0, 0, 1],
    },
    'DoubleNote': {
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
    },
    'TripleNote': {
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
    },
    'QuadNote': {
        '0e': [1, 1, 1, 1, 0],
        '1e': [1, 1, 1, 0, 1],
        '2e': [1, 1, 0, 1, 1],
        '3e': [1, 0, 1, 1, 1],
        '4e': [0, 1, 1, 1, 1],
    },
    'QuintNote': {
        '0f': [1, 1, 1, 1, 1],
    },
    'NewLine': {
        '9p': 'newline',  # Represents a new line
    },
}


def find_token(token):
    for category, tokens in grammar.items():
        if isinstance(tokens, dict) and token in tokens:
            return tokens[token]
    return None

def text_to_midi2(text, output_file="result_FIX.mid", logger=None):
    try:
        def is_pattern(token):
            # Check if a token is a valid Pattern
            return find_token(token) is not None

        # Initialize variables
        i = 0
        current_section = []
        all_sections = []  # To store all separate sections
        total_skips = 0
        all_tokens = []

        # Validation: Input must have an even number of characters
        if len(text) % 2 != 0:
            raise ValueError("Error: Input must have an even number of characters.")

        # Parse tokens
        while i < len(text):
            token = text[i:i + 2]
            if is_pattern(token) or token in ['9p']:
                all_tokens.append(token)
                if logger:
                    logger(f"Valid token: {token}")
            else:
                # Stop further execution by raising an error immediately
                raise ValueError(f"Error: Invalid token '{token}'.")
            i += 2

        # Validation: Input cannot start with '9p'
        if all_tokens[0] == '9p':
            raise ValueError("Error: Input cannot start with 'NewLine' (9p).")

        # MIDI File Setup
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # Process tokens
        last_token_was_pattern = False  # Track if the last token was a valid Pattern
        for token in all_tokens:
            if token == '9p':  # Handle NewLine
                if not last_token_was_pattern:
                    raise ValueError("Error: 'NewLine' (9p) must follow a valid 'Pattern'.")
                if current_section:
                    all_sections.append(current_section)  # Save the current section
                    current_section = []  # Start a new section
                last_token_was_pattern = False
            else:  # Handle Patterns
                pattern = find_token(token)
                if pattern is not None:
                    current_section.append(pattern)
                    last_token_was_pattern = True

        # Debug output for the correct sections
        for section in all_sections:
            if logger:
                logger(f"Section: {section}")
            flipped_section = [list(row) for row in zip(*section)]
            if logger:
                logger(f"Flipped Section: {flipped_section}")

            # Generate MIDI notes from flipped_section
            starting_pitch = math.ceil(60 + len(section) / 2)
            for column in flipped_section:
                current_pitch = starting_pitch
                switch1, switch2 = True, True
                empty_switch = True
                for note in column:
                    if note == 1:
                        empty_switch = False
                        if switch1:
                            track.append(Message('note_on', note=current_pitch, velocity=64, time=(total_skips * 100)))
                            total_skips = 0
                            switch1 = False
                        else:
                            track.append(Message('note_on', note=current_pitch, velocity=64, time=0))
                    current_pitch -= 1

                current_pitch = starting_pitch
                for note in column:
                    if note == 1:
                        if switch2:
                            track.append(Message('note_off', note=current_pitch, velocity=64, time=100))
                            switch2 = False
                        else:
                            track.append(Message('note_off', note=current_pitch, velocity=64, time=0))
                    current_pitch -= 1

                if empty_switch:
                    total_skips += 1

        # Save the MIDI file with the specified name
        mid.save(output_file)
        if logger:
            logger(f"MIDI file generated successfully as '{output_file}'.")

    except ValueError as ve:
        if logger:
            logger(str(ve), is_error=True)
        else:
            print(f"\033[91m{ve}\033[0m")  # Print error in red text
    except Exception as e:
        if logger:
            logger(f"An unexpected error occurred: {e}", is_error=True)
        else:
            print(f"\033[91mAn unexpected error occurred: {e}\033[0m")  # Print unexpected errors in red text




# text_to_midi2('0a9c9d4e4e0f0f0f0f0f0e6d6d9d9c0a9p0f0f0f5d5d0f0f0f0e0a0a9c9c0a0c0f9p0b0d0e2d2d0c0b0a0a0a0a4b9c7c4c0b9p0a0a0a0a0a0b0b0b0b0b0b0a0a0a0a0a')
# text_to_midi2('4e1b8d5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c6c5c8c5c6c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c8d1b4e9p0f0a0f0a0f0b3e1c4d4d4d4d4d4d4d4d4d0a0f0b3e1c4d4d4d4d4d4d1c3e0b0e4b2c4d5c4d5c4d5c4d5c4d5c4d2c4b0e0b3e1c4d4d4d4d4d4d1c3e0b0f0a4d4d4d4d4d4d4d4d4d1c3e0b0f0a0f0a0f9p0f0a0f0a0f0a0f0a0f0a4e1b8d5c5c5c5c0a0f0a0f0a0e3b5c5c3b1e3b1e3b1e8c3e8d4d5c4d5c4d5c4d5c4d8d3e8c1e3b1e3b1e3b5c5c3b0e0a0f0a0f0a5c5c5c5c8d1b4e0a0f0a0f0a0f0a0f0a0f9p0f0a0f0a1e4b1e4b1e4b1e4b1e4b1e3c4d0a1e8c4d4d4d4d1c3e0f6c4d7d1e1e1e1e1e1e1e7d4d6c4d7d1e1e1e1e1e1e1e7d4d6c0f3e1c4d4d4d4d8c1e0a4d3c1e4b1e4b1e4b1e4b1e4b1e0a0f0a0f9p0f0a0f0a0f0a4e1b8d5c5c5c8d1b4e0a0f0a0f0f0e2d3e4e0e0f0f0d0c0c0b1c1b2b1b2b1b2b1b2b1b2b1b2b1b2b1b1c0b0c0c0d0f0f0e4e3e2d0e0f0f0a0f0a4e1b8d5c5c5c8d1b4e0a0f0a0f0a0f9p0f0a0f0a0f0a0f0a0f4b1e4b0e9c0e9d0e7c3e4e0f0e3d7c7c0f0f7c2b1d3d3d3d3d3d3d3d3d3d3e3d3d3d3d3d3d3d3d3d3d1d2b0e0f7c7c3d0e0f4e3e7c0e9d0e9c0e4b1e4b0f0a0f0a0f0a0f0a0f9p0f0a0f0a0e3b1d5c6c5c5c5c4d8d3e4e0f0a0f0c3b0a0a4e1b3e4e0a0a0a9d4c1b1b1b1b1b1b0b0a0b1b1b1b1b1b1b4c9d0a0a0a0f4e0b0f0a0a3b0c0f0a0f4e3e8d4d5c5c5c6c5c1d3b0e0a0f0a0f9p0f0a0e4b1d8c5c4d5c4d5c4d1d1e0e0f0f0a0f0a4d0a0a0f0a0f0f0a0a4b0e0a0a0f4d0f1c0d2d5d2d0d1c0f4d0f0a0a0e4b0a0a0f0f0a0f0a0a4d0a0f0a0f0f0e1e1d4d5c4d5c4d5c8c1d4b0e0a0f9p3e1b4d5c4d5c4d5c4d5c4d5c4d5c4d8d3e0a0f0a5c0a0a0f0a0f0f1b1c3b4b0a0a0f3d9c1b0d0e0f0e0d1b9c3d0f0a0a4b3b1c1b0f0f0a0f0a0a5c0a0f0a3e8d4d5c4d5c4d5c4d5c4d5c4d5c4d1b3e9p0f0a0f0a7d3c6c4d5c4d6c4d6d0f0f0f0f0a0f0a4d0a0a0f0a0f0f0a0a0a0f0a0a0d1c0d1c0d4c2b4c0d1c0d1c0d0a0a0f0a0a0a0f0f0a0f0a0a4d0a0f0a0f0f0f0f6d4d6c4d5c4d6c3c7d0a0f0a0f9p0f0a0f0a0f0a4e1b8d5c5c5c4d8d4d2e1e4b0f4e9c4b4b1e8c2e1e0a4b4b3c2d6c6c6c6c6c6c8c9c8c6c6c6c6c6c6c2d3c4b4b0a1e2e8c1e4b4b9c4e0f4b1e2e4d8d4d5c5c5c8d1b4e0a0f0a0f0a0f9p0f0a0f0a0f0a0f0a0f4b1e4b0f0a0f0b0f0b3e2e1e0e3e5d3c0f0f0b4c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c4c0b0f0f3c5d3e0e1e2e3e0b0f0b0f0a0f4b1e4b0f0a0f0a0f0a0f0a0f9p0f0a0f0a0e3b1d5c5c5c5c5c5c5c1d3b0e0a0e0e0e6d3d1d0d0f0f0e6d6d7c3d5c2c5c2c5c2c5c2c5c2c5c2c5c2c5c3d7c6d6d0e0f0f0d1d3d6d0e0e0e0a0e3b1d5c5c5c5c5c5c5c1d3b0e0a0f0a0f9p0f0a0f0a0f0a0f0a0f0a0f0a0f4b1e8c4d0a0f0b3e1c4d4d4d4d1e5c4d1d1e0e0f0f0f0e1e1d4d5c4d1d1e0e0f0f0f0e1e1d4d5c1e4d4d4d4d1c3e0b0f0a4d8c1e4b0f0a0f0a0f0a0f0a0f0a0f0a0f9p0f0a0f0a0f0a0f0a0e3b1d5c5c5c5c5c5c0a0f0a0f0a0e3b5c5c3b0e0a0f0a1e3b4d5c4d5c4d5c4d5c4d5c4d5c4d3b1e0a0f0a0e3b5c5c3b0e0a0f0a0f0a5c5c5c5c5c5c1d3b0e0a0f0a0f0a0f0a0f9p0f0a0f4b1e8c4d4d4d4d4d4d4d4d4d4d4d4b1e8c4d4d4d4d4d4d4d4d4d4d8c1e4b8c4d6c4d5c4d5c4d5c4d6c4d8c4b1e8c4d4d4d4d4d4d4d4d4d4d8c1e4b4d4d4d4d4d4d4d4d4d4d4d8c1e4b0f0a0f9p0c1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b0b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b1b0c')