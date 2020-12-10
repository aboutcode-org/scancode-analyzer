.. _lic_detection_issue_types:

License Detection Issue Types
=============================

There are 4 types of license information as segregated by scancode-toolkit, based on rule types.

- text
- notices
- tags
- references.

Note that this is the order of precedence, as in in a file-region if there's one type higher in this
order and other several types lower in the order, the issue in the file-region is likely in the
former type. For example if one of the matches is matched to a `notice` rule and other matches
to `reference` rules, then the file-region in question is likely a License Notice.

These carry different importance of the license information present, and thus in case of license
scan errors, there are fundamentally different types of problems which may require different
approaches to solve them.

These are primarily segregated by the type of the rule matched, having the largest
``matched_length`` value, as a preliminary approach. It could also be determined by
NLP Sentence Classifiers (BERT), fine-tuned on the Scancode Rules.

Result Attributes
-----------------

In the results of the analysis, two of the attributes has this information:

    1. ``region_license_error_case``
    2. ``region_license_error_sub_case``

Here, the ``region_license_error_case`` attribute represents the main issue types in terms of how
clearly the license information is referred to. The 4 possible values of this are:

- `text` - :ref:`case_lic_text`
- `notice` - :ref:`case_lic_notice`
- `tag` - :ref:`case_lic_tag`
- `reference` - :ref:`case_lic_ref`

The ``region_license_error_sub_case`` attribute represents further types of cases in these.

.. _cases_sub_cases_table:

All Cases and their Sub-cases Table
-----------------------------------

.. list-table::
    :widths: 15 15
    :header-rows: 1

    * - ``region_license_error_case``
      - ``region_license_error_sub_case``

    * - ``text``
      - ``legal-lic-files``

    * - ``text``
      - ``non-legal-lic-files``

    * - ``text``
      - ``lic-text-fragments``

    * - ``notice``
      - ``and-or-except-notice``

    * - ``notice``
      - ``single-key-notice``

    * - ``tag``
      - ``tag-coverage``

    * - ``tag``
      - ``other-tag-structures``

    * - ``tag``
      - ``false-positives``

    * - ``reference``
      - ``lead-in-refs``

    * - ``reference``
      - ``low-coverage-refs``

    * - ``reference``
      - ``unknown-refs``

.. _case_lic_text:

License Texts
-------------

.. note::

    Value of ``region_license_error_case`` :- ``text``

License Text Files
^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``legal-lic-files``

- [More Than 90% License Words/Legal File]

Here the “is_license_text” plugin is used to detected if it’s a License File or Not, also “is_legal”
can be used for the detection, so an OR operation between these two cases.

So, if the full text is there in the “matched_text” we can go ahead and craft the rule from the
``matched_text``.

License Texts in Files
^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``non-legal-lic-files``

- [with less than 90% License Words]

In some cases, one of the “is_license_text” and “is_legal” tags, or even both could be False, and it
still could be classified as a License Text because

- the Rule it was partially matched was a license text rule
- the ``license-type`` sentence classifier designated it as a license text

Note: In this case how “is_license_text” and “is_legal” is calculated could be updated, based on
common mistakes.

Full text doesn’t exist in matched_text
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``lic-text-fragments``

Where the Full text doesn’t exist in matched_text and we have to go to/fetch the source file which
was scanned.

This is a common occurance in new unique license texts, which aren't fully present. Normally these
are detected by the ``3-seq`` matcher stage.

On scanning License Texts Present in scancode, by reindexing the license index to the state before
that particular text was added, we can see how the scan results look when entirely new license texts
are encountered.

So it seems as the license text is large, and varies a lot from already existing license texts, the
entire text doesn’t exist inside “matched_text”, so we have to go to the source file which was
scanned and add it from there.

For example these are the results for the “cern-ohl-w-2.0.LICENSE” file scanned by taking scancode
to a state where it wasn’t added.

Scan Result File has multiple partial matches

- "          it applies as licensed under CERN-OHL-S or CERN-OHL-W"
- "          licensed under CERN-OHL-S or CERN-OHL-W as appropriate."
- "      licensed under a licence approved by the Free Software"
- "          interfaced, which remain licensed under their own applicable"
- "      direct, indirect, special, incidental, consequential, exemplary,\n
  punitive or other damages of any character including, without\n
  limitation, procurement of substitute goods or services, loss of\n
  use, data or profits, or business interruption, however caused\n
  and on any theory of contract, warranty, tort (including\n
  negligence), product liability or otherwise, arising in any way\n
  in relation to the Covered Source, modified Covered Source\n
  and/or the Making or Conveyance of a Product, even if advised of\n
  the possibility of such damages, and You shall hold the"
- "  7.1 Subject to the terms and conditions of this Licence, each"
- "      You may treat Covered Source licensed under CERN-OHL-W as"
- "      licensed under CERN-OHL-S if and only if all Available"

Clearly the actual license has a lot more text, which we can only get by going to the source.

.. _case_lic_notice:

License Notices
---------------

.. note::

    Value of ``region_license_error_case`` :- ``notice``

Exceptions, Rules with Keys having AND/OR
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``and-or-except-notice``

Where there are multiple "notice" license detections, not of the same license name, in a single
file. These are often:

- dual licenses
- exceptions

These have multiple license detections and some times new combinations are detected, and has to be
added to the Rules.

Single key notices
^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``single-key-notice``

This is the general case of License Notice cases, so if it's a license notice case and doesn't fall
into the other license notice cases detailed below, then it belongs in this category.

These are often detected as License Notices are often unique in projects, and for these rules can be
crafted with fairly high confidence as almost always the entire text is present in "matched_text".

.. _case_lic_tag:

License Tags
------------

.. note::

    Value of ``region_license_error_case`` :- ``tag``

Wrong License Tag Detections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``tag-coverage``

Among all  “is_license_tag” = True cases, if match_coverage is less than 100, then it is a wrong
license detection, and as tags are small and matched_text almost always contains the whole tag, a
Rule can be created from these class of Problems.

This is the general case of License Tag cases, so if it's a license tag case and doesn't fall into
the other license tag cases detailed below, then it belongs in this category.

Other common Structures of Tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``other-tag-structures``

There exists specific Tags, for group of projects, and these are mostly found in source code files,
in the code itself.

Like for example::

    <small>License: <a href="http://www.fsf.org/licensing/licenses/fdl.html">GNU Free Documentation License (FDL)</a></small>

Or ``MODULE_LICENSE`` present in linux kernel source code.

We can cluster the data according to occurrences of same types of structures, and attributes used to
cluster/separate could be:

- Programming Language
- Type of Files?

Related Issue - https://github.com/nexB/scancode-toolkit/issues/707

Finding False Positives from License Tags Detections
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``false-positives``
    In this case, value of ``license_scan_analysis_result`` :- ``false-positives``

Now, the “is_license_tag” is obviously always true for these, but the “match_coverage” is always 100
in these cases. These are almost always wrongly detected by some handful of rules which has only the
words gpl/lgpl or like that. So we further narrow our search down to only 1-word rules having
is_license_tag = True.

But this also includes a lot of correct detections, which are correctly detected.

This classifying of “False Positives” from “Correct Tag Detection” is solely based on the
matched text, and should be solved by a BERT based sentence classifier. The binary classification
would be between false-positives and license-tags.

The data needed to train that model, which we can get from two places:-

1. The already existing scancode license rules, has a lot of examples of False Positives and
   Correct License Tags
2. More training data

We could make use of the classifier confidence scores to only look at ambigous cases only.

Issue to be noted -

In some cases some more lines above and below are needed to be added to these false_positive rules,
as the ``matched_text`` can be too general for a false positive rule. This could require
manual work.

.. _case_lic_ref:

License References
------------------

.. note::

    Value of ``region_license_error_case`` :- ``reference``

Those with low match coverages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``low-coverage-refs``

This is the most common type of license detection errors, as there exist a lot of
license references, and they can be added. These are also highly fixable problems, as almost always
the whole license reference is captured in ``matched_text``

We should separate these location wise, and add as new rules without any manual oversight.

This is the general case of License Reference cases, so if it's a license reference case and doesn't
fall into the other license reference cases detailed below, then it belongs in this category.

unknown file license references
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``unknown-refs``

In many cases the license that is referred to is in another file, and only the filename is given,
and not the license name. Example - "see license in file LICENSE.txt"

In these cases if there are more context/specific wording add these as new unknown rules.

So we separate these based on their matched_rules, i.e. if these are matched to an “unknown” or
similar kinds of non-explicitly named rules.

Other wise discard, as this is a issue to be handled separately, by implementing a system in
scancode where these links are followed and their license added.

Introduction to a License Notice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::

    Value of ``region_license_error_sub_case`` :- ``lead-in-refs``

There are cases where the RULE name begins with ``lead-in_unknown_``, i.e. these are known lead-ins
to licenses, so even if the exact license isn't detected, it can be reported that there is a
license reference here.

Here we could add to the Rulebase, the license reference, or as in the example case below, craft a
new rule by joining the two existing ones

Example case:-

``Dual licensed under`` is ``lead-in_unknown_30.RULE``

say there is another rule: ``MIT and GPL``

and the text we scan is : ``Dual licensed under MIT and GPL``

To Note: If they appear quite frequently, it is okay to craft a new rule. Because we cannot just add
all combinations of lead-ins and license names.

