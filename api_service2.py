import requests
from typing import Dict, Any


class MCQGeneratorAPI2:
    def __init__(self):
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://app.kangaroos.ai',
            'priority': 'u=1, i',
            'referer': 'https://app.kangaroos.ai/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

    def generate_questions(self, topic: str, num_questions: int) -> Dict[int, Dict[str, Any]]:
        """
        Get quiz questions from the API.
        
        Args:
            topic: The topic for the quiz
            num_questions: Number of questions to generate
            
        Returns:
            Dict[int, Dict[str, Any]]: Dictionary containing quiz questions and answers
            
        Raises:
            APIError: If there's an error with the API request
        """
        try:
            json_data = {
                'topic': topic,
                'education_level': '18+',
                'number_of_questions':num_questions,
            }

            response = requests.post('https://kangroos-ai-dqhgks3gba-uc.a.run.app/mcq', headers=self.headers, json=json_data)
            return True, self._parse_quiz_text(response.json()['output']['text'])

        except requests.RequestException as e:
            ...

    def _parse_quiz_text(self, quiz_text: str) -> Dict[int, Dict[str, Any]]:
        """
        Parse the markdown quiz text into a structured format.
        
        Args:
            quiz_text: Raw quiz text from the API
            
        Returns:
            Dict[int, Dict[str, Any]]: Parsed quiz data
        """
        import re
        
        # Remove any unnecessary parts (like title or any unwanted text)
        quiz_text = re.sub(r'#.*\n', '', quiz_text)  # Remove quiz title
        quiz_data = {}

        # Split the input into questions and options
        questions = re.findall(r'\*\*(\d+)\. (.*?)\*\*\s*(.*?)(?=\*\*|$)', quiz_text, re.DOTALL)

        for question in questions:
            question_number = question[0]
            question_text = question[1].strip()
            options_text = question[2].strip().splitlines()

            options = {}
            for option in options_text:
                match = re.match(r'([a-d])\)\s*(.*)', option.strip())  # Changed to use ')' instead of '.' 
                if match:
                    options[match.group(1)] = match.group(2).strip()

            quiz_data[int(question_number)] = {
                "text": question_text,
                "options": options,
                "answer": ""  # Placeholder for the answer
            }

        # Extract the answer key section
        answer_key_section = re.search(r'Answers?:\s*(.*)', quiz_text, re.DOTALL)
        if answer_key_section:
            answer_key_text = answer_key_section.group(1).strip()
            answer_key_lines = answer_key_text.splitlines()

            for line in answer_key_lines:
                match = re.match(r'(\d+)\.\s*([a-d])', line.strip())
                if match:
                    question_number = int(match.group(1))
                    answer = match.group(2)
                    if question_number in quiz_data:
                        quiz_data[question_number]["answer"] = answer
        
        return quiz_data 