from app import create_app
from dotenv import load_dotenv
import uvicorn
import os

# Load environment variables from .env file
load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    host = os.getenv('HOST', '127.0.0.1')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    uvicorn.run(
        "run:app",
        host=host,
        port=port,
        reload=debug
    )

