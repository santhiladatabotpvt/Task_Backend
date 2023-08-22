from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict
from cachetools import TTLCache
import random
import string

app = FastAPI()
security = HTTPBearer()
cache = TTLCache(maxsize=100, ttl=300)  # Cache to store posts for 5 minutes

# Pydantic schema for signup request
class SignupRequest(BaseModel):
    email: str
    password: str

# Pydantic schema for login request
class LoginRequest(BaseModel):
    email: str
    password: str

# Pydantic schema for post request
class PostRequest(BaseModel):
    text: str

# Pydantic schema for post response
class PostResponse(BaseModel):
    postID: str

# Pydantic schema for get posts response
class GetPostsResponse(BaseModel):
    posts: Dict[str, str]  # Dictionary to store postID and text

# Pydantic schema for token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

def generate_token():
    # Generate a random string token of length 32
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return token

def authenticate_token(token: HTTPAuthorizationCredentials = Depends(security)):
    # Check if token is valid and present in cache
    if token.credentials not in cache:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token.credentials

@app.post("/signup", response_model=TokenResponse)
def signup(user: SignupRequest):
    # Here, you would typically save the user to a database
    # For simplicity, we'll just return a randomly generated token
    token = generate_token()
    cache[user.email] = token  # Store the token in the cache with the email as the key
    return TokenResponse(access_token=token, token_type="bearer")

@app.post("/login", response_model=TokenResponse)
def login(user: LoginRequest):
    # Here, you would typically validate the user's credentials against a database
    # For simplicity, we'll assume the login is successful
    token = generate_token()
    cache[user.email] = token  # Store the token in the cache with the email as the key
    return TokenResponse(access_token=token, token_type="bearer")

@app.post("/addPost", response_model=PostResponse)
def add_post(post: PostRequest, token: str = Depends(authenticate_token)):
    # Check if payload size exceeds 1MB
    if len(post.text.encode()) > 1048576:
        raise HTTPException(status_code=400, detail="Payload size exceeds 1MB")
    
    # Here, you would typically save the post to a database
    # For simplicity, we'll just generate a random postID and store it in the cache
    post_id = generate_token()
    cache[post_id] = post.text
    
    return PostResponse(postID=post_id)

@app.get("/getPosts", response_model=GetPostsResponse)
def get_posts(token: str = Depends(authenticate_token)):
    # Here, you would typically retrieve the user's posts from a database
    # For simplicity, we'll retrieve the posts from the cache
    user_posts = {post_id: text for post_id, text in cache.items() if text != token}
    
    return GetPostsResponse(posts=user_posts)

@app.delete("/deletePost/{post_id}")
def delete_post(post_id: str, token: str = Depends(authenticate_token)):
    # Here, you would typically delete the post from a database
    # For simplicity, we'll delete the post from the cache
    if post_id in cache and cache[post_id] != token:
        del cache[post_id]
    else:
        raise HTTPException(status_code=404, detail="Post not found")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
