
Starknet/Cairo implementation of Bura card game

 
Bura is a popular Soviet/Russian card game. Game is played with a 36-card deck. Cards rank in their natural order. For rules of the game see Wikipedia page below.
https://en.wikipedia.org/wiki/Bura_(card_game)


Clone the repo and run:

python3 app/game.py

System requirements: Windows 11 that has WSL2 with GUI support installed. Have not been tested but should run on Linux as well.

Package requrements:

Pygame. For installation run:

pip install pygame

Asyncio. For installation run:

pip install asyncio

Starknet/Cairo. Installation instructions are here

https://starknet.io/docs/quickstart.html#quickstart

pip3 install ecdsa fastecdsa sympy

pip3 install cairo-lang


![image](https://user-images.githubusercontent.com/20588945/184055201-218c09ce-02fd-4100-8e90-7dd2bb43bdda.png)


Cards can be selected by mouse click, and then played by pressing send button:
![image](https://user-images.githubusercontent.com/20588945/184055374-7f11735b-594c-44e2-9429-88502ca30abf.png)


Next round starts by pressing continue... button:
![image](https://user-images.githubusercontent.com/20588945/184055620-7fde2e05-af22-4d48-aa1f-cd50329073ec.png)




