import asyncio
from utils.logo import generate_logo


print(asyncio.run(generate_logo("Shreyash\n Dheemar", bg="unsplash", square=True)))
