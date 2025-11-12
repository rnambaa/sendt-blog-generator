from src.blog_generation import BlogGenerator
from src.chunking import PdfChunker
from typing import Dict, Any

class BlogService:
    """
    Orchestrates blog generation tasks across API endpoints.
    Keeps track of current tone, language, and other session parameters.
    """

    def __init__(self):
        self.pdf_chunker = PdfChunker()
        self.chunks = self.pdf_chunker.chunk(save_results=True) 

        self.blog_generator = BlogGenerator(chunks=self.chunks)

        self.tone = None

    def set_tone(self, tone: str) -> Dict[str, str]:
        """
        Set the tone for subsequent blog post generations (optional).
        
        Args:
            tone (str): Desired tone (e.g., 'professional', 'casual', 'technical')
        Returns:
            dict: Confirmation response containing the set tone
        """
        self.tone = tone
        return {"tone": self.tone}

    def generate_blog(self, purpose: str, language: str) -> Dict[str, str]:
        """
        Generates a blog post based on the provided purpose, applies any configured
        tone modifications, and translates to the specified language if requested.
        
        Args:
            purpose (str): The intended purpose or topic for the blog post
            language (str): Target language for translation (optional, defaults to English)
            
        Returns:
            dict: Generated blog post in markdown format
            
        Note:
            - Tone modification is only applied if tone was previously set via set_tone()
            - Translation is only applied if language parameter is provided
            - Generated content is based on pre-processed PDF chunks
        """

        blog_post = self.blog_generator.generate_blog(purpose=purpose)

        # Apply tone and translation if specified by user 
        if self.tone:
            blog_post = self.blog_generator.modify_tone(blog_post, self.tone)

        if language: 
            blog_post = self.blog_generator.translate(blog_post, language) # returns english by default

        return {"markdown": blog_post}
