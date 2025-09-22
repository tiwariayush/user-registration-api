from typing import Dict


class HealthController:
    
    @staticmethod
    def check_health() -> Dict[str, str]:
        return {"status": "healthy"}
    
