"""Start the local paper-game test bench. No network service or API key required."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent/'src'))
from void_throne.server import main
if __name__=='__main__':main()
