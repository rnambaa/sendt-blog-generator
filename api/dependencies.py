from api.services.blog_service import BlogService

# singleton instance shared across routers for stateless memory 
blog_service = BlogService()
