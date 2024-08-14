.. _collect:

Data Collection
---------------

The entire process starts with collecting some initial data. This data should be
collected from :ref:`the recording device <recording>` using the same hardware and
recording settings that will be used for regular analysis.

Begin continuous recording with:

  .. code-block:: sh

    python3 -m apr -a monitor

Stop recording with:

  .. code-block:: sh

    # From the same terminal session (will likely corrupt current video)
    Ctrl+C

    # Signal to finish recording and exit
    python3 -m apr -a monitor -s

    # Signal to finish recording and wait for process to exit
    python3 -m apr -a monitor -S

    # Signal to stop immediately (will likely corrupt last video)
    python3 -m apr -a monitor -H

Recordings will be saved to ``./_workspace/rotating/``.

.. note::

   Clapping hands together is a great demonstration exercise. This can be set
   in ``config.yml`` with ``models: [clap]``.
