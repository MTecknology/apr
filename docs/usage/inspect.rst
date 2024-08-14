.. _inspect:

Manual Inspection
------------------

After ``model.{pth,wav}`` are generated, the ``inspect`` action can be used to
manually review individual video (``.mkv``) files.

    .. code-block:: sh

       python3 -m apr -a inspect -i $path_to_mkv

This returns a list of frames where the trained noise was detected.

    .. image:: /images/inspect_single.webp
       :alt: Inspect run on a single file
       :width: 90%

These frames can then be reviewed/tagged using :ref:`the review utility <review>`
and then used :ref:`train <train>` an improved model.
