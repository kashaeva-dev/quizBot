import os
import re
import pickle
import argparse

question_pattern = r"(Вопрос [\d]+:\s)(.*)"
answer_pattern = r"(Ответ:\s)(.*)"


def get_quiz_content(directory, target_filepath):
    quiz_content = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        print(f'Start file: {filename}')
        with open(filepath, encoding='KOI8-R') as quiz_file:
            quiz_contents = quiz_file.read()
        question_blocks = quiz_contents.split('\n\n\n')
        for question_block in question_blocks:
            question_parts = question_block.split('\n\n')
            for question_part in question_parts:
                if question_part.startswith('Вопрос'):
                    question_match = re.search(question_pattern, question_part, re.S)
                    if question_match:
                        question = question_match.group(2).replace('\n', ' ')
                elif question_part.startswith('Ответ'):
                    answer_match = re.search(answer_pattern, question_part, re.S)
                    if answer_match:
                        answer = answer_match.group(2).replace('\n', ' ')
                    question_answer = (question, answer)
                    quiz_content.append(question_answer)
        save_quiz_content(target_filepath, quiz_content)
        quiz_content = []
    return quiz_content


def save_quiz_content(filepath, data):
    with open(filepath, 'wb') as quiz_content_file:
        pickle.dump(data, quiz_content_file)


def load_quiz_content(filepath):
    with open(filepath, 'rb') as quiz_file:
        quiz_content = pickle.load(quiz_file)

    return quiz_content


def create_parser():
    parser = argparse.ArgumentParser(
        prog="Get quiz content",
    )
    parser.add_argument('--source_directory',
                        default='quiz-questions',
                        help='Path to directory with files which contain quiz questions',
                        )
    parser.add_argument('--target_directory',
                        default='.',
                        help='Path to save quiz content',
                        )
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    directory = args.source_directory
    target_directory = args.target_directory

    target_filepath = os.path.join(target_directory, 'quiz_content.txt')
    get_quiz_content(directory, target_filepath)
