from cx_Freeze import setup,Executable
setup(name="Block Game",
         version="1.0",
         description="Hit the black blocks, avoid the red",
         executables=[Executable("block_game.py")])