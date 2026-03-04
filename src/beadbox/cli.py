import subprocess
import json
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class BeadboxCLI:
    """Wrapper for the Beadbox ('bd') command line interface."""
    
    @staticmethod
    def is_available() -> bool:
        """Check if the 'bd' CLI is available on the system."""
        try:
            result = subprocess.run(
                ["bd", "--version"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Beadbox CLI availability check failed: {e}")
            return False

    @staticmethod
    def list_beads() -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Run 'bd ls --json' and return the parsed result.
        Returns a tuple: (success_boolean, list_of_beads).
        """
        try:
            result = subprocess.run(
                ["bd", "ls", "--json"], 
                capture_output=True, 
                text=True, 
                shell=True
            )
            if result.returncode == 0:
                # Some basic cleanup in case the CLI prints something else before JSON
                output = result.stdout.strip()
                try:
                    beads = json.loads(output)
                    if isinstance(beads, list):
                        return True, beads
                    else:
                        logger.error("Beadbox CLI JSON output is not a list")
                        return False, []
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Beadbox CLI JSON output: {e}")
                    return False, []
            else:
                logger.error(f"Beadbox CLI error (ls): {result.stderr}")
                return False, []
        except Exception as e:
            logger.error(f"Exception calling Beadbox CLI: {str(e)}")
            return False, []
