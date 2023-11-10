import abc
import re
import typing


class Part(abc.ABC):
    """Base class for parts of a symbolic expression."""

    __slots__ = ()


_PartType = typing.TypeVar('_PartType', bound=Part)


class Match(typing.Generic[_PartType]):
    """An object that represents the result of a RE pattern match."""

    def __new__(cls, result, context):
        """Check argument types."""
        if not isinstance(result, Part):
            raise TypeError(
                f"Result must be a Part"
                f", not {type(result)}"
            ) from None
        if not isinstance(context, (re.Match, typing.Mapping)):
            raise TypeError(
                f"Context may be a Match object or a Mapping"
                f", not {type(context)}"
            )
        return super().__new__(cls)

    def __init__(
        self,
        result: _PartType,
        context: typing.Union[re.Match, typing.Mapping],
    ) -> None:
        self.result = result
        """The result of the match attempt."""
        self._context = self._set_context(context)

    def _set_context(self, user: typing.Any) -> dict:
        """Normalize the instance context from user input."""
        if isinstance(user, re.Match):
            return self._set_from_match(user)
        if isinstance(user, typing.Mapping):
            return self._set_from_mapping(user)

    def _set_from_match(self, match: re.Match):
        """Set the instance context from a match object."""
        return {
            'start': match.start(),
            'end': match.end(),
            'string': match.string,
        }

    def _set_from_mapping(self, mapping: typing.Mapping):
        """Set the instance context from a mapping."""
        attrs = (
            'start',
            'end',
            'string',
        )
        return {k: mapping.get(k) for k in attrs}

    @property
    def start(self) -> int:
        """The starting index in `string` of the match."""
        return self._context['start']

    @property
    def end(self) -> int:
        """The ending index in `string` of the match."""
        return self._context['end']

    @property
    def string(self) -> str:
        """The target string."""
        return self._context['string']

    @property
    def remainder(self) -> str:
        """The unparsed portion of `string` after `end`."""
        return self.string[self.end:]

    def __bool__(self) -> bool:
        """Always true, like `re.Match`."""
        return True

    def __str__(self) -> str:
        """A simplified representation of this object."""
        attrs = {
            'result': 'result',
            'context': '_context',
        }
        return ', '.join(f"{k}: {getattr(self, v)}" for k, v in attrs.items())


class Factory(typing.Protocol):
    """Abstract protocol class for symbolic factories."""

    @abc.abstractmethod
    def parse(self) -> Match: ...


@typing.runtime_checkable
class FactoryType(Factory, typing.Protocol):
    """Runtime protocol for symbolic factories."""


