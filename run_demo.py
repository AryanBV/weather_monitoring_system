import time
import subprocess
from src.utils.logger import logger

def run_demo(duration_minutes=5):
    logger.info(f"Starting Weather Monitoring System demo for {duration_minutes} minutes")
    
    try:
        # Start the main application
        process = subprocess.Popen(["python", "main.py"], stderr=subprocess.PIPE)
        
        # Run for the specified duration
        time.sleep(duration_minutes * 60)
        
        # Terminate the process
        process.terminate()
        process.wait(timeout=10)  # Wait for up to 10 seconds for the process to terminate
        
        # Check if there were any errors
        _, stderr = process.communicate()
        if stderr:
            logger.error(f"Errors occurred during demo run: {stderr.decode()}")
        else:
            logger.info("Demo completed successfully. Check logs and visualizations for results.")
    
    except subprocess.TimeoutExpired:
        logger.error("Demo process did not terminate in time. Forcing termination.")
        process.kill()
    except Exception as e:
        logger.error(f"An error occurred during the demo: {str(e)}")
    finally:
        if process.poll() is None:
            process.kill()  # Ensure the process is terminated

if __name__ == "__main__":
    run_demo()