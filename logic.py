import math
import json
from mido import MidiFile, MidiTrack, Message

grammar = {
    'Start': ['Sequence'],
    'Sequence': [
        ['Pattern'],
        ['Pattern', 'Sequence'],
        ['Pattern', 'NewColumn', 'Sequence']
    ],
    'Pattern': [
        ['SingleNote'], ['DoubleNote'], ['TripleNote'], ['QuadNote'], ['QuintNote']
    ],

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
    'NewColumn': {
        '9p': 'newline',
    },
}


def tokenize(text):
    if len(text) % 2 != 0:
        raise ValueError("Error: Input must have an even number of characters.")
    tokens = [text[i:i + 2] for i in range(0, len(text), 2)]
    # Validation: Input cannot start with '9p'
    if tokens[0] == '9p':
        raise ValueError("Error: Input cannot start with 'NewColumn' (9p).")
    return tokens


def parse_Start(tokens):
    result = parse_Sequence(tokens, 0)
    if result is not None and result['index'] == len(tokens):
        return result
    else:
        raise ValueError("Error: Unable to parse the input text according to the grammar.")


def parse_Sequence(tokens, index):
    patterns = []
    while index < len(tokens):
        result_pattern = parse_Pattern(tokens, index)
        if result_pattern is not None:
            patterns.append(result_pattern['pattern'])
            index = result_pattern['index']
            # Check if next token is 'NewColumn'
            if index < len(tokens):
                result_newcolumn = parse_NewColumn(tokens, index)
                if result_newcolumn is not None:
                    patterns.append({'type': 'NewColumn'})
                    index = result_newcolumn['index']
        else:
            break
    if patterns:
        return {'type': 'Sequence', 'patterns': patterns, 'index': index}
    else:
        return None


def parse_Pattern(tokens, index):
    for parse_func in [parse_SingleNote, parse_DoubleNote, parse_TripleNote, parse_QuadNote, parse_QuintNote]:
        result = parse_func(tokens, index)
        if result is not None:
            return {'pattern': result['note'], 'index': result['index']}
    return None


def parse_SingleNote(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token in grammar['SingleNote']:
        note_pattern = grammar['SingleNote'][token]
        return {'note': {'type': 'SingleNote', 'token': token, 'pattern': note_pattern}, 'index': index + 1}
    else:
        return None


def parse_DoubleNote(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token in grammar['DoubleNote']:
        note_pattern = grammar['DoubleNote'][token]
        return {'note': {'type': 'DoubleNote', 'token': token, 'pattern': note_pattern}, 'index': index + 1}
    else:
        return None


def parse_TripleNote(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token in grammar['TripleNote']:
        note_pattern = grammar['TripleNote'][token]
        return {'note': {'type': 'TripleNote', 'token': token, 'pattern': note_pattern}, 'index': index + 1}
    else:
        return None


def parse_QuadNote(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token in grammar['QuadNote']:
        note_pattern = grammar['QuadNote'][token]
        return {'note': {'type': 'QuadNote', 'token': token, 'pattern': note_pattern}, 'index': index + 1}
    else:
        return None


def parse_QuintNote(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token in grammar['QuintNote']:
        note_pattern = grammar['QuintNote'][token]
        return {'note': {'type': 'QuintNote', 'token': token, 'pattern': note_pattern}, 'index': index + 1}
    else:
        return None


def parse_NewColumn(tokens, index):
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token == '9p':
        return {'type': 'NewColumn', 'index': index + 1}
    else:
        return None


def process_parse_tree(parse_tree, track, logger=None):
    patterns = parse_tree['patterns']
    current_section = []
    all_sections = []
    total_skips = 0

    for p in patterns:
        if p['type'] == 'NewColumn':
            if current_section:
                all_sections.append(current_section)
                current_section = []
        else:
            current_section.append(p['pattern'])

    if current_section:
        all_sections.append(current_section)

    # Process each section
    for section in all_sections:
        if logger:
            logger(f"Section: {section}")
        flipped_section = [list(row) for row in zip(*section)]
        if logger:
            logger(f"Flipped Section: {flipped_section}")

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


def text_to_midi2(text, output_file="result_FIX.mid", logger=None):
    try:
        tokens = tokenize(text)
        parse_tree = parse_Start(tokens)

        # Print the parse tree and save to a file
        parse_tree_str = json.dumps(parse_tree, indent=2)
        print(parse_tree_str)
        with open('parse_tree.txt', 'w') as f:
            f.write(parse_tree_str)

        # MIDI File Setup
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        # Process the parse tree to generate MIDI
        process_parse_tree(parse_tree, track, logger)
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


# Example usage:
# text_to_midi2('1c2c3c4c')
