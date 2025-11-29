import time 
import ollama
from dataclasses import dataclass
import re
import ipaddress
from urllib.parse import urlparse

@dataclass
class UserInput:
    raw_text: str
    goal_type: str
    target: str
    timestamp: float

class GoalIntake:
    def __init__(self, prompt_message="What is your Target and Goal?"):
        self.prompt_message = prompt_message
        self.client = ollama.Client(host="http://localhost:11434")
        self.goal_schema = [
            "network_scan",
            "data_retrieval",
            "verification",
            "analysis",
            "task_execution",
            "reporting",
            "other"
        ]
        self.DOMAIN_REGEX = re.compile(
                r"^(?:[a-zA-Z0-9]"       # First character of the domain
                r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"  # Sub domain + hostname
                r"[a-zA-Z]{2,}$"         # Top-level domain
            )

    def get_goal(self):
        # Prompt the user for their goal

        command = input(self.prompt_message).strip()
        goal_type = self.determine_goal_type(command)
        target = self.extract_target(command)
        timestamp = time.time()
        
        user_input = UserInput(
            raw_text=command,
            goal_type=goal_type,
            target=target,
            timestamp=timestamp
        )
        
        
        return user_input

    def determine_goal_type(self, command:str):
        # Uses an LLM to classify the command into goal types"
        system_prompt = (
            "You are an AI intent classifier for an autonomous cybersecurity agent. "
            "Classify the user command into one of the following categories:\n"
            f"{', '.join(self.goal_schema)}.\n"
            "Return ONLY the category name, with no extra words."
        )


        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ]
        
        response = self.client.chat(
            model="llama3.1",
            messages=messages,
            
        )
        label = response["message"]["content"].strip()

        if label in self.goal_schema:
            return label
        else:
            return "other"

    def extract_target(self, command: str):
        """
        Uses LLM to extract and validate target. If invalid, asks AI to re-prompt user.
        """
        system_prompt = (
            "You are an AI assistant for a cybersecurity agent. "
            "Extract the target (IP address, domain, or URL) from the user's command. "
            "If the extracted target is invalid, respond with instructions for the user to provide a valid target. "
            "Always return a valid target."
            "Just return the target without any extra text."
        )

        # Initial extraction attempt
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ]

        while True:
            response = self.client.chat(model="llama3.1", messages=messages)
            target = response["message"]["content"].strip()

            if self.validate_user_target(target):
                # Valid target found
                return target
            else:
                # Ask AI to generate a user prompt for a valid target
                prompt_request = (
                    "The previously extracted target was invalid. "
                    "Ask the user to provide a valid IP address, domain name, or URL. "
                    "Only return the new target provided by the user."
                )
                messages.append({"role": "system", "content": prompt_request})
                # Here we could simulate user input via AI or wait for real user input
                # For example:
                user_input = input("Agent ⟶ Enter a valid target: ").strip()
                messages.append({"role": "user", "content": user_input})


    def validate_user_target(self, target:str):
        # takes discovered targets and validates that they are in fact valid targets (domain, URL, IP)
        text = target.strip()
        import ipdb; ipdb.set_trace()
        # check for IP address
        try:
            ipaddress.ip_address(text)
            return True
        except ValueError:
            print("Not a valid IP address.")
        
        # Check for domain name
        if self.DOMAIN_REGEX.match(text):
            return True
        else:
            print("Not a valid domain name.")
        
        # Check for URL
        parsed_url = urlparse(text)
        if parsed_url.scheme and parsed_url.netloc:
            return True
        else:
            print("Not a valid URL.")   
        
        return False