import uvicorn
from server import app  # direct import since both files are at the same level
from dotenv import load_dotenv

load_dotenv()


def main():
    uvicorn.run(
        "server:app",  # points to module:variable
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
