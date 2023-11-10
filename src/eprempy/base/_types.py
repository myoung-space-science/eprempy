import typing

from . import _protocols


MeasurableType = typing.TypeVar('MeasurableType', bound=_protocols.Measurable)
"""Type variable representing explicitly measurable objects."""


MetricType = typing.TypeVar('MetricType', bound=_protocols.HasUnit)
"""Type variable representing objects with a unit."""


MeasuredType = typing.TypeVar('MeasuredType', bound=_protocols.Measured)
"""Type variable representing objects with data and a unit."""


MeasurementType = typing.TypeVar(
    'MeasurementType',
    bound=_protocols.Measurement,
)
"""Type variable representing measurement-like objects."""


ComplexType = typing.TypeVar('ComplexType', bound=_protocols.Complex)
"""Type variable for objects that implement the complex-valued protocol."""


RealType = typing.TypeVar('RealType', bound=_protocols.Real)
"""Type variable for objects that implement the real-valued protocol."""


SequenceType = typing.TypeVar('SequenceType', bound=_protocols.Sequence)
"""Type variable representing real-vauled sequence-like objects."""


ArrayType = typing.TypeVar('ArrayType', bound=_protocols.Array)
"""Type variable representing real-vauled array-like objects."""


ScalarType = typing.TypeVar('ScalarType', bound=_protocols.Scalar)
"""Type variable representing real-vauled scalar objects."""


