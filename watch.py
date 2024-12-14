import sys
import time
import subprocess
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import Logger

class CodeReloader(FileSystemEventHandler):
    def __init__(self, logger: Logger):
        self.process = None
        self.logger = logger

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            self.logger.info(f"\n✨ Detected change in {event.src_path} ✨")
            self.logger.info("🔄 Reloading... 🔄")
            
            if self.process:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
                
            self.process = subprocess.Popen([sys.executable, 'main.py'])

def start_hot_reload():
    logger = Logger()

    path = "."
    event_handler = CodeReloader(logger)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    
    logger.info("🚀 Starting hot reload watcher... 🚀")
    logger.info("👀 Watching for file changes... 👀")
    
    observer.start()
    try:
        event_handler.process = subprocess.Popen([sys.executable, 'main.py'])
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if event_handler.process:
            parent = psutil.Process(event_handler.process.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        observer.stop()
        logger.info("\n🛑 Hot reload stopped 🛑")
    
    observer.join()

if __name__ == "__main__":
    start_hot_reload()
