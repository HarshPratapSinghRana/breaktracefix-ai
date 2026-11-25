# Auto-import all attack scenarios to trigger registry registration
import backend.app.services.attack_engine.scenarios.prompt_attacks
import backend.app.services.attack_engine.scenarios.disclosure_attacks
import backend.app.services.attack_engine.scenarios.agency_attacks
import backend.app.services.attack_engine.scenarios.rag_and_auth_attacks

__all__ = [
    "prompt_attacks",
    "disclosure_attacks",
    "agency_attacks",
    "rag_and_auth_attacks"
]

