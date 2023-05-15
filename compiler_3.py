import os
import time
import openai

def parse_ai_file(ai_file):
    with open(ai_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_context(py_file):
    if os.path.isfile(py_file):
        with open(py_file, 'r') as f:
            return f.read()
    return ''

def summarize_commands(lines, context):
    max_tokens = 4050
    while max_tokens > 300:
        try:
            command_str = ' '.join(lines)

            # Check if command_str is too long
            if len(command_str.split()) > max_tokens:
                command_str = ' '.join(command_str.split()[:max_tokens]) + '...'

            # Determine how many tokens are left for the context
            remaining_tokens = max_tokens - len(command_str.split()) - 200
            print('remaining tokens', remaining_tokens)
            context = ' '.join(context.split()[:remaining_tokens]) + '...' if len(context.split()) > remaining_tokens else context
            prompt = f"""summarize this file: how to activate the commands and what the command does.
            This is a talon voice file. Be Detailed.
            file: {command_str}
            context: {context}
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']

        except Exception:
            print("Error processing", lines, context)
            max_tokens -= 300
            print(f"Reducing max tokens to {max_tokens} and trying again.")

    print("Could not process request after several attempts.")



def write_summary(file_path, summary, lines):
    new_file_path = file_path.replace('.ai', '.ai2')
    with open(new_file_path, 'w') as f:
        f.write(f'"""\n {summary}\n"""')
        f.write(''.join(lines))

def process_files(dir_path, ):
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.ai'):
            file_path = os.path.join(dir_path, file_name)
            lines = parse_ai_file(file_path)
            context = read_context(file_path.replace('.ai', '.py'))
            summary = summarize_commands(lines, context, )
            print('flown_path: ', file_path, summary)
            write_summary(file_path, summary, lines)
            # time.sleep(20)
        elif os.path.isdir(os.path.join(dir_path, file_name)):
            process_files(os.path.join(dir_path, file_name), )
process_files('.')
