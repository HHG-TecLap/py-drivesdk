API Reference
==============

Controlling the supercars
*************************

Controller
~~~~~~~~~~~
.. autoclass:: anki.Controller
    :members:

Vehicle
~~~~~~~~
.. autoclass:: anki.Vehicle
    :members:

Scanner
~~~~~~~
.. autoclass:: anki.control.scanner.Scanner
    :members:



Vehicle models
**************

VehicleState
~~~~~~~~~~~~
.. autoclass:: anki.control.vehicle.VehicleState
    :members:

Lights
~~~~~~
.. autoclass:: anki.Lights
    :members:


Track models
************

TrackPiece
~~~~~~~~~~
.. autoclass:: anki.TrackPiece
    :members:

TrackPieceType
~~~~~~~~~~~~~~
.. autoclass:: anki.TrackPieceType
    
    .. autoattribute:: START
    .. autoattribute:: FINISH
    .. autoattribute:: STRAIGHT
    .. autoattribute:: CURVE
    .. autoattribute:: INTERSECTION

Lane support
************

BaseLane
~~~~~~~~
.. autoclass:: anki.BaseLane
    :members:

Lane3
~~~~~
.. autoenum:: anki.Lane3
    :members:

Lane4
~~~~~
.. autoenum:: anki.Lane4
    :members:

Exceptions
**********
.. automodule:: anki.errors
    :members: