"""Run a small bilingual template demonstration."""

from .tools import BilingualTemplateManager


def main() -> None:
    manager = BilingualTemplateManager(
        [
            {
                "key": "confirmation",
                "english": "Hello {name}, your request {request_id} is confirmed.",
                "french": "Bonjour {name}, votre demande {request_id} est confirmée.",
            }
        ]
    )
    print(manager.render("confirmation", "fr", {"name": "Alex", "request_id": "R-1001"}))


if __name__ == "__main__":
    main()
