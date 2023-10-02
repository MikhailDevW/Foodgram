import re
from django.core.exceptions import ValidationError


def slug_validator(value):
    pattern = r'^[-a-zA-Z0-9_]+$'
    if re.match(pattern, value) is None:
        raise ValidationError(
            'Упс... Слаг должен содержать только буквы и цифры.'
        )
