"""Password strength rules shared by the API and the admin (matches the signup form)."""

import re

from django.core.exceptions import ValidationError


class CharacterClassValidator:
    """Require an uppercase letter, a lowercase letter, a digit and a symbol."""

    checks = (
        (r"[A-Z]", "an uppercase letter"),
        (r"[a-z]", "a lowercase letter"),
        (r"[0-9]", "a number"),
        (r"[^A-Za-z0-9]", "a symbol"),
    )

    def validate(self, password, user=None):
        missing = [label for pattern, label in self.checks if not re.search(pattern, password)]
        if missing:
            raise ValidationError(
                f"Password must contain {', '.join(missing)}.", code="password_character_classes"
            )

    def get_help_text(self):
        return "Your password must contain an uppercase letter, a lowercase letter, a number and a symbol."
