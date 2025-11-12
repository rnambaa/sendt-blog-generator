# TODO: figure out later 
import os 
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json 
import requests 
from ollama import generate, chat
import re 
from typing import Dict, Any 
from src.config.paths import DATA_DIR


class OllamaModel(): 
    """
    A wrapper class for Ollama language models that provides generation and chat functionality.
    Attributes:
        model_name (str): The name/identifier of the Ollama model to use
        model_parameters (Dict[str, Any]): Configuration parameters for the model
    """
    def __init__(self, model_name: str, model_parameters: Dict[str, Any]):
        # generation model 
        self.model_name = model_name
        self.model_parameters = model_parameters


    def generate(self, prompt: str) -> str: 
        """
        Generate text using the Ollama model's generation functionality.
        Args:
            prompt (str): The user's input prompt
        """
        try: 
            response = generate(
                model=self.model_name, 
                prompt=prompt,
                options=self.model_parameters, 
            )
            return response.response
        
        except: 
            raise RuntimeError("Could not connect to Ollama server, check that it is listening on 127.0.0.1:11434")
    
    def chat(self, prompt: str, system_prompt: str, example: tuple) -> str: 
        """
        Generate text using the Ollama model's chat functionality with context.
        Args:
            prompt (str): The user's input prompt
            system_prompt (str): Context and instructions for the model's behavior
            example (tuple): A (query, response) tuple providing an example interaction            
        """
        try: 
            response = chat(
                model=self.model_name, 
                messages=[
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': example[0]},
                        {'role': 'assistant', 'content': example[1]},
                        {'role': 'user', 'content': prompt},
                ],
                options=self.model_parameters, 
            )
            return response.message.content
        except: 
            raise RuntimeError("Could not connect to Ollama server, check that server it is listening on 127.0.0.1:11434")



class BlogGenerator(): 
    """
    A blog generation system using Ollama language models.
    
    This class provides 3 core methods which are: blog_generation, tone modification, translation.
    It uses company context & post example(s) in markdown format to
    maintain consistent brand voice and messaging across generated content.
        
    Attributes:
        chunks (Dict[str, dict]): Company context and example data loaded from JSON
        gen_model (OllamaModel): Primary model for blog generation and tone modification
        translation_model (OllamaModel): Specialized model for language translation
    """
    def __init__(self, chunks: Dict[str, dict] = None):
        # load & store context chunks 
        self.chunks = chunks if chunks else self._load_chunks(filename="chunks.json")

        # -- generation model & params -- 
        self.gen_model = OllamaModel(
            model_name="mistral:latest",
            model_parameters= {             # https://ollama.readthedocs.io/en/modelfile/#parameter
                "seed": 42, 
                "temperature": 0.8,
                "num_predict": 700, 
            }
        )
        # -- translation model & params -- 
        self.translation_model = OllamaModel(
            model_name="zongwei/gemma3-translator:4b",
            model_parameters= {             # https://ollama.readthedocs.io/en/modelfile/#parameter
                "seed": 42, 
                "temperature": 0.8,
                "num_predict": 900, 
            }
        )

    def _load_chunks(self, filename: str) -> Dict[str, dict]: 
        """
        Loads company context and example data from a JSON file.
        Args:
            filename (str): Name of the JSON file in the DATA_DIR containing chunks
        """
        filepath = DATA_DIR / filename
        with open(filepath, 'r') as file: 
            data = json.load(file)
        return data 
        
    def generate_blog(self, purpose: str, retries=3) -> str: 
        """
        Generate a new blog post based on company context and specified topic.
        
        Creates a 300-400 word blog post in markdown format using company information
        as context and example blog posts as style guides. Includes validation to
        ensure clean markdown output.
        
        Args:
            purpose (str): The topic or purpose for the blog post
        Returns:
            str: Generated blog post in markdown format
        """
        # structure company information as context for system prompt 
        company_context = [chunk['text'] for chunk in self.chunks.values() if chunk['type'] == 'description']
        company_context = "\n\n".join(company_context)
        
        system_prompt = f"""
        You are an expert at writing blog posts (300-400 words) in markdown format only. 
        You write engaging, informative blog posts that are informed by the company’s mission, tone, and target audience, which is described in the documents below:  

        {company_context}        
        """

        # structure example(s) as context for user prompt & assistant response  
        query_example = "Describe why a home battery is a good choice for energy."
        blog_example = [chunk['text'] for chunk in self.chunks.values() if chunk['type'] == 'example']
        blog_example = "\n\n".join(blog_example)

        # final user prompt 
        prompt = f"""
        Now write a new blog post for this company in english. The topic of this blog post is: {purpose}
        Output only the final blog post in Markdown format, return ONLY markdown. Keep the blog post to 300-400 words. 
        """
        # heuristic markdown output validation 
        for _ in range(retries): 
            blog_post = self.gen_model.chat(prompt, system_prompt, (query_example, blog_example))
            blog_post = blog_post.strip()
            # check for pure markdown
            if blog_post.startswith("#"): 
                return blog_post 
            # Regex to match ```markdown ... ```
            match = re.match(r"^```markdown\s*(.*?)\s*```$", blog_post, re.DOTALL)
            if match:
                return match.group(1).strip() # return only the inner markdown
            # retry inference 
            print(f"Attempt {_+1} did not return clean markdown. Retrying...")

        # retries are exhausted 
        raise ValueError("LLM output could not be parsed as markdown after retries.")
    

    def modify_tone(self, blog_post: str, tone: str = None, retries=3) -> str: 
        """
        Modify the tone and style of an existing blog post while preserving content.
                
        Args:
            blog_post (str): Original blog post in markdown format
            tone (str, optional): Desired tone for the blog post
        Returns:
            str: Blog post with modified tone in markdown format
        """

        prompt = f"""
        You are an editor improving tone and style. Change the following markdown blog post: 
        Markdown post: 

        {blog_post}
        
        Return ONLY the markdown in the same structure, keep the same content of the blog the exact same, but change the tone to the following: {tone}. 
        """
        # heuristic markdown output validation
        blog_post = blog_post.strip()
        for _ in range(retries): 
            blog_post = self.gen_model.generate(prompt)
            blog_post = blog_post.strip()
            # check for pure markdown
            if blog_post.startswith("#"): 
                return blog_post 
            # Regex to match ```markdown ... ```
            match = re.match(r"^```markdown\s*(.*?)\s*```$", blog_post, re.DOTALL)
            if match:
                return match.group(1).strip() # return only the inner markdown
            # retry inference 
            print(f"Attempt {_+1} did not return clean markdown. Retrying...")

        # retries are exhausted 
        raise ValueError("LLM output could not be parsed as markdown after retries.")


    def translate(self, blog_post: str, language: str, retries=3) -> str: 
        """
        Translate a blog post from english to the specified language while maintaining structure.
        
        Args:
            blog_post (str): Original blog post in markdown format (assumed to be in English)
            language (str): Target language for translation
        Returns:
            str: translated blog post in markdown format, or original if target is English

        """
        # check if desired post is in english 
        if not language.strip().lower() == "english": 
            prompt = f"""
            You are expert translation model from english to {language}.
            Translate the following markown post into {language}, keep the structure the same, return ONLY markdown: 

            {blog_post}
            """
            # heuristic markdown output validation 
            for _ in range(retries): 
                blog_post = self.translation_model.generate(prompt)
                blog_post = blog_post.strip()
                # check for pure markdown
                if blog_post.startswith("#"): 
                    return blog_post 
                # Regex to match ```markdown ... ```
                match = re.match(r"^```markdown\s*(.*?)\s*```$", blog_post, re.DOTALL)
                if match:
                    return match.group(1).strip() # return only the inner markdown
                # retry inference 
                print(f"Attempt {_+1} did not return clean markdown. Retrying...")

            # retries are exhausted 
            raise ValueError("LLM output could not be parsed as markdown after retries.")

        else: 
            return blog_post

